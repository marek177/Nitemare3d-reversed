# Nitemare 3D Win 1.10 — Ghidra 12.2, prechod 4

## Zistenie

Rozbalil som **13 message-map záznamov so 131 neprázdnymi položkami**, smerujúcimi na **118 rôznych handlerov**. Z nich 27 nemalo samostatný funkčný vstup; všetky boli doplnené. Tabuľky, ich signature-zero sentinely a near reťazce predkov sú označené v Ghidre ako dáta s referenciami.

Najdôležitejšia sémantická oprava: v skúmanom **Win16 EXE hudbu prepína F2 (`VK 71h`) a zvuk F3 (`VK 72h`)**. Staršie označenie Q/R bolo chybné: dekompilátor zobrazil tie isté bajty ako ASCII znaky `'q'/'r'`, hoci táto cesta dostáva Windows virtual-key kódy. Doložená je celá cesta od message-map cez podpisový dispatcher a wrapper po toggle funkciu a texty Music/Sound on/off.

Nejde o tvrdenie o DOS ovládaní. Runtime hra nebola spustená a úplná 1:1 parita zostáva otvorená.

## Identita

Ghidra 12.2 build 20261016, Java 25.0.2, headless projekt `WIN110`. EXE má 230 400 B a SHA-256 `12fe5168783446275802e0e947898261b5eca6b88288f3a895fc1faa4c544481`. Kódové NE segmenty 1–4 sú v projekte `1000/1008/1010/1018`, inicializované DS dáta segmentu 10 sú `1048`.

## Dôkazový reťazec a formát

| Status | Tvrdenie | Zdroj | Istota |
|---|---|---|---|
| Confirmed | Map record má near base pointer a far pointer na entries. | Načítané záznamy DS, napr. `1048:006C = 07A4,02A0,1000`; spotrebiteľ `1000:1B52` ide cez base word a far entry pointer. | High |
| Confirmed | Entry má 10 B, signature word +4 a handler far pointer +6/+8. | Lookup `1000:1B18`, dispatcher `1B52`; načítané dáta aj pôvodné NE source chains. | High |
| Confirmed | Signature 0 zastavuje lookup; porovnávajú sa slová +0 a +2; vracia sa prvá zhoda. | Telo `1000:1B18`; krok pointera je +10. | High |
| Confirmed | 131 handler selectorov a 13 selectorov entry tabuliek sú doložené pôvodnými NE type-2 chains. | `verify_message_maps.py`, `pass4/verification.json`. | High |
| Confirmed | Klávesové správy view majú signature 14 a štyri konkrétne handlery. | Map `1048:006C`, entries `1000:02A0–02C7`; tabuľka nižšie. | High |
| Confirmed | Signature 14 vedie cez `1000:1DA4`, kde sa odovzdáva wParam a oba wordy lParam. | Signature switch na `1C8B`, word index 13 → `1DA4`; PUSH `[BP+0C]`, `[BP+08]`, `[BP+0A]`, potom objekt. | High |
| Confirmed | Klávesové wrappery posielajú key z `[BP+0C]` a flags z `[BP+08]` do `1010:8CD2`. | `09D6/09E8/09FA/0A2A` disassembláž. | High |
| Confirmed | VK 71h/72h volajú hudobný/zvukový toggle. | `8E5E SUB AL,0D`, `8E62 SUB AL,64`, nasledujúci DEC; cally `8E94 → DDB2`, `8E9E → DDFC`; textové a flag dôkazy nižšie. | High |

Podopreté dátové štruktúry:

| Map offset | Pole |
|---|---|
| `+0` | word: near pointer na base map v DS, nula ukončuje ancestry |
| `+2/+4` | far offset/selector na prvú entry |

| Entry offset | Pole |
|---|---|
| `+0` | selector0, porovnávaný lookupom |
| `+2` | selector1, porovnávaný lookupom |
| `+4` | signature; nula = sentinel |
| `+6/+8` | far offset/selector handlera |

Priame okenné správy a command/command-UI položky používajú tie isté štruktúry, ale selector0 nie je vždy bežná správa okna. Hodnoty 0 alebo FFFF sa preto nemajú premenovať na konkrétne Windows message číslo bez príslušnej command dispatch cesty.

## Rozbalené mapy

| DS map | Base map | Entries | Počet bez sentinelu |
|---|---|---|---:|
| `0010` | `080A` | `1000:0028` | 28 |
| `080A` | `0766` | `1008:018E` | 9 |
| `0766` | 0 | `1000:065A` | 0 |
| `0016` | `064A` | `1000:0000` | 1 |
| `064A` | `05A4` | `1000:05A4` | 5 |
| `05A4` | `0766` | `1000:0530` | 10 |
| `002A` | `064A` | `1000:0014` | 1 |
| `0040` | `05DC` | `1000:0155` | 11 |
| `05DC` | `05A4` | `1000:6442` | 34 |
| `0056` | `077E` | `1000:0295` | 0 |
| `077E` | `0766` | `1008:008A` | 3 |
| `006C` | `07A4` | `1000:02A0` | 18 |
| `07A4` | `05A4` | `1008:00D4` | 11 |

Väzby `0040 → CMainFrame`, `0056 → CNite3wDoc`, `006C → CNite3wView` nadväzujú na doložené gettery a tabuľky z prechodu 3. Prázdna vlastná mapa CNite3wDoc neznamená absenciu zdedených handlerov.

## CNite3wView: vstup a fokus

| Správa | Hodnota | Entry | Handler | Podopreté správanie |
|---|---:|---|---|---|
| WM_KEYDOWN | `0100` | `1000:02A0` | `1010:09D6` | odovzdá key a flags do `8CD2` |
| WM_KEYUP | `0101` | `1000:02AA` | `1010:09E8` | rovnaký core; release je odvodený z flags |
| WM_SYSKEYDOWN | `0104` | `1000:02B4` | `1010:09FA` | core; potom pri key=9 a zápornom GETKEYSTATE(12h) volá `1000:12BE(object)` |
| WM_SYSKEYUP | `0105` | `1000:02BE` | `1010:0A2A` | core |
| WM_SIZE | `0005` | `1000:02C8` | `1010:0A3C` | `12BE`; `2BE6`; zapíše objektové slová `+1C/+1E` |
| WM_KILLFOCUS | `0008` | `1000:02FA` | `1010:0ABE` | `12BE`; `2D9C(4)` |

V samotnom kill-focus handleri nie je priamy zápis do key masiek `3756/3757`. Toto **nie je dôkaz**, že sa nikdy nenulujú v jeho callee grafe. Úplné správanie po strate fokusu vyžaduje ďalší statický trace a runtime keydown → focus-loss → keyup pokus.

Core `8CD2` používa `pressed = ((flags & 8000h) == 0)`. V maske byte `3756` pracuje s bitmi Escape=01, Up=02, Down=04, Left=08, Right=10, right Shift=20, left Shift=40, Ctrl=80. Alt je bit 01 a Space bit 02 v byte `3757`. Pre Shift sa scancode rozlišuje cez `flags & 7Fh` proti `2Ah/36h`. Ide o doložený statický model; poradie zmiešaných vstupov zostáva runtime úlohou.

## Oprava F2/F3 a prevencia dekompilačného omylu

Microsoft dokumentuje, že key messages prenášajú virtual-key kód vo wParam, a uvádza `VK_F2=71h`, `VK_F3=72h`, `VK_F4=73h`:

- https://learn.microsoft.com/en-us/windows/win32/inputdev/virtual-key-codes
- https://learn.microsoft.com/en-us/windows/win32/inputdev/using-keyboard-input

Táto dokumentácia objasňuje názvy konštánt; spojenie s konkrétnym Win16 EXE poskytuje vyššie uvedená binárna cesta. Staršie tvrdenie „Q prepína hudbu, R efekty“ pre tento Windows build je opravené.

| VK | Core cesta | Priamy účinok a dôkaz |
|---:|---|---|
| `71h` = F2 | `8E94 → DDB2` | byte `4BE1 ^= 1`; texty `Music on/off` na DS `19BA/19C4`; príslušné stop/start a config cally |
| `72h` = F3 | `8E9E → DDFC` | byte `4BE2 ^= 1`; texty `Sound on/off` na DS `19CE/19D8`; ďalšie config/SFX cally |

Nezávislá cesta z command map: root `0010`, selector1 `800Ah` → `1010:018E` s 32-bitovým PUSH `71h` pred call `8CD2`; selector1 `800Bh` → `1010:01B8` s PUSH `72h`. V týchto krátkych wrapperoch je horný word stlačenej dword konštanty nula, takže core dostáva key a nulové flags. Automatický C export môže zobraziť iba jeden argument a skryť tento detail.

V core nie je pre F2/F3 samostatný filter predchádzajúceho keydownu ani flags `4000h`. Každé normálne pokračujúce volanie s pressed=true a týmto VK dôjde k toggle ceste. Skutočnú kadenciu opakovaných správ týmto prechodom nemeriam.

## Merateľný výsledok

| Metrika | Pred prechodom 4 | Po prechode 4 |
|---|---:|---:|
| Interné funkčné vstupy | 1 362 | 1 389 |
| Dokončené interné dekompilácie | 1 362 | 1 389 |
| EXTERNAL položky, osobitne | 310 | 310 |
| Inštrukčné bajty | 157 470 | 158 055 |
| Definované dáta v code segmentoch | 6 031 | 7 445 |
| Neklasifikované bajty | 6 187 | 4 188 |

131 entries a 13 sentinelov predstavuje 1 440 B dátových záznamov. Čistý prírastok definovaných code dát je 1 414 B, pretože časť bajtov bola definovaná už predtým. Ďalších 78 B map records sa nachádza v DS dátovom segmente a do code coverage sa nezapočítava. Pribudlo 585 B inštrukcií. Úspešný C export nepotvrdzuje správnosť všetkých typov ani sémantiky.

## Reprodukcia

`N3DExportMessageMaps.java` prejde šesť koreňov a zdedené mapy; exportuje každý záznam po prvý signature-zero sentinel. `N3DRecoverCandidates.java` doplní 27 chýbajúcich vstupov. `N3DDefineMessageMaps.java` označí dokázané 6/10-bajtové štruktúry, sentinely a dátové referencie. `verify_message_maps.py` kontroluje pôvodný EXE hash, všetky selektory/signatures/offsety, 144 segmentových relokácií, contiguous entry adresy, sentinely, podpisovú vetvu 14 a raw key-dispatch aritmetiku.

Zachované sú pôvodné lookup/dispatch C exporty a listing, aktualizované anotácie, overovacie tabuľky, projekt a logy. Dokumentácia nemá byť čítaná ako dôkaz, že všetkých 131 handlerov bolo plne sémanticky zrekonštruovaných.

## Ďalšie otvorené dôkazy

- Runtime F2/F3 vrátane repeat, kombinácií Alt a zmeny fokusu; sledovať `3756/3757`, `4BE1/4BE2` a správy 0100/0101/0104/0105.
- Rozobrať celý focus-loss callee graf a porovnať key masky pred/po návrate do aplikácie.
- Z command ID → handler doplniť menu/resource popisy a rozlíšiť user-facing akcie od frameworkových command-UI update handlerov.
- Dokončiť zostávajúcich 4 188 neklasifikovaných bajtov a sémanticky overovať predchádzajúcich kandidátov; všetky funkcie nie sú vysvetlené samotným počtom vstupov.

**Istota:** High pre formát, raw väzby, F2/F3 opravu a uvedené lokálne operácie; Medium pre širšie UI a frameworkové roly; Unknown pre plné runtime správanie a 1:1 paritu.
