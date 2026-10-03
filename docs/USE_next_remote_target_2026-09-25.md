# USE / interakcie — ďalší audit: cieľová bunka, diaľkové dvere a otvorené trezory

**Dátum: 25. 9. 2026**

## Výsledok a rozsah dôkazu

Vznikli dva nové samostatné C++20 modely a tri testy: výber cieľovej bunky USE, plán vybraných zápisov diaľkových dverí a syntetická kontrola spojenia s predchádzajúcou opravou inventára. Pri čítaní reportu USER.SAV sa zároveň našiel nevyjasnený rozdiel v tvrdeniach o inicializácii `0x51A5`.

**Nie je to nová disassemblácia NITE3W.EXE.** V lokálnych súboroch boli iba tri výstupy predchádzajúceho auditu. Verejná stránka RGB Classic Games ponúka Win16 shareware 1.8, nie dôkaz totožnosti s cieľovým EXE 1.10. Pokus o získanie ZIP súboru zlyhal: lokálny curl nemohol vyriešiť názov hostiteľa a samostatný download nástroj tiež zlyhal. Ani úspešné stiahnutie 1.8 by samo neoverilo binárku 1.10. Strom druhého repozitára `Nite3d-win3.11` obsahoval audit a model časovania, nie potrebný EXE/disassembly.

Nové výsledky preto označujeme ako **kontrolu reportov**, **odvodenie medzi reportmi** alebo **test moderného modelu**. Ich staršie štítky VERIFIED_EXE sa tu neopätovne necertifikujú.

## 1. Diaľkové dvere: prijatie príkazu nie je to isté ako vykonanie pohybu

Report `REMOTE_DOORS_AND_DOS_CROSSCHECK_2026-09-22.md` uvádza, že príkazy `0x1E/0x1F` filtrujú dverové záznamy podľa triedy pripojeného objektu `0x3B/0x3C`, skupiny `OBJECT+1` a číselného stavu. Príkazová vetva zapíše `door+0x14 = 1` pred volaním helpera `3:188A`.

Report `nite3w_user_sav_story_flags_2026-09-23.md` zase uvádza, že helper `FUN_1010_188A` pri nenulovom `0x51AB` predčasne končí. Toto je spoločný príznak súvisiaci aj so skriptovaným režimom E1M7, nie vlastnosť konkrétneho dverového záznamu.

Ich spojením dostávame nasledujúci **model zdokumentovaného výrezu**:

| Príkaz | Vybraný stav pred volaním | `51AB` | Zápis aktivácie v callerovi | Model stavu po helperi |
|---|---|---|---|---|
| `0x1E` | 1 alebo 3 | 0 | 1 | 2 |
| `0x1F` | 0 alebo 2 | 0 | 1 | 3 |
| `0x1E` | 1 alebo 3 | nenulové | 1 | pôvodný stav |
| `0x1F` | 0 alebo 2 | nenulové | 1 | pôvodný stav |
| ktorýkoľvek z týchto dvoch | 4 alebo iný nevybraný stav | ľubovoľné | bez zápisu týmto výrezom | pôvodný stav |

Zachovanie skoršieho zápisu aktivácie pri predčasnom návrate je **odvodenie z poradia uvedeného v dvoch reportoch**. Priame overenie celého callera a callee v presne identifikovanej binárke zostáva otvorené. Rovnako nejde o tvrdenie, že každá kombinácia testovacích vstupov je v bežnej hre dosiahnuteľná.

Konkrétny syntetický prípad prešiel testom:

```text
Príkaz 0x1E, trieda 0x3B, zhodná skupina 0:
  pred: state=1, activation=77, story51AB=1
  po modelovaných zápisoch: state=1, activation=1
  operácia so skupinovým príznakom: stále PENDING
```

Číslo 77 je zámerne testovacia hodnota; nie je tvrdením o normálnom stave originálu.

## 2. Stav 4 nesmie zaniknúť pri zjednodušení na otvorené/zatvorené

`USE_INTERACTION_RE.md` uvádza číselné stavy 0 a 4 ako priechodné pre kolízny helper. Diaľkové príkazy podľa druhého reportu vyberajú 1/3 a 0/2. **Priechodnosť a oprávnenie na prechod diaľkovým príkazom sú rozdielne otázky.**

Nový model preto uchováva stav ako číslo a pre stav 4 neplánuje prechod ani zápis aktivácie. Nedáva stavom všeobecné názvy Open/Closed. Test prešiel cez všetkých 65 536 vstupných hodnôt 16-bitového stavového API pri oboch príkazoch a oboch hodnotách brány. To je test odolnosti moderného API, nie dôkaz existencie 65 536 herných stavov.

## 3. Skupinová maska nie je zoznam skutočne otvorených dverí

Zdrojový report výslovne uvádza zmenu bitu `0x51A4` aj vtedy, keď sa nezmenil žiadny zhodný fyzický dverový záznam. Implementácia teda nesmie automaticky podmieniť túto operáciu počtom zmenených dverí.

Dostupné formulácie používajú slovo „toggle“, ale neposkytujú konkrétnu inštrukciu zápisu pre každý príkaz. V tomto balíku sa preto **nevymýšľa XOR ani OR/AND** a do `0x51A4` sa nič nezapisuje. `groupFlagUpdateRemainsPending` explicitne označuje chýbajúcu operáciu; nemá význam „príkaz je hotový“.

Odmietnutie indexu skupiny mimo 0..7 je nová bezpečnostná podmienka bajtovej masky. Nie je to zistenie o originálnom správaní pri poškodených dátach a neznamená to osem pomenovaných kariet v hre. Overenie karty pri vstupe do terminálu je oddelené od neskoršieho vykonania príkazu.

Zvuky `0x25/0x26`, časovanie, animácia, prekážky, MAP zápisy a kanónové príkazy nový model nevykonáva.

## 4. Cieľová bunka USE: 252 preskokov pri nedostatočnej modernej kontrole hraníc

Report uvádza lineárne delty podľa oktantu:

```text
[-64, +1, +1, +64, +64, -1, -1, -64]
```

Model `resolveUseTarget` používa túto smerovú väzbu a zvlášť kontroluje výsledné X a Y. Neprepočítava plávajúci uhol na pôvodný oktant, pretože tento ďalší prevod nie je predmetom modelu.

Test všetkých **64 × 64 × 8 = 32 768** kombinácií platnej zdrojovej bunky a oktantu dal:

| Výsledok | Počet |
|---|---:|
| Platná susedná bunka | 32 256 |
| Cieľ mimo mapy pri geometrickej kontrole | 512 |
| Z týchto odmietnutí by samotný lineárny rozsah 0..4095 nesprávne prijal | 252 |

Príklad: z `(63,10)` pri oktante 1 musí moderné bezpečné API oznámiť cieľ mimo mapy. Samotné `index + 1` však ukáže na `(0,11)`, čo je platný prvok poľa, ale nesprávny geometrický sused.

Počet 252 je `63 riadkov × 2 východné oktanty + 63 riadkov × 2 západné oktanty`. Horné a dolné preskoky už odmieta aj kontrola lineárneho rozsahu.

**Nie je to dôkaz 252 chýb v originálnej hre ani v aktuálnej hlavnej slučke portu.** Originál pracuje so segmentovaným ukazovateľom a môže sa spoliehať na nepriechodný okraj dát. Ide o test nebezpečného zjednodušenia pri budúcej integrácii.

Offset je počítaný voči runtime MAP bufferu, bez archívnej hlavičky. Neplatné zdrojové súradnice sa kontrolujú ešte pred sčítaním, vrátane INT32_MIN/MAX, aby nevzniklo pretečenie moderného C++.

## 5. Nový problém v zdrojoch: nevyjasnená inicializácia kanónového príznaku

V `nite3w_user_sav_story_flags_2026-09-23.md` sú dve tvrdenia:

- Úvod mapuje počiatočnú sekvenciu `01 00 00 00 00 00 00 00` na adresy `0x51A4..0x51AB` pri `FUN_1010_0EF6`. Z toho pre `0x51A5` vyplýva 0.
- Riadok tabuľky pre `0x51A5` zároveň uvádza inicializáciu na 1.

Môže ísť o rôzne fázy inicializácie, napríklad nový session a neskoršie načítanie levelu. **Report ich však pri druhom tvrdení neodlišuje.** Je to konflikt alebo nedostatočne určená životnosť v dokumentácii, nie dôkaz chyby EXE.

Na uzavretie treba konkrétne writery do `0x51A5` a ich poradie pri new game, level load a LOAD. Nový model nedáva kanónom žiadnu predvolenú hodnotu. Strojovo čitateľný záznam je v `evidence/source_conflicts.json`.

## 6. SAFE/TRUNK: register namiesto vymysleného dokončenia

Reporty dokladajú smerovanie objektových typov `0x26/0x27` do `3:AD9E` a kombinačný prompt pri type `0x26`. To neuzatvára ani jeden celý handler.

`evidence/safe_trunk_register.json` oddeľuje uvedené kotvy od otvorených otázok: výber kombinácie podľa epizódy/levelu/variantu, spôsob porovnania, zrušenie a zlé zadanie, stavové polia, odmena, opakované otvorenie, zápisy do MAP a save/load. Samotná prítomnosť reťazcov `01532`, `080993`, `372535` nedokazuje ich priradenie ani správnosť číselného parsera odstraňujúceho úvodné nuly.

Na základe reportu nebol pomenovaný žiadny ďalší neznámy FUN symbol ako nový binárny objav. Kód trezoru ani odmeny sa nevymýšľali.

## 7. Skutočne vykonané testy

Finálna verzia bola kompilovaná so `-Wall -Wextra -Wpedantic -Werror`.

| Test | Kontroly v jednom behu | Výsledok |
|---|---:|---|
| Cieľová bunka, hranice, neplatné oktanty/súradnice | 1 147 907 | 0 zlyhaní |
| Výber diaľkových záznamov, stavy, skupiny, brána 51AB | 1 703 692 | 0 zlyhaní |
| Syntetické spojenie s predchádzajúcou lokálnou opravou | 11 | 0 zlyhaní |

GCC 14.2 a Clang 17 × Debug/Release/UBSan × tri testy: **18 úspešných behov**. Samostatný Release CMake/CTest projekt: **3/3 prešli**. Kontroly používajú vlastný CHECK, nie runtime assert, preto nezanikajú pri `NDEBUG`.

Prvý vývojový zápis nového testu mal lexikálnu chybu `0x1E+c`; zmenila sa na `0x1E + c`. Pôvodné chybové logy sú zachované v `logs/development/`. Nejde o zistenie v prevzatom kóde používateľa. Finálne logy sú osobitne v `logs/`.

Neuskutočnilo sa spustenie originálu, grafický SDL beh, MSVC/Windows build, úplný build repozitára ani meranie pokrytia jeho všetkých funkcií. Test modelu voči explicitnej tabuľke z reportu nie je nezávislé potvrdenie reportu pôvodnou hrou.

## 8. Percentá a stav integrácie

Predchádzajúce **80–90 %** zostáva iba historickým pracovným intervalom, nie aktuálnym meraním. Tento krok percento statickej analýzy EXE nezvyšuje.

Pribudli konkrétne testované modely, rozlíšenie neúplných efektov príkazu, kontrola hraníc a odhalený rozpor zdrojov. Nepribudol priamy assemblerový dôkaz k SAFE/TRUNK ani úplný dverový automat. GitHub sa nemenil a hlavná slučka portu sa týmto balíkom neopravila ani nerozšírila automaticky.

## Zdroje

Presné repozitárové cesty a Git blob SHA z aktuálnych čítaní sú v `evidence/sources.json`. Ide o provenienciu prečítaných reportov, nie tvrdenie, že bol získaný zodpovedajúci EXE.

1. `docs/USE_INTERACTION_RE.md`, blob `5c03321b2cf24641e9aeb8dca50f5f2e5abe5692`.
2. `docs/REMOTE_DOORS_AND_DOS_CROSSCHECK_2026-09-22.md`, blob `c1a07b2d24ebdec122345004fa022661e0f9eb3b`.
3. `analysis/nite3w_user_sav_story_flags_2026-09-23.md`, blob `cf14797841707cbfac65b7d47ad85d11375a2188`.
4. Predchádzajúci lokálny balík `USE_interakcie_audit_2026-09-25.zip`, jeho opravené hlavičky v `prior_fix/`.
5. Strom `marek177/Nite3d-win3.11` na revízii `791394730187ae0ded48e423fd11aa0d68f70f10`.
6. RGB Classic Games, https://www.classicdosgames.com/game/Nitemare-3D.html — iba hľadanie alternatívnej binárky; žiadny bajtový dôkaz nebol získaný.