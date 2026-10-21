# Nitemare 3D — porovnanie oblastí k 21. 10. 2026

**Upozornenie k percentám:** Ide o expertné orientačné pásma rozsahu porozumenia pôvodným algoritmom, NIE meranú pôvodná-hra-vs-remake 1:1 paritu ani podiel produkčného kódu. Staré odhady pochádzali z menej dôkladného výskumného štádia, preto rozdiel percent nie je objektívne namerané zlepšenie.

## Predtým a teraz

| Oblasť | Skorý orientačný odhad | Dnešný orientačný stav RE | Konkrétne zlepšenie |
|---|---:|---:|---|
| Renderer, poznanie algoritmov | ~60 % | 92–96 % | VEC, 304 ownerov, 16.16, CEDC/22CA, IMG/XLAT; 42/42 pixelov JEDNÉHO writeru |
| GUARD AI | ~45 % | 93–97 % | stavy, death, special-state a lokálne RNG vetvy |
| Enemy HP/damage | ~25 % | 86–92 % | damage gate, rejection, lokálne dôkazy |
| Weapons/ammo/FIRE | ~30 % | 89–94 % | class36 pickup, fire clock, input mask, projectile lifecycle |
| USER.SAV | ~60 % | 89–94 % | DOS/Win16 LOAD scalars, odlišné formáty |
| DOS/Win16 EXE statika | ~54 % | 98–99 % | MZ/NE, opcodes, fixups, WinG/palette/clock |

Historický globálny odhad z 15.10. oproti 21.10.: statické/semantické **99–99,5 → ~99–99,5 %**, behaviorálne **97–98 → ~97–98 %**, pripravenosť na paritné testy **96–97 → ~96–97 %**. Lokálne dôkazy pribudli, nie však celosystémové acceptance. Historický údaj full-parity 89–92 % bol heuristický, **nie** dôkaz 89–92 % pixelovej alebo gameplay parity; aktuálny status: **NEPREUKÁZANÉ 1:1**.

## Súčasné oblasti (výskumné odhady znalosti, nie produkčná parita)

| Oblasť | Odhad znalosti | Hlavné otvorené otázky |
|---|---:|---|
| Dátové formáty/mapy | 97–99 % | rare asset/map varianty |
| DOS/Win16 static callgraph | 98–99 % | nepriamy CFG a skryté vetvy |
| Scheduler/ticks | 94–97 % | E2M10 reentry/ABA, tick vs frame |
| RNG | 96–98 % | koniec DEMO, rejection ordering |
| DEMO | 94–97 % | EOF, input/RNG full ledger |
| Player/key/collisions | 94–97 % | per-tick FIRE/USE, hrany kolízií |
| OBJECT/door/remote | 93–96 % | secret per-tick, remote triggers |
| GUARD/bosses | 90–96 % | boss death/transform a multi-actor |
| Weapons/projectiles | 89–94 % | presné firing, stale-depth, FB–FE |
| Wall renderer | 92–96 % | celý pre/post-wall framebuffer |
| Sprites/HUD/palette | 89–95 % | coverage, shade a RGB6 DAC |
| SAVE/LOAD | 89–94 % | prvý post-LOAD frame/cache |
| SFX/MUSIC | 82–90 % | presné audio timing a output |
| Win16 gameplay | 89–94 % | message-loop/WinG porovnanie |

### Čo konkrétne pribudlo (podľa originálneho kódu/meraní)
- V078 1520/1520 korekcií U; V079 1808/1808 pôvodných perspective-U výpočtov so zachytenými operandmi.
- V080 pôvodný stenový writer x=8: 42/42 byte-for-byte, ale **nie** 64000 pixelov celého frame.
- V081 hráč: Y-krok 11, jedna skrátená kolízia o 6, hranica Y=3291 v E1M1.
- V083: 22/22 ľavých otočení −6, V084B: ALT+šípky = strafe bez zmeny angle.
- V085/V086: 1716 pôvodných RAM vzoriek, 1688 v zhode s host held set, 28 na hranici prechodu, 8/8 Ctrl/Alt/Space masiek. Tieto vzorky **nie sú** emulované ticky.
- DEMO V082: zhodný RNG prefix 35 draws v dvoch oprávnených reláciách; zhoda 220 RNG tuple nepreukazuje rovnaký scheduler context.

### Jediný prijateľný dôkaz pixelového testu
Súčasne zhodný originálny a kandidatny tick/input/kamera/assets/hash; presne 64 000/64 000 indexovaných framebuffer bajtov a 768/768 6-bit DAC hodnôt, žiadny maskovaný neoverený región. Potom osobitne sprites, HUD, SAVE/LOAD, DEMO, AI a level coverage. **Aktívny src/renderer/Raycaster.cpp stále používa diagnostické DDA.**

Podklady: V078_DOS20_TEXTURE_U_22CA_RUNTIME_SK.md, V079_DOS20_CEDC_PERSPECTIVE_RUNTIME_SK.md, V080_DOS20_AUTHENTIC_IMG_WALL_RUNTIME_SK.md, V081_DOS20_LIVE_E1M1_PLAYER_COLLISION_RUNTIME_SK.md, V084B_DOS20_LIVE_E1M1_ALT_STRAFE_SK.md, V085_V086_DOS20_LIVE_E1M1_ACTION_MASKS_SK.md.
