# Nitemare 3D – static analysis functions, batch 07

Primary source: raw binary `N3D-19.exe` (DOS 1.9). Ghidra C export is usage only on xrefy; during `59F0` and `5F74` is export miestami damage zlými boundary, therefore is rozhodujúci raw 16-bit disassembly.

## 1. Functions closed / výrazne spresnené

| DOS 1.9 | Proposed name | Meaning | Confidence |
|---|---|---|---|
| `1000:59F0` | `UpdateGuardState(guard,object)` | dispatcher 22 AI/runtime stavov `0x00–0x15` | Confirmed |
| `1000:5F26` | `UpdateAllGuards()` | iterates guard pool krokom `0x1A` and calls `59F0` | Confirmed |
| `1000:5F66` | `SetGuardState11(guard)` | sets `guard+0x0B = 11` | Confirmed |
| `1000:5F74` | `ApplyPlayerHitToGuard(guard,object)` | player→guard damage, lethal/nonlethal transition, score, pain/death animation | Confirmed |
| `1000:9F98` | `SelectDeathAnimationVariant(guard,object)` | selects valid death-variant `0..7` z class descriptoru | High |
| `1000:9FFC` | `SelectPainAnimationVariant(guard,object)` | selects valid pain-variant `0..7` z class descriptoru | High |

Podporný helper `1000:54D8` is teraz possible safely interpretovať as set animačného runtime state: writes sprite/frame, timer and dvojicu `state/next_state`.

---

## 2. `1000:59F0` – exact GUARD state dispatcher

Dispatcher reads `guard+0x0B`. If is value > `0x15`, only skončí. Jump table has 22 items.

### Confirmed arrays guard recordu

- `+0x00` – first frame / sprite-frame base
- `+0x01` – count/range frameov
- `+0x06` – general timer/countdown
- `+0x08` – index linked 28-B object recordu
- `+0x0A` – behavior/strategy mode
- `+0x0B` – current state
- `+0x0C` – next/return state
- `+0x0D` – value synchronizovaná to linked map/object record during smrti
- `+0x10` – HP
- `+0x11` – orientation/direction
- `+0x12` – hit/pain runtime byte; after hit sa sets on 8
- `+0x13/+0x14` – signed movement offsets X/Y
- `+0x17` – result direction/visibility testu

### Jump table DOS 1.9

| State | Raw target | Behaviorálny meaning |
|---:|---:|---|
| `00` | `15A3C` | timed animation; cyklí frame range, timer--, then `state=next_state` |
| `01` | `15A7A` | wait/delay; after countdown prejde to `02` |
| `02` | `15A94` | pripraví animation/move sequence; through `54D8` creates `state 00 -> next 03` |
| `03` | `15AD4` | perception/attack decision; buď animation `00 -> 04`, or behavior helper |
| `04` | `15B1A` | attack branch; perception + attack/projectile helper; subsequently animation `00 -> 05` |
| `05` | `15B76` | separate behavior/movement handler |
| `06` | `15B7E` | movement + orientation; timer--, after ňom `state=03` |
| `07` | `15BBA` | search/reacquire rozhodovanie, strategy-specific branch |
| `08` | `15C0A` | movement/reacquire; can process to `02` |
| `09` | `15C74` | death/finalize/transform runtime; sem direction finálna death sequence |
| `0A` | `15F20` | no-op / terminal |
| `0B` | `15F20` | no-op / terminal; external helper `5F66` sem vie guard prepnúť |
| `0C` | `15CDC` | orientation/movement helper with parametrom 0 |
| `0D` | `15CDC` | shared handler with `0C` |
| `0E` | `15CF2` | scripted toggle cycle – sleduje global toggle `0x4307` |
| `0F` | `15D22` | scripted toggle cycle + timer, prechod `10` / animation return |
| `10` | `15DA8` | scripted toggle cycle + LOS/test; sets timer 8 and `state=0F` |
| `11` | `15E0E` | timer + new direction + nulovanie movement offsetov; return to `07` |
| `12` | `15E6C` | effect/death-prelude recovery: `object+1A -= 5`, timer--; then `state=next` |
| `13` | `15EB6` | scripted displacement through `58DE` |
| `14` | `15EC8` | long countdown; pod 96 tickov calls movement helper; during konci special callback |
| `15` | `15EFA` | pain/hit animation: postup frame range, then `state=next_state` |

Note: hex state `0x12` = decimal 18, `0x13` = 19, `0x14` = 20, `0x15` = 21.

### State 00 – exact logic

```c
object->frame++;
if (object->frame >= guard->frame_base + guard->frame_count)
    object->frame = guard->frame_base;

if (--guard->timer <= 0)
    guard->state = guard->next_state;
```

### State 12h / decimal 18

```c
if (object->frame < guard->frame_base + guard->frame_count - 1)
    object->frame++;

object->effect_1A -= 5;
if ((int8)object->effect_1A < 0)
    object->effect_1A = 0;

if (guard->timer > 0)
    guard->timer--;

if (guard->timer == 0 && object->effect_1A == 0)
    guard->state = guard->next_state;
```

This branch sa uses during lethal hit, if `object+0x1A > 0`, and then prejde to state 09.

### State 15h / decimal 21

Is čistý hit/pain animation wrapper. increase `object->frame`; when reach end guard frame range, sets `guard->state = guard->next_state`.

---

## 3. `1000:5F26` – UpdateAllGuards

Raw loop confirms:

- guard pool base `0x264E:0x21F9`
- guard stride = `0x1A` = 26 bytes
- count guardov = word `0x6274`
- linked object = `guard+0x08 * 0x1C + 6`, segment `0x21F9`
- for each guard calls `1000:59F0`

Pseudokód:

```c
for (i = 0; i < guard_count; i++) {
    Guard *g = &guards[i];
    Object *o = &objects[g->object_index];
    UpdateGuardState(g, o);
}
```

---

## 4. `1000:5F66` – SetGuardState11

Function is only:

```c
guard->state = 0x0B;
```

Keďže state 0B v `59F0` direction directly on exit, is external spôsob prepnutia guard to inertného/terminal state.

---

## 5. `1000:5F74` – ApplyPlayerHitToGuard

This is main player-hit router for guardov.

### 5.1 Input damage

First call is already identify `1000:8586 ComputeDamageToGuard()`.

```c
damage = ComputeDamageToGuard(guard, object);
```

### 5.2 Lethal branch

If `damage >= guard->HP`:

1. `guard->HP = 0`
2. selects death animation variant through `9F98`
3. executes death-side-effect helper (if global mode `0x418E != 1`)
4. sets death animation through `54D8`
5. if `object+0x1A > 0`, sets `state=0x12`, `next=0x09`
6. otherwise sets `state=0x00`, `next=0x09`
7. pripočíta score through `84F4 GetGuardKillScore()`
8. prekreslí score through `8998(4)`
9. synchronizuje `guard+0x0D` to linked world/map recordu

Therefore death pipeline is:

```text
8586 damage
   ↓ lethal
HP = 0
   ↓
9F98 death animation variant
   ↓
state 12h -> state 09   (ak object+1A > 0)
     alebo
state 00h -> state 09
   ↓
86D2/final death-transform logic z state 09
   ↓
84F4 score
   ↓
8998(4) HUD score
```

### 5.3 Non-lethal branch

If damage = 0, function skončí without change HP.

Otherwise:

```c
guard->HP -= damage;
guard->byte12 = 8;
```

Then sa pain reakcia changes according to `guard+0x0A` strategy and current state.

#### Strategy special branches

- `strategy == 2`: zvolí pain variant and sets animation wrapper, which sa returns to state `08`
- `strategy == 4`: pain transition sa skips
- other: uses všeobecnú state-dependent pain logic

#### Current-state pain routing

For current state `03..15h` uses second jump table:

| Current state | Reakcia on non-lethal hit |
|---:|---|
| `03`, `04`, `0B` | without state transition |
| `07`, `08`, `15` | special pain branch; after animation wrapperi return to `05` |
| other `05..14` | stores current state to `next_state`, sets `state=15h` |

Najdôležitejšia všeobecná branch:

```c
guard->sprite = painSprite[class][variant];
object->frame = low8(guard->sprite);
if (guard->state != 0)
    guard->next_state = guard->state;
guard->state = 0x15;   // decimal 21
```

Thereby is confirmed, that state `0x15` is pain/hit animation, which sa after completion returns to previous state.

---

## 6. `1000:9F98` – SelectDeathAnimationVariant

Function returns variant `0..7`.

- if `guard+0x12 == 0` and class descriptor flag on `+0x59` is nonzero, returns directly `7`
- otherwise generuje `rand() % 7`
- opakuje selection, until corresponding item class descriptoru `+0x4B + variant*2` is not nonzero

Working pseudokód:

```c
int SelectDeathAnimationVariant(Guard *g, Object *o) {
    Desc *d = class_desc[o->type];
    if (g->byte12 == 0 && d->death7_present)
        return 7;
    do {
        v = rand() % 7;
    } while (d->death_anim[v] == 0);
    return v;
}
```

---

## 7. `1000:9FFC` – SelectPainAnimationVariant

Same algoritmus, but uses other part class descriptoru:

- special flag `+0x49`
- variant pointers/IDs `+0x3B + variant*2`

```c
int SelectPainAnimationVariant(Guard *g, Object *o) {
    Desc *d = class_desc[o->type];
    if (g->byte12 == 0 && d->pain7_present)
        return 7;
    do {
        v = rand() % 7;
    } while (d->pain_anim[v] == 0);
    return v;
}
```

Thereby máme confirmed, that enemy/class descriptor has separate tables for pain and death animations.

---

## 8. New exact combat/state diagram

```text
player projectile / hit
        ↓
5F74 ApplyPlayerHitToGuard
        ↓
8586 ComputeDamageToGuard
        ├── damage == 0 → return
        │
        ├── non-lethal
        │      ↓
        │   HP -= damage
        │   byte12 = 8
        │      ↓
        │   9FFC SelectPainAnimationVariant
        │      ↓
        │   state 15h (pain) → previous state
        │   alebo wrapper → state 05 / 08
        │
        └── lethal
               ↓
             HP=0
               ↓
             9F98 SelectDeathAnimationVariant
               ↓
       state 12h/00h → state 09
               ↓
        Final death / transform
               ↓
           score + HUD
```

## 9. Dopad on backlog

Before batch 07 was working backlog hlbokej analysis approximately **1 078** functions z original skupiny 1 086 evidence-based functions. `59F0` and `5F74` already patrili between older first 200 manually posúdených DOS functions, so their prehĺbenie samo o sebe this specific backlog neznižuje. `9F98` and `9FFC` are however mimo this starej first-200 skupiny and teraz are hlboko closed.

**New working backlog: approximately 1 076 functions.**

Number remains mierne movement, because raw binary check can objaviť additional hidden function boundaries, which Ghidra nevytvorila as separate functions.