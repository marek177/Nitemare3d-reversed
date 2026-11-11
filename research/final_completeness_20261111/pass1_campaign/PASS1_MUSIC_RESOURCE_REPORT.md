# DOS 2.0: loader hudobných zdrojov a reálny SND.DAT

## Funkcia a CFG

FAR rutina 0C2B:0298 má presné hranice `[0C548,0C64D)`, **261 B / 90 inštrukcií**. Prieskum CFG od vstupu overil celé telo proti kanonickému obrazu a inventáru. Priame vetvy smerujú na hranice v tomto rozsahu; pokračovanie za CALL je podmienené návratom callee. Skoková tabuľka sa v tele nenachádza.

Vstup je WORD ID na SS:[BP+6]. ENTER rezervuje 200 B lokálnych dát; prvých 192 B adresára sa číta do SS:[BP-C4h]. Rutina ukladá SI/DI/BP a obnovuje svoj lokálny stack; plný register/segment ABI cez externé volania zostáva otvorený. DS/ES/SS explicitne neprepína. Časť lokálnych dát potom dereferencuje pomocou DS:[BX], hoci pointer vznikol zo SS lokálu; úspech prirodzeného behu vyžaduje príslušný pamäťový model, ktorý táto dávka neuzatvára.

```text
id = WORD argument
if byte DS:414D == 0 and id != 0: return
if DWORD DS:17D0 != 0: call 11EE:2052(DWORD DS:17D0)
call 0C2B:0282()
call 0277:008A(local_directory_far_pointer, offset=0, count=192)
entry = local_directory + ((6*id) mod 65536)
length = WORD entry[0]
signed_offset = DWORD entry[2]
read_offset = signed_offset < 0 ? negate32(signed_offset) : signed_offset
if length == 0: call error("Tune %d not found", id)
DX:AX = call 11EE:2065(length)
DWORD DS:17D0 = DX:AX
if DX:AX == NULL: return
call 0277:008A(buffer, read_offset, length)
if id == 0:
    call 10BF:000C(39h, 0, 0, buffer_segment, buffer_offset)
else if signed_offset >= 0:
    call 10BF:0B7A(buffer)
else:
    call 10BF:0B25(buffer)
call 0C2B:00AA()
return
```

Pre rozhrania 2052/2065 sa uvádza priamo závislosť: ich používanie zodpovedá uvoľneniu a alokácii bufferu, celý CRT kontrakt nie je uzavretý. Rovnako sa nepredpokladá úplná sémantika zvukových volaní 10BF. Poradie WORD argumentov osobitného volania 000C vyplýva zo zásobníka; význam ovládacieho kódu 39h sa touto dávkou nedokazuje.

Dôležité otvorené vetvy: ID nemá v tele guard 0..31; násobenie a adresa sú 16-bit. Error volanie pri length=0 nemá vlastnú návratovú vetvu a pri návrate by vykonávanie pokračovalo. Po uvoľnení starého nenulového ukazovateľa sa tento globál ihneď nevynuluje; prepíše ho až návrat ďalšej alokácie. Následky pri zlyhaní či nenávratovom error callee zostávajú na overenie. INT32_MIN v zápornom offsete sa neguje modulárne, nie matematickým neobmedzeným abs.

## Väzba na súbor

Reader 0277:008A používa file name DS:01AE, ktorého pôvodné bajty sú `snd.dat\0`. Načíta/uchová file handle, seekuje na DWORD offset a žiada presný WORD počet bajtov; porovná návrat s požadovanou dĺžkou. Presné filesystem/CRT chybové kontrakty zostávajú závislosťou. V tejto dávke sa reálny asset číta priamo z `L:\nite3d\nite3\dos\SND.DAT`, 548 930 B, SHA-256 `f3434984d315531602d32285cb8ff55990bba786f5fb37f53710e88379388614`. Párovanie vychádza z používateľovho adresára, nie zo zachyteného runtime otvorenia.

Prvých 192 B tvorí 32 záznamov `<WORD length, signed DWORD offset>` zodpovedajúcich presnému výrazu loadera. Pre každý je doložený offset, length, hranice a SHA payloadu v `snd_directory_first32.csv`.

- ID 0: length 3204, offset 960, začiatok payloadu `IBK 1Ah`.
- ID 1..15: payloady začínajú `MThd`, header length 6. Big-endian header declares format, track count a division. Všetkých 15 payloadov sa rozdelilo na presne deklarovaný počet `MTrk` chunkov, spolu **288 chunkov**, bez prekročenia hraníc alebo trailing bajtov.
- ID 16: length 0, offset 193675; na tomto offsete sa nachádza prefix `Creative Voi`. Nulový length je pre túto rutinu error vetva; samotný prefix nepreukazuje použitie tohto záznamu.
- ID 17..31: length 0, offset 0.

Všetky nenulové offsety prvých 32 záznamov sú nezáporné; záporná prehrávacia vetva nemá v tomto asset podinventári priamy dátový exemplár. MIDI event streamy, význam udalostí, výsledný zvuk, ďalšie adresárové oblasti a všetkých 548 930 bajtov assetu zatiaľ nie sú analyzované. Tagy a chunkové hranice preto neznamenajú úplnú validáciu MIDI ani celého SND.DAT.

## NON-CODE pole a reprodukcia

Nové pole **DS:17D0, `[28EE0,28EE4)`, 4 B**, je počiatočne NULL a skladá sa z offset/segment WORDov výsledku DX:AX, následne odovzdaných ako FAR buffer do readera. Je to mutable FAR16 buffer pointer, PARTIAL. Chybový formát `Tune %d not found` bol už evidovaný a nezapočítava sa znova.

`audit_pass1_music_resource.py IMAGE INVENTORY DECODER_DIR SND_DAT OUT` reprodukuje byte/decode/CFG dôkazy, typové pole a reálne resource/chunk hranice. Výstupy `pass1_music_resource/`: `instructions.csv`, `cfg_edges.csv`, `far_calls.csv`, `data_fields.csv`, `snd_directory_first32.csv`, `midi_track_chunks.csv`, `summary.json`. Nevykonáva pôvodný loader, filesystem ani zvukový hardvér.

Po promócii z mapy `pass1_music_selector`: **54 677 B PARTIAL, 2 574 B CLASSIFIED ONLY, 44 B UNKNOWN, 0 B DEEP VERIFIED**. Nezávislá kontrola overila 650 intervalov, ich SHA a presné členstvo 57 295 B bez dier/prekryvov. Centrálny katalóg: 44 funkčných rozsahov, 1 561 inštrukcií / 3 674 B kódu, 55 523 B typovaných dát celého obrazu; 54 675 B typovaných historických NON-CODE dát. Rozdiel 2 B voči PARTIAL zostáva neuzavretá relokácia.

Žiadny nový replay ani prirodzený runtime test. Predchádzajúce controlled prípady zostávajú 6 663 plus samostatne 65 548 prefixových prípadov. Nové výsledky zatiaľ nie sú publikované na GitHub.

## Aktualizácia 13 oblastí

Metodika percenta: uzavreté jednotky / úplný inventár jednotiek oblasti. Úplné menovatele zatiaľ chýbajú, nové percentá sú N/A a predošlé sú orientačné. Funkcia, buffer a resource interpretácia zostávajú PARTIAL.

| Oblasť | Predošlý odhad | Nové % | Nové potvrdenie | Neznáme / blokátor | Konkrétny ďalší krok |
|---|---:|---|---|---|---|
| Mapy a formáty | 99 % | N/A | 32 SND záznamov a 288 chunk hraníc | zvyšok assetu a MIDI udalosti | ďalší resource adresár |
| Dátové typy a konštanty | 95 % | N/A | 4 B mutable FAR buffer | lifetime a chybové vetvy | alokačný kontrakt |
| Tabuľky a ukazovatele | 93 % | N/A | stride 6, signed offset | bounds ID a indexy | calleri 0298 |
| Funkcie / ASM / CFG | 90 % | N/A | 261 B / 90 inštrukcií | externé kontrakty | CRT a audio callee |
| RNG | 97 % | N/A | bez nového dôkazu | caller inventár | RNG ledger |
| Scheduler | 96 % | N/A | bez nového dôkazu | audio ordering | ukončenie/prehrávanie |
| DEMO a vstupy | 96 % | N/A | bez nového dôkazu | režimový flag | DS:3CD6 writeri |
| Renderer / VGA | 94 % | N/A | bez nového dôkazu | clipping | spotrebitelia flagov |
| GUARD / bossovia | 93 % | N/A | bez nového dôkazu | lifecycle | inicializátory |
| Zbrane / projektily | 92 % | N/A | bez nového dôkazu | kolízie | kolízne vetvy |
| Sprity / HUD / paleta | 92 % | N/A | bez nového dôkazu | textový lifetime | SS čítania po návrate |
| SAVE / LOAD | 92 % | N/A | audio pointer oddelený od zdrojových dát | pointer reset po LOAD | serializačné rozsahy |
| Windows Win16 | 92 % | N/A | bez nového Win dôkazu | resource parity | Win loader |

## Runtime testy na vykonanie

Zachytiť reálne otvorený `snd.dat`, load bázu, DS/SS, ID a obsah lokálneho adresára; overiť čítanie 192 B, alokáciu, file offset a celú payload dĺžku. Osobitne ID 0, ID 1..15, vypnutý enable flag, nulový length a zlyhanie alokácie. Záporný offset možno skúšať iba ako označený kontrolovaný experiment, keďže prvých 32 záznamov reálneho assetu taký exemplár nemá. Zaznamenať lifetime DS:17D0 a zvukové volania bez náhrad. Zatiaľ nevykonané.
