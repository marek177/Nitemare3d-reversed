# Publikácia dôkazov 2026-11-12

Analytická snímka bola publikovaná do `marek177/Nitemare3d-reversed`, vetva `codex/final-re-completeness-20261111`.

- Commit: `ba27379dd28c9a689d15233b0fd7017867f50114`.
- Predchodca: `52924ebf849dd79d15af9d7c164b8304f50cae87`.
- Tree: `376b90438ce434dd948cdd68cd8e6c16b19ff59d`.
- Overených 628 zmenených/pridaných súborov vrátane dvoch manifestov; každý Git blob SHA súhlasí s lokálnym obsahom.
- Overené zachovanie ďalších 4 113 repository blobov mimo zmenenej množiny.
- Rekurzívny tree nebol skrátený; nulové nezhody. Overený aj nový branch head, parent a tree commit objektu.
- Aktualizácia vetvy použila očakávaný predchádzajúci commit a `force=false`.

Publikovaná PASS1 mapa: `pass1_fcb_prefix/noncode_intervals.csv/json`, 57 101 B PARTIAL, 150 B CLASSIFIED ONLY, 44 B UNKNOWN, 0 B DEEP VERIFIED. SHA CSV `899ba518a5b8b64b24837e4f40f14e0c918e0bbb2777d2e13ae0803bb42482ed`. Mapa má presne 57 295 baseline bajtov a 887 overených intervalov bez dier a prekryvov.

Katalóg: 109 bounded funkčných rozsahov, 4 068 nezávisle dekódovaných inštrukcií / 10 156 B kódu. Typované dáta celého obrazu 57 987 B. Kontrolované replay prípady 915 637 plus osobitne evidovaný smerový prefix. Prirodzené DOSBox-X/game runtime testy 0. Tieto počty nie sú sémantické percentá ani úplný inventár hry.

Presné publikované cesty a hash hodnoty sú v `publication_update_20261112/manifest.json`, pripravený payload a jeho SHA v `meta.json`. Remote `PUBLICATION_DELTA_MANIFEST.json` a `PUBLICATION_OMITTED_GENERATED.json` uchovávajú mapu obsahu a hash veľkých reprodukovateľných výstupov. Originálne herné EXE, úplné assety, decoder/emulator DLL a veľké case dumpy sa nenahrávali. Externé Microsoft source snapshoty sú identifikované manifestom s pevnými URL a SHA; plné ASM zdroje neboli zahrnuté.

Po vytvorení analytickej snímky nasleduje iba metadátová oprava: tento receipt, report a renderer publikovaného stavu. Referencia na analytický commit ostáva stabilná, aby nevznikal nekonečný reťazec receiptov odkazujúcich samých na seba. Historické reporty zachovávajú pôvodné poznámky o čase publikácie; aktuálny receipt ich nahrádza iba pre stav publikovanej snímky.

Kampaň zostáva neukončená. Stále treba uzavrieť zostávajúce CLASSIFIED ONLY/UNKNOWN, sémantiku PARTIAL oblastí, knižničné kontrakty, neznáme funkcie, gameplay/renderer a Win16 paritu aj prirodzené runtime dôkazy. PE32 sa nevytvára.
