# NFS World reverse performance tuning solver

This package was built from the supplied `nfsw.exe`, `nfsw.exe.i64`, `attributes.bin`, and `commerce.bin`.

## What was extracted

- `attributes.bin` is a VPAK containing the primary `db` vault.
- `performancepart` class hash: `0x93E84FF7`.
- Its 11 fields are present in the primary vault. The fields relevant to the tuning algorithm are 32-bit integers in the fixed layout:
  - `topspeed`: offset `0x10`
  - `handling`: offset `0x20`
  - `acceleration`: offset `0x24`
- `commerce.bin` is another VPAK containing the `commerce` vault.
- It contains **645** `performancepart` collections.
- It also contains **645 readable `t0_*` names**. Hashing every name with the game's VLT32 hash maps **645/645** names to the 645 collections, with no collision in this set.
- Of these, **565** belong to the six actual performance slots:
  - engine: 97
  - forced induction: 96
  - transmission: 92
  - suspension: 92
  - brakes: 96
  - tires: 92
- The remaining **80** are `miscparts`; all have H/A/T = 0 and are not used as one of the six normal performance slots by the solver.

Example mappings from the supplied files:

| ProductId | TopSpeed | Acceleration | Handling |
|---|---:|---:|---:|
| `t0_pistonhead_tires_elite_commonrarity` | 7 | 6 | 10 |
| `t0_pistonhead_forcedinduction_elite_uncommonrarity` | 16 | 12 | 0 |
| `t0_pistonhead_suspension_elite_greyrarity` | 14 | 6 | 9 |
| `t0_custom_brakes_pro_uncommonrarity` | 0 | 0 | 50 |

The complete table is in `nfsw_performanceparts.csv`.

## Confirmed game algorithm

At `nfsw.exe` around `0x664330`, the game reads each performance part:

- Handling -> `[part+0x20]`
- Acceleration -> `[part+0x24]`
- TopSpeed -> `[part+0x10]`

Each integer is converted to float and multiplied by the single-precision constant `0.01f` (`0.009999999776482582`).

At `0x672230`, the game sums the three normalized dimensions and computes:

```
f = 1 / (1 + (2/3) * (H + A + T) / 100)

wH = (H/100) * f
wA = (A/100) * f
wT = (T/100) * f
wStock = 1 - wH - wA - wT
```

The EXE constant for `2/3` is the float32 value `0.6666666865348816`.

For every vehicle metric, the four `pvehicle` values are blended as:

```
result = B0*wStock + B1*wH + B2*wA + B3*wT
```

where `B0` is stock and `B1/B2/B3` are the second/third/fourth values of that metric.

The displayed integer is produced by `CVTTSS2SI`, i.e. float -> integer truncation toward zero. For normal positive ratings this has the same result as floor.

The algebraic form is the formula from the supplied screenshot:

```
D = H + A + T + 150

result =
    B0 * (225/D - 0.5)
  + B1 * (1.5*H/D)
  + B2 * (1.5*A/D)
  + B3 * (1.5*T/D)
```

So the screenshot formula is confirmed, with `x=Handling`, `y=Acceleration`, `z=TopSpeed`.

## Reverse solver

`nfsw_reverse_tuning_solver.py` takes:

1. Four TopSpeed values of the selected car: `stock,H,A,T`
2. Four Acceleration values: `stock,H,A,T`
3. Four Handling values: `stock,H,A,T`
4. The three displayed tuned values: `TopSpeed,Acceleration,Handling`

Example:

```bash
python nfsw_reverse_tuning_solver.py \
  --topspeed "210.25,320.5,470.75,690" \
  --acceleration "190,335.5,510.25,645.75" \
  --handling "205.5,350.25,525,660.5" \
  --observed "430,427,442" \
  --max-results 50 \
  --output solutions.csv
```

Useful switches:

- `--exclude-custom` excludes `t0_custom_*` special/developer parts.
- `--allow-empty` allows a stock/unmodified slot with H=A=T=0.
- `--max-results N` limits printed concrete sets.
- `--output file.csv` saves the shown concrete solutions.
- `--self-test` runs the included consistency test.

The solver first finds possible aggregate `(sumHandling, sumAcceleration, sumTopSpeed)` triples that reproduce the displayed values. It then uses a meet-in-the-middle search across the six slots to recover concrete `t0_*` part sets. Because different parts can have identical H/A/T triples, the inverse problem can legitimately have multiple solutions; the solver reports them rather than inventing a unique answer.