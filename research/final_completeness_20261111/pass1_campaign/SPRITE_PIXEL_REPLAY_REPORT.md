# Scaled sprite renderer: celé telo a model VGA zápisov

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

SHA cases `35155f462ebd8f5078d8533f704010f5f15189beabfe640faa499d8327c3efe9`. Nových4608 seeded scenárov; funkcia sa nepridáva druhýkrát, katalóg zostáva118rozsahov. Žiadne nové file typy ani promócie:57102PARTIAL/149CLASSIFIED ONLY/44UNKNOWN/0DEEP VERIFIED. Tri prirodzené DOSBox scenáre sa nemenia. Výsledok zatiaľ lokálny, bez novej GitHub publikácie.

## Aktualizácia 13 oblastí

Nové % = uzavreté jednotky / úplný inventár oblasti. Úplné menovatele chýbajú, preto N/A. Iniciačný runtime nie je percento gameplay completeness.

| Oblasť | Predošlý odhad | Nové % | Aktuálny dôkaz (staršie riadky zachované) | Zostávajúce neznáme / blokátor | Najbližší konkrétny krok |
|---|---:|---|---|---|---|
| Mapy a formáty |99 %|N/A|skutočný BSF54 B load/decode|iné BSF/role blokov|resource sloty v runtime|
| Dátové typy a konštanty |95 %|N/A|511 runtime DWORD mimo file|149 B iba klasifikované, 44 B UNKNOWN|nepriame segmentové prístupy|
| Tabuľky a ukazovatele |93 %|N/A|12 lokálnych FAR konštrukcií 21FD:264E odlíšených od DS:264E|aliasy/dynamické indexy|watchpointy na 44 UNKNOWN B|
| Funkcie / ASM / CFG |90 %|N/A|celé pôvodné telo,4608 pixel scenárov|clipped draw a caller domény|kombinovaný clipping/pixel test|
| RNG |97 %|N/A|bez RNG runtime|prvý srand/rand|RNG caller trace|
| Scheduler |96 %|N/A|clock init prebehol medzi bodmi|main loop/scheduler|loop vstup|
| DEMO a vstupy |96 %|N/A|bez input/demo runtime|driver a demo|prirodzené demo|
| Renderer / VGA |94 %|N/A|mask/plane store,transparentnosť a unsigned depth|skutočné VGA registre a výstup|DOSBox frame dump|
| GUARD / bossovia |93 %|N/A|bez AI runtime|map init|selector doména|
| Zbrane / projektily |92 %|N/A|bez damage runtime|effect callery|damage trace|
| Sprity / HUD / paleta |92 %|N/A|VGA init, nie vizuálna parita|paleta/sprity|resource load|
| SAVE / LOAD |92 %|N/A|BSF native file-check vrátený|SAVE/LOAD a chybové I/O|diskové scenáre|
| Windows Win16 |92 %|N/A|bez Win runtime|NE prostredie|samostatný Win16 test|

## Runtime testy na vykonanie

Pri prirodzenom0156:05DE entry zachytiť slot, source buffer, SS depth tabuľku a kompletné VGA sequencer/graphics-controller nastavenie. Porovnať výstup štyroch rovín pred/po s modelom a samostatne screenshot. Nasledujúca statická/replay dávka má spojiť už overené clippingové vetvy s pixelovou slučkou a preveriť zaokrúhlenie, prázdne rozsahy aj source-offset wrap; Win16 ekvivalent zostáva samostatne otvorený.
