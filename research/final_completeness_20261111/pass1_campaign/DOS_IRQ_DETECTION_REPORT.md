# DOS 2.0 — probe caller, IRQ profily a obnovený handler

11. 11. 2026. PARTIAL, nové DEEP VERIFIED0 B, nové runtime testy0. Staticky obnovených päť kandidátnych rozsahov; jeden28 B handler nebol v hashovo overenom staršom inštrukčnom inventári.

## Caller reakcia na DSP failure

Device init image1A37D najprv pripraví bufferové adresové polia. Na1A3B6 porovná bázuCS:2DF0 s nulou. Iba pri nule volá DSP probe1B768. Nasledujúce JAE na1A3C1 rozlišuje CF: pri CF1 okamžite vráti AX=FFFFh. **Prvé zlyhanie teda neignoruje.** Globálna báza0300h sa pritom nevymaže.

Pri ďalšom vstupe s nenulovou bázou, vrátane0300h po neúspechu, sa DSP base probe vynechá. Pokračuje sa IRQ candidate probe1B65C, ktorého CF sa tiež kontroluje a pri CF1 sa vraciaFFFFh. Bez výsledkov tejto ďalšej detekcie nemožno vyhlasovať globálnu chybu či úspešnú inicializáciu neexistujúcej karty.

Po úspešnom IRQ probe init uloží vrátený AX doCS:2010. Hodnota sa teda na tejto ceste spresňuje ako vybraný IRQ code; vstup0 v tomto poli znamená automatický výber. Následne overuje mixerový readback a podľa výsledku vykoná dodatočné mixer zápisy. Vybraný vektor prepíše finálnym handleromCS:4A18 a nakoniec vrátiCS:2010. Úplná funkcia závisí od externých portových odpovedí, bufferového kontextu DS a ďalších helperov; neoznačuje sa za sémanticky uzavretú.

## Presné tabuľky a stavové polia

Súvislý dátový blok image `[1A355,1A379)` má36 B. Pred ďalším kódom1A37D zostávajú4 B, ktoré sa touto dávkou neklasifikovali.

| CS15BF rozsah end-exclusive | Typ / použitie |
|---|---|
| 4765..4767 | WORD vybraný profile index |
| 4767..476D | BYTE[5] mask ports + nulový sentinel |
| 476D..4772 | BYTE[5] mask bits |
| 4772..477C | WORD[5] IVT byte offsets |
| 477C..4782 | BYTE[5] IRQ codes + nulový sentinel |
| 4782..4786 | FAR16 uložený pôvodný vektor |
| 4786..4787 | BYTE uložená mask hodnota |
| 4787..4789 | WORD probe interrupt event flag |

| Index | Code | Port | Mask bit | IVT byte offset |
|---:|---:|---:|---:|---:|
| 0 | 7 | 21h | 80h | 003Ch |
| 1 | 5 | 21h | 20h | 0034h |
| 2 | 3 | 21h | 08h | 002Ch |
| 3 | 2 | 21h | 04h | 0028h |
| 4 | 10 | A1h | 04h | 01C8h |

Typy vychádzajú z konkrétnych indexed loadov, index doubling pre WORD vektory, sentinel vetiev a fixných save/restore zápisov. `profiles.csv` obsahuje všetky položky. Samotné načítané porty a IVT offsets sú potvrdené bajty; správanie PIC/hardvérových IRQ ešte nie je runtime overené.

## Candidate probe a životnosť dočasného vektora

Pri nenulovomCS:2010 vyhľadá zhodu v code tabuľke, pri nule začína indexom0. Kandidát s portovým sentinelom0 končí AX=FFFFh/CF1. Pre každého kandidáta uloží aktuálnu masku a vektor, nainštalujeCS:5A02, upraví mask port a nastaví event WORD na0. Pošle sekvenciu DSP command BYTE40h,7Fh,80h,1,1 cez skutočný helper a čaká s BX=3.

Úspech požaduje event==1. Pri neúspechu vykoná portové ukončenie, obnoví masku aj uložený vektor, zvýši index a pokračuje ďalším profilom. Po neúspechu zvoleného nenulového code sa teda môže skúšať aj ďalší vyšší profil; pôvodný filter sa neopakuje.

Na úspešnej vetve obnoví/upraví masku, pošle commandD3h, uloží index a vráti zero-extended IRQ code/CF0. V tejto vetve **neobnovuje starý vektor**; dočasný handler zostáva do jeho nahradenia finálnym handlerom v init callerovi. Prerušenie medzi týmito bodmi ani globálny teardown nie sú touto lokálnou analýzou uzavreté.

## Nový handler mimo historického inventára

Zápisy na1B6C4..1B6D0 priamo ukladajú offset5A02h aCS do vybraného IVT slotu. Tento dôkaz poskytuje vstup image1B5F2. Nezávislé dekódovanie `[1B5F2,1B60E)` dalo13 inštrukcií/28 B, končiacich IRET. V historickom inventári nebol ani jeden z týchto13 začiatkov; absencia je overená proti konkrétnemu hash-pinned inventáru, nie proti všetkým starým reportom.

Handler vykoná CLD, uloží AX,DX, prečíta base+Eh, zapíše1 doCS:4787, pošle20h na port20h ajA0h, obnoví DX,AX a IRET. Event je latch1, nie počítadlo. IRET má obnoviť vstupné FLAGS zo stack frame; platnosť reálneho frame a prirodzené vyvolanie IRQ sa ešte netestovali. **Neznamená to, že týchto28 B patrilo do pôvodných57 295 NON-CODE**: chýba pôvodná intervalová mapa.

## DSP byte helpery

Read helper čaká najviacFFFFh pollov base+Eh na bit7. Po vyčerpaní CX aj tak prejde k IN z base+Ah; nemá samostatnú lokálnu timeout návratovú vetvu. Write helper obdobne polluje base+Ch, ale po vyčerpaní aj tak vykoná OUT pôvodného command BYTE. Z toho nevyplýva prirodzený timeout ani správnosť zariadenia; je to lokálny ASM kontrakt.

## Reprodukcia a pokrytie

`python audit_dos_irq_detection.py IMAGE HISTORICAL_INSTRUCTIONS ABSOLUTE_DECODER_DIRECTORY OUT_DIR`. `dos_irq_detection/` obsahuje päť inštrukčných CSV, priame control hrany, dátové intervaly, profily a summary s chýbajúcimi historickými začiatkami.

| Kandidát | Image end-exclusive | Inštrukcie / B |
|---|---|---:|
| device_init | 1A37D..1A44A | 87/205 |
| temporary_irq_handler | 1B5F2..1B60E | 13/28 |
| dsp_read_byte | 1B60E..1B62F | 15/33 |
| dsp_write_byte | 1B62F..1B65C | 32/45 |
| irq_candidate_probe | 1B65C..1B768 | 96/268 |

Nových579 B kódu a36 B dát prešlo centrálnou kontrolou bez konfliktu. Katalóg:32 kandidátnych rozsahov,1110 inštrukcií/2557 B,848 B dát,167955 B aktuálne neposúdených,93 intervalov. Prijaté controlled replay prípady zostávajú32; nové percentá N/A, DEEP VERIFIED0 B.

Ďalší krok: riadený replay dočasného handlera a IRQ probe s explicitným port/BIOS/IRQ adapterom, vrátane restore vetiev; potom DOSBox-X s prirodzeným hardvérovým IRQ. Nevynechať jednotlivé mask/vector stavy a neprezentovať synthetic event injection ako dôkaz fyzickej karty.
