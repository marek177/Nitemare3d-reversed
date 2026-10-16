# Nitemare 3D — RE MAX v0.58: GUARD smrť, skóre, zvuk a výber variantu

**16. október 2026.** Zákaz zámien: `ORIGINAL STATIC` je dôkaz z pôvodných bajtov, nie dôkaz runtime 1:1. Táto lokálna v0.58 nadväzuje na v0.57, nie je aktuálnou GitHub verziou a nemení percento celkovej parity.

## 1. Identita pôvodných binárok

| Profil | Identita (SHA-256) | Rozsah | Adresovanie |
|---|---|---|---|
| DOS 2.0 | `e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297` | 171 360 B | Unpacked unrelocated load image `IMG:xxxxx` |
| Win16 1.10 | `12fe5168783446275802e0e947898261b5eca6b88288f3a895fc1faa4c544481` | 230 400 B | NE logical segment 3 `NE3:xxxx` |
| Win16 alt | `144e96bb649c5463d440c343ad982ed8e5f143e788c9af08bbb890fcd1b3db22` | 230 224 B | NE logical segment 3 `NE3:xxxx` |

Všetky tri presné identifikátory boli znovu skontrolované čítaním **pôvodných súborov**, bez spustenia hry. Pôvodné bajty ani originálne súbory nie sú v analytickom balíku.

## 2. Nové uzavretie: tri triedové dispatchery

| Funkcia | DOS IMG | Win16 NE3 v1.10 | Win16 NE3 alt | Dĺžka |
|---|---|---|---|---:|
| Skóre `OBJECT+06` triedy `08..20` | `84FE` | `9F10` | `9E62` | 145 B |
| Death-event selector `08..1F` | `9CF2` | `B6A0` | `B5F2` | 194 B |
| Event selector pri nonfatal `old GUARD.state=07` | `9EB4` | `B862` | `B7B4` | 236 B |
| Variant na lethal vetve | `9FB4` | `B94E` | `B8A0` | 100 B |
| Variant na nonlethal vetve | `A018` | `B9B2` | `B904` | 100 B |

Pri každom z 5 originálnych tiel sú po maskovaní **iba presne určených operandových bájtov, tabuľkových WORD targetov a jediného padding bajtu** inštrukcie totožné naprieč tromi buildmi. **775 B × 3 buildy** bolo porovnaných, 219 triedových skokových smerovaní bolo fyzicky dekódovaných a všetky tri table-target relatívne mapy zodpovedajú.

Doslovne: skóre testuje `unsigned(class-8) <= 0x18` a jeho 25-prvková CS jump-tabľka; oba event selectory testujú `unsigned(class-8) <= 0x17` (24 prvkov). Mimo rozsah vracajú `0` (skóre alebo event selector). **Nulový event selector ešte nie je dôkaz nulového zvukového výstupu.**

### Kompletná matica hraničných tried a pevne zakódovaných návratov

Stĺpce obsahujú 16-bit **signed skóre** a číselný *event selector* (nie názov súboru). Symbol `rng%N+K` označuje práve jeden **lokálny** odber v danej zvukovej funkcii, pokiaľ sa na ňu vykoná volanie. Pre všetkých 256 tried je CSV.

| Trieda hex | Skóre | Lethal event selector | State-7 event selector |
|---|---:|---|---|
| `08` | 25 | 35 | 34 |
| `09` | 75 | 8 | rng%3+56 |
| `0A` | 50 | 7 | rng%3+56 |
| `0B` | 100 | 36 | 59 |
| `0C` | 250 | 4 | 20 |
| `0D` | 150 | 19 | 21 |
| `0E` | 200 | 14 | 16 |
| `0F` | 100 | rng%3+11 | rng%2+54 |
| `10` | 100 | rng%3+11 | rng%2+54 |
| `11` | 0 | 0 | 6 |
| `12` | 150 | 7 | 63 |
| `13` | 150 | 7 | 60 |
| `14` | 200 | 35 | 0 |
| `15` | -1000 | 0 | 0 |
| `16` | 1000 | 0 | 18 |
| `17` | 100 | 70 | 72 |
| `18` | 200 | 70 | 71 |
| `19` | 0 | 0 | 0 |
| `1A` | 25 | 74 | 73 |
| `1B` | 100 | 2 | 13 |
| `1C` | 100 | 2 | 13 |
| `1D` | 250 | 9 | 56 |
| `1E` | 250 | 70 | 61 |
| `1F` | 200 | 70 | 61 |
| `20` | 50 | 0 | 0 |

Nové dôsledky:

1. **Trieda `15` (hex) má skóre −1000** (`0xFC18`) v každom builde. Pri fatal vetve `CWD` rozšíri návrat AX do DX:AX a `ADD`/`ADC` pripočíta signed score k dword skóre. Ak bude táto vetva dosiahnutá, nie je správne klampovať skóre na nezáporné hodnoty. Cesta k bežnému usmrteniu triedy `15` však nie je potvrdená: samotný scalar pre túto triedu po špeciálnom FAR callbacku nastaví poškodenie na nulu (`DOS IMG:8628..8637`). Pri GUARD HP>0 bez ďalších callback-side-effects preto neprejde lethal testom.
2. **Trieda `20` (hex) má +50 bodov**, ale mimo rozsah dvoch SFX rozbočovačov vyberie default selector `0`. To je konkrétny verziovo identický fallback, nie potvrdená existencia konkrétneho GUARD v hre.
3. Smrteľná zvuková vetva tried `0F/10` vyberá `11 + RNG%3`; nonlethal starý state `07` používa pri triedach `09/0A` `56 + RNG%3` a pri `0F/10` `54 + RNG%2`. Tieto odbery nie sú vykonávané v každom zasiahnutí automaticky. Celkové vnorené SFX effects môžu mať ďalšie volania.

## 3. Poradie pri lethal vetve (DOS `IMG:5F74`, Win16 `NE3:80F8`)

```text
DamageScalar(...)          // aspoň jeden RNG pri bežnom vstupe do scalara
if GUARD.HP <= low8(damage):
    GUARD.HP = 0
    variant = FatalVariant(GUARD+12, descriptor+59, slots+4B)
    if modeWord != 1:     // DOS DS:4190 / Win16 DS:4C26
        DeathEventSelector(OBJECT.class)   // môže mať vlastný RNG
    // initial object/seq update: descriptor selector + returned variant
    score16 = ScoreByClass(OBJECT.class)   // signed: trieda 15 -> -1000
    scoreDWORD += sign_extend(score16)    // 32-bit ADD/ADC
    DispatchEvent(4)                      // presné nested účinky nezavreté
    *(farptr(OBJECT+0C)+1) = GUARD+0D    // lokálny zápis; význam MAP po LOAD otvorený
    return
```

Dôkazové adresy DOS: `5F88` damage; `5F9C` lethal compare; `5FA3` nulovanie HP; `5FAD` fatal variant; `5FB8` mode compare a `5FC7` sound; `6007` aktualizačná rutina; `6016` score; `601E` signed `CWD`; `601F/6023` 32-bit `ADD/ADC`; `6029` event; `6034..603F` finálny pointerový zápis. Win16 tomu zodpovedajú priame operandy a identické funkčné cesty, no jednotlivé absolútne offsety sú build-specific.

**Nesmie sa tvrdiť, že modeWord=1 potlačí skóre alebo animačnú vetvu.** Lokálne preskakuje volanie death-event selectora. Vonkajšie a prípadné callback efektové volania sa ešte majú analyzovať.

## 4. Odlišné selektory pre lethal a nonlethal

Dve 100 B rutiny majú rovnaký tvar a rozdielne deskriptorové polia:

| Kontrakt | Fatal variant | Nonfatal variant |
|---|---|---|
| Rýchly návrat 7 bez RNG vyžaduje | `GUARD+12==0` a descriptor byte `+59!=0` | `GUARD+12==0` a descriptor byte `+49!=0` |
| Alternatíva | `RNG()%7 -> 0..6` | `RNG()%7 -> 0..6` |
| Ak je vybraný slot nulový | retry pri descriptor byte `+4B + 2*i == 0` | retry pri `+3B + 2*i == 0` |
| Matem. mŕtvy porovnávací skok | `RNG()%7 == 7` | `RNG()%7 == 7` |

Lethal cesta nemení `GUARD+12` pred výberom variantu; ten môže použiť no-RNG fast slot 7 alebo vykonať ľubovoľný kladný počet RNG odberov. Pri nonlethal vetve je dôkaz významne silnejší: **ak sa vykoná volanie variant selectora zo zásahového wrappera, pred ním sa bez ďalšieho FAR callbacku nastaví `GUARD+12=8`.** Teda fast no-RNG branch je v tejto priamo analyzovanej nonlethal trase nedosiahnuteľný; musí dôjsť aspoň k jednému odberu RNG (a môže dôjsť k opakovaniu). `strategy=4` sa do selectora vôbec nedostane, hoci DamageScalar už RNG spotreboval.

Pri `GUARD old state=7` sa pred nonfatal odpočítaním HP podmienene zavolá **state-7 event selector**, čo môže spotrebovať ďalší RNG v triedach vyššie. Nie je možné nahradiť celú vetvu jedným náhodným rozhodnutím.

Ak všetkých sedem slotových nízkych bajtov zostáva nula a rýchla vetva nie je dostupná, lokálny assembler nemá dokončovaciu vetvu (opakujúce RNG). Je to **symbolická patologická podmienka**, nie dokázaná bežná herná chyba. Diagnostické modely používajú bezpečnostný limit/exception, ktoré **nie sú** súčasťou originálneho správania.

## 5. Nové zúženie „selector 0 = silent?“ (DOS-only)

`IMG:C686` prijíma vybraný číselný SFX selector a pred prehrávaním testuje:

- `DS:414E` (globálny enable-byte); ak je 0, okamžitý návrat;
- `BX = selector * 6` a `WORD [DS:3F64 + BX]`; ak je 0, okamžitý návrat;
- pri nenulových hodnotách nasledujú ďalšie rozhodnutia a volania do zvukového backendu.

Pre **selector 0** sa teda testuje presne `DS:3F64` — samotná nula ako ID nie je dostatočný dôkaz ticha. Potrebný je SND slot0 + loader writer/read audit a Win16 ekvivalent, potom runtime iba pre autentický zvukový výstup.

## 6. Čo bolo skutočne overené

- 3/3 exact SHA-256 originály, prečítané lokálne; žiadna emulácia hry.
- 5 funkčných tiel s dĺžkami 145/194/236/100/100 B naprieč 3 buildmi, rozdiely iba na explicitných operandoch/tabuľkách/jednom nevykonanom padding bajte.
- 73 skokových cielení na build = **219 fyzicky dekódovaných triedových cieľov**; skóre/event výsledky boli kontrolované proti nezávislému referenčnému poľu.
- Zásahový wrapper má statické opcode svedectvá pre HP gate, conditional death-event a signed 32-bit add; vo všetkých troch buildoch boli overené aj priame FAR target-offset volania (Win16 NE relocation detail ešte nie je uzavretý).
- V0.58 `variant` fast path, `%7` RNG rejection a dve rozdielne základné deskriptorové tabuľky; úplný dosah databáz deskriptorov nebol tvrdený.
- 22 Python unit testov + 1 C++17 synthetic executable; pôvodné herné runtime merania **0**.

## 7. Otvorené hranice RE MAX v0.59

Najvyššiu hodnotu má statický `GUARD+12` úplný writer/reader audit, class `15` FAR callback a celá `OBJECT+18` cache/generation závislosť. Spolu s dátovým auditom skutočných IMG sequence deskriptorov môžu rozhodnúť, či fast/no-RNG a retry vetvy sú prirodzene dosiahnuteľné. `UNKNOWN_FRONTIER_v058.csv` má presné nasledujúce úlohy.

**Záver:** výsledok uzatvára lokálne skórovacie, audio-selektorové a variantné rozhodovacie funkcie, nie celé GUARD death, nie 100 % RNG, ani dokončený zvukový/pixelový runtime. **Percento celkovej 1:1 parity sa nemení.**
