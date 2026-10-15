# RE MAX v0.36 – RNG pri zásahu chráneného hráča a rozdiel DOS verzií

**15. október 2026.** Priamy statický audit pôvodných, fingerprintovaných DOS
**v1.0, v1.7, v1.9 a v2.0**. Nie je použitá emulácia pôvodnej hry ani
nový gameplay trace. Táto práca uzatvára presné poradie jednej konkrétnej
rutiny *incoming actor damage*, nie všetky DAMAGE/WEAPON/GUARD subsystémy.

## Hlavný výsledok

Staré DOS verzie testujú dva ochranné predpoklady **pred** volaním producenta
poškodenia. DOS v2.0 volá producenta **pred** oboma kontrolami a navyše má
samostatný hit-indicator timer. Toto mení možnú spotrebu globálneho RNG
bez zmeny HP.

| Build | Wrapper v unpacked image | Ochrana | Stav smrti 2 | Damage producer CALL | HP |
| --- | --- | --- | --- | --- | --- |
| DOS 1.0 | `6792` | `6798` | `679F` | `67B4 → 8350` | `3FDF` |
| DOS 1.7 | `690C` | `6912` | `6919` | `692E → 866A` | `40F7` |
| DOS 1.9 | `6A70` | `6A76` | `6A7D` | `6A92 → 87CE` | `4187` |
| **DOS 2.0** | `6A70` | **`6A99`** | **`6AA0`** | **`6A84 → 87D8`** | `4189` |

Adresy sú **offsety do rozbaleného MZ load image**, nie CS:IP pri behu
alebo fyzické offsety packed distribúcie. Cieľ volania sa nezískava
tipovaním z funkčného názvu: originálny opcode `9A` obsahuje far offset
a segment, ktoré sa normalizujú ako `16*segment + offset`.
Originálne skoky `JNE` po ochrannej kontrole a `JE` po stave smrti
smerujú do spoločného `POP SI; POP DI; LEAVE; RETF` epilógu.

### Staré verzie – priame vetvenie

```text
if protection_flag != 0: return
if game_state == 2: return
damage = calculate_actor_damage(actor)  // MAY draw RNG for class 08/09/0A/11..14
if damage >= HP:
    HP = 0
    game_state = 2
    lethal_branch_effects()
else:
    HP -= damage
HUD_update()
```

### DOS v2.0 – zmenené poradie

```text
damage = calculate_actor_damage(actor)
if damage != 0:
    hit_indicator_countdown = 3    // DS:417A, writer image 6A93

if protection_flag != 0: return    // DS:4151, test 6A99
if game_state == 2: return        // DS:3CD4, test 6AA0

if damage >= HP:
    HP = 0                       // DS:4189
    game_state = 2
    lethal_branch_effects()
else:
    HP -= damage
HUD_update()
```

**To nie je zovšeobecnený záznam všetkých útokov.** Je to správanie
konkrétneho wrappera; iné projectile/hazard cesty môžu mať ďalšie ochranné
brány. Výpočet `calculate_actor_damage` je ďalšia pôvodná funkcia a
neznamená vždy náhodný odber. V predchádzajúcej v0.35 sa v DOS v2.0
identifikovali triedovo špecifické priame RNG callsites:

| OBJECT class | Damage-producer RNG call | Výpočet |
| --- | --- | --- |
| `08` | `8860` | `RNG & 7` |
| `09/0A` | `886C` | `RNG & 15` |
| `11/12/13/14` | `887C` | `RNG & 31` |
| ostatné | podľa vetvy | nemožno automaticky tvrdiť, že každá spotrebuje RNG |

**Dôsledok:** pri volaní tohto wrappera s ochranným príznakom a
RNG-triedou môže DOS v2.0 spotrebovať jeden RNG draw a pri nenulovom
výsledku nastaviť indikátor, hoci HP zostáva rovnaké. V DOS v1.0,
v1.7 a v1.9 táto wrapper vetva skončí ešte pred producentom. To je
príčina možného deterministického driftu medzi verziami, alebo medzi
originálom v2.0 a portom implementujúcim staršie poradie.

Tento nález je už **historicky naznačený v**
`docs/Nitemare3D_MSDOS_all_available_versions_audit_2026-09-24.md`.
Nový prínos v0.36 je nezávislé znovuoverenie všetkých štyroch vlastnených
bináriek, presné opcode/skokové dôkazy, executable CI model a
build-fingerprint-gated verifier. Nesmie byť prezentovaný ako
novoobjavený mechanizmus bez pôvodnej dokumentácie.

## Ďalšia zriedkavá vetva: HP=0 a nulové poškodenie

Podmienka porovnáva **unsigned** `damage >= HP` (zodpovedá inštrukcii
`CMP AL,[BP-1]; JB nonlethal`), nie `damage > HP`.
Ak sa wrapper dostane k HP porovnaniu pri **HP=0, damage=0, game_state!=2**
a bez ochrany, ide do **lethal** vetvy. Tá nastaví HP na 0 a
`game_state=2`, hoci vypočítané poškodenie je nula.

Toto je presný **branch-local static contract**, nie dôkaz, že normálny
gameplay vytvára živého hráča s HP=0. Ide o kandidáta pre cheat/debug
rare-flag runtime dosiahnuteľnosť. Pri bežnej smrteľnej udalosti je stav
smrti okamžite prepnutý na 2 a ďalší útok sa už touto vetvou nespracuje.

Zároveň ak `damage=0` a `HP>0`, vetva neodíde predčasne:
`HP -= 0` a spoločný HUD update sa vykoná (ak sú ochranné brány
neaktívne). Či má tento HUD call viditeľný výsledok, sa tu nemeria.

## Indikátor – presné štyri updater invokácie, nie štyri video frame-y

DOS v2.0:

- `6A8F`: `OR AL,AL; JE 6A99` – nulové poškodenie nenastaví countdown.
- `6A93`: `MOV WORD PTR DS:[417A],3` – writer pred oboma ochrannými testami.
- `A236`: signed `countdown >= 0` gate.
- `A23D`: decrement countdown a kontrola nového znamienka.
- `A24A`: push vykresľovacieho kódu **4** (po dekremente stále nenegatívne).
- `A243`: push vykresľovacieho kódu **3** (prvý decrement na -1).
- `A2BA`: dispatch do `980C`.

| Invocation od nastavenia 3 | Pred → po | Príkaz |
| --- | --- | --- |
| 1. | 3 → 2 | kód 4 |
| 2. | 2 → 1 | kód 4 |
| 3. | 1 → 0 | kód 4 |
| 4. | 0 → −1 | kód 3 (vyčistenie) |
| 5. | −1 → −1 | žiadna akcia z tejto timer vetvy |

**Časová jednotka neoverená:** štyri aktualizačné *invokácie* nemusia
byť štyri viditeľné frame-y alebo štyri rovnako dlhé časové intervaly.
Konkrétny output framebuffer, paleta a vnorený callback nie sú
z tohto branch-only auditu dokázané. Môže ísť o indikáciu zásahu,
ale test nezaistí, či dôjde k vykresleniu po každej chránenom zásahu.

## Identity štyroch nezávislých vstupov

| Build | Unpacked MZ load image bytes | SHA-256 |
| --- | ---: | --- |
| DOS 1.0 | 154448 | `113ea529e4247a5991f9dde2bd49e04b61f5714a8ea838d027014cac261e004a` |
| DOS 1.7 | 170848 | `df85d457e752860dc8fc8c39c4c36ba1c62f03b0e704f1365ee618d8ed8447ff` |
| DOS 1.9 | 171296 | `e29a8d058fdf3033241f4f711bca273fb168d750f8f972047e1be8f3d946529e` |
| DOS 2.0 | 171360 | `e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297` |

`tools/n3d_v036_protected_hit_probe.py` overuje najskôr hash a až
potom presné opcode witnesses, ciele FAR volania, obidva early-return
skoky a príslušný epilóg. Pôvodné EXE a herné dáta sa necommitujú.

```sh
python tools/n3d_v036_protected_hit_probe.py \
  --dos10 /private/N3D_DOS_v1.0_IDA.EXE \
  --dos17 /private/N3D_DOS_v1.7_IDA.EXE \
  --dos19 /private/N3D_DOS_v1.9_IDA.EXE \
  --dos20 /private/N3D_DOS_v2.0_IDA.EXE
```

Po overení fingerprintov sa má zobraziť `all_available_profiles_pass:
true` a `all_four_builds_checked: true`. Synthetic-fixture testy
bez originálnych bajtov kontrolujú samotný verifier. C++ referenčný
model `N3DV036ProtectedHitOrdering.hpp` je zámerne úzko ohraničený,
s vopred dosadenou `calculatedDamage` hodnotou. Nedomýšľa
pôvodné interné RNG volania ani efekty death SFX.

**OPEN pre 1:1:** skutočný event ledger pod ochranným príznakom, poradie
RNG vo všetkých nested caller-och, dostupnosť `HP=0/state!=2`,
stav indikátora po LOAD, rendering kódov 3/4 a rozdielne buildy
Win16. Táto statická oprava **nezvyšuje celkové percentá 1:1 parity**.
