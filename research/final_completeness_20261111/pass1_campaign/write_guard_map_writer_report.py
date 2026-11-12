"""python write_guard_map_writer_report.py OUTPUTS_DIR"""
import hashlib,json,sys
from pathlib import Path
r=Path(sys.argv[1]);read=lambda p:json.loads((r/p).read_text());a=read('guard_cell_move_replay/summary.json');v=read('dosbox_map_writers_runtime/independent_verification.json');f=read('guard_map_writer_fields/summary.json');vers=read('guard_move_dos_versions/summary.json');c=read('campaign_catalog/summary.json')
for x in a['files']+v['files']+f['files']+vers['files']:assert hashlib.sha256(Path(x['path']).read_bytes()).hexdigest()==x['sha256']
assert c['functions']==146 and c['runtime_tests']==26 and c['controlled_instruction_replay_cases']==1003217 and c['runtime_buffer_refinement_bytes_already_in_pass1']==4122 and c['record_field_refinements']==26
text='''# DOS2: presn\xe9 mapBYTE1 writery a GUARD pohybov\xe1 rutina

\u0160tyri predt\xfdm nepriraden\xe9 zmeny mapov\xe9ho bufferu maj\xfa priamy writer d\xf4kaz. P\xf4vodn\xe1 funkcia **04C7:0422** obnovuje saved-underlay cez **04C7:044C** a n\xe1sledne zapisuje aktu\xe1lny token objektu cez **04C7:06A9**. Nat\xedvny scen\xe1r zachoval98 konkr\xe9tnych MOV pred/po p\xe1rov:49 restore a49 occupancy z\xe1pisov. Z r\xe1mcov a26/28B z\xe1znamov sa potvrdili p\xe1ry **GUARD24/actor168/tokenA5** a **GUARD25/actor174/tokenA4**.

Nov\xfd bounded PARTIAL rozsah m\xe1249 in\u0161trukci\xed/683B v687B spane a6912 controlled replay pr\xedpadov. Katal\xf3g je **146 rozsahov /6034 in\u0161trukci\xed /15260B**,58034B typed file d\xe1t,1003217 riaden\xfdch pr\xedpadov a26 original-EXE scen\xe1rov. Runtime record refinements sa zv\xe4\u010d\u0161ili o108 u\u017e typovan\xfdchB na4122B/16intervalov. Pribudlo12 caller-specific field-role evidence riadkov; celkovo26, nie26 nov\xfdch jedine\u010dn\xfdch pol\xed.

PASS320 sa nemen\xed: **57118B PARTIAL /149B CLASSIFIED ONLY /28B UNKNOWN /0B DEEP VERIFIED**, presne57295B. Nov\xe9 roly spres\u0148uj\xfa existuj\xface record[350][28] aGUARD[100][26], nie nov\xfd typovan\xfd byte union. Mapa `pass1_xms_move_request/noncode_intervals.csv` SHA497d10a11959dbae3d17f495e803569e229c13434658ec94c231d29784f47efe ost\xe1va aktu\xe1lna.

## Nat\xedvny d\xf4kaz po jednej in\u0161trukcii

Breakpointy pre11 vybran\xfdch priamych ES BYTE+1 store kandid\xe1tov sa aktivovali a\u017e po map-init n\xe1vrate0D29:09C4. Interpreter registrov vypo\u010d\xedtal skuto\u010dn\xfa adresu zo zachyten\xe9ho ES aBX/DI; detailn\xfd z\xe1znam vznikol iba pre \u0161tyri po\u017eadovan\xe9 targety so skuto\u010dnou zmenou hodnoty. Pre ka\u017ed\xfd pozit\xedvny z\xe1sah:

1. CPU stoj\xed na p\xf4vodnom MOV pred vykonan\xedm; zachov\xe1 sa8192B mapy, cel\xfd14142B actor/guard/table blok a64B okolie SS:BP.
2. Nain\u0161taluje sa code breakpoint na nasleduj\xfacu in\u0161trukciu a vykon\xe1 sa p\xf4vodn\xfd MOV.
3. Post-breakpoint m\xe1 rovnak\xe9 DS/ES/SS/SP/AX/BX/CX/DX a IP+4. Cel\xe1 mapa sa mus\xed l\xed\u0161i\u0165 presne v jednom targetBYTE a nov\xe1 hodnota sa mus\xed rovna\u0165 AL.
4. Actor/guard blok a stack frame s\xfa medzi t\xfdmito dvoma bodmi byte-exact nezmenen\xe9. Post breakpoint sa odstr\xe1ni a scen\xe1r pokra\u010duje.

Nie je to priradenie writerPC pod\u013ea asynchr\xf3nneho BPLM cache eventu. Oba potvrden\xe9 opcode bloky s\xfa **26 88 47 01 = MOV BYTE PTR ES:[BX+1],AL** a ich p\xf4vodn\xe9 bajty sa nez\xe1visle porovn\xe1vaj\xfa s EXE. Debugger nevytv\xe1ra tieto z\xe1pisy do hernej RAM. Nat\xedvny load0824 d\xe1va writerCS0CEBh, DS=SS2F95h a record/map segment2A21h, alias canonical21FDh.

|Image target|Map byte offset|Zachyten\xe9 meniace z\xe1pisy|
|---|---:|---:|
|2716Fh|6753|39|
|27171h|6755|49|
|271A5h|6807|1|
|2723Bh|6957|9|

98 z\xe1pisov vysvet\u013euje, pre\u010do4 endpoint rozdiely neznamenaj\xfa iba4 intern\xe9 z\xe1pisy: rutina do\u010dasne obnovuje podklad a token vlo\u017e\xed znovu aj vtedy, ke\u010f objekt ost\xe1va v rovnakej bunke. Tieto prechodn\xe9 stavy v koncovom s\xfabore nevidno.

Scen\xe1r m\xe1340 candidate code stops,53 zachovan\xfdch startup/menu/init stavov a801 jedine\u010dn\xfdch raw capture s\xfaborov. V\u0161etky23 zdroje a ich izolovan\xe9 k\xf3pie ostali hashovo nezmenen\xe9. Kon\u010d\xed sa **04C7:06AD po poslednom po\u017eadovanom store**, teda uprostred funkcie pred lookup0176; nejde o d\xf4kaz n\xe1vratu poslednej celej GUARD aktualiz\xe1cie alebo v\u0161etk\xfdch jej callee. \u017diadny z98 one-MOV p\xe1rov s\xe1m nem\xe1 in\xfd raw mapov\xfd rozdiel.

Watch28 UNKNOWN zostal bez cached-value-change udalost\xed a zachoval sa aj fin\xe1lny snapshot cel\xfdch57295 NON-CODEB. St\xe1le to nepozoruje reads/same-value writes. Vybran\xfdch11 store foriem nie je whole-program exhaustive writer d\xf4kaz: samostatn\xfd static CSV ukazuje13 explicitn\xfdch ES BYTE+1 store foriem dodan\xe9ho invent\xe1ra vr\xe1tane2WORX foriem, a in\xe9 indexovan\xe9/alias/string cesty sa t\xfdm neuzatv\xe1raj\xfa.

## Objektov\xe9 argumenty a roly pol\xed

V\u0161etky98 zachovan\xe9 r\xe1mce maj\xfa caller return **04C7:0FBA**, po PUSHCS+NEARCALL04C7:0FB7 v otvorenej nadradenej funkcii04C7:0D80. Callee0422 m\xe1 ENTER0Ah, ulo\u017e\xed SI/DI a kon\u010d\xed FAR RETF; caller odstra\u0148uje8B dvoch FAR argumentov:

|Argument|Native hodnota|V\xfdznam v tomto calle |
|---|---|---|
|[BP+6,+8]|2A21:28BE alebo28D8|26B GUARD slot24 alebo25|
|[BP+0A,+0C]|2A21:1266 alebo130E|28B actor record168 alebo174|

Indexy sa nevym\xfd\u0161\u013eaj\xfa pod\u013ea tokenu: GUARD `(offset-264Eh)/26`, actor `(offset-6)/28`, s rozsahmi100/350 pod\u013ea u\u017e dolo\u017een\xfdch tabuliek. GUARD WORD+8 sa zhoduje s linked actor indexom168/174. TokenA4/A5 je actor BYTE0 ulo\u017een\xfd do mapBYTE1; nie je to jedine\u010dn\xe9 ID cel\xe9ho objektu ani d\xf4kaz toto\u017enosti konkr\xe9tneho mon\u0161tra/bossa.

Najd\xf4le\u017eitej\u0161ie spresnen\xe9 caller-specific roly s\xfa: GUARD+0D saved underlying mapBYTE1; GUARD+13/+14 signedBYTE coordinate deltas; GUARD+0B mode; actor+0C DWORD FAR current map cell; actor+10/+12 WORD coordinates; actor+03 animation phase; GUARD+0/+1 animation base/span; GUARD+0E low lookup result. Z\xe1znamy s\xfa v `consumer_field_roles.csv`, spolu s presn\xfdmi consumer in\u0161trukciami a PARTIAL rozsahom.

Pri044C verifier kontroluje, \u017ee ES:BX je actor current-cell FAR a AL=GUARD+0D. Pri06A9 je AL=actor+0, GUARD+0D u\u017e zachytil p\xf4vodn\xfd obsah novej bunky a actor FAR s\xfahlas\xed s v\xfdpo\u010dtom zo s\xfaradn\xedc. Napr\xedklad prv\xfd p\xe1rA5 zachyt\xe1va coordinate0=3104 pred restore a3112 pred reinsert, coordinate1=3360; GUARD delta0=8,delta1=0. Druh\xfd p\xe1r m\xe1 zachyten\xe9 signed deltas\u22128/\u22128. Neskor\u0161ie kol\xedzie a cel\xfd pohybov\xfd pl\xe1n sa neodvodzuj\xfa iba z t\xfdchto dvoch vektorov.

## Presn\xfd mapov\xfd v\xfdpo\u010det

P\xf4vodn\xfd WORD v\xfdpo\u010det na066A..0681 je:

```text
rowTerm = ((coord1 & FFC0h) * 2) & FFFFh
colTerm = arithmetic_shift_right(signed16(coord0 & FFDFh),5)
offset = (373Eh + rowTerm + colTerm) & FFFFh
segment = relocated21FDh
```

Pre be\u017en\xe9 nez\xe1porn\xe9 s\xfaradnice v64\xd764 mape je to373Eh +128*floor(coord1/64)+2*floor(coord0/64). T\xfdm sa mapov\xe9 storage minor/major osi via\u017eu na actor coordinate0/1 v tomto consumerovi; neprira\u010fuje sa geografick\xfd smer alebo v\u0161eobecn\xe9 n\xe1zvy sveta bez \u0161ir\u0161ieho renderer kontraktu. Pri signed/overflow okrajoch sa mus\xed zachova\u0165 presn\xfd WORD/AND/SAR algoritmus. T\xe1to funkcia nem\xe1 vlastn\xfd v\u0161eobecn\xfd bounds guard pre ka\u017ed\xfa vypo\u010d\xedtan\xfa adresu; replay pou\u017e\xedva v\xfdslovne norm\xe1lne poz\xedcie s bezpe\u010dn\xfdm okrajom aj pre signedBYTE velocity extremes.

## Cel\xe9 riadiace telo0422: rekon\u0161trukcia

Presn\xe9 image hranice s\xfa **[05092,05341)**. Zo687B spanu patr\xed683B do249 dek\xf3dovan\xfdch in\u0161trukci\xed. \u0160tyri bajty mimo entryCFG s\xfa exportovan\xe9 v `cfg_unreached_bytes.csv`; nie s\xfa automaticky padding ani bezpe\u010dn\xe9 alternat\xedvne vstupy. CFG nem\xe1 jump table.

```text
pre_update(guardFAR,actorFAR)
old_cell.BYTE1 = guard.saved_underlay
dx = signed8(guard.delta0); dy = signed8(guard.delta1)
xProbe = actor.coord0 + dx + sign(dx)*16
yProbe = actor.coord1 + dy + sign(dy)*16
blocked0 = dx!=0 && (probe(xProbe,coord1-16) || probe(xProbe,coord1+16))
blocked1 = dy!=0 && (probe(coord0-16,yProbe) || probe(coord0+16,yProbe))
step0 = blocked0 ? 0 : dx; step1 = blocked1 ? 0 : dy
if guard.mode!=8 || (!blocked0 && !blocked1):
    vector_helper(actor.coord0,actor.coord1,step0,step1)
    actor.coord0 += step0; actor.coord1 += step1       // WORD wrap
    propagate(actorFAR,step0,step1)
if guard.mode==6 && blocked0 && blocked1:
    if game_rand()&1: step0=-dx; guard.delta0=low8(step0)
    else: step1=-dy; guard.delta1=low8(step1)
if step0!=0 || step1!=0:
    actor.phase = low8(actor.phase+1)
    if zeroextend(guard.base)+zeroextend(guard.span) <= actor.phase:
        actor.phase = guard.base
motion_helper(guardFAR,step0,step1)
actor.cellFAR = map_pointer(actor.coord0,actor.coord1)
guard.saved_underlay = actor.cellFAR.BYTE1
actor.cellFAR.BYTE1 = actor.token
lookup = cell_lookup(actor.cellFAR)
if lookup != FFFFh: guard.lookupBYTE = low8(lookup)
```

Mode8 potl\xe1\u010da **cel\xfd positional move blok**, ak je blokovan\xe1 aspo\u0148 jedna os; n\xe1sledn\xe9 animation/motion bookkeeping ale nemus\xed by\u0165 presko\u010den\xe9. Mode6 pri oboch blokovan\xfdch osiach n\xe1hodne obr\xe1ti jednu p\xf4vodn\xfa velocity BYTE; poz\xedcie sa v tomto calle n\xe1sledne neposun\xfa znovu. Neg\xe1cia\u2212128 vytvor\xed local WORD+128, ale sp\xe4tn\xfd BYTE z\xe1pis80h zost\xe1va signed\u2212128 pre \u010fal\u0161ie \u010d\xedtanie. Lookup skip je presne AXFFFFh, nie v\u0161eobecn\xfd signed-negative test.

Nat\xedvne pozorovan\xe92sloty maj\xfa mode8. Mode6 bounce, in\xe9 mode values a signed edge dom\xe9ny v tejto d\xe1vke preukazuje p\xf4vodn\xe9 telo v riadenom modeli, nie prirodzen\xe1 dostupnos\u0165 t\xfdchto stavov u ka\u017ed\xe9ho GUARD typu. Neboli pomenovan\xe9 ako konkr\xe9tna boss strat\xe9gia.

## Controlled replay a z\xe1vislosti

6912 pr\xedpadov =2loady \xd72poz\xedcie \xd79signed velocity p\xe1rov \xd716collision response masks \xd73mode hodnoty(0,6,8) \xd72RNG parity \xd72lookup v\xfdsledky(FFFF,1234). Vol\xe1 sa cel\xe9 p\xf4vodn\xe9 telo0422; kontroluje sa cel\xfd8192B mapov\xfd buffer a v\u0161etk\xfdch26/28B z\xe1znamov, poradie volan\xed, argumenty, BP/SI/DI/DS/SP. Poz\xedcie zah\u0155\u0148aj\xfa stred a bl\xedzkos\u0165 cell boundary; animation seeds0/19/255 pokr\xfdvaj\xfa reset hranicu aj BYTE wrap. Underlay0 a52h s\xfa modelov\xe9 vstupy; nonzero underlay sa automaticky nevyd\xe1va za nat\xedvne pozorovanie tohto scen\xe1ra.

Sedem z\xe1visl\xfdch funkci\xed je **stubovan\xfdch**:083D:19E4 pre-update,04C7:0254 collision,0637:04B4 vector helper,0AEA:015E propagation,0FBA:01A0 RNG,04C7:00B0 motion helper a00F7:0176 cell lookup. Stub domain v\xfdslovne neprepisuje \u010fal\u0161ie record polia; p\xf4vodn\xe9 z\xe1vislosti m\xf4\u017eu ma\u0165 \u0161ir\u0161ie \xfa\u010dinky. Preto v\xfdsledok uzatv\xe1ra caller control/field kontrakt v danom modeli, nie cel\xfd AI alebo kol\xedzny algoritmus. Autorstvo konkr\xe9tneho kompil\xe1tora/runtime kni\u017enice sa z t\xfdchto C-style prologov neidentifikuje.

## Bounded DOS cross-version porovnanie

Re\xe1lne obrazy/invent\xe1re DOS ozna\u010den\xed10/11/12/15/17/18/19/20 s\xfa pripnut\xe9 SHA,7 unik\xe1tnych obrazov(18=19). Vo v\u0161etk\xfdch8 sa na\u0161iel unik\xe1tny0422 prologov\xfd vzor a zhodn\xfd cel\xfd normalizovan\xfd687B layout aj CFG. Call/branch adresy, absolute displacements a MOVCX map segment s\xfa maskovan\xe9 a p\xf4vodn\xe9 bindingy exportovan\xe9. Record member offsets, signed oper\xe1cie, podmienky mode6/8 a controlflow zost\xe1vaj\xfa v porovnan\xed zachovan\xe9.

Je to bounded byte/CFG d\xf4kaz; maskovan\xe9 segmentov\xe9/map/callee adresy nie s\xfa automaticky s\xe9manticky zviazan\xe9. \u017diadny nov\xfd Win16 ekvivalent alebo prirodzen\xe1 DOS/Win16 AI parity sa nepreukazuje. Raw rozdiely a normaliza\u010dn\xe9 hash hodnoty s\xfa v `guard_move_dos_versions/dos_version_comparison.csv`.

## Artefakty a reprodukcia

`runtime_watch_map_writers.py DOSBOXX GAMEFOLDER IMAGE RELOCS OUT WORK startup CDIMAGE` zachyt\xed sc\xe9nu bez gameplay key z\xe1sahov navy\u0161e. `verify_map_writer_capture.py IMAGE RELOCS CURRENT_MAP OUT WORK` over\xed v\u0161etk\xfdch98 one-MOV p\xe1rov, argumenty, pointery, podklady a rodi\u010dovsk\xfd callerFBA. `audit_guard_map_writer_fields.py IMAGE RUNTIME WORK INVENTORY OUT` exportuje native98row trace,108B/4record refinements,12field roles a vybran\xe9 static store formy.

`audit_replay_guard_cell_move.py IMAGE INVENTORY DECODER EMULATOR OUT` rekon\u0161truuje cel\xe9 telo/CFG a6912case matrix. `audit_guard_move_dos_versions.py` s rovnak\xfdmCLI over\xed8DOS ozna\u010den\xed. Po `independent_decode_and_catalog.py ABS_DECODER OUTPUTS` tento writer a `render_campaign_status.py OUTPUTS pass1_xms_move_request GUARD_MAP_WRITER_REPORT.md` obnovia aktu\xe1lny stav. Raw801bin captures a p\xf4vodn\xe9EXE/assets sa nepublikuj\xfa; presn\xe9 cesty/SHA a v\u0161etky harnesses sa zachovaj\xfa. Publikovanie novej d\xe1vky potvrdzuje samostatn\xe1 receipt.

## Aktualiz\xe1cia 13 oblast\xed

Nov\xe9 s\xe9mantick\xe9 percento = uzavret\xe9 jednotky/\xfapln\xfd invent\xe1r oblasti. \xdapln\xe9 menovatele st\xe1le ch\xfdbaj\xfa, preto N/A. Historick\xe9 orienta\u010dn\xe9 odhady sa nenahr\xe1dzaj\xfa odhadnut\xfdm \u010d\xedslom. Nov\xe9 v\xfdsledky s\xfa PARTIAL; UNKNOWN28B, CLASSIFIED ONLY149B a DEEP VERIFIED0 sa nemenia.

|Oblas\u0165|Predo\u0161l\xfd odhad|Nov\xe9 % / metodika|Nov\xfd potvrden\xfd d\xf4kaz|Zost\xe1vaj\xface nezn\xe1me|Blokuj\xfaci probl\xe9m|Najbli\u017e\u0161\xed krok|
|---|---:|---|---|---|---|---|
|Mapy a form\xe1ty|99 %|N/A,closure/invent\xe1r|v\u0161etky4targety maj\xfa presn\xe9 BYTE1 writery;98z\xe1pisov|in\xe9 mapov\xe9 cesty a alias writery|selected direct store formy nie exhaustive|\u0161\xedri\u0165 trace cez \u010fal\u0161ie object/map oper\xe1cie|
|D\xe1tov\xe9 typy a kon\u0161tanty|95 %|N/A,closure/invent\xe1r|12caller-specific rol\xed,108B native rawrecord refinement|in\xe9 polia100/350records|iba2native GUARD sloty|zost\xe1vaj\xface record fields a consumers|
|Tabu\u013eky a ukazovatele|93 %|N/A,closure/invent\xe1r|GUARD24\u2192actor168 a25\u2192174;FARcell pointer zcoord0/1|in\xe9 linky,lifecycle a invalid\xe1cia|2p\xe1ry nie cel\xe1 tabu\u013eka|GUARD allocation/destruction/link callery|
|Funkcie / ASM / CFG|90 %|N/A,closure/invent\xe1r|0422whole controlbody683B/249instructions/6912replay|7mockcallee a4CFG gapB|callee effects neuzavret\xe9|04C7:0254 a nadraden\xe10D80|
|RNG|97 %|N/A,closure/invent\xe1r|mode6bothblocked parity branch staticky/replay|prirodzen\xfd mode6 RNG a global order|native bolmode8|native mode6 situ\xe1cia a randtrace|
|Scheduler|96 %|N/A,closure/invent\xe1r|worldupdate vedie doGUARD callerFBA a98stores|cadence,in\xe9strategy/timer interactions|hust\xe9debugstops|riedky multi-tick/strategy trace|
|DEMO a vstupy|96 %|N/A,closure/invent\xe1r|bez nov\xe9ho gameplay key input prebeholGUARDmove|DEMO a riaden\xfd pohyb/v\xfdstrel|iba no-input sc\xe9na|gameplay input a DEMOtrace|
|Renderer / VGA|94 %|N/A,closure/invent\xe1r|\u017eiadny nov\xfd pixel parity d\xf4kaz|renderer golden/clipping/scanout|storetrace nie pixel golden|object movement verzus spritedraw|
|GUARD / bossovia|93 %|N/A,closure/invent\xe1r|underlay restore/rebind,mode8 gate,mode6bounce model|0254collision,0D80AI,boss strat\xe9gia|2native mode8sloty a7stuby|0254validator a0D80strategy CFG|
|Zbrane / projektily|92 %|N/A,closure/invent\xe1r|\u017eiadny nov\xfd damage d\xf4kaz|projectile/collision/effects|bezv\xfdstrelu|controlled projectile trace|
|Sprity / HUD / paleta|92 %|N/A,closure/invent\xe1r|actor phaseBYTEanimation base/span kontrakt|spriteID/phase timing a draw caller|framecounter nie cel\xfdrender|animation consumer a sprite selection|
|SAVE / LOAD|92 %|N/A,closure/invent\xe1r|4mapBYTE1writes ozna\u010den\xe9 dynamick\xe9state|serializ\xe1cia actor/map underlay a rollback|metadata prefix nie cel\xe9SAVE|payload fields preactor/guard/map|
|Windows Win16|92 %|N/A,closure/invent\xe1r|8DOS normalized wholecallerCFG,\u017eiadnyWin d\xf4kaz|Winactor/collision equivalent|\u017eiadnyWin16runtime|fixup-backed actor move mapping|

## Runtime testy na vykonanie

1. Rekon\u0161truova\u0165 a testova\u016504C7:0254 bez collision stubu: presn\xe9 tile/occupancy/player collision rules a n\xe1vratov\xe9 dom\xe9ny. Potom roz\u0161\xedri\u0165 caller0422replay o p\xf4vodn\xfdvalidator.
2. Nadraden\xfd04C7:0D80: spoji\u0165 native return0FBA s strategy/target states, type8 spr\xe1van\xedm a prirodzen\xfdmi mode6/boss vetvami. Samotn\xfd map tokenA4/A5 nepomenova\u0165 za bossID.
3. GUARD allocator,underlay nezero/overlap,pre-update19E4,vector4B4/propagation15E/motion00B0 a lookup0176 sideeffects; korektne oddeli\u0165 caller model od cel\xe9ho AI.
4. UNKNOWN28 na\u010falej sk\xfama\u0165 cez segmentov\xe9/indexovan\xe9 pr\xedstupy,staging a map boundaries. Tento recordrefinement nerob\xed z paragraph gaps dok\xe1zan\xfdpadding. Pokra\u010dova\u0165 gameplay damage/DEMO/SAVE/Win16; PE32 sa nevykon\xe1va.
'''
(r/'GUARD_MAP_WRITER_REPORT.md').write_text(text,encoding='utf-8');print('GUARD_MAP_WRITER_REPORT.md written')
