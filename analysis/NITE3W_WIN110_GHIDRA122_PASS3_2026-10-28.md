# Nitemare 3D Win 1.10 — Ghidra 12.2, prechod 3

## Zistenie

V hernom segmente `1010` som explicitne obnovil a typovo označil dve bounded switch tabuľky a štyri súvislé tabuľky far pointerov. Pribudlo **16 interných funkčných vstupov**: hlavný dispatcher `1010:DB94` a 15 cieľov virtuálnych tabuliek. Spojil som tri gettery s priamymi názvami herných tried `CMainFrame`, `CNite3wDoc`, `CNite3wView`.

Zároveň som zdokumentoval presnú maticu command-line zápisov a hlavný stavový dispatcher vrátane dvoch oddelených časových čítaní a spoločnej cesty stavov 7/8. Ide o statický model, nie o runtime timing dôkaz.

Nie všetky vetvy parsera sú novo objavené: predchádzajúci C export ich už čiastočne dekompiloval na požiadanie, hoci viaceré ich inštrukcie neboli v uloženom listingu definované. Tento prechod dopĺňa explicitný control-flow, označené dáta, reprodukovateľné overenie a konkrétny register účinkov.

## Vstup

Rovnaký Windows NE EXE, 230 400 B, SHA-256 `12fe5168783446275802e0e947898261b5eca6b88288f3a895fc1faa4c544481`. Ghidra 12.2 build 20261016, JDK 25.0.2, headless projekt `WIN110`. DOS ani Win16 1.8 sa týmto prechodom neposudzovali. Nebol vykonaný beh hry.

## Dôkazy

| Status | Tvrdenie | Zdroj a presné miesto | Istota |
|---|---|---|---|
| Confirmed | Parser má tabuľku 22 wordov a 12 rôznych cieľov. | `1010:1162 SUB AX,62h`, `1165 CMP AX,15h`, vetva JA, skok `116D` cez `CS:[BX+1172]`, tabuľka `1172–119D`. | High |
| Confirmed | Stavový dispatcher má 11 wordov a 7 rôznych cieľov. | `DBBD` číta `46B6`; `DBC0 DEC AX`; `DBC1 CMP AX,0Ah`; JA; skok `DBCB` cez `CS:[BX+DBD0]`, tabuľka `DBD0–DBE5`. | High |
| Confirmed | Štyri tabuľky obsahujú 206 far pointerov a 131 rôznych cieľov. | NE seg3 type-2 relokačné chains; súvislé selector zdroje vždy na `entry+2`. Načítané oba wordy overuje `N3DDefineFarTable.java`. | High |
| Confirmed | Vstup `0664` vracia deskriptor CMainFrame. | `MOV AX,0030; RETF 2`; `1048:0030` → názov `1000:014A`, size `00BE`, base `1048:05AC` = CFrameWnd. | High |
| Confirmed | Vstup `0852` vracia deskriptor CNite3wDoc. | `MOV AX,0046; RETF 2`; `1048:0046` → názov `1000:028A`, size `0036`, base `1048:076E` = CDocument. | High |
| Confirmed | Vstup `0970` vracia deskriptor CNite3wView. | `MOV AX,005C; RETF 2`; `1048:005C` → názov `1000:035E`, size `0020`, base `1048:05BC` = CView. | High |
| Confirmed | Dispatcher sa volá z `1010:00EC`, keď helper `1000:3D72` vráti AX=0; bridge vracia 1. | Priamy call na `1010:00FF`, telo bridge. | High pre poradie; identita OnIdle a frekvencia zostávajú Inferred/Unknown |

## Štyri tabuľky

| Rozsah vrátane konca | Počet | Prvý cieľ a podopreté priradenie |
|---|---:|---|
| `1010:04D4–0643` | 92 | `1000:2BFE` vracia deskriptor základnej CDialog; presná odvodená identita tejto tabuľky zostáva otvorená. |
| `1010:0792–0831` | 40 | `1010:0664` → CMainFrame. |
| `1010:08DC–094F` | 29 | `1010:0852` → CNite3wDoc. |
| `1010:0BA0–0C53` | 45 | `1010:0970` → CNite3wView. |

Priradenie prvého slotu ku getteru je Confirmed. Úplné pomenovanie všetkých metód a runtime dosiahnuteľnosť každého slotu zostávajú Partial. Pôvodné počty funkcií zahŕňajú aj malé prázdne metódy a gettery, preto nie sú mierou pochopenia hry.

## Command-line parser `1010:1118`

Caller `1010:0030` po inicializačných volaniach posiela do parsera argumenty odvodené z objektových polí. Parser vytvorí pracovný reťazec cez `1008:6C3C`, iteruje tokeny cez `1008:6B06`, očakáva `'-'` v prvom bajte a dispatchuje podľa **druhého bajtu tokenu**. Tu nevidno kontrolu celkovej dĺžky tokenu.

Číselný formát na `DS:0D88` je doslovný `%d`, textový `DS:0D8C` je `%s`. Rozpoznané písmená sú malé; neexistuje tu prevod na lowercase. Chybová vetva `1010:110C` posiela text `DS:0D70 = Invalid command line` do `1018:3118`; úplný návratový/ukončovací kontrakt tejto callee sa neuzatvára.

| Voľba | Vstup vetvy | Doložený účinok |
|---|---|---|
| `-b` | `11A6` | byte `46AE = 1` |
| `-c` | `11AE` | ďalší token cez `%d` do word `469C` |
| `-d` | `11CE` | `%d` → word `4698` |
| `-e` | `11D4` | `%d` → word `46A8` |
| `-f` | `11DA` | `%d` → word `469A` |
| `-l` | `11E0` | `%d` → word `46A6`, potom `DEC word [46A6]` |
| `-o` | `1204` | byte `46AB = 1` |
| `-p` | `120C` | `%s` → buffer `46BE`, potom call `1010:52AE` |
| `-r` | `1230` | word `46B8 = 1` |
| `-s` | `1238` | byte `46AA = 0` |
| `-w` | `1240` | `%d` → word `4BD4`; `AND byte [4BD4],F8h`; call `1010:5208` s word `4BD4` |

**Hraničné správanie:** návrat konverzie `1008:6442` nie je v týchto vetvách kontrolovaný. `-l` preto vykoná decrement aj po návrate z neúspešnej konverzie, ak táto cesta normálne pokračuje; `-w` obdobne vykoná maskovanie a ďalšie volanie. Presný výsledok chýbajúceho tokenu a nesprávneho čísla vyžaduje model tokenizéra, konvertora a chybovej callee. Z tejto tabuľky sa bez ďalších xrefs neodvodzujú všeobecné používateľské názvy nastavení.

Overil som všetkých 256 hodnôt druhého bajtu: po sign extension, odčítaní `62h` a unsigned porovnaní zostávajú v rozsahu iba `b..w`; 11 písmen má nepredvolenú vetvu. Toto je test aritmetického modelu a raw tabuľky, nie test celej hry.

## Dispatcher `1010:DB94`

Pred dispatchom:

1. `GETACTIVEWINDOW()` musí zodpovedať wordu `DS:00B6`; inak sa funkcia vráti.
2. Ak `word DS:0240 != 0`, nuluje ho, volá `1018:2FC6(0)` a nuluje byte `46AC`.
3. Zoberie word `46B6`, odčíta 1 modulo 2^16 a unsigned porovná s 10. Priamy tabuľkový rozsah je teda presne pôvodný stav 1–11. Iné hodnoty tu nič nedispatchujú.

| Stav `46B6` | Cieľ | Doložená cesta |
|---:|---|---|
| 1 | `DBE6` | Vetví podľa `46B8`, `46B4` a následne story bajtov. Podrobnosti nižšie. |
| 2–6 | `DCE1` | Priamy RETF v tomto dispatcheri; neznamená celkovú neaktivitu hry v týchto stavoch. |
| 7 | `DCBE` | `D6C6 → 1018:0C42`; znovu `D6C6 → 963E`; potom `95AE`. |
| 8 | `DC8C` | Pri `46B8 != 0` najprv `90CE`; potom spoločná cesta stavu 7. |
| 9 | `DC9A` | `0F8E`, potom `DESTROYWINDOW(DS:00B6)`. |
| 10 | `DCAA` | `D6C6`, odovzdanie návratu DX:AX do `6C78`. |
| 11 | `DCB8` | Volanie `6D2C`. |

V stavoch 7/8 sa **D6C6 volá dvakrát**, oddelene pred oboma konzumentmi. Zlúčenie na jedinú snímku by zmenilo doložené poradie; jednotky, časový zdroj a runtime kadencia sa v tomto prechode neuzatvárajú.

Vetva stavu 1:

- Pri `46B8 != 0` volá `DAA0` a vracia sa.
- Inak `46B4=1/2` ide do `D9C6`; `46B4=3` volá `3B7C(4)` a pokračuje; `46B4=0` pokračuje priamo. Ostatné hodnoty sa vracajú.
- Pri `byte46B0=0` zavolá `1018:3322(1)`; potom vždy `E2FA(0Ch)`.
- Ak `byte51A8 != 0` a `byte4C1D == 0`, volá `1018:19A6` s bezprostrednými hodnotami `10h` a `00070005h`, potom končí túto cestu.
- Inak pri `byte51A9 != 0` volá `1018:0AB0(10)` a vracia sa.
- Inak pri `byte51AA != 0` volá `C67A` a vracia sa.
- Inak nastaví `word46B6=7`, zavolá `1018:2F6C` a vracia sa.

Tieto podmienky a poradie sú Confirmed. Príbehové názvy udalostí, úplná sémantika každej callee a dosiahnuteľnosť v konkrétnej epizóde zostávajú Partial/Unknown.

## Pokrytie

| Metrika | Pred prechodom 3 | Po prechode 3 |
|---|---:|---:|
| Interné funkčné vstupy | 1 346 | 1 362 |
| Dokončené interné dekompilácie | 1 346 | 1 362 |
| EXTERNAL položky, osobitne | 310 | 310 |
| Inštrukčné bajty | 156 889 | 157 470 |
| Definované dáta v code segmentoch | 5 141 | 6 031 |
| Neklasifikované bajty | 7 658 | 6 187 |

Pribudlo 581 B inštrukcií a 890 B dát: 824 B far pointerov a 66 B switch tabuliek. Pokles neklasifikovaných bajtov preto nie je percentom hotovej sémantiky alebo parity.

## Reprodukcia a limity

`scripts/verify_pass3.py` kontroluje hash EXE, presné bajty oboch guardov a nepriamych skokov, všetkých 33 raw cieľových wordov, 256 znakových hodnôt a 65 536 stavových wordov. Z predtým overených NE chain sites reprodukuje 206 pointerov a 15 nových kandidátov. Ghidra skript nezávisle kontroluje načítané wordy pointerov.

Ghidra poradie: `N3DRecoverGameSwitches.java` → `N3DRecoverCandidates.java candidates4.txt` → `N3DDefineFarTable.java game_far_pointer_tables.tsv` → `N3DInspectClassMetadata.java ... game_metadata_offsets.txt` → `N3DApplyEvidenceAnnotations.java verified_annotations.tsv` → export a coverage. Zachované sú tabuľky, anotácie, pôvodný EXE, projekt a logy.

Nasledujúce rozlišujúce dôkazy:

- Breakpoint `1118`: zachytiť tokeny a DS zápisy pre platné aj chybné argumenty; preveriť návrat `110C/3118` a výsledok konverzií.
- Breakpoint `DB94`: zachytiť aktiváciu okna, `46B6/46B8/46B4`, story bajty a presné dve hodnoty `D6C6` pre stavy 7/8.
- Dotiahnuť message-map metadata herných tried k handlerom a ich HWND/object väzbám.
- Preveriť 6 187 zostávajúcich bajtov ako code/data/padding a spojiť funkčný register s predchádzajúcimi kanonickými identitami.

**Istota:** High pre lokálne vetvenie, priame zápisy/volania, raw tabuľky a názvy tried; Medium pre širšie frameworkové roly; Unknown pre kompletné runtime správanie a 1:1 paritu.
