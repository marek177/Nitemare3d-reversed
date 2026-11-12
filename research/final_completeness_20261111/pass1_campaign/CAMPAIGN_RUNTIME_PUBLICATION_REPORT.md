# Publikovanie runtime a analytickej dávky

Overený analytický commit: `2ced761cb0bf1eece24a224e92c05636058ab0ae`, parent `8052ec6328b320633babef328e4e6f3831de041a`, vetva `codex/final-re-completeness-20261111`, repozitár `marek177/Nitemare3d-reversed`.

Publikovaných bolo 154 nových alebo zmenených textových blobov vrátane manifestov. Každý blob bol porovnaný s lokálne vypočítaným Git SHA-1; ďalších 4731 existujúcich blobov bolo overene zachovaných. Tree `ad26449624274896d89c0a8e40e2721acd33095f` má spolu4885 blobov. Aktualizácia vetvy použila kontrolu predchádzajúceho HEAD a nebola vynútená. Následný read potvrdil analytický commit ako HEAD v okamihu publikácie.

Obsah: aktuálna mapa PASS320,122 ohraničených funkčných rozsahov,5 nezávisle overených zachovaných DOSBox inicializačných scenárov, sprite clipping/pixel replay, CRT/input/heap dôkazy a hook rodina8 DOS štítkov. Runtime session prefixy sa prekrývajú. PARTIAL57102B /CLASSIFIED ONLY149B /UNKNOWN44B /DEEP VERIFIED0B, spolu57295B. Integrita mapy ani počet skúšok nedokazujú plnú sémantickú úplnosť.

Pôvodné EXE, herné dáta, dekóder/emulátor binárky a raw runtime memory dumpy sa nepublikovali. Ich veľkosti, hashe a spôsob reprodukcie sú v manifestoch a harness skriptoch. Pôvodné source ASM tretích strán sa tiež nezavádzajú. Raw capture proof obsahuje lokálne cesty; pre prenos treba vytvoriť novú zachovanú session s presnými vstupnými súbormi a príslušným verifierom.

`publication_runtime_20261112/meta.json`, `manifest.json`, `omitted.json` a `payload.json` uchovávajú lokálny publikačný podklad. `CAMPAIGN_RUNTIME_PUBLICATION_RECEIPT_20261112.json` je strojové potvrdenie analytickej snímky. Samostatný následný metadata commit môže aktualizovať tento report, receipt a centrálny prehľad; analytický commit vyššie zostáva nemennou referenciou overených154 blobov.

Kampaň zostáva otvorená. Nie je vytvorený PE32 port ani vykonaný merge do hlavnej vetvy. Najbližšia analytická priorita zostáva audit nepriamych prístupov do44 UNKNOWN bajtov a slotuDS2356, potom prirodzená inicializačná cesta za0476:015C a renderer/Win16 parita.
