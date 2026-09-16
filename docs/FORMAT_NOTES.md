# Nitemare 3D Windows data-format notes

## MAP.1 / MAP.2 / MAP.3

- byte 0..1: little-endian level count (`11`, `10`, `10`)
- header size: 514 bytes
- each level: 8192 bytes
- grid: 64 x 64 cells
- each cell: 2 bytes (`wall/tile id`, `object/item id`)

Episode 1 contains 11 chunks; E1M11 is retained as the demo map.

## IMG.1 / IMG.2 / IMG.3

- offset 0: 32-bit reserved/unknown value
- offset 4 onward: 32-bit little-endian slot/sequence offset table
- first table value is the first payload offset (`0xBC00` in the supplied files)
- payload frames: width byte, height byte, 8 metadata bytes, then width*height indexed pixels
- pixels are stored x-major/column-major

The slot table contains zeros, duplicates and offsets that are not always exact frame starts, so raw table values are retained.

## SND.DAT / UIF.DAT

Archive descriptors are 6 bytes: `uint16 length` + `uint32 absolute offset`. The descriptor whose `offset + length == file_size` terminates the index.

## GAME.PAL

The supplied `GAME.PAL` is structurally an 8-bit PCX file with a standard 256-color palette trailer.

## DEMO.1 / DEMO.2 / DEMO.3

All three supplied files use 3 x uint16 header words followed by 8-byte records. The second 32-bit value is monotonic and is exposed as `tick`; the first remains `rawInputState` until its bit mapping is confirmed from NITE3W.EXE.

## ENDING.FLI

Standard FLI/FLC-family header. The supplied animation is 320x200x8 with 488 frames in the header.

## OBJECTS.* / WALLS.*

Line-oriented editor definition tables with logical fields `hex_id`, `visual_code`, `image_name`, `class_name`, and description. Runtime semantics are only promoted from raw names when confirmed by executable or gameplay evidence.
