# V070 Renderer 1:1 – verifikačný záznam, 2026-10-20

**Účel:** Priblížiť ohraničený originálny DOS2 raster a sprite writer
bez nekontrolovaného zásahu do živého DDA preview.

## Nové implementované dôkazové vrstvy

| Layer | Pôvodný dôkaz | Lokálna implementácia | 1:1 limit |
|---|---|---|---|
| UI/IMG blit | V073 natural `097A:07DE`, x8,y4,22x96, key0, page0 | `Dos20TransparentVgaBlit.hpp` + Python oracle | Neoverené ďalšie page flags, clipping, RGB a finálny framebuffer |
| Sprite column | Instruction-backed DOS2 `1000:1B3E` | `Dos20SpriteStripeEvidence.hpp` používa existujúci `N3DDos20SpriteRaster.hpp` | Projekcia, ordering, animácie, depth ties vo všetkých scénach neuzavreté |
| Wall scaled VGA column | V066 DOS2 writer 097A:0599..05D5 | `Dos20ScaledColumn.hpp` sampled/XLAT/planar model | One original bounded call, not full scene |
| Wall VEC/projected | V067 pôvodný snapshot, 36/36 WORD | import dôkazových headerov a testov | 2 V069 offscreen projekcie, ďalšie uhly |
| Wall owner/span | V067/V068/V069 pôvodný snapshot, 304/304 owner, 162/162 span bytes | V067/068 modely; V069 forward model nie je zahrnutý | v ďalších kamerách, texture U/V |
| Indexed/DAC difference | V066 originálny framebuffer/VGA source-vs-source | striktne binárny comparator | bez presne párovaného pôvodného remaku nemôže potvrdiť parity |

## Test execution

V lokálnom kontajneri boli vykonané:
- 6/6 CTest (modely projection/span/pool + oba raster testes), Debug.
- 6/6 CTest s `-fsanitize=undefined -fno-sanitize-recover=all`.
- 26 Python oracle testov: 25 prešlo, 1 bol preskočený bez pôvodného komerčného snapshotu.
- 13 Python syntetických kontrol V066 oracle; `n3d_pixel_diff.py` negative tests PASS.
- Inštalátor 1. aplikácia/2. aplikácia/dry-run/conflict rollback PASS na syntetickom checkoute.

Naším dátovým cieľom nie sú percentá zdrojákov, ale **nula pixelových
odlišností pri synchronizovanom pokuse**. Nové testy **neznamenajú** nič o
celohrovom percentuálnom dokončení rendereru.
