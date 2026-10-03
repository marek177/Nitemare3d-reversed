# Nitemare 3D – static analysis functions, batch 06

Primary source: **raw binary `N3D-19.exe` (DOS 1.9)**. Ghidra `.c/.gzf` and older RE notes are usage only on xrefy, comparison and named already confirm class. Names functions are analytické, nie original symbol.

This batch uzatvára jadro **score → damage → death transition → player damage → weapon verify → HUD redraw** v block `1000:84F4–8998`.

## 1. Súhrn functions

| DOS 1.9 | Proposed name | Kategória | Confidence |
|---|---|---|---|
| `1000:84F4` | `GetGuardKillScore(object)` | combat / score | Confirmed |
| `1000:8586` | `ComputeDamageToGuard(target,hitObject)` | combat / player→enemy | High |
| `1000:86AA` | `IsSpecialGuardClass(classId)` | guard predicate | High |
| `1000:86D2` | `FinalizeGuardDeathState9(guard,object)` | GUARD state machine / death | High |
| `1000:87CE` | `ComputeGuardContactDamage(object)` | combat / enemy→player | Confirmed |
| `1000:88B2` | `UpdateWeaponOverlayAnimation()` | weapon / HUD animation | High |
| `1000:8998` | `RedrawHudSection(sectionId)` | HUD dispatcher | Confirmed |

---

# 2. `1000:84F4` – GetGuardKillScore

Raw start:

```asm
LES BX,[BP+0A]
MOV AL,ES:[BX+06]       ; object class
SUB AX,0008
CMP AX,0018
JA  return_zero
ADD AX,AX
XCHG AX,BX
JMP WORD PTR CS:[BX+0152]
```

Function therefore uses `OBJECT+0x06` as internú GUARD class and dispatchuje classy `0x08–0x20` through 25-element jump table. Caller `1000:6016` sign-extenduje return value and pripočíta ju to 32-bit score `0x4180:0x4182`, then calls `RedrawHudSection(4)`.

## Exact class → score table v DOS 1.9

| Class | Name | Score |
|---:|---|---:|
| `08` | Bat | 25 |
| `09` | Frankenstein | 75 |
| `0A` | Mummy | 50 |
| `0B` | Skeleton | 100 |
| `0C` | Mrs H. | 250 |
| `0D` | Zelda | 150 |
| `0E` | Vampira | 200 |
| `0F` | Baddie #1 | 100 |
| `10` | Baddie #2 | 100 |
| `11` | Dracula – humanoidná phase | 0 |
| `12` | Cemetery Gargoyle | 150 |
| `13` | Garden Gargoyle | 150 |
| `14` | Dracula-Bat transformovaná phase | 200 |
| `15` | Penelope | **−1000** |
| `16` | Dr. Hamerstein | **1000** |
| `17` | Tall slim robot | 100 |
| `18` | Trashcan robot | 200 |
| `19` | Cannon | 0 |
| `1A` | Ghost | 25 |
| `1B` | Goldie | 100 |
| `1C` | Greenie | 100 |
| `1D` | Demon boss | 250 |
| `1E` | Alien #1 | 250 |
| `1F` | Alien #2 | 200 |
| `20` | GUARD25 | 50 |
| mimo rozsahu | default | 0 |

### Pseudokód

```c
int16_t GetGuardKillScore(Object far *obj)
{
    switch (obj->class_id) {
      case 0x08: return 25;
      case 0x09: return 75;
      case 0x0A: return 50;
      case 0x0B: return 100;
      case 0x0C: return 250;
      case 0x0D: return 150;
      case 0x0E: return 200;
      case 0x0F: return 100;
      case 0x10: return 100;
      case 0x11: return 0;
      case 0x12: return 150;
      case 0x13: return 150;
      case 0x14: return 200;
      case 0x15: return -1000;
      case 0x16: return 1000;
      case 0x17: return 100;
      case 0x18: return 200;
      case 0x19: return 0;
      case 0x1A: return 25;
      case 0x1B: return 100;
      case 0x1C: return 100;
      case 0x1D: return 250;
      case 0x1E: return 250;
      case 0x1F: return 200;
      case 0x20: return 50;
      default:   return 0;
    }
}
```

**Important korekcia:** Ghidra `.c` export during this function incorrectly pohltil part jump-table data as instructions. Raw binary is jednoznačná.

---

# 3. `1000:8586` – ComputeDamageToGuard

Function creates base damage:

```text
seed = 8 * signed16(hitObject+0x18 - 0x4550) + (rand() % 25)
```

Then uses class targetu `OBJECT+0x06` for range `0x0C–0x1F`, active weapon `0x418D` and nakoniec difficulty `0x417E`.

## Weapon ID

current mapovanie runtime selectorov:

- `W0` = Single Plasma
- `W1` = Wand
- `W2` = Silver Pistol
- `W3` = Multi Plasma

## Class/weapon resistance matrix before difficulty

| Class / enemy | W0 | W1 | W2 | W3 |
|---|---:|---:|---:|---:|
| `0C` Mrs H. | 1/8 | 1/8 | 1/8 | 1/8 |
| `0D` Zelda | 1/8 | **1/2** | 1/8 | 1/8 |
| `0E` Vampira | 1/8 | 1/8 | **1/2** | 1/8 |
| `0F` Baddie #1 | 1/256 | **1/2** | 1/256 | 1/256 |
| `10` Baddie #2 | 1/256 | **1/2** | 1/256 | 1/256 |
| `11` Dracula | 1/8 | 1/8 | **1/2** | 1/8 |
| `12` Cemetery Gargoyle | 1/4 | 1/4 | 1/4 | 1/4 |
| `13` Garden Gargoyle | 1/4 | 1/4 | 1/4 | 1/4 |
| `14` Dracula-Bat | 1/8 | 1/8 | **1/2** | 1/8 |
| `15` Penelope | 0 | 0 | 0 | 0 |
| `16` Dr. Hamerstein | special | special | special | special |
| `17` Tall slim robot | 1/4 | 1/256 | 1/4 | 1/4 |
| `18` Trashcan robot | 1/8 | 1/256 | 1/16 | 1/8 |
| `19` Cannon | 0 | 0 | 0 | 0 |
| `1A` Ghost | 0 | **1/2** | 0 | 0 |
| `1B` Goldie | 1/2 | 1/2 | 1/2 | 1/2 |
| `1C` Greenie | 1/2 | 1/2 | 1/2 | 1/2 |
| `1D` Demon boss | 1/8 | 1/8 | 1/8 | 1/8 |
| `1E` Alien #1 | 1/8 | 0 | 1/8 | 1/8 |
| `1F` Alien #2 | 1/4 | 0 | 1/4 | 1/4 |

Class `0x16` does not use normálny multiplier: if `0x6268 == 3`, sets base damage on `3`, otherwise on `0`. Up to then príde difficulty scaling.

Class `0x15` moreover calls osobitnú text/event branch and then sets damage on `0`.

## Difficulty player → guard

| `0x417E` | Result |
|---:|---|
| 0 / easy | damage ×2 |
| 1 / medium | ×1 |
| 2 / hard | damage ÷2 |

Result sa zhora saturuje on `255`. V analyzovanom helperi is not explicitný lower clamp.

## Caller – confirmation meaning

Caller `1000:5F74`:

1. calls `8586`,
2. zeros AH and stores low-byte damage,
3. compares ho with `GUARD+0x10` HP,
4. if `damage >= HP`, sets HP on nulu and ide to death branches,
5. otherwise odpočíta damage from `GUARD+0x10`.

Thereby is meaning `8586` **High up to prakticky confirmed on call-site úrovni**.

---

# 4. `1000:86AA` – IsSpecialGuardClass

DOS 1.9 returns true for exact množinu:

```text
{ 0x15, 0x16, 0x19, 0x21 }
```

Therefore:

- `0x15` Penelope
- `0x16` Dr. Hamerstein
- `0x19` Cannon
- `0x21` Dancers

Two confirmed call-site meaning:

- `1000:99EB`: during draw guard markerov to map/HUD priestoru sa these classy skip;
- `1000:A9D2`: during count active generických guard sa these classy nezapočítajú.

Najbezpečnejší analytický name is therefore `IsSpecialGuardClass()` – exact množina is confirmed, dizajnový shared name these four class nie.

## Version difference

| Version | Address | True for classy |
|---|---:|---|
| DOS 1.0 | `1000:8230` | `15,16,19` |
| DOS 1.1 | `1000:8450` | `15,16,19` |
| DOS 1.5 | `1000:84AA` | `15,16,19,21` |
| DOS 1.7 | `1000:8546` | `15,16,19,21` |
| DOS 1.9 | `1000:86AA` | `15,16,19,21` |

**Class `0x21` was to tohto predicate add between DOS 1.1 and 1.5.**

---

# 5. `1000:86D2` – FinalizeGuardDeathState9

Caller is large GUARD state-machine during `1000:59F0`. Jump-table for `GUARD+0x0B` posiela **state 9** on block `1000:5C74`, which calls `86D2`.

Function on start:

```c
object->flags_05 |= 1;
guard->state_0B = 0x0A;
```

Then branch according to `object->class_id` v range `0x09–0x1F`.

## Normal class branches

Classy `09, 0A, 12, 13, 1A, 1E, 1F` before návratom znovu čistia bit 0 v `object+0x05`:

```c
object->flags_05 &= 0xFE;
```

Other normal classy skončia without tohto clearu.

## Dracula `0x11` → Dracula-Bat `0x14`

Special branch is binary jednoznačná:

```c
object->byte04 = random(8);
object->class_id = 0x14;
object->byte1A = 0x23;

guard->state_0B = 8;
guard->next_0C  = 2;
guard->timer_06 = 1;
guard->hp_10    = 0xFF;

linkedMapRecord[1] = object->byte00;
CallGuardTransitionHelper(..., 2);
PlayEventOrSound(0x22, ...);
```

Thereby is confirmed:

- humanoidný Dracula is class `0x11`;
- its fatálna branch **is not finálna death**;
- premení sa on class `0x14`;
- second phase dostane new **255 HP**;
- death/state machine sa returns to active state 8.

Therefore score helper correctly gives `0x11 → 0 bodov` and up to `0x14 → 200 bodov`.

## Dr. Hamerstein `0x16`

Class `0x16` ide to samostatnej event branches:

- runs event/sound ID `0x12` with parametrom `0x00020000`;
- calls auxiliary text/event routine with global far pointer store during `0x1086`;
- sets `0x430B = 1`;
- sets `0x3CD4 = 0`.

Is to jednoznačne **special boss/event completion path**, but user-facing meaning all global still is not on 100 % named.

---

# 6. `1000:87CE` – ComputeGuardContactDamage

Function najprv zoberie object position `+0x10/+0x12`, posunie their `>>6`, odpočíta player `0x415E/0x4160` and calls distance helper.

Base:

```text
base = distance > 0 ? floor(100 / distance) : 100
```

Then class-specific transform:

| Class | Damage before difficulty |
|---:|---|
| `08` | `rand() & 7` = 0–7 |
| `09`,`0A` | `rand() & 15` = 0–15 |
| `0B` | `base / 4` |
| `0C`,`1D`,`1E` | `base` |
| `0D–10` | `base / 2` |
| `11–14` | `rand() & 31` = 0–31 |
| `15` | `base / 2` |
| `16` | 33 if `0x6268 != 3 && 0x4308 == 0`, otherwise 100 |
| `17`,`18` | `base / 2` |
| `19` | 100 |
| `1A–1C` | `base / 2` |
| `1D`,`1E` | `base` |
| `1F`,`20` and above default | `base / 2` |

## Difficulty guard → player

| Difficulty | Result |
|---:|---|
| 0 / easy | damage ÷2 |
| 1 / medium | ×1 |
| 2 / hard | damage ×2 |

To is exactly opačný direction as `8586`.

## Caller `1000:6A70`

Caller:

- nepoužije damage during debug/verify state `0x4151 != 0` or when `0x3CD4 == 2`;
- calls `87CE`;
- if damage >= health `0x4187`, health = 0 and aktivuje death state;
- otherwise odpočíta damage;
- subsequently calls `RedrawHudSection(5)`.

Meaning `87CE` is therefore **Confirmed**.

---

# 7. `1000:88B2` – UpdateWeaponOverlayAnimation

Function is runtime animátor weapons v HUD:

- if `0x418D == 0xFF`, nič nekreslí;
- `0x41A6` is index animation frame;
- tables `0x1404[]` and `0x140E[]` dávajú X/Y offset;
- result position save to `0x41A8/0x41AA`;
- active weapon selector `0x418D` selects 10-byte grafický descriptor;
- `0x41A4` is transition state;
- during completion one transition direction calls `RedrawHudSection(12)`;
- during switch animation prenesie pending weapon `0x41A2` to active weapon `0x418D`;
- finálne calls sprite/blit helper `0156:07DE`.

Thereby sa spája batch05 `RequestWeaponSwitch(9072)` with real HUD prechodom.

---

# 8. `1000:8998` – RedrawHudSection(sectionId)

This **is not OBJECT/AI dispatcher**. Is to large HUD/status renderer with ID `0..22`.

DOS 1.9 najprv checks `0x141A`; if is nonzero, jednorazovo prejde grafické deskriptory `0x3510..0x3628` after 10 byte and reset this init flag. Up to then process section ID.

## DOS 1.9 jump table

| ID | Branch | Finding meaning |
|---:|---:|---|
| 0 | `8A06` | calls weapon overlay update `88B2` |
| 1 | exit | no-op |
| 2 | `8A06` | weapon overlay update |
| 3 | `8A16` | format dvojicu `0x6268`, `0x626A+1` – level/episode style HUD text |
| 4 | `8A63` | **score (`0x4180` dword)** |
| 5 | `8AA9` | **health (`0x4187`) + health graphic/gauge** |
| 6 | `8B24` | prakticky no-op for ID 6 |
| 7 | `8B2A` | stat `0x4189`, clamp 100 |
| 8 | `8B7C` | stat `0x418A`, clamp 100 |
| 9 | `8BCE` | stat `0x41AE`, clamp 100 |
| 10 | exit | no-op |
| 11 | exit | no-op |
| 12 | `8C23` | **selected weapon icon (`0x418D`)** |
| 13 | `8C50` | 4 bit ikony z `0x4190` |
| 14 | `8CB6` | iterate bit ikony z `0x4191` |
| 15 | exit | no-op |
| 16 | exit | no-op |
| 17 | exit | no-op |
| 18 | `8CFC` | 3 fixné blocks + optional counter `0x3CD8/0x3CDA` |
| 19 | `8D62` | percent gauge `0x41AC`, škála 0..18 |
| 20 | `8DC1` | percent gauge `0x41AD`, škála 0..18 |
| 21 | `8E2B` | dvojité HUD graphic according to flagu `0x3CD2` |
| 22 | `8E6C` | format dword `0x415E`, condition `0x3CD4` |

### Priame call-site evidence

- enemy kill path: `8998(4)` after pripočítaní score;
- player damage path: `8998(5)` after zmene health;
- weapon overlay transition `88B2`: `8998(12)`;
- additional pickup/input branches use other section ID.

Therefore `RedrawHudSection(sectionId)` is very safe name.

---

# 9. Cross-version mapovanie

| Function | DOS 1.0 | DOS 1.1 | DOS 1.5 | DOS 1.7 | DOS 1.9 |
|---|---:|---:|---:|---:|---:|
| GetGuardKillScore | `807A` | `829A` | `82F4` | `8390` | `84F4` |
| ComputeDamageToGuard | `810C` | `832C` | `8386` | `8422` | `8586` |
| IsSpecialGuardClass | `8230` | `8450` | `84AA` | `8546` | `86AA` |
| FinalizeGuardDeathState9 | `8254` | `8474` | `84D2` | `856E` | `86D2` |
| ComputeGuardContactDamage | `8350` | `8570` | `85CE` | `866A` | `87CE` |
| UpdateWeaponOverlayAnimation | `8434` | `8654` | `86B2` | `874E` | `88B2` |
| RedrawHudSection | `851A` | `873A` | `8798` | `8834` | `8998` |

Addresses are `1000:xxxx` load offsets.

## Version change, which are not only relocation

### `IsSpecialGuardClass`

- DOS 1.0/1.1: `{15,16,19}`
- DOS 1.5/1.7/1.9: `{15,16,19,21}`

Class `0x21` therefore pribudla to special predicate between 1.1 and 1.5.

### HUD dispatcher

- DOS 1.0/1.1 accepts ID up to `0x17` (=23);
- DOS 1.5+ accepts only to `0x16` (=22);
- DOS 1.5+ has moreover before switchom separate one-shot HUD init/clear path.

To dokazuje, that between build prebehla also functional refaktorizácia HUD, nie only move code.

---

# 10. Combat chain, which is after this batch static closed

```text
player shot / projectile collision
        |
        v
1000:5F74 common hit handler
        |
        +--> 8586 ComputeDamageToGuard
        |       + class × weapon resistance
        |       + difficulty
        |       + clamp <=255
        |
        +--> GUARD+10 HP subtract / lethal test
                 |
                 +--> lethal: GUARD death/state chain
                           |
                           +--> 86D2 state-9 finalizer
                           |      + Dracula 11 -> Bat 14 + HP=255
                           |      + Hamerstein special event
                           |
                           +--> 84F4 GetGuardKillScore
                           |      + add signed score to 4180:4182
                           |
                           +--> 8998(4) redraw score

GUARD/object contact with player
        |
        +--> 87CE ComputeGuardContactDamage
        |      + distance/class/RNG
        |      + difficulty
        |
        +--> player HP 4187
        +--> death state if lethal
        +--> 8998(5) redraw health

weapon switch
        |
        +--> 9072 RequestWeaponSwitch       [batch05]
        +--> 88B2 UpdateWeaponOverlayAnimation
        +--> 8998(12) redraw selected weapon
```

---

# 11. Status after batch 06

Najdôležitejší posun:

1. score helper is complete decode including negatívneho score;
2. player→enemy damage has exact resistance maticu and difficulty scaling;
3. enemy→player damage has exact class/distance table and opačný difficulty scaling;
4. Dracula transformácia is directly confirmed raw DOS binary;
5. Hamerstein has separate boss/event completion path;
6. HUD dispatcher has distinguish main section ID;
7. cross-version mapping ukazuje specifically functional zmeny 1.1→1.5.

## Next vhodná batch 07

Najvyššiu value has teraz hlboký analysis okolia callerov:

- `1000:5F74` – common enemy hit/death handler, rozbiť all nonlethal/lethal branches;
- `1000:59F0` – entire GUARD state dispatcher `state 0..21`;
- `1000:54D8`, `5Axx–5Fxx` – guard transition/animation helpers;
- `1000:8EBC–9174` – dokončiť weapon/ammo/fire pipeline and name all HUD section callery.

Priorita for prenositeľný N3D core: **`59F0` + `5F74`**.