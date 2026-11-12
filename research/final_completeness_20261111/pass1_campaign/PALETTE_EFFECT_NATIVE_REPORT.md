# DOS2: pôvodca DAC227/235, celý palette flash cyklus a natívny RNG

Otvorená nezrovnalosť z predošlej dávky je vysvetlená priamym writer dôkazom: **0D29:16CA volá083D:1CFC s argumentom1**. Táto reset cesta nastaví countdown80/phase0 a cez pôvodný port helper0156:0150 nastaví DAC235 a scénový DAC index227 na čiernu. RAM paletu neprepisuje. Prvý scheduler palette tick iba zmení countdown80→79 a single-colour helper nevolá.

Druhý nový natívny scenár prešiel aj celým prvým **čierna→biela→čierna** cyklom, vrátane skutočného RNG a návratu follow-up083D:0EA0. Pribudli dve bounded PARTIAL funkcie:77 inštrukcií/233B,2288 controlled replay prípadov a2 zachované original-EXE scenáre. Katalóg **145 rozsahov /5785 inštrukcií /14577B**,58034B typed file dát,996305 controlled cases a25 natural-runtime scenárov.

PASS320 zostáva **57118B PARTIAL /149B CLASSIFIED ONLY /28B UNKNOWN /0B DEEP VERIFIED**, presne57295B. Typed NON-CODE57116B, rozdiel2B je naďalej otvorený DS2358 relocation WORD. Žiadny nový kód alebo typová promócia v pôvodnom NON-CODE. BSS scalar refinement nižšie sa do file-backed57295B nezapočítava.

## Presné funkcie, ASM a CFG

|Funkcia|Image interval, exclusive end|Kód|Kontrakt|
|---|---|---:|---|
|0156:0150..016D|[016B0,016CD)|29B/15inštrukcií|FAR caller-cleanup,4WORD args: index,R,G,B, používa ich lowBYTE|
|083D:1CFC..1DC9|[0A0CC,0A199)|204B/62inštrukcií v205Bspane|FAR caller-cleanup, lowBYTE WORDargumentu je reset/tick voľba|

Medzera1B na083D:1D43 má bajt90h a nie je dosiahnutá CFG z deklarovaného vstupu: predchádza jej unconditional JMP. Nezapočítava sa ako vykonaná inštrukcia ani ako dokázaný padding. Obe telá sú porovnané s kanonickými EXE bajtmi, historickým inventárom a nezávislým16-bit iced-x86 dekódom; ASM a CFG sú v `palette_effect_replay`.

Port helper zoberie index z `[BP+6]`, R/G/B z `[BP+8,+0A,+0C]`. OUT015B posiela index na03C8; OUT0162/0166/016A posielajú R/G/B na03C9. Všetky4opcode bajty súEEh. AH vynuluje, AX končí lowBYTE blue, DX=03C9h. BP a caller stack sa obnovia. Nezapisuje hernú RAM paletu a nerobí vlastnú6-bit masku: emitované255 sa v skutočnom6-bit DAC číta ako63. Táto hardvérová maska je v novom natívnom white scenári aj priamo zachytená, nie iba predpokladaná.

## Stav a gating palette automatu

|DS2771 offset|Šírka|Typ / použitie|
|---|---:|---|
|3634|2B|WORD countdown; testuje sa hodnota pred decrementom|
|3636|1B|BYTE phase; nula vs nenula, pôvodné assignmenty0/1|
|D2F7|1B|BYTE scene DAC index, v tejto mape227|
|626A /626C|WORD/WORD|episode /level index, existujúci runtime kontext|

Prvé3 polia majú image-equivalent2AD44..2AD47 a34A07..34A08, teda4B **mimo file image**. `runtime_scalar_fields.csv` ich uvádza oddelene; nemení sa58034B typed file union ani už uvádzaných4054B BSS **tabuliek**. Toto číslo nie je úplným inventárom všetkých BSS scalarov.

Pred akýmkoľvek resetom/decrementom rutina vypočíta `n=(level_index+1)&FFFF`. Pri episode2 okamžite vráti; pri episode3 vráti, ak signed16(n)<10. V bežnej kladnej level doméne je preto epizóda3 povolená od level indexu9. Pri overflow alebo záporných indexoch sa zachováva skutočný signed/wrapped test, nie zjednodušené neobmedzené `level>=9`.

```c
if (episode == 2 || (episode == 3 && (int16_t)(level+1) < 10)) return;
if ((uint8_t)arg != 0) {
    countdown = 80; phase = 0;
    set_colour(235,0,0,0); set_colour(scene_index,0,0,0);
    return;
}
old = countdown; countdown = (uint16_t)(countdown-1);
if (old != 0) return;
if (phase != 0) {
    phase = 0;
    countdown = 160 + ((int16_t)game_rand() % 240);
    set_colour(235,0,0,0); set_colour(scene_index,0,0,0);
    followup_083D_0EA0();
    return;
}
phase = 1; countdown = 3;
set_colour(235,255,255,255); set_colour(scene_index,255,255,255);
```

Modulo v pseudokóde je signed IDIV remainder. Pôvodný rand wrapper/CRT už staticky vracia0..32767, takže prirodzený nový countdown leží160..399. Záporné mock AX hodnoty v edge probes sú mimo tohto zdrojového kontraktu; nie sú vyhlásené za prirodzenú hernú chybu. Nových12 chained seed prípadov vykonáva pôvodný rand wrapper, CRT LCG aj multiply helper namiesto RNG stubu a kontroluje presný DWORD stav.

Vzhľadom na **postdecrement test starej hodnoty** sa po reset80 biela zapne až na81.tick invokácii. Po bright countdown3 sa návrat do čiernej vykoná na4.tick invokácii. Po random160..399 je ďalší white prechod na161..400.tick invokácii. Tieto počty vychádzajú zo statického kódu a riadených86-invocation sekvencií; natívny marker test nepočíta každý tick jednotlivo. Nepriraďujú sa bez ďalšieho merania sekundám alebo garantovanej8Hz kadencii, keďže scheduler nedobieha preskočené bucket zmeny.

## Natívny writer scenár: reset a prvý tick

`dosbox_palette_writer_runtime` má84 code states,454 raw capture súborov a explicitne aktivuje palette breakpointy až po map-init/musical-call marker0D29:0A31. Reset vstup083D:1CFC má FAR caller return0D29:16CF a WORDarg1. Pred resetom je DAC227=(26,5,21), DAC235=(36,6,29), zhodný s RAM paletou. Prvý native helper má args(235,0,0,0), druhý(227,0,0,0). Pred každým zo4OUT sú zachytené DX a AL, po poslednom OUT je DAC znovu prečítaný. Celá paleta pred/po sa musí líšiť presne v cieľovej RGB trojici.

Po prvom helperi je čierny len235, po druhom aj227; RAM paleta ostáva pôvodná. Effect state je80/0. Prvý palette tick má FAR return0BDE:03A3, WORDarg0 a zmení80/0→79/0 bez single-colour helper callu. To vysvetľuje predošlý DAC/RAM rozdiel ešte **pred prvým scheduler world-update**. Nepovyšuje sa to na tvrdenie, že žiadna iná palette cesta v celom scheduleri nemôže zapisovať porty.

Aj tento beh zachoval prvý scheduler návrat do0D29:16EA. Nameraný elapsed17 nahradil18 z predošlého behu, oba vybrali sync flip; zhodné64000 visible pixel indexy sú reprodukovateľnosťou dvoch behov toho istého emulátora, nie nezávislým pixel golden. Breakpoint prestávky nedokazujú produkčnú kadenciu.

## Natívny celý prvý cyklus a RNG

Prvý dlhší pokus zachytil white DAC63/63/63, ale vypršal150s wall deadline pred dark return. Má successFalse/runtime_tests0 a neimportuje sa medzi25 úspešných scenárov. V2 má300s pozorovací limit a dosiahol pôvodný koncový kód083D:1D94 po návrate EA0.

`dosbox_palette_cycle_runtime_v2` zachoval94 code states,582 raw capture súborov,6 single-colour volaní a všetkých24 pôvodných OUT. Bez prepisovania CPU/RAM cez debugger pozoroval:

|Fáza|Native efektový stav|Skutočný DAC235 a227|
|---|---|---|
|reset|countdown80,phase0|0/0/0|
|white branch, pred assignmentom|countdownFFFFh poDEC,phase0|pred prechodom čierny|
|po2white helperoch|countdown3,phase1|63/63/63; pôvodný OUT poslal255|
|dark branch, pred phase clear|countdownFFFFh poDEC,phase1|pred prechodom biely|
|po pôvodnom RNG|seed1→2745024,AX41|ešte biely|
|po2dark helperoch aEA0 návrate|countdown201,phase0|0/0/0|

Natívny RNG transition zodpovedá LCG `(1*214013+2531011)&FFFFFFFF=2745024`, návratu `(state>>16)&7FFF=41` a countdown160+(41%240)=201. Je to priamo zachytené prirodzené **palette RNG volanie**. Nepreukazuje to globálne poradie všetkých RNG volaní predtým, seed serializáciu ani DEMO determinismus.

EA0 má zachovaný17B/5instruction context: pushDWORD20000h, pushWORD66, FAR CALL0C2B:03D6, addSP6, RETF. Celý follow-up sa v natívnom cykle vrátil. To je statická väzba na zvukové ID66/flags20000h a návrat natívneho call chainu, nie dôkaz počuteľného zvuku ani úplného WORX/digitálneho audio správania v headless nosound profile.

Verifier kontroluje každý call frame, všetky port register hodnoty, presnúDAC zmenu konkrétneho indexu, DWORD RNG stav pred/po, AX41, stavové assignmenty aj pôvodné EE opcodes. VGA debugger príkazy sú iba readback a na konci explicitný GC read-map capture/restore; žiadny debugger OUT na03C8/03C9 nevytvára skúmané farebné zmeny.

## Nové štyri mapové endpoint rozdiely

Po dlhšom priebehu už nemožno požadovať immutable raw MAP buffer, hoci pri prvom scheduler návrate bol8192/8192B rovný level payloadu. Teraz sa líšia4B, všetky BYTE1 z64×64 stride2 buniek:

|Map byte offset|Storage major/minor|Pôvodné→endpoint|
|---:|---|---|
|6753|52/48|A5→00|
|6755|52/49|00→A5|
|6807|53/11|00→A4|
|6957|54/22|A4→00|

Tieto indexy sú storage súradnice, **nie dokázané worldX/Y**. `map_endpoint_differences.csv` obsahuje aj presné image adresy. Writer, objektová identita a význam A4/A5 v tejto dávke nie sú určené. Presun tokenov je nový konkrétny AI/world trace cieľ; nejde o automaticky dokázanú korupciu alebo uzavretý GUARD pohyb. Zostávajúcich28 UNKNOWN bajtov sa nezmenilo; všetkých57295 NON-CODEB ostáva zachovaných vo finálnom snapshote.

## Kontrolované prípady a DOS verzie

2288 nových prípadov:1680 episode/level/reset/state gate prípadov,180 countdown/phase/signed-RNG edge prípadov,344 invokácií zo4 chained86call cyklov,72 lowBYTE port helper prípadov a12 pôvodných RNG chain prípadov s DWORD seedmi pri2load bázach. Ostatné effect matrix/cycle prípady RNG stubujú; EA0 sa v riadenom modeli stubuje. Port hook zaznamenáva pôvodné OUT, nesimuluje VGA DAC;6-bit latched výsledok preukazuje oddelený natívny beh.

Krížový audit číta reálne obrazy/inventáre DOS označení10/11/12/15/17/18/19/20,7 unikátnych obrazov(18=19). Všetkých8 má **bajtovo totožný29B single-colour helper**.205B flash span má vo všetkých zhodný normalizovaný kód,62instruction starts a66CFG hrán. Maskujú sa iba absolute memory displacements a call/branch adresy; všetky pôvodné operand bindings sú exportované. Zhodný CFG po maskovaní nie je dôkaz zhodnej sémantiky dátových adries alebo downstream callees. Žiadny nový Win16 runtime/CFG ekvivalent sa touto dávkou nepreukazuje.

## Reprodukcia a súčasný stav

`audit_replay_palette_effect.py IMAGE INVENTORY DECODER EMULATOR OUT` a `audit_palette_effect_dos_versions.py` reprodukujú ASM/CFG, matrix, native RNG chains a bounded DOS porovnanie. `runtime_watch_palette_writer.py`/`verify_palette_writer_capture.py` zachytia reset/firsttick; `runtime_watch_palette_cycle_v2.py`/`verify_palette_cycle_capture.py` celé tri fázy. Runtime skripty majú vstupy DOSBOXX GAMEFOLDER IMAGE RELOCS OUT WORK startup CDIMAGE; verifier IMAGE RELOCS CURRENT_MAP OUT WORK. Zdrojové EXE a23gameasset files ostali hashovo nezmenené.

`audit_palette_writer_fields.py IMAGE RUNTIME WORK INVENTORY OUT` a `audit_palette_cycle_fields.py IMAGE RUNTIME WORK OUT` vytvoria native OUT/state/RNG a map delta CSV. Raw binárne captures, pôvodné assets a native DLL sa nepublikujú, ale sú pripnuté SHA a reprodukovateľnými harnesses. `independent_decode_and_catalog.py`, tento writer a `render_campaign_status.py OUTPUTS pass1_xms_move_request PALETTE_EFFECT_NATIVE_REPORT.md` obnovia súhrn. Novú GitHub dávku potvrdzuje osobitná receipt; staršie tvrdenie „writer DAC227/235 unknown“ je týmto novým dôkazom pre DOS2 epizóda1/level0 reset/cycle aktualizované.

## Aktualizácia 13 oblastí

Pre každú oblasť nové sémantické percento = uzavreté jednotky/úplný inventár. Menovatele stále chýbajú, preto N/A; staré orientačné odhady sa neprezentujú ako meranie. Nové funkcie/runtime dôkazy sú PARTIAL. UNKNOWN28B a CLASSIFIED ONLY149B ostávajú, DEEP VERIFIED0B.

|Oblasť|Predošlý odhad|Nové % / metodika|Nový dôkaz|Zostávajúce neznáme|Blokujúci problém|Najbližší krok|
|---|---:|---|---|---|---|---|
|Mapy a formáty|99 %|N/A,closure/inventár|4konkrétne BYTE1 endpoint zmeny po dlhšom behu|writer,A4/A5,world axes|iba endpointy|presný writer breakpoint pre4adresy|
|Dátové typy a konštanty|95 %|N/A,closure/inventár|countdownWORD/phaseBYTE/sceneDACBYTE,4B BSS refinement|všetci alias writeri,lifecycle|nie celý BSS inventár|state a scene-index callery|
|Tabuľky a ukazovatele|93 %|N/A,closure/inventár|DAC235+scene227, RAM/DAC divergence vysvetlená|iné scene-index hodnoty a alias227=235|iba jeden native sceneindex|ďalšie map header domény|
|Funkcie / ASM / CFG|90 %|N/A,closure/inventár|2telá233B/77instructions,2288replay|EA0 downstream a neuzavreté callees|runtime path nie celá hra|audio/cache a map-writer telá|
|RNG|97 %|N/A,closure/inventár|prirodzený palette seed1→2745024/AX41;12native-CRT modelchains|globálne poradie,seedy,DEMO,SAVE|iba palette RNG event|RNG call trace počas world/DEMO|
|Scheduler|96 %|N/A,closure/inventár|palette reset a tick80→79, prirodzený flash cyklus|presné intervaly,skip/catchup a iné vetvy|nepočítaný každýtick/debug timing|riedky multi-tick trace|
|DEMO a vstupy|96 %|N/A,closure/inventár|dlhší bez-input gameplay do palette cycle end|DEMO a pohyb/výstrel|iba startup menu keys|riadené gameplay vstupy a DEMO|
|Renderer / VGA|94 %|N/A,closure/inventár|24nativeOUT aDACblack/white/black,index-helper8DOS rawmatch|pixelgolden,clipping a scanout|headless paused readback|nezávislý renderer golden a clippingcases|
|GUARD / bossovia|93 %|N/A,closure/inventár|mapBYTE1 tokeny sa zmenili,writer nepriradený|AIobjekty/boss stavy|endpoint nie actor trace|breakpointy A4/A5 map writerov|
|Zbrane / projektily|92 %|N/A,closure/inventár|žiadny nový damage dôkaz|damage/collision domény|bez výstrelu|controlled firing a projectile trace|
|Sprity / HUD / paleta|92 %|N/A,closure/inventár|DAC227/235writer uzavretý pretestedcestu;gates/counter/RNGcycle|ďalšie epizódy,inépalety/callee role|jedna natívna mapa|gatedep2/ep3/sceneindex runtime|
|SAVE / LOAD|92 %|N/A,closure/inventár|žiadny nový SAVE dôkaz|payload54709B,rollback,RNGserialization|prefix nie celý formát|SAVE/LOAD schema a izolovaný runtime|
|Windows Win16|92 %|N/A,closure/inventár|DOS8label helper/CFG compare,žiadny novýWin dôkaz|Win paletteAPI/flash ekvivalent|žiadnyWin16runtime|fixup-backed Win effect mapping|

## Runtime testy na vykonanie

1. MapBYTE1 zmeny: priamo sledovať zapisujúce inštrukcie k image2716F/27171/271A5/2723B (decimal adresy sú autoritatívne v CSV), zachytiť DS/ES/base/index a actor pointer. Pred použitím breakpointov adresy znovu prepočítať z CSV, nie slepo podľa textového hex prepisu.
2. Efekt v episode2 a episode3 level8/9, scene index iný než227 alebo rovný235; rozlíšiť gated no-write od neaktívneho frame. Post-decrement a RNGcall poradie porovnať s riedkym scheduler trace.
3. Source for sceneDAC D2F7, všetci countdown/phase writeri a audioID66 downstream. Skutočný zvuk overiť samostatným zvukovým profilom; headless nosound návrat nie je audio-output parity.
4. UNKNOWN28 ďalej analyzovať cez dynamické segmenty/indexované refs a resource/map boundaries. Nula zmien ani paragraph alignment nie je padding proof. Ďalej gameplay damage/DEMO/SAVE a Win16; PE32 sa nevykonáva.
