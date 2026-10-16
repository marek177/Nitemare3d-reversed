# WORX Toolkit 2.1 — RE‑1TO1‑MAX v0.15: MIDI event decode, running status a CALL ordering

**Dátum:** 16. 10. 2026. **Dôkaz:** priamo prečítané nezmenené strojové bajty dvoch používateľských, úplne rozbalených DOS EXE, plus regresný C++17 model. Ani jeden originálny EXE nie je súčasťou verejného repozitára.

## Binárne identity a adresy

| Build | SHA-256 unpacked MZ *image* | 16-bit WORX CS image base |
| --- | --- | --- |
| Nitemare 3-D DOS 1.9 | `e29a8d058fdf3033241f4f711bca273fb168d750f8f972047e1be8f3d946529e` | `0x15BB0` |
| Nitemare 3-D DOS 2.0 | `e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297` | `0x15BF0` |

Plne rozbalené súbory obsahujú MZ hlavičku dlhú `0x1C00`. Referencie `44EE`, `3A4D` atď. v tomto dokumente sú **CS:IP offsety WORX segmentu DOS 2.0**, nie priamo file offsety. DOS 1.9 má v skúmanom kóde `IP_old = IP_new + 4` a jeho WORX obrazový základ je o `0x40` bajtov skôr.

## 1. `15BF:44EE–4552`: všetky lokálne cesty MIDI event prefixu

| IP | Dôsledok pôvodnej inštrukcie |
| --- | --- |
| `44EE` | `AL = ES:[DI]`; prvý test `AL == FFh` smeruje na meta vetvu `4546`. |
| `44F5` | Pri ne-meta testuje bit 7. Pri novom statuse (`AL & 80h`) zapisuje celé **WORD** `AX` do `CS:[(2*track)+2D63]` a zvyšuje `DI` o 1. Pri running status (`AL < 80h`) ponechá cache aj aktuálne `DI` bez zmeny. |
| `44FF` | Z cache znovu načíta `AX`; pred výpočtom `SI=(AL>>4)` nuluje `AH`; podľa `CS:[2DA4+SI]` načíta `CL`, nuluje `CH`. |
| `4513` | Pre volanie `3A4D` načíta celé `AX` opäť z cache. |
| `4518` | Ak `CX=0`, nečíta dátový bajt. Inak číta prvý dátový bajt do `BH`, `DI++`, `CX--`. |
| `451F` | Ak `CX` potom nie je 0, číta druhý dátový bajt do `BL`, `DI++`. **Za druhým čítaním už nenasleduje DEC CX.** |
| `4525` | Priame `CALL 3A4D`; pred zvyšnými effectmi prefix `3A4D–3A66` zapíše štyri globálne polia. |
| `4528` | Priame `CALL 45F9` (VLQ delta, 32-bit `DX:AX`, `DI` sa obalí na 16 bitov). |
| `452B` | **Až po oboch CALL** znovu načíta globálny `CS:[2DC0]`, vypočíta index a uloží `DI` do `CS:[2D22+2*i]`, následne spodný `AX` a vrchný `DX` do `CS:[2CA2+4*i]`, `CS:[2CA4+4*i]` v tomto poradí. |
| `4543` | `JMP 44B4` bez bezprostredného RET; pri nulovom ďalšom delta čase môže vykonať ďalšiu udalosť toho istého tracku. |

Statická 16-bajtová tabuľka počtu dátových parametrov `CS:2DA4..2DB3` (indexované horným nibblom MIDI statusu) je **presne**:

```
status high nibble: 0 1 2 3 4 5 6 7 8 9 A B C D E F
parameter count:    0 0 0 0 0 0 0 0 2 2 2 2 1 1 2 0
```

**Neobvyklý, ale binárne potvrdený detail:** pre kanálový status `Cxh`/`Dxh` (jeden dátový bajt) sa prvý parameter uloží do `BH`, no `BL` zostane **spodný bajt `BX` pred čítaním**, t. j. `low8(2*track)`. Pre počet 0 zostanú `BH` aj `BL` z pôvodného `BX`; pre dva parametre obidve hodnoty pochádzajú zo streamu, no `CX` pri `CALL 3A4D` je stále 1. Nasledujúci transitive kód môže polia používať. Nemožno ich „z bezpečnostných dôvodov“ vynulovať.

## 2. Bezpodmienečný prefix `15BF:3A4D–3A66`

`3A4D` z `AL` tvorí horný nibble statusu a nízky nibble kanála a zapíše, v danom poradí:

1. `CS:2DC4 = AL & 0Fh` — kanál;
2. `CS:2DC8 = AL & F0h` — typ udalosti;
3. `CS:2DC5 = BH` — prvé dátové pole;
4. `CS:2DC6 = BL` — druhé dátové pole.

Až potom `3A67` testuje `CS:[2DBC] & 06h` a rozhodne o ďalšom systéme (priamy MIDI backend `58F8`, speaker/FM/AdLib a ich vnorené callee cesty). **Tieto vnorené telá v0.15 neoznačuje za hotové.** C++ `MidiDispatchTail3a67` je povinný explicitný callback pre kanálovú udalosť; chýbajúci backend skončí zjavnou výnimkou namiesto falošného „success“.

## 3. `FF` meta vetvy: zloženie s už auditovanými v0.13/v0.14 kontraktmi

- `FF 2F`: `DI` sa posunie za typ `2F`, potom sa **bez čítania length byte a bez `45F9`** vykoná EOT `458C`, ktorá mení aktivitu a prípadne replay / stop / znovuvstup.
- `FF 51`: `455D` preskočí práve jeden length byte, prečíta tri tempo bajty, zavolá PIT helper `466A` (môže vyvolať x86 `DIV` trap); **až po úspešnom návrate** pokračuje do `45F9` a commit `452B`.
- iný `FF` type: `4553` prečíta **jeden 8-bit length byte**, preskočí presne toľko payload bajtov s 16-bit DI wrap, pokračuje do `45F9` a commit `452B`.
- V každej meta ceste sa preskočí `CALL 3A4D` a cache bežiaceho MIDI statusu zostane nezmenená.

`midi_event_step_44ee` implementuje **presne jeden** takýto shell (všetky vyššie uvedené lokálne branch rozhodnutia) a končí na hranici ďalšieho `JMP 44B4`. Nesľubuje dokončené vykonanie track scheduleru ani fyzického PIT, DOS alebo OPL back-endu. Pri event-ready vstupe zo `44B3` je `AX=0` a teda nový `WORD` status má nulové `AH`; pre instruction-level audit je vstupné AX explicitný parameter.

## 4. Cross-build DOS 1.9 ↔ 2.0: bez funkčných zmien v auditovaných oknách

Na pôvodných dvoch obrazoch bol vyladený byte-by-byte audit s prísnymi fixnými hashmi:

| Rozsah vo v2.0 | Dĺžka | Odlišné bajty pri porovnaní s v1.9 (+4 IP) | Typ rozdielu |
| --- | ---: | ---: | --- |
| `44EE..4552` channel event pipeline | 101 B | 8 | všetkých 8 je byte adresného operandu `old=new+4` |
| `3A4D..3A6E` dispatch prefix | 34 B | 5 | všetkých 5 je byte adresného operandu `old=new+4` |
| `4546..4552` meta prefix (prekryv) | 13 B | 0 | byte-identické |
| `2DA4..2DB3` nibble tabuľka | 16 B | 0 | byte-identické (v1.9 pri `2DA8`) |

V troch **kódových** rozsahoch bolo rozpoznaných presne **13 zmenených operandových bajtov**, žiadne iné rozdiely. 22 opcode okien, 7 priamych branch targetov, 2 CALL ciele a SHA-256 štyroch rozsahov preveruje `other/worx/tools/audit_midi_events_v015.py`; reproducibilný JSON je `other/worx/data/worx21_midi_events_v015.json`. Tento dôkaz sa nevzťahuje automaticky na iné oblasti runtime ani iné verzie.

## 5. Testy, výsledky a nesplnené podmienky 1:1

- Integrovaný C++17 test pre nový status a 2 parametre, running status pri 1 parametri, nulový F0 parametrický count, 16-bit cursor/pointer alias, modifikáciu `ES:DI`/indexu volaným backendom, meta other/tempo/EOT, výnimky pri chýbajúcom zariadení a nekonečnom VLQ bez terminátora.
- Statický Python test kontroluje manifest voči pevným adresám a podpisom; pri nastavených `WORX_N3D_V19_EXE` + `WORX_N3D_V20_EXE` prečíta originály a overí aj detekciu poškodeného bajtu.
- **Lokálne:** 9/9 CTest skupín uspelo, s oboma originálnymi súbormi; táto kontrola **nezahŕňa** reálny DOSBox runtime, CPU flagy/stack v `3A4D`, presné IRQ/OPL poradie ani prípad nerekurentného `3A4D` návratu.

**Otvorené do 100 %:** `3A67` transitive subtree, `58F8/3B5B/38A7`, celá reentry reťaz `44B4` vrátane index aliasovania a prípadov, keď callback nevráti, `FF 2F` replay `4265/4389`, reálne externé driver porty, časovanie IRQ. Počet plne/čiastkovo auditovaných vstupných INT63 handlerov stále **41/79**; v0.15 pridáva interný parser shell, nie nových 79-handler parity.
