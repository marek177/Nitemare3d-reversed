# Nitemare 3D – static analysis functions, batch 05

Source base: `N3D-19.exe` (DOS 1.9) as primary binary source. `N3D-19.exe.c` and older index are usage only as pomôcka on function boundaries/xrefy. Names below are analytické, nie original symbol.

## AND. DOS XMS / cache backend

| DOS 1.9 | Proposed name | Meaning | Confidence |
|---|---|---|---|
| `1000:769A` | `ManageXmsBackedResourceCache(mode)` | mode 0 initializes cache and XMS, mode 1 unlock+free XMS block, mode 2 resets cache links | High |
| `1000:790A` | `CopyConventionalBlockToXmsPool(src,size)` | zaokrúhli size on 1 KiB, zostaví XMS Move descriptor, copies conventional→XMS, posunie pool offset | High |
| `1000:79C6` | `CopyXmsPoolBlockToConventional(dst,xmsOff,size)` | zaokrúhli size on 1 KiB and copies XMS→conventional through XMS Move | High |
| `1000:7A44` | `MoveBlockToXmsAndEncodeOffset(record)` | move block to XMS and nahradí original pointer negative/encode XMS offset | Medium-High |
| `1000:7A78` | `LoadBlockIntoLruCacheSlot(record)` | selects najstarší cache slot, free link, restores block z XMS or copies z original source | Medium-High |
| `1000:7B4E` | `LoadBlockIntoRoundRobinCacheSlot(record)` | uses second cache with rotate index, restores content z XMS/original source | Medium-High |
| `1000:7BF6` | `CacheResourceTableEntry(index)` | deduplikuje table records and presúva small blocks to XMS-backed cache | Medium |
| `1000:7CFA` | `AcquireCachedResourceTableEntry(index)` | finds existing cache slot or obsadí LRU slot and restores content | Medium-High |
| `1000:7DFA` | `XmsDetectAndGetEntryPoint()` | `AX=4300h INT 2Fh`; during success `AX=4310h INT 2Fh`, stores `ES:BX` entry point | Confirmed |
| `1000:7E20` | `XmsQueryLargestFreeBlockKb()` | XMS function `AH=08h`; return AX = najväčší free block v KiB | Confirmed |
| `1000:7E38` | `XmsAllocateBlockKb(sizeKb)` | XMS `AH=09h`, `DX=size`; during success returns handle z DX | Confirmed |
| `1000:7E5A` | `XmsFreeBlock(handle)` | XMS `AH=0Ah` | Confirmed |
| `1000:7E74` | `XmsMoveBlock(moveDescriptor)` | XMS `AH=0Bh`, `DS:SI` -> 16-byte XMS Move descriptor | Confirmed |
| `1000:7E9C` | `XmsLockBlock(handle)` | XMS `AH=0Ch`; success returns lineárnu address `DX:BX` | Confirmed |
| `1000:7EBA` | `XmsUnlockBlock(handle)` | XMS `AH=0Dh` | Confirmed |

### XMS cross-version anchor

| Function | DOS 1.0 | DOS 1.1 | DOS 1.5 | DOS 1.7 | DOS 1.9 |
|---|---:|---:|---:|---:|---:|
| XMS detect / entry | `1000:7980` | `1000:7BA0` | `1000:7BFA` | `1000:7C96` | `1000:7DFA` |
| Query free (08h) | `1000:79A6` | `1000:7BC6` | `1000:7C20` | `1000:7CBC` | `1000:7E20` |
| Allocate (09h) | `1000:79BE` | `1000:7BDE` | `1000:7C38` | `1000:7CD4` | `1000:7E38` |
| Free (0Ah) | `1000:79E0` | `1000:7C00` | `1000:7C5A` | `1000:7CF6` | `1000:7E5A` |
| Move (0Bh) | `1000:79FA` | `1000:7C1A` | `1000:7C74` | `1000:7D10` | `1000:7E74` |
| Lock (0Ch) | `1000:7A22` | `1000:7C42` | `1000:7C9C` | `1000:7D38` | `1000:7E9C` |
| Unlock (0Dh) | `1000:7A40` | `1000:7C60`* | `1000:7CBA` | `1000:7D56` | `1000:7EBA` |

`*` DOS 1.1 C export zrejme zlúčil next code to tela this functions (76 row namiesto ~13); binary inštrukčná sequence XMS unlock is however same. Is to next evidence, that boundary needs to verify v EXE.

## B. Player projectile runtime

| DOS 1.9 | Proposed name | Finding behavior | Confidence |
|---|---|---|---|
| `1000:7F8C` | `ResolvePlayerProjectileCollision(cell,x,y)` | reads vlastnosti mapovej cells, handles blokovanie/special boundary records; during hit entity checks difference coordinates and calls damage handler `5F74` | High |
| `1000:8138` | `AdvancePlayerProjectile(projectile)` | DDA/Bresenham-like substep movement; after each kroku calls `7F8C`; during collision switches status on impact, reset frame, selects impact sprite and sets flag `0x10` | High |
| `1000:8226` | `UpdatePlayerProjectilePool()` | iterate 8 slotov, stride `0x2A`; status 1 = let, status 2 = impact animation; aktualizuje frame according to time and sprite tables; during letu calls `8138` | High |
| `1000:8EBC` | `SelectProjectileFlightSpriteForCurrentWeapon()` | selects sprite offset z `{0,2,0,0}` + base `D50D` according to current weapons `418D` | Medium |
| `1000:8EE2` | `SelectProjectileImpactSpriteForCurrentWeapon()` | selects sprite offset z `{1,3,1,1}` + base `D50D`; directly sa uses during collision v `8138` | High |

### Projectile slot – partially rekonštruované arrays

Pool: `0x41B4`, 8 × `0x2A` bytes.

- `+0x0C` byte: runtime state (`1` flying, `2` impact; `0` inactive)
- `+0x11` byte: animation frame
- `+0x12` byte: sprite/effect type index
- `+0x13` byte: flags; during impacte sa sets bit `0x10`
- `+0x16/+0x18` dword: next animation timestamp
- `+0x1E` word: X position
- `+0x20` word: Y position
- first ~12 bytes: DDA/Bresenham movement state (major axis/error/divide/steps) – exact names individual členov still open

## C. DOS mouse backend

| DOS 1.9 | Proposed name | Evidence | Confidence |
|---|---|---|---|
| `1000:8346` | `MouseGetPositionAndButtons(x,y,buttons)` | INT 33h function 03h; maskuje button state `& 3`, returns X/Y | Confirmed |
| `1000:837A` | `MouseSetPosition(x,y)` | INT 33h function 04h | Confirmed |
| `1000:839E` | `MouseShowCursor()` | **new function boundary missing v C exporte**; INT 33h function 01h | Confirmed |
| `1000:83B6` | `MouseHideCursor()` | **new function boundary missing v C exporte**; INT 33h function 02h | Confirmed |

## D. Weapon/ammo helpers

| DOS 1.9 | Proposed name | Behavior | Confidence |
|---|---|---|---|
| `1000:8F08` | `ConsumeAmmoForCurrentWeapon()` | according to `418D` decrements corresponding ammo counter; during `4151!=0` nič nespotrebuje; subsequently calls HUD/event dispatcher `8998` | High |
| `1000:8F6C` | `AddOrSetAmmo(param1,mode)` | v jednom mode adds +20 to limitu ~100; v druhom sets value 50; map param1→ammo counter sa differs according to mode | Medium-High |
| `1000:901C` | `UpdateWeaponFireGate(mode,request)` | uses weapon-dependent limit z tables `143C+weapon` and reads/inkrementuje counter `1440`; probably cadence/cooldown gate | Medium |
| `1000:9072` | `RequestWeaponSwitch(weapon)` | if is not weapon active, sets ju okamžite; otherwise stores pending weapon `41A2` and sets prechodový status `41A4` | High |

## Conclusion batch 05

This batch oddeľuje three meaning subsystémy, which were predtým v anonymných `FUN_...` block:

1. stabilný DOS XMS/cache backend,
2. player projectile runtime,
3. DOS mouse + part weapon/ammo state machine.

Najdôležitejší new binary finding are functions `1000:839E` and `1000:83B6`, which C export nevyčlenil. To confirms, that function count z `.c` exportu cannot považovať for complete count actual functional boundaries.

Next vhodná batch: large game dispatchery `1000:84F4`, `1000:86D2`, `1000:87CE`, `1000:8998` rozbiť on case/family blocks and assign their k OBJECT / enemy / pickup / weapon event.