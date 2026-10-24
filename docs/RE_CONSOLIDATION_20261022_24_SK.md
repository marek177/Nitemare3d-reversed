# Výskumná konsolidácia 22.–24. 10. 2026 — DOS a Win16

## Zámer a hranice dôkazov
Táto aktualizácia spája existujúci audit z 22.10. s analýzami používateľa z 23.–24.10. Používateľ v samostatných reláciách pracoval s DOS dekompilátmi `N3D-10/11/12/15/17/18/19/20.c`, s Win16 variantmi `NITE3W` (v1.0, v1.3, v1.6, v1.8, v1.10) a so skupinami archivovaných savegame. Bez priloženia konkrétnych binárnych artefaktov do tohto commitu nejde o nové SHA-potvrdené extrakcie ani opakovanie všetkých runtime experimentov. Stav každého tvrdenia preto rozlišujeme.

**R** = doložené original-game runtime vo starších repo reportoch; **S** = statická rekonštrukcia; **T** = nový syntetický/kontraktový test; **O** = otvorené.

## Priame mosty do implementácie
| Subsystém | Dôkaz, ktorý už máme | Bezpečný kódový krok | Čo sa stále nesmie tvrdiť |
|---|---|---|---|
| Input | R: V085/V086 Ctrl=0x0080, Alt=0x0100, Space=0x0200, vrátane kombinácií | vstupné bity; rearm/fire event tests | presné tick-atomické fire poradie |
| Player | R: V081, V083, V084/B: obmedzené E1M1 kroky, rotácie ±6, clipping | testovacie vektory s presnými predpokladmi | univerzálne kolízne pravidlo |
| Projectile | R: V056, V083: jeden 0→1→2→0 lifecycle; S: 21FD cache +0x18 | typovaný model záznamu a sledovanie vlastníctva zápisov | všeobecné collision/damage/stale-depth |
| Renderer | R/B: V078 1520/1520 U; V079 1808/1808 CEDC; V080 jeden x8 writer 42/42 | stage-replay a prísna framebuffer/DAC kontrola | pixel-perfect 320×200 celej hry |
| Save/load | R: V059 Win16 v1.10 save/load view; archívne DOS/Win save korpusy analyzované v 23.10 relácii | lossless raw transport, verzionované field maps po verifikácii | DOS↔Win plná kompatibilita |
| DEMO/RNG | R: V063/V076 original seed/ledger na ohraničených prefixoch | chronologický event ledger + first-divergence report | kompletná frame/tick deterministika |
| GUARD/OBJECT | S: uložené polia, state21/state41 výskumné vetvy | invarianty rozmeru a ABI, per-slot scheduler trace | všetci bossovia, E2M10 ABA |
| Maps | S: 0x25–0x28 cross-build štyri opakované hodnoty, overený obmedzený vizuálny efekt | verzionované MAP decode test vectors | absolútna sémantika vo všetkých 31 mapách |

## Čo pribudlo 23.–24.10 v pracovných rozhovoroch
1. DOS dekompiláty a archívy viacerých verzií sa používajú na hľadanie vynechaných vetiev, offsetov a duplicitných nálezov; bez uloženej matice byte-to-address sú konkrétne nové adresy **nepotvrdené pre túto publikáciu**.
2. Win16 dekompiláty 1.0–1.10 sa porovnávajú v rovnakých subsystémoch (savegame, timer, message loop, input, renderer). Odlišnosti musia byť naviazané na verziu, nie prenesené na všetky vydania.
3. Savegame korpusy (`10,11,12,15,17,19,20` DOS a `10,13,16,18,110` Windows) sú podkladom pre binárnu štruktúrnu maticu; žiadne komerčné dáta nie sú súčasťou repozitára.
4. Implementačné smerovanie: prvý krok je bezstratový binárny round-trip a porovnávač, až potom stavové polia a konverzie. [OpenNitemare3D implementačný most](https://github.com/marek177/OpenNitemare3D/blob/main/docs/OCT22_24_2026_IMPLEMENTATION_BRIDGE.md).

## Prioritné akceptačné testy
1. **SAVE byte fidelity:** `encode(decode(blob)) == blob` cez všetky potvrdené vydania a negatívne varianty; nesmie dôjsť k tichému prepísaniu neznámych bajtov.
2. **Same-tick input:** presné Ctrl/Alt/Space skeny, press-release/held maska, správne označenie host polling vs guest tick.
3. **First divergence:** prvá odchýlka v tick, slot, RNG draw, objekt update order, projectile status, player XY a angle.
4. **Renderer:** porovnať presne 64 000 indexed pixelov a 768 DAC bajtov toho istého checkpointu, nie iba vizuálnu podobnosť.
5. **LOAD resume:** prvý originálny update/frame po load, obnovenie skrytých cache a stavov.
6. **Cross-build:** DOS 1.x→2.0 a Win16 1.0→1.10 testovať samostatne, nepretláčať spoločné offsety bez per-version dôkazu.

## Otvorené P0
- presné scheduler poradie, E2M10 ABA, natural stale-depth hit;
- projektil damage a boss/special death;
- kompletné DEMO EOF+input+RNG chronológie;
- secret-door USE range, smer, posuv per tick;
- originálny VEC renderer plný gameplay framebuffer + DAC;
- prvý post-LOAD frame a Win16 súbežné hodiny.

## Protokol pridávania nových faktov
Každý nový fakt nech má: originálny build/EXE SHA; presné CS:IP/DS:offset alebo formát offset; citovaný raw zdroj; metódu (S/R/T); rozsah testovaných scenárov; reprodukčné kroky; otvorené protipríklady. **Nikdy** neprepisovať hypotézu na 1:1 len na základe prekladu C kódu alebo syntetického CI.

## Existujúce zdroje
- [Index všetkých runtime a statických poznatkov (22.10.)](RE_ALL_RUNTIME_STATIC_20261022_SK.md)
- [Curated evidence registry](RE_EVIDENCE_REGISTRY_20261022.json)
- [Ghidra cache alias](RE_STATIC_GHIDRA_CACHE_20261022_SK.md)
- [Original FIRE pickup](RE_DOS20_FIRE_PICKUP_20261022_SK.md)
- [Parity bridge](RE_ALLINONE_PARITY_BRIDGE_20261022_SK.md)
