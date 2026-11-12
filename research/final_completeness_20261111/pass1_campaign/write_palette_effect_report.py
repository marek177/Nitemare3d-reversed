"""python write_palette_effect_report.py OUTPUTS_DIR"""
import hashlib,json,sys
from pathlib import Path
r=Path(sys.argv[1]);read=lambda p:json.loads((r/p).read_text());a=read('palette_effect_replay/summary.json');v=read('dosbox_palette_writer_runtime/independent_verification.json');cy=read('dosbox_palette_cycle_runtime_v2/independent_verification.json');vers=read('palette_effect_dos_versions/summary.json');c=read('campaign_catalog/summary.json');fields=read('palette_effect_fields/summary.json');cyclefields=read('palette_cycle_fields/summary.json')
for x in a['files']+v['files']+cy['files']+vers['files']+fields['files']+cyclefields['files']:assert hashlib.sha256(Path(x['path']).read_bytes()).hexdigest()==x['sha256']
assert c['functions']==145 and c['runtime_tests']==25 and c['controlled_instruction_replay_cases']==996305 and a['cases']==2288
text='''# DOS2: p\xf4vodca DAC227/235, cel\xfd palette flash cyklus a nat\xedvny RNG

Otvoren\xe1 nezrovnalos\u0165 z predo\u0161lej d\xe1vky je vysvetlen\xe1 priamym writer d\xf4kazom: **0D29:16CA vol\xe1083D:1CFC s argumentom1**. T\xe1to reset cesta nastav\xed countdown80/phase0 a cez p\xf4vodn\xfd port helper0156:0150 nastav\xed DAC235 a sc\xe9nov\xfd DAC index227 na \u010diernu. RAM paletu neprepisuje. Prv\xfd scheduler palette tick iba zmen\xed countdown80\u219279 a single-colour helper nevol\xe1.

Druh\xfd nov\xfd nat\xedvny scen\xe1r pre\u0161iel aj cel\xfdm prv\xfdm **\u010dierna\u2192biela\u2192\u010dierna** cyklom, vr\xe1tane skuto\u010dn\xe9ho RNG a n\xe1vratu follow-up083D:0EA0. Pribudli dve bounded PARTIAL funkcie:77 in\u0161trukci\xed/233B,2288 controlled replay pr\xedpadov a2 zachovan\xe9 original-EXE scen\xe1re. Katal\xf3g **145 rozsahov /5785 in\u0161trukci\xed /14577B**,58034B typed file d\xe1t,996305 controlled cases a25 natural-runtime scen\xe1rov.

PASS320 zost\xe1va **57118B PARTIAL /149B CLASSIFIED ONLY /28B UNKNOWN /0B DEEP VERIFIED**, presne57295B. Typed NON-CODE57116B, rozdiel2B je na\u010falej otvoren\xfd DS2358 relocation WORD. \u017diadny nov\xfd k\xf3d alebo typov\xe1 prom\xf3cia v p\xf4vodnom NON-CODE. BSS scalar refinement ni\u017e\u0161ie sa do file-backed57295B nezapo\u010d\xedtava.

## Presn\xe9 funkcie, ASM a CFG

|Funkcia|Image interval, exclusive end|K\xf3d|Kontrakt|
|---|---|---:|---|
|0156:0150..016D|[016B0,016CD)|29B/15in\u0161trukci\xed|FAR caller-cleanup,4WORD args: index,R,G,B, pou\u017e\xedva ich lowBYTE|
|083D:1CFC..1DC9|[0A0CC,0A199)|204B/62in\u0161trukci\xed v205Bspane|FAR caller-cleanup, lowBYTE WORDargumentu je reset/tick vo\u013eba|

Medzera1B na083D:1D43 m\xe1 bajt90h a nie je dosiahnut\xe1 CFG z deklarovan\xe9ho vstupu: predch\xe1dza jej unconditional JMP. Nezapo\u010d\xedtava sa ako vykonan\xe1 in\u0161trukcia ani ako dok\xe1zan\xfd padding. Obe tel\xe1 s\xfa porovnan\xe9 s kanonick\xfdmi EXE bajtmi, historick\xfdm invent\xe1rom a nez\xe1visl\xfdm16-bit iced-x86 dek\xf3dom; ASM a CFG s\xfa v `palette_effect_replay`.

Port helper zoberie index z `[BP+6]`, R/G/B z `[BP+8,+0A,+0C]`. OUT015B posiela index na03C8; OUT0162/0166/016A posielaj\xfa R/G/B na03C9. V\u0161etky4opcode bajty s\xfaEEh. AH vynuluje, AX kon\u010d\xed lowBYTE blue, DX=03C9h. BP a caller stack sa obnovia. Nezapisuje hern\xfa RAM paletu a nerob\xed vlastn\xfa6-bit masku: emitovan\xe9255 sa v skuto\u010dnom6-bit DAC \u010d\xedta ako63. T\xe1to hardv\xe9rov\xe1 maska je v novom nat\xedvnom white scen\xe1ri aj priamo zachyten\xe1, nie iba predpokladan\xe1.

## Stav a gating palette automatu

|DS2771 offset|\u0160\xedrka|Typ / pou\u017eitie|
|---|---:|---|
|3634|2B|WORD countdown; testuje sa hodnota pred decrementom|
|3636|1B|BYTE phase; nula vs nenula, p\xf4vodn\xe9 assignmenty0/1|
|D2F7|1B|BYTE scene DAC index, v tejto mape227|
|626A /626C|WORD/WORD|episode /level index, existuj\xfaci runtime kontext|

Prv\xe93 polia maj\xfa image-equivalent2AD44..2AD47 a34A07..34A08, teda4B **mimo file image**. `runtime_scalar_fields.csv` ich uv\xe1dza oddelene; nemen\xed sa58034B typed file union ani u\u017e uv\xe1dzan\xfdch4054B BSS **tabuliek**. Toto \u010d\xedslo nie je \xfapln\xfdm invent\xe1rom v\u0161etk\xfdch BSS scalarov.

Pred ak\xfdmko\u013evek resetom/decrementom rutina vypo\u010d\xedta `n=(level_index+1)&FFFF`. Pri episode2 okam\u017eite vr\xe1ti; pri episode3 vr\xe1ti, ak signed16(n)<10. V be\u017enej kladnej level dom\xe9ne je preto epiz\xf3da3 povolen\xe1 od level indexu9. Pri overflow alebo z\xe1porn\xfdch indexoch sa zachov\xe1va skuto\u010dn\xfd signed/wrapped test, nie zjednodu\u0161en\xe9 neobmedzen\xe9 `level>=9`.

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

Modulo v pseudok\xf3de je signed IDIV remainder. P\xf4vodn\xfd rand wrapper/CRT u\u017e staticky vracia0..32767, tak\u017ee prirodzen\xfd nov\xfd countdown le\u017e\xed160..399. Z\xe1porn\xe9 mock AX hodnoty v edge probes s\xfa mimo tohto zdrojov\xe9ho kontraktu; nie s\xfa vyhl\xe1sen\xe9 za prirodzen\xfa hern\xfa chybu. Nov\xfdch12 chained seed pr\xedpadov vykon\xe1va p\xf4vodn\xfd rand wrapper, CRT LCG aj multiply helper namiesto RNG stubu a kontroluje presn\xfd DWORD stav.

Vzh\u013eadom na **postdecrement test starej hodnoty** sa po reset80 biela zapne a\u017e na81.tick invok\xe1cii. Po bright countdown3 sa n\xe1vrat do \u010diernej vykon\xe1 na4.tick invok\xe1cii. Po random160..399 je \u010fal\u0161\xed white prechod na161..400.tick invok\xe1cii. Tieto po\u010dty vych\xe1dzaj\xfa zo statick\xe9ho k\xf3du a riaden\xfdch86-invocation sekvenci\xed; nat\xedvny marker test nepo\u010d\xedta ka\u017ed\xfd tick jednotlivo. Neprira\u010fuj\xfa sa bez \u010fal\u0161ieho merania sekund\xe1m alebo garantovanej8Hz kadencii, ke\u010f\u017ee scheduler nedobieha presko\u010den\xe9 bucket zmeny.

## Nat\xedvny writer scen\xe1r: reset a prv\xfd tick

`dosbox_palette_writer_runtime` m\xe184 code states,454 raw capture s\xfaborov a explicitne aktivuje palette breakpointy a\u017e po map-init/musical-call marker0D29:0A31. Reset vstup083D:1CFC m\xe1 FAR caller return0D29:16CF a WORDarg1. Pred resetom je DAC227=(26,5,21), DAC235=(36,6,29), zhodn\xfd s RAM paletou. Prv\xfd native helper m\xe1 args(235,0,0,0), druh\xfd(227,0,0,0). Pred ka\u017ed\xfdm zo4OUT s\xfa zachyten\xe9 DX a AL, po poslednom OUT je DAC znovu pre\u010d\xedtan\xfd. Cel\xe1 paleta pred/po sa mus\xed l\xed\u0161i\u0165 presne v cie\u013eovej RGB trojici.

Po prvom helperi je \u010dierny len235, po druhom aj227; RAM paleta ost\xe1va p\xf4vodn\xe1. Effect state je80/0. Prv\xfd palette tick m\xe1 FAR return0BDE:03A3, WORDarg0 a zmen\xed80/0\u219279/0 bez single-colour helper callu. To vysvet\u013euje predo\u0161l\xfd DAC/RAM rozdiel e\u0161te **pred prv\xfdm scheduler world-update**. Nepovy\u0161uje sa to na tvrdenie, \u017ee \u017eiadna in\xe1 palette cesta v celom scheduleri nem\xf4\u017ee zapisova\u0165 porty.

Aj tento beh zachoval prv\xfd scheduler n\xe1vrat do0D29:16EA. Nameran\xfd elapsed17 nahradil18 z predo\u0161l\xe9ho behu, oba vybrali sync flip; zhodn\xe964000 visible pixel indexy s\xfa reprodukovate\u013enos\u0165ou dvoch behov toho ist\xe9ho emul\xe1tora, nie nez\xe1visl\xfdm pixel golden. Breakpoint prest\xe1vky nedokazuj\xfa produk\u010dn\xfa kadenciu.

## Nat\xedvny cel\xfd prv\xfd cyklus a RNG

Prv\xfd dlh\u0161\xed pokus zachytil white DAC63/63/63, ale vypr\u0161al150s wall deadline pred dark return. M\xe1 successFalse/runtime_tests0 a neimportuje sa medzi25 \xfaspe\u0161n\xfdch scen\xe1rov. V2 m\xe1300s pozorovac\xed limit a dosiahol p\xf4vodn\xfd koncov\xfd k\xf3d083D:1D94 po n\xe1vrate EA0.

`dosbox_palette_cycle_runtime_v2` zachoval94 code states,582 raw capture s\xfaborov,6 single-colour volan\xed a v\u0161etk\xfdch24 p\xf4vodn\xfdch OUT. Bez prepisovania CPU/RAM cez debugger pozoroval:

|F\xe1za|Native efektov\xfd stav|Skuto\u010dn\xfd DAC235 a227|
|---|---|---|
|reset|countdown80,phase0|0/0/0|
|white branch, pred assignmentom|countdownFFFFh poDEC,phase0|pred prechodom \u010dierny|
|po2white helperoch|countdown3,phase1|63/63/63; p\xf4vodn\xfd OUT poslal255|
|dark branch, pred phase clear|countdownFFFFh poDEC,phase1|pred prechodom biely|
|po p\xf4vodnom RNG|seed1\u21922745024,AX41|e\u0161te biely|
|po2dark helperoch aEA0 n\xe1vrate|countdown201,phase0|0/0/0|

Nat\xedvny RNG transition zodpoved\xe1 LCG `(1*214013+2531011)&FFFFFFFF=2745024`, n\xe1vratu `(state>>16)&7FFF=41` a countdown160+(41%240)=201. Je to priamo zachyten\xe9 prirodzen\xe9 **palette RNG volanie**. Nepreukazuje to glob\xe1lne poradie v\u0161etk\xfdch RNG volan\xed predt\xfdm, seed serializ\xe1ciu ani DEMO determinismus.

EA0 m\xe1 zachovan\xfd17B/5instruction context: pushDWORD20000h, pushWORD66, FAR CALL0C2B:03D6, addSP6, RETF. Cel\xfd follow-up sa v nat\xedvnom cykle vr\xe1til. To je statick\xe1 v\xe4zba na zvukov\xe9 ID66/flags20000h a n\xe1vrat nat\xedvneho call chainu, nie d\xf4kaz po\u010dute\u013en\xe9ho zvuku ani \xfapln\xe9ho WORX/digit\xe1lneho audio spr\xe1vania v headless nosound profile.

Verifier kontroluje ka\u017ed\xfd call frame, v\u0161etky port register hodnoty, presn\xfaDAC zmenu konkr\xe9tneho indexu, DWORD RNG stav pred/po, AX41, stavov\xe9 assignmenty aj p\xf4vodn\xe9 EE opcodes. VGA debugger pr\xedkazy s\xfa iba readback a na konci explicitn\xfd GC read-map capture/restore; \u017eiadny debugger OUT na03C8/03C9 nevytv\xe1ra sk\xfaman\xe9 farebn\xe9 zmeny.

## Nov\xe9 \u0161tyri mapov\xe9 endpoint rozdiely

Po dlh\u0161om priebehu u\u017e nemo\u017eno po\u017eadova\u0165 immutable raw MAP buffer, hoci pri prvom scheduler n\xe1vrate bol8192/8192B rovn\xfd level payloadu. Teraz sa l\xed\u0161ia4B, v\u0161etky BYTE1 z64\xd764 stride2 buniek:

|Map byte offset|Storage major/minor|P\xf4vodn\xe9\u2192endpoint|
|---:|---|---|
|6753|52/48|A5\u219200|
|6755|52/49|00\u2192A5|
|6807|53/11|00\u2192A4|
|6957|54/22|A4\u219200|

Tieto indexy s\xfa storage s\xfaradnice, **nie dok\xe1zan\xe9 worldX/Y**. `map_endpoint_differences.csv` obsahuje aj presn\xe9 image adresy. Writer, objektov\xe1 identita a v\xfdznam A4/A5 v tejto d\xe1vke nie s\xfa ur\u010den\xe9. Presun tokenov je nov\xfd konkr\xe9tny AI/world trace cie\u013e; nejde o automaticky dok\xe1zan\xfa korupciu alebo uzavret\xfd GUARD pohyb. Zost\xe1vaj\xfacich28 UNKNOWN bajtov sa nezmenilo; v\u0161etk\xfdch57295 NON-CODEB ost\xe1va zachovan\xfdch vo fin\xe1lnom snapshote.

## Kontrolovan\xe9 pr\xedpady a DOS verzie

2288 nov\xfdch pr\xedpadov:1680 episode/level/reset/state gate pr\xedpadov,180 countdown/phase/signed-RNG edge pr\xedpadov,344 invok\xe1ci\xed zo4 chained86call cyklov,72 lowBYTE port helper pr\xedpadov a12 p\xf4vodn\xfdch RNG chain pr\xedpadov s DWORD seedmi pri2load b\xe1zach. Ostatn\xe9 effect matrix/cycle pr\xedpady RNG stubuj\xfa; EA0 sa v riadenom modeli stubuje. Port hook zaznamen\xe1va p\xf4vodn\xe9 OUT, nesimuluje VGA DAC;6-bit latched v\xfdsledok preukazuje oddelen\xfd nat\xedvny beh.

Kr\xed\u017eov\xfd audit \u010d\xedta re\xe1lne obrazy/invent\xe1re DOS ozna\u010den\xed10/11/12/15/17/18/19/20,7 unik\xe1tnych obrazov(18=19). V\u0161etk\xfdch8 m\xe1 **bajtovo toto\u017en\xfd29B single-colour helper**.205B flash span m\xe1 vo v\u0161etk\xfdch zhodn\xfd normalizovan\xfd k\xf3d,62instruction starts a66CFG hr\xe1n. Maskuj\xfa sa iba absolute memory displacements a call/branch adresy; v\u0161etky p\xf4vodn\xe9 operand bindings s\xfa exportovan\xe9. Zhodn\xfd CFG po maskovan\xed nie je d\xf4kaz zhodnej s\xe9mantiky d\xe1tov\xfdch adries alebo downstream callees. \u017diadny nov\xfd Win16 runtime/CFG ekvivalent sa touto d\xe1vkou nepreukazuje.

## Reprodukcia a s\xfa\u010dasn\xfd stav

`audit_replay_palette_effect.py IMAGE INVENTORY DECODER EMULATOR OUT` a `audit_palette_effect_dos_versions.py` reprodukuj\xfa ASM/CFG, matrix, native RNG chains a bounded DOS porovnanie. `runtime_watch_palette_writer.py`/`verify_palette_writer_capture.py` zachytia reset/firsttick; `runtime_watch_palette_cycle_v2.py`/`verify_palette_cycle_capture.py` cel\xe9 tri f\xe1zy. Runtime skripty maj\xfa vstupy DOSBOXX GAMEFOLDER IMAGE RELOCS OUT WORK startup CDIMAGE; verifier IMAGE RELOCS CURRENT_MAP OUT WORK. Zdrojov\xe9 EXE a23gameasset files ostali hashovo nezmenen\xe9.

`audit_palette_writer_fields.py IMAGE RUNTIME WORK INVENTORY OUT` a `audit_palette_cycle_fields.py IMAGE RUNTIME WORK OUT` vytvoria native OUT/state/RNG a map delta CSV. Raw bin\xe1rne captures, p\xf4vodn\xe9 assets a native DLL sa nepublikuj\xfa, ale s\xfa pripnut\xe9 SHA a reprodukovate\u013en\xfdmi harnesses. `independent_decode_and_catalog.py`, tento writer a `render_campaign_status.py OUTPUTS pass1_xms_move_request PALETTE_EFFECT_NATIVE_REPORT.md` obnovia s\xfahrn. Nov\xfa GitHub d\xe1vku potvrdzuje osobitn\xe1 receipt; star\u0161ie tvrdenie \u201ewriter DAC227/235 unknown\u201c je t\xfdmto nov\xfdm d\xf4kazom pre DOS2 epiz\xf3da1/level0 reset/cycle aktualizovan\xe9.

## Aktualiz\xe1cia 13 oblast\xed

Pre ka\u017ed\xfa oblas\u0165 nov\xe9 s\xe9mantick\xe9 percento = uzavret\xe9 jednotky/\xfapln\xfd invent\xe1r. Menovatele st\xe1le ch\xfdbaj\xfa, preto N/A; star\xe9 orienta\u010dn\xe9 odhady sa neprezentuj\xfa ako meranie. Nov\xe9 funkcie/runtime d\xf4kazy s\xfa PARTIAL. UNKNOWN28B a CLASSIFIED ONLY149B ost\xe1vaj\xfa, DEEP VERIFIED0B.

|Oblas\u0165|Predo\u0161l\xfd odhad|Nov\xe9 % / metodika|Nov\xfd d\xf4kaz|Zost\xe1vaj\xface nezn\xe1me|Blokuj\xfaci probl\xe9m|Najbli\u017e\u0161\xed krok|
|---|---:|---|---|---|---|---|
|Mapy a form\xe1ty|99 %|N/A,closure/invent\xe1r|4konkr\xe9tne BYTE1 endpoint zmeny po dlh\u0161om behu|writer,A4/A5,world axes|iba endpointy|presn\xfd writer breakpoint pre4adresy|
|D\xe1tov\xe9 typy a kon\u0161tanty|95 %|N/A,closure/invent\xe1r|countdownWORD/phaseBYTE/sceneDACBYTE,4B BSS refinement|v\u0161etci alias writeri,lifecycle|nie cel\xfd BSS invent\xe1r|state a scene-index callery|
|Tabu\u013eky a ukazovatele|93 %|N/A,closure/invent\xe1r|DAC235+scene227, RAM/DAC divergence vysvetlen\xe1|in\xe9 scene-index hodnoty a alias227=235|iba jeden native sceneindex|\u010fal\u0161ie map header dom\xe9ny|
|Funkcie / ASM / CFG|90 %|N/A,closure/invent\xe1r|2tel\xe1233B/77instructions,2288replay|EA0 downstream a neuzavret\xe9 callees|runtime path nie cel\xe1 hra|audio/cache a map-writer tel\xe1|
|RNG|97 %|N/A,closure/invent\xe1r|prirodzen\xfd palette seed1\u21922745024/AX41;12native-CRT modelchains|glob\xe1lne poradie,seedy,DEMO,SAVE|iba palette RNG event|RNG call trace po\u010das world/DEMO|
|Scheduler|96 %|N/A,closure/invent\xe1r|palette reset a tick80\u219279, prirodzen\xfd flash cyklus|presn\xe9 intervaly,skip/catchup a in\xe9 vetvy|nepo\u010d\xedtan\xfd ka\u017ed\xfdtick/debug timing|riedky multi-tick trace|
|DEMO a vstupy|96 %|N/A,closure/invent\xe1r|dlh\u0161\xed bez-input gameplay do palette cycle end|DEMO a pohyb/v\xfdstrel|iba startup menu keys|riaden\xe9 gameplay vstupy a DEMO|
|Renderer / VGA|94 %|N/A,closure/invent\xe1r|24nativeOUT aDACblack/white/black,index-helper8DOS rawmatch|pixelgolden,clipping a scanout|headless paused readback|nez\xe1visl\xfd renderer golden a clippingcases|
|GUARD / bossovia|93 %|N/A,closure/invent\xe1r|mapBYTE1 tokeny sa zmenili,writer nepriraden\xfd|AIobjekty/boss stavy|endpoint nie actor trace|breakpointy A4/A5 map writerov|
|Zbrane / projektily|92 %|N/A,closure/invent\xe1r|\u017eiadny nov\xfd damage d\xf4kaz|damage/collision dom\xe9ny|bez v\xfdstrelu|controlled firing a projectile trace|
|Sprity / HUD / paleta|92 %|N/A,closure/invent\xe1r|DAC227/235writer uzavret\xfd pretestedcestu;gates/counter/RNGcycle|\u010fal\u0161ie epiz\xf3dy,in\xe9palety/callee role|jedna nat\xedvna mapa|gatedep2/ep3/sceneindex runtime|
|SAVE / LOAD|92 %|N/A,closure/invent\xe1r|\u017eiadny nov\xfd SAVE d\xf4kaz|payload54709B,rollback,RNGserialization|prefix nie cel\xfd form\xe1t|SAVE/LOAD schema a izolovan\xfd runtime|
|Windows Win16|92 %|N/A,closure/invent\xe1r|DOS8label helper/CFG compare,\u017eiadny nov\xfdWin d\xf4kaz|Win paletteAPI/flash ekvivalent|\u017eiadnyWin16runtime|fixup-backed Win effect mapping|

## Runtime testy na vykonanie

1. MapBYTE1 zmeny: priamo sledova\u0165 zapisuj\xface in\u0161trukcie k image2716F/27171/271A5/2723B (decimal adresy s\xfa autoritat\xedvne v CSV), zachyti\u0165 DS/ES/base/index a actor pointer. Pred pou\u017eit\xedm breakpointov adresy znovu prepo\u010d\xedta\u0165 z CSV, nie slepo pod\u013ea textov\xe9ho hex prepisu.
2. Efekt v episode2 a episode3 level8/9, scene index in\xfd ne\u017e227 alebo rovn\xfd235; rozl\xed\u0161i\u0165 gated no-write od neakt\xedvneho frame. Post-decrement a RNGcall poradie porovna\u0165 s riedkym scheduler trace.
3. Source for sceneDAC D2F7, v\u0161etci countdown/phase writeri a audioID66 downstream. Skuto\u010dn\xfd zvuk overi\u0165 samostatn\xfdm zvukov\xfdm profilom; headless nosound n\xe1vrat nie je audio-output parity.
4. UNKNOWN28 \u010falej analyzova\u0165 cez dynamick\xe9 segmenty/indexovan\xe9 refs a resource/map boundaries. Nula zmien ani paragraph alignment nie je padding proof. \u010ealej gameplay damage/DEMO/SAVE a Win16; PE32 sa nevykon\xe1va.
'''
(r/'PALETTE_EFFECT_NATIVE_REPORT.md').write_text(text,encoding='utf-8');print('PALETTE_EFFECT_NATIVE_REPORT.md written')
