# -*- coding: utf-8 -*-
"""python write_sprite_pixels_report.py OUTPUTS"""
import json,sys
from pathlib import Path
r=Path(sys.argv[1]);s=json.loads((r/'sprite_pixel_replay/summary.json').read_text());old=(r/'SPRITE_CLIP_PREFIX_REPORT.md').read_text(encoding='utf-8');table=old[old.index('## Aktualizácia 13 oblastí'):old.index('## Runtime testy na vykonanie')]
table=table.replace('|renderer201inštrukcií/CFG211hrán; prefix648scenárov|zvyšok pixelovej slučky|port/pixel replay|','|celé pôvodné telo,4608 pixel scenárov|clipped draw a caller domény|kombinovaný clipping/pixel test|')
table=table.replace('|clipping precedence a36 očakávaných divide faultov|caller validácia a VGA výstup|clipping caller domény|','|mask/plane store,transparentnosť a unsigned depth|skutočné VGA registre a výstup|DOSBox frame dump|')
text='''# Scaled sprite renderer: celé telo a model VGA zápisov

Funkcia **0156:05DE..07DD** z predchádzajúcej dávky sa teraz vykonáva celá, od ENTER po FAR návrat. Žiadna jej inštrukcia ani callee sa nenahrádza; telo nemá podvolania. Nová skúška zahŕňa port OUT záznam a pamäťové store hooks. Porty a VGA roviny sú **modelované**, nejde o nový DOSBox runtime ani hardvérovú paritu.

## Potvrdené lokálne správanie

- Zdroj je usporiadaný po stĺpcoch: index `source_column*resource_height + source_row`. Výber súradníc je odvodený z rovnakého truncovaného16.16 stepu; pri zväčšení3× sa zlomok tretiny nevyjadruje presne.
- Source BYTE **1Fh** je transparentný: nevykoná video store. Iné hodnoty sa zapisujú bez farebnej transformácie.
- Pri object BYTE+5 bit10h=0 sa stĺpec kreslí len pri **unsigned depth_table[x] <= slot_depth**. Rovnosť sa kreslí; väčšia hodnota vrátane8000h proti1234h sa preskočí. Bit10h=1 depth test obchádza.
- Sequencer index2 sa vyberie OUT3C4h. Na3C5h nasleduje maska `ROL8(11h,x&3)` a následne rotácia o1 na ďalší stĺpec. Nízke4bity vyberajú rovinu. Pri carry z rotácie sa zvýši bajtový video offset; OUT zachová príznak carry používaný nasledujúcou vetvou.
- CPU adresa video store pri týchto vstupoch je `page*16 + 80*(y+row) + floor((x+column)/4)`, aktívna rovina `(x+column)&3`. Obe stránky A000h/A400h sa preverujú samostatne.
- Ukončenie source-width prebehne **pred** nasledujúcim zápisom masky. Ak sa skôr vyčerpá cieľový počet stĺpcov, posledná rotovaná maska sa ešte zapíše pred ukončením cez DEC/JNE. Celé poradie port udalostí sa porovnáva, nie iba konečný framebuffer.

## Pseudokód pre skúšanú neorezanú doménu

```text
step = floor((source_height << 16) / target_height)
for target_column while source_column < source_width and remaining_columns != 0:
    select_plane_mask()
    if object_bypass or depth[x+target_column] <= slot_depth:  // unsigned
        for target_row in 0..target_height-1:
            source_column = floor(target_column*step / 65536)
            source_row = floor(target_row*step / 65536)
            pixel = source[source_column*source_height + source_row]
            if pixel != 31: planar_store(page, x+target_column, y+target_row, pixel)
    advance_fixed_point_column()
    if source_column_reached_width: break
    rotate_and_output_next_mask()
    decrement_remaining_columns()
```

Pseudokód nie je náhrada celého clippingu; jeho presné else-if poradie a hraničné delenie sú v `SPRITE_CLIP_PREFIX_REPORT.md`. V tejto dávke je clipping vypnutý platnými hranicami pre izolované overenie pixelovej slučky.

## Reprodukcia a rozsah

`replay_sprite_pixels.py IMAGE ABS_EMULATOR OUT` overí kanonický SHA a pre oba load segmenty aplikuje1670 skutočných relokácií. Pôvodný renderer beží s DS=SS default DGROUP; source DS sa mení pôvodnými inštrukciami. Model pozoruje všetky OUT a všetky video stores s práve aktívnou maskou. Samostatný matematický model predikuje presné adresy, šírky, hodnoty, masky a poradie; následne porovná štyri65536B plane obrazy inicializované A5h. Obyčajná Unicorn linear VRAM sa nepovažuje za skutočný VGA plane framebuffer.

**4608 scenárov,0 odchýlok** = 2load ×4Xalignment ×2page ×2sourcewidth(2,5) ×2sourceheight(2,5) ×3scale(1,2,3) ×3pixelpattern ×4depthpattern ×2bypass. Pixelové vzory: všetko transparentné, nepriehľadné/rôzne hodnoty a zmiešaná transparentnosť. Depth stĺpce obsahujú1233h,1234h,1235h,8000h s posunom vzoru. Všetky scenáre kontrolujú tiež návrat DS/SS/SP/BP/SI/DI a konečnýES.

Každý case má hash celých štyroch modelovaných rovín v `cases.csv`; `representative_stores.csv` uchováva presné udalosti vybraných zmiešaných vzorov. Summary pinne SHA cases. Neskúša sa implicitne celý register ABI, neplatné počty LOOP, source wrap, všetky mierky, clipped pixel kombinácie alebo prirodzené vstupy. Pozorovaný memory model nevykonáva plnú emuláciu VGA graphics-controller režimov, latchov a čítania.

'''+f"SHA cases `{s['cases_sha256']}`. Nových4608 seeded scenárov; funkcia sa nepridáva druhýkrát, katalóg zostáva118rozsahov. Žiadne nové file typy ani promócie:57102PARTIAL/149CLASSIFIED ONLY/44UNKNOWN/0DEEP VERIFIED. Tri prirodzené DOSBox scenáre sa nemenia. Výsledok zatiaľ lokálny, bez novej GitHub publikácie.\n\n"+table+'''## Runtime testy na vykonanie

Pri prirodzenom0156:05DE entry zachytiť slot, source buffer, SS depth tabuľku a kompletné VGA sequencer/graphics-controller nastavenie. Porovnať výstup štyroch rovín pred/po s modelom a samostatne screenshot. Nasledujúca statická/replay dávka má spojiť už overené clippingové vetvy s pixelovou slučkou a preveriť zaokrúhlenie, prázdne rozsahy aj source-offset wrap; Win16 ekvivalent zostáva samostatne otvorený.
'''
(r/'SPRITE_PIXEL_REPLAY_REPORT.md').write_text(text,encoding='utf-8');print(json.dumps(dict(report='SPRITE_PIXEL_REPLAY_REPORT.md',cases=s['cases'])))
