# Nitemare 3D — RE-MAX NEXT 7: `REP MOVS` pointer provenance a `OBJECT+0x18`

**Dátum:** 20. október 2026  
**Metóda:** striktne statický, read-only audit dvoch pôvodných DOS EXEPACK binárok z používateľského súkromného archívu `N3D-version-lab-ready.zip`. Žiadne spustenie Nitemare 3D, patchovanie originálu, screenshot parity ani GitHub push.  
**Adresovanie:** `IMG:xxxxx` = offset v originálnom rozbalenom, nerealokovanom, headerless MZ load image; nie DOSBox-X runtime `CS:IP`.

## 1. Identita originálov a rozsah overenia

| Build | Rozbalený image | SHA-256 rozbaleného originálu |
|---|---:|---|
| DOS 1.9 | 171 296 bajtov | `e29a8d058fdf3033241f4f711bca273fb168d750f8f972047e1be8f3d946529e` |
| DOS 2.0 | 171 360 bajtov | `e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297` |

Verifier kontroluje presnú identitu pred každou adresovou interpretáciou. Rekonštruuje pôvodné EXEPACK bajty v pamäti a používa GNU objdump na 16-bitovú lineárnu pomocnú disassembláciu. **29 `REP MOVS` miest na build je lineárny census do začiatku CRT entry, nie súbor všetkých vykonateľných pamäťových writerov.** Nástroj odmieta iný SHA a nemodeluje DOS runtime.

## 2. Uzavretie pôvodu cieľového registra pre 29 miest

NEXT 6 evidoval 29 doslovných kandidátov (`REP MOVS`) na build; 5 zásobníkových a jedna 40-bajtová kopírovacia operácia už boli lokálne typované. **Zostávalo 23 inštrukčných miest bez typovania cieľového registra.** Teraz je pôvod bezprostredného cieľa pre všetkých 29 miest lokálne klasifikovaný. Zároveň 8 dvojíc `MOVSW/MOVSB` tvorí 8 kombinovaných operácií, takže vzniká **21 logických kopírovaní** na build.

| Rodina | REP sites/build | Lokálna cieľová sémantika | Výhrada |
|---|---:|---|---|
| `STACK_WORK_BUFFER` | 5 | pracovný rámec cez `SS:BP`, `ES=SS` | globálne aliasy sa nevyvodzujú |
| `FIXED_DS_40` | 1 | `DS:41DE`, DOS2 `DS:41E0`, 40 B | známa DS oblasť, nie automaticky objektová |
| `FIXED_DS_STRING` | 4 | `DS:3464` DOS1.9, `DS:3466` DOS2; text/append | NUL scan bez celoprogramového limitu |
| `FIXED_DS_16` | 2 | `DS:4144`, 16 B | presná lokálna dĺžka |
| `LOCAL_FRAME_27` | 2 | `BP`-lokálny cieľ s posunom po 41 B | identifikácia zásobníka vyžaduje invariant `DS=SS` |
| `ALLOCATOR_90` | 2 | `malloc(0x5A)` → alokovaný DS pointer → 90 B | nutná platnosť allocator kontraktu/disjointness |
| `GLOBAL_TEXT_TO_STACK` | 10 | päť C reťazcov → zloženie v `BP-0x102` | iba pre nepozmenené zdrojové texty a `DS=SS` |
| `RECORD_TEXT_TO_STACK` | 2 | FAR reťazec `record+0E/+10` → `BP-0x2C` | dĺžka vstupného textu nie je globálne ohraničená |
| `RECORD_FARPTR_41` | 1 | 41 B späť do `record+0E/+10` | vlastník/rozsah FAR pointera ostáva transitive OPEN |
| **Spolu** | **29** | **21 logických prenosov** | globálna alias-free parita nepreukázaná |

### Prečo staré „13 dynamických cieľov“ neplatí

Pri desiatich miestach `A754..A838` (v DOS2 `A790..A874`) je FAR pointer **zdroj**, nie cieľ. Kód použije `REPNE SCAS`, potom `XCHG SI,DI` a segmentové `PUSH/POP` tak, že cieľom `REP MOVS` je lokálny textový buffer `BP-0x102` pri štandardnom `DS=SS`.

Rovnaké obrátenie smeru vysvetľuje dve miesta `E210/E214` (DOS2 `E24C/E250`): kopírujú vstupný text z FAR pointera do 44-bajtového lokálneho buffera `BP-0x2C`, nie do herného OBJECT poolu. Reálne dynamicky cielený `REP MOVS` s neuzavretým transitive vlastníkom je preto v tejto evidovanej množine **jeden na build**, `IMG:E268` (DOS2 `E2A4`). Toto nie je tvrdenie, že ostatné typy nikdy nemôžu aliasovať alebo že neexistujú iné kopírovacie helpery.

## 3. Päť inicializovaných zdrojových FAR pointerov, presný počet bajtov

V DOS1.9 majú všetky nižšie uvedené FAR pointery segment `276Dh`; v DOS2 `2771h`. Offsets pointerov a cieľov zostali rovnaké.

| Zdrojový descriptor DS | Ukazuje na DS | Vyhradená iniciačná oblasť | Skutočný C reťazec vrátane NUL | Význam |
|---|---|---:|---:|---|
| `0F28/0F2A` | `0EA6` | 130 B | 130 B | text portálu |
| `0D72/0D74` | `0D5E` | 20 B | 19 B | červený pentagram |
| `0D8C/0D8E` | `0D76` | 22 B | 21 B | zelený pentagram |
| `0DA4/0DA6` | `0D90` | 20 B | 20 B | modrý pentagram |
| `0DBE/0DC0` | `0DA8` | 22 B | 22 B | žltý pentagram |

Report obsahuje iba číselné metadáta a SHA-256 textov, nie pôvodné komerčné textové bajty. Overených je všetkých 16 hypotetických kombinácií štyroch voliteľných pripojení. Prvá kopírovaná správa má 130 B vrátane NUL; append nahrádza starý NUL, takže maximálna dĺžka je:

`130 + (19−1) + (21−1) + (20−1) + (22−1) = 208 B`

Lokálne `ENTER 0x102` poskytuje 258 B pracovného rámca. Rezerva je preto **50 B**, ak zostane pôvodný text nemenný a segmentové invarianty platia. Štaticky to uzatvára **lokálnu bezpečnosť dĺžky originálnych textov**, nie ochranu pred zmenou ich zdrojových bufferov.

## 4. Posledný record+0E/+10: zúženie na editor UI

| Dôkaz | DOS 1.9 | DOS 2.0 |
|---|---|---|
| Editor vstup | `IMG:E1A2` | `IMG:E1DE` |
| Priamy near volajúci | `IMG:ECC3` | `IMG:ECFF` |
| Caller odovzdáva | `ES:SI` | `ES:SI` |
| Stride volajúcej tabuľky | 18 B (`ADD SI,12h`) | 18 B |
| Vetva | typ `record+05 == 4` | rovnaká |
| Buffer záznamu | FAR `record+0E/+10` | rovnaký |
| Final `REP MOVSD*10 + MOVSB` | `IMG:E268` = 41 B | `IMG:E2A4` = 41 B |

Tento pôvodný near-caller je silným **lokálnym dôkazom UI textového editora**, nie všeobecného OBJECT-kopírovania. Ešte musíme preveriť každý writer FAR polí `+0E/+10` vo všetkých konkrétnych UI záznamoch, chýbajúce nepriamo volané cesty, rozsah editovateľného reťazca a všetky chyby alokácie. Nepochybné je poradie `editor copy-in → text spracovanie → 41-byte copy-out`; bez úplného pointer owner grafu nemožno vyhlásiť globálnu non-alias bezpečnosť.

## 5. Vzťah k `OBJECT+0x18`

| Operácia | DOS 1.9 | DOS 2.0 |
|---|---|---|
| Projekčný zápis WORD | `IMG:0B47A` | `IMG:0B4B6` |
| Damage čítanie WORD | `IMG:08592` | `IMG:0859C` |
| Referenčná hĺbka | `DS:4550` | `DS:4552` |

NEXT 7 **nepridal druhý potvrdený writer `OBJECT+0x18`**. Miesto toho zúžil, ktoré pôvodne nerozlíšené `REP MOVS` vôbec môžu byť predmetom ďalšieho transitive owner auditu. Počet typovaných `REP MOVS` tak nemožno používať ako dôkaz, že `OBJECT+18` je globálne zapisované iba raz: ďalšie prípadné aliasy cez near/far helpery, priame `MOV`, výstavbu poolu, SAVE/LOAD, heap alebo nestandardné stavy zostávajú otvorené. Stale-depth accepted-hit tiež zostáva **OPEN**.

## 6. Reprodukovateľnosť a hranica platnosti

```bash
python3 source/next7_verify.py \
  --archive /private/N3D-version-lab-ready.zip \
  --out evidence
N3D_VERSION_LAB_ARCHIVE=/private/N3D-version-lab-ready.zip \
  python3 -m unittest discover -s tests -p 'test_next7.py' -v
```

Originály sú kontrolované presným SHA-256. Verifikátor pracuje iba s číselnými opcode/metadátovými dôkazmi a *neukladá/neredistribuuje* originálny obsah EXE. Testy sú naviazané na súkromné originály, nie na syntetický substitút. `OBJdump` lineárny prechod nie je úplným recursive CFG.

**Status:** 29/29 `REP MOVS` lokálne roztriedených; 23/23 pôvodných neotypovaných miest dostalo ohraničenú zdrojovo-cieľovú klasifikáciu; päť statických textov bezpečne zložených do 258 B buffera v 16 hypotetických kombináciách; konkrétny UI writer 41 B lokalizovaný. Celoprogramový `OBJECT+18` writer/read/alias census, INT63 externí AH klienti, DEMO RNG runtime a celková 100 % parita **neuzavreté**. Nevyvodzovať nové percento znalostí z počtu lokálnych uzáverov.
