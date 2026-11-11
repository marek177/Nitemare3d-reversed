# PASS1: 256-bajtová CRT ASCII klasifikácia

Obraz SHA-256 `e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297`. Tabuľka **DS:2369..2469**, obraz **[29A79,29B79)**, má 256 BYTE bitmask položiek. Rozsah podporuje spotrebiteľ na 12C3C..12C40: načíta BL z bajtu, vynuluje BH a testuje DS:[BX+2369h]. Tým je nominálne adresovateľných všetkých 256 indexov, nie iba počiatočný nenulový ASCII prefix.

| Maska | Presná množina indexov s bitom |
|---|---|
| 01h | A..Z |
| 02h | a..z |
| 04h | 0..9 |
| 08h | TAB, LF, VT, FF, CR a medzera |
| 10h | ASCII interpunkcia 21h..2Fh,3Ah..40h,5Bh..60h,7Bh..7Eh |
| 20h | 00h..1Fh a DEL 7Fh |
| 40h | iba medzera 20h |
| 80h | 0..9, A..F, a..f |

Skript overuje **úplnú rovnosť množín pre každý bit cez všetkých 256 položiek**. Indexy 80h..FFh majú všetky masky nulové; nejde o padding iba preto, že sú nulové. Byte pred bázou sa touto dávkou nepreznačuje. Ide o statický počiatočný obsah, nie dôkaz runtime nemennosti.

## Xrefs a prompt správanie

V historickom inventári je 13 literálnych prístupov k báze 2369h; každý sa overil proti obrazu a nezávislému dekóderu. Presné sites a ASM sú v `pass1_ctype/references.csv`. Nie všetci calleri majú rovnaký indexový kontrakt: prompt helper 0D29:0720 používa CBW a signed index. Pri vstupnom BYTE >=80h preto číta **pred** nominálnou bázou, nie z nulovej hornej polovice tabuľky. Známa 256-bajtová tabuľka túto odlišnú cestu neoprávňuje ignorovať.

Pri ASCII vstupoch 00h..7Fh sa prompt bit 02h dá presne pomenovať ako lowercase test a následné AL-20h ako ASCII uppercase transformácia. Pri vysokých bajtoch treba zvlášť analyzovať obsah pred tabuľkou a pôvod input hodnôt. DF a prirodzené caller DS zostávajú otvorené. Konkrétna značka CRT sa zo samotnej bitovej konvencie nepriraďuje.

## Reprodukcia a pokrytie

`audit_pass1_ctype.py IMAGE INVENTORY DECODER_DIR OUT` kontroluje SHA, explicitný zero-extended BYTE index, všetky maskové množiny a 13 referencií. Produkuje 256 adresných položiek, typový rozsah, xrefs a summary. `promote_pass1_fields.py` používa predchádzajúcu mapu `pass1_prompt_fields/noncode_intervals.csv`. Výstupy sú v `pass1_ctype/`.

Všetkých **256 B** prešlo z CLASSIFIED ONLY do PARTIAL. Aktuálne **PARTIAL 50 357 B, CLASSIFIED ONLY 6 894 B, UNKNOWN 44 B, DEEP VERIFIED 0 B**, spolu 57 295 B. Predošlá mapa: 50 101 / 7 150 / 44 / 0 B. Netypované relokačné PARTIAL bajty zostávajú 20 B. Nový prirodzený runtime ani replay sa nevykonal; enumerácia maskových množín je statická kontrola, nie 256 runtime testov.

DOSBox-X plán: vstupné AL z input helpera, signed index v promptoch, DS a prípadní writeri tabuľky. Ďalší krok: zvyšných 6 894 CLASSIFIED ONLY bajtov a kontrakt vysokých input hodnôt, bez sémantického percenta z počtu klasifikačných položiek.


## Aktualizácia 13 oblastí

Nové sémantické percento je všade N/A: úplný inventár kontraktov/polí/vetiev chýba. Metodika je uzavreté jednotky / úplný inventár oblasti, runtime parity osobitne. Historické percentá sú orientačné odhady.

| Oblasť | Predošlý odhad | Nové % | Potvrdenie | Neznáme / blokátor | Ďalší krok |
|---|---:|---|---|---|---|
| Mapy a formáty | 99 % | N/A | opravená mapa a flagy | prirodzené súbory | serializačná stopa |
| Dátové typy a konštanty | 95 % | N/A | 190 polí/33 zdrojov; 256 B ASCII table | 20 relokačných B bez typu | roly segmentov |
| Tabuľky a ukazovatele | 93 % | N/A | 13 classification xrefs; exact mask sets | writeri/lifetime | pointer watchpointy |
| Funkcie / ASM / CFG | 90 % | N/A | 34 rozsahov, 1 150 inštrukcií | kontrakty/dosiahnuteľnosť | caller stopy |
| RNG | 97 % | N/A | bez nového dôkazu | caller inventár | RNG ledger |
| Scheduler | 96 % | N/A | staršie PIT dôkazy zachované | tick ordering | PIT spotrebitelia |
| DEMO a vstupy | 96 % | N/A | bez nového dôkazu | determinizmus | párová DEMO stopa |
| Renderer / VGA | 94 % | N/A | bit reversal začlenený | clipping/orientácia | payload spotrebiteľ |
| GUARD / bossovia | 93 % | N/A | nominálne pole 100×26 | AI/lifecycle | inicializátory |
| Zbrane / projektily | 92 % | N/A | bez nového dôkazu | kolízie/sloty | kolízne vetvy |
| Sprity / HUD / paleta | 92 % | N/A | 60 počiatočných UI textov | textový lifetime | SS čítania po návrate |
| SAVE / LOAD | 92 % | N/A | mapové/flagové rozsahy | LOAD parity | párový stav |
| Windows Win16 | 92 % | N/A | staršie NE dôkazy zachované | callback DS/import ABI | runtime selektory |

