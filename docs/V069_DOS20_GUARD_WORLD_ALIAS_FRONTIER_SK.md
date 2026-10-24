# Nitemare 3D — V069: GUARD41 terminal / WORLD alias, interakčná deaktivácia a bulk-copy frontier

**20. október 2026.** Revízia pôvodných, hashovo identifikovaných **DOS V1.2 a DOS V2.0 MZ EXE** + nezávislé opätovné vyhodnotenie starších autentických **DOS V2.0 V067 CPU/W traceov**. **Nevznikol nový runtime beh originálnej hry a nebola preukázaná originál–remake 1:1 parita.**

## 1. Pôvodné binárky a rozlíšenie adresovania

| Originálny súbor | SHA-256 |
|---|---|
| DOS V1.2 `N3D-12.exe` | `f7074660ed26525d2cc5ccd16a6e5ac011f29aaf819dc8ca24ebe39f0fd793e5` |
| DOS V2.0 `N3D-UNFU.exe` | `552d250ef773014a7f56ecdd7939559005fa990ebc7a6e435e6a7a49d372f301` |

Všetky `IMG:` adresy sú **offsety načítaného MZ obrazu bez 512-bajtovej hlavičky**. Nepoužívaj ich priamo ako aktuálne runtime `CS:IP` bez mapovania relokácie. Pôvodné hry/dáta a surové tracey sa do GitHubu necommitujú.

## 2. Nová zistená alternatívna WORLD-deaktivačná cesta

Originálny 21-bajtový helper je **byte-identický v oboch DOS buildoch**. Obsahuje:

```asm
MOV BYTE PTR ES:[BX+01],00
AND BYTE PTR ES:[BX+05],FE
```

Operácia **nuluje WORLD+01 a ruší bit0 príznakov WORLD+05**. **Neobsahuje zníženie GUARD count ani GUARD.state write.**

| Audit | DOS V1.2 IMG | DOS V2.0 IMG |
|---|---|---|
| WORLD cleanup helper (21B) | `B2E0` | `B5A2` |
| Interakčný WORLD dispatcher | `B2F6` | `B5B8` |
| Jediný nájdený priamy near CALL na helper | `B51A` | `B7DC` |
| Dva doslovné FAR callery dispatchera | `61F8,620A` | `6446,6458` |
| Kolízne/property bit `0x04` brány | `61EE,6200` | `643C,644E` |
| Property table | `DS:D068` | `DS:D10C` |
| Priame čítania property pri kolízii | `61D9,61E7` | `6427,6435` |

Dispatcher má triedny výber pre `0x2F–0x3D`; vetva mimo intervalu sa však môže dostať na spoločnú cleanup cestu. Pri `WORLD class=0x0F` je `(0x0F-0x2F)&0xFFFF=0xFFE0 >0x0E`, teda nejde o triedu, ktorú možno pre tento helper bezpečne vylúčiť *iba podľa čísla triedy*. Dosiahnutie závisí aj od interakcie/kolízie, vlastnosti `bit 0x04` a úspešného dohľadania WORLD ukazovateľa. **Prirodzená dosiahnuteľnosť po smrti GUARD41 zostáva OPEN.**

## 3. Reštrikcia blokových operácií (iba pre presné známe zápisy)

Dva pôvodné, staticky dekódované blokové clear opcodes na každom DOS builde:

| Zápis | DOS V1.2 IMG | DOS V2.0 IMG | Cieľový offset rozsah |
|---|---|---|---|
| 16×`STOSD` (64 bajtov) | `52EC` | `5534` | `36FE..373D` |
| 2048×`STOSW` (4096 bajtov) | `9618` | `98A2` | `0000..0FFF` |

Obe oblasti sú **offsetovo disjunktné** s poľom 100×26 bajtov GUARD na `264E..3075`, aj pri hypotetickom aliasovaní segmentu. Toto vylučuje **len dve známe** operácie, nie všetky `memcpy/REP/SAVE/LOAD`.

Skontrolované pôvodné DOS V2.0 `REP MOVS` opcodes: **29/29** na známom odvodenom zozname, tvoria **21 logických prenosov**. Jedna 41-bajtová kopírovacia vetva má **neuzavretý transitive FAR destination/owner**: `IMG:E2A4` (lokálny caller súvisí s UI editor record, nie je dokladom bežného GUARD-slot copy). Priame opcode census **nepreukazujú neprítomnosť indirektných writer aliasov**.

## 4. Kontrola existujúceho pôvodného runtime V067 (nie nové spustenie)

Opätovne spracované dve predtým autenticky zaznamenané originálne DOS V2.0 relácie:

| Original V067 relácia | CPU inštrukcie | Pamäťové W | Vykonanie interaktora/cleanup |
|---|---:|---:|---:|
| Short | 900 000 | 187 676 | **0** |
| Long (dva súvislé rotated súbory) | 2 200 000 | 445 249 | **0** |
| Spolu | **3 100 000** | **632 925** | **0 v daných ohraničených behových intervaloch** |

V týchto strojových stopách sa tiež nevyskytol instrumentovaný zápis prekrývajúci `GUARD count DS:6276`, ani zápis nulujúci sledovaný `WORLD+01`. Tieto obmedzené negatívne výsledky nesmú byť prezentované ako dôkaz večnej neaktivity helpera, neexistencie dropu alebo úplného slot-free auditu.

## 5. Reprodukcia, úroveň verifikácie a hranice

**Súkromný úplný dôkazový balík:** `N3D_GUARD41_ALIAS_BULK_STATIC_V069_20261020.zip`, **17 994 B**, SHA-256 `168ce6f69fd13db4334b6d53335117ae46ff4fc965a00d3ab90523b25bf99a39`. Obsahuje originálne-byte-gated `tools/verify_v069.py`, všetkých 29 odvodených `REP MOVS` riadkov, CSV, JSON, SHA manifest a slovenskú správu. Pôvodné EXE a raw tracey sú externé súkromné vstupy. Úplný audit **PASS**, 23/23 úmyselne pozmenených prípadov správne zamietnutých.

**Verejný GitHub kontrolný skript** `tools/n3d_v069_guard_world_alias_check.py` je úmyselne **užšia statická podmnožina**. Overí SHA oboch originálnych EXE a signatúry helpera/callerov, dve blokové operácie a count konštruktora. **Nespracúva V067 raw trace, ani celú 29-site typed REP MOVS tabuľku.** CI workflow `.github/workflows/n3d-v069-guard-world-alias.yml` vykonáva len testy s *umelými byte fixtures* (10/10 PASS), nie originálny DOS gameplay alebo remake.

Spustenie verejnej statickej podmnožiny nad súkromnými originálnymi binárkami:

```bash
python3 tools/n3d_v069_guard_world_alias_check.py \
  --dos12 /private/N3D-12.exe \
  --dos20 /private/N3D-UNFU.exe
```

Spustenie úplného súkromného verifikátora je uvedené v `README_SK.md` v súkromnom ZIP.

**Otvorené P0:** indirektné/bulk/SAVE-LOAD aliasy GUARD/WORLD, volania kolízneho interaktora za iných podmienok po `state0A`, drop lifecycle, fyzické odstránenie GUARD slotu a original-versus-clean-room porovnanie. Žiadne zvýšenie globálnych 1:1 percent.
