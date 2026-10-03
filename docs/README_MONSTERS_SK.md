# Nitemare 3D → GZDoom/ZDoom: MONSTERS a rotácie

Tento súbor drží **monštrá oddelene od objektov**. Číslo `sprite group` je logická skupina exportovaných BMP (`object ID + 256`). Ak skupina v ZIPe chýba, je to výslovne označené.

## Rotácie – pravidlá

- **ROT8_4PHASE**: prvých 32 obrázkov = 8 smerových blokov × 4 fázy pohybu. Pre GZDoom sa preusporiadajú po fázach: A=`01,05,09,13,17,21,25,29`, B=`02,06,...30`, C=`03,07,...31`, D=`04,08,...32`.
- **ROT4_8PHASE**: prvých 32 obrázkov = 4 smerové bloky × 8 fáz. V obrazoch Penelope/Dr. Hamerstein je poradie blokov vizuálne `Side-A, Front, Side-B, Back`. Do Doom 8-rotácie treba diagonály dočasne duplikovať alebo neskôr dokresliť.
- **ROT0**: sprite je kamerovo orientovaný/front-facing; v Doom formáte použite rotáciu `0` (`XXXXA0`).
- **ROT4_STATIC**: 4 mapové orientácie N/E/S/W; pre Doom 8 rotácií sa dočasne zdvojnásobia diagonály.
- **SPECIAL/UNKNOWN**: nedávať do bežnej rotačnej pipeline, kým nebude hotový osobitný audit.

Dôležité: pri ROT8 je poradie oktantov O0→O7 jasne blokové, ale **ľavo/pravá orientácia voči Doom číslam 2–8 sa má potvrdiť v GZDoom teste**. Ak je zrkadlovo opačná, stačí vymeniť `2↔8`, `3↔7`, `4↔6`.

## Zoznam monštier

| Monster | Prefix | Rotácia | Epizódy / group / frames | Poznámka |
|---|---|---|---|---|
| Penelope | `PENE` | **ROT4_8PHASE** | E1: 444 / 32; E3: 368 / 32 | Frames 01-32 form four direction blocks x 8 movement phases. |
| Dr. Hamerstein | `DRHM` | **ROT4_8PHASE** | E1: 452 / 46; E3: 376 / 46 | Frames 01-32 form four direction blocks x 8 movement phases. |
| Bat | `NBAT` | **ROT0** | E1: 384 / 12; E2: 384 / 12 | View-independent flying animation; spawn IDs still have N/E/S/W. |
| Frankenstein | `FRNK` | **ROT8_4PHASE** | E1: 388 / 53; E2: 388 / 53 | Frames 01-32 visibly form 8 directions x 4 movement phases. |
| Mummy | `MUMY` | **ROT8_4PHASE** | E1: 392 / 53; E2: 392 / 53 | Frames 01-32 visibly form 8 directions x 4 movement phases. |
| Dancers | `DANC` | **SPECIAL** | E1: 396 / 20 | GUARD26 scripted/mixed sequence; keep outside normal monster rotation pipeline. |
| Skeleton | `SKEL` | **ROT8_4PHASE** | E1: 400 / 54; E2: 400 / 54 | Frames 01-32 visibly form 8 directions x 4 movement phases; later action/death frames differ. |
| Mrs H. | `MRSH` | **ROT0** | E1: 404 / 16; E2: 404 / 16 | Front-facing animation family; no clear 8-direction walk bank. |
| Zelda | `ZELD` | **ROT0** | E1: 408 / 16; E2: 408 / 16 | 16-frame front-facing/casting/death sequence. |
| Vampira | `VAMP` | **ROT0** | E1: 412 / 16; E2: 412 / 16 | Front-facing animation family. |
| Baddie #1 | `BD01` | **ROT8_4PHASE** | E1: 416 / 53; E2: 416 / 53 | Frames 01-32 visibly form 8 directions x 4 movement phases. |
| Baddie #2 | `BD02` | **ROT8_4PHASE** | E1: 424 / 53; E2: 424 / 53 | Same directional family as Baddie #1. |
| Dracula | `DRAC` | **ROT0** | E1: 432 / 19; E2: 432 / 19 | Front-facing animation/transformation sequence; includes bat-related frames. |
| Cemetary wall Gargoyle | `CGAR` | **ROT0** | E1: 436 / 16; E2: 436 / 16 | Front-facing animation/explosion/casting sequence. |
| Garden wall Gargoyle | `GGAR` | **ROT0** | E1: 440 / 16; E2: 440 / 16 | Front-facing animation/explosion/casting sequence. |
| Cannon | `CANN` | **ROT4_STATIC** | E1: 460 / 5; E2: 456 / 5 | Four N/E/S/W map orientations plus action frame(s); no walking rotation bank. |
| Tall slim robot | `RBT1` | **ROT0** | E2: 444 / 16 | Supplied E2 group shows front-facing animation only. |
| Trashcan robot | `RBT2` | **UNKNOWN** | E2: 448 / ? | Defined in OBJECTS.2, but its expected BMP group is absent from supplied ZIP. |
| Ghost | `GHST` | **ROT0** | E3: 384 / 18 | Front-facing floating/attack/death animation. |
| Goldie | `GOLD` | **ROT0** | E3: 388 / 16 | Front-facing animation. |
| Greenie | `GRNI` | **ROT0** | E3: 392 / 16 | Front-facing animation. |
| Demon | `DEMN` | **ROT0** | E3: 396 / 17 | Front-facing animation. |
| Alien #1 | `ALN1` | **ROT8_4PHASE** | E3: 400 / 45 | Frames 01-32 visibly form 8 directions x 4 movement phases. |
| Alien #2 | `ALN2` | **ROT8_4PHASE** | E3: 408 / 45 | Frames 01-32 visibly form 8 directions x 4 movement phases. |

## Oddelenie podľa typu rotácie

- **ROT8_4PHASE:** Frankenstein, Mummy, Skeleton, Baddie #1, Baddie #2, Alien #1, Alien #2
- **ROT4_8PHASE:** Penelope, Dr. Hamerstein
- **ROT4_STATIC:** Cannon
- **ROT0:** Bat, Mrs H., Zelda, Vampira, Dracula, Cemetary wall Gargoyle, Garden wall Gargoyle, Tall slim robot, Ghost, Goldie, Greenie, Demon
- **SPECIAL:** Dancers
- **UNKNOWN:** Trashcan robot

## Predbežné target názvy Doom sprite lumpov

Použité 4-znakové prefixy sú v tabuľke vyššie. Príklad Frankenstein: `FRNKA1` … `FRNKA8`, `FRNKB1` … `FRNKB8`, atď. Kompletný automatický mapping prvých 32 rotačných snímok je v `rotation_frame_mapping.csv`.