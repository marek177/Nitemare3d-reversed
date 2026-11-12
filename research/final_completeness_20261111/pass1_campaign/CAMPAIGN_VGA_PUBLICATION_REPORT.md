# Overená GitHub publikácia: VGA a nadväzujúce dôkazy

Analytický commit [338a23e550909f2fb57acd21439bb4407fcdbb69](https://github.com/marek177/Nitemare3d-reversed/commit/338a23e550909f2fb57acd21439bb4407fcdbb69) na vetve `codex/final-re-completeness-20261111` nadväzuje na `932ba4742380056cf3d20ed20573acf83bec606c`. Overenie: 2026-11-12 09:53:59 UTC.

Pred presunom vetvy bolo overených198 nových alebo zmenených textových blobov podľa presného Git SHA1 vrátane UTF-8/BOM. Všetkých4873 ostatných blobov sa zachovalo; výsledná analytická snímka obsahuje5071 blobov. Branch update použil očakávaný pôvodný HEAD a force=false; následné čítanie potvrdilo nový commit.

Obsah:130 ohraničených DOS funkcií,4993 nezávisle dekódovaných inštrukcií/12456B;974287 riadených replay prípadov, oddelené prefixové testy a14 prirodzených DOSBox-X scenárov. Najnovšia dávka overuje pôvodný PCX dekodér a stĺpcový VGA blitter,64000 indexovaných pixelov zadnej stránky s explicitne pridaným CD assetom,8DOS labelov/7obrazov. Ďalšie nové dôkazy zahŕňajú UIF font2, SND tabuľku/CPU trace, DAC readback a oddelený Win16 paletový doplnok.

PASS320 zostáva PARTIAL57102 /CLASSIFIED ONLY149 /UNKNOWN44 /DEEP VERIFIED0. SHA mapy `3021969d4e4348715816361fa387631e7d6cfd9fc9dcc136e26073f0f9984d1b`. Kampaň nie je dokončená. Prirodzený back-buffer nie je úplná viditeľná/RGB/gameplay alebo Win16 parita.

Pôvodné EXE, celé assety, native tool knižnice a raw memory dumpy neboli publikované. Všetky nové položky sú textové dôkazy, skripty alebo konfigurácie. Veľké generované tabuľky a runtime dumpy majú v PUBLICATION_OMITTED_GENERATED.json hashy a veľkosti; reprodukcia vyžaduje presné lokálne zdroje a historické inventáre. Súbory z chybných alebo neoverených nových runtime pokusov neboli do tejto delty vybrané; staršie historické položky sa nemažú.

Strojový receipt je CAMPAIGN_VGA_PUBLICATION_RECEIPT_20261112.json. Lokálna príprava a manifest sú publication_vga_20261112/meta.json, manifest.json a payload.json. Nová analytická snímka je nemenný commit vyššie; následná metadata aktualizácia doplní toto potvrdenie a aktuálne odkazy, preto môže mať vetva novší HEAD.
