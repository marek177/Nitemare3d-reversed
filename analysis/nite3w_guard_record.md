# NITE3W guard/runtime record reconstruction

Source executable SHA-256: `12fe5168783446275802e0e947898261b5eca6b88288f3a895fc1faa4c544481`

## CONFIRMED debug-format XREF

Segment 3 at `0xABD7` pushes the format string:

`class %d, strength %d, strategy %d\nstate %d, nextstate %d, timer %d\noctant %d, resoct %d`

The preceding pushes can be mapped to printf-style arguments in reverse order.

| Record offset | Width | Confirmed semantic |
|---|---:|---|
| +0x06 | word | timer |
| +0x08 | word | index used to derive class |
| +0x0A | byte | strategy |
| +0x0B | byte | state |
| +0x0C | byte | nextstate |
| +0x10 | byte | strength |
| +0x11 | byte | octant |
| +0x12 | byte | resoct |

### Class lookup

The code performs:

`imul bx, es:[si+0x08], 0x1C`

then reads a byte from a second table at `[bx + 0x6D6C]`.

Therefore the runtime record does not appear to store the printed class directly at the inspected offsets. Offset +0x08 indexes a second table whose records have a confirmed stride of 0x1C bytes; the byte at that table's base field is printed as `class`.

This is an important distinction: the 0x1C stride belongs to the indexed class/definition table at this XREF. It must not yet be called the guard runtime-record size.

## CONFIRMED correction to earlier working hypothesis

A separate visible-object path near segment 3 `0xCE91` uses `imul ..., 0x1A`, i.e. a 26-byte table stride. It is a distinct structure/table from the 0x1C definition table above.

Earlier audit language suggesting a general 0x1C gameplay/guard record was too broad. The evidence now supports at least two distinct fixed-size records:
- 0x1C (28 bytes): class/definition table reached through runtime-record +0x08.
- 0x1A (26 bytes): separate visible-object/vector-related table in the 0xCExx path.

## Strength is not yet renamed HP

`strength` is a confirmed original semantic label because it is printed by shipped executable debug code. Whether it represents current HP, base HP, attack strength, durability, or another quantity remains unresolved. It will be promoted to HP only after a decrement/death-state or initialization chain proves that interpretation.
