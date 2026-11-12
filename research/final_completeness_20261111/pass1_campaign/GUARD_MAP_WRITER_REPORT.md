# DOS2: presné mapBYTE1 writery a GUARD pohybová rutina

Štyri predtým nepriradené zmeny mapového bufferu majú priamy writer dôkaz. Pôvodná funkcia **04C7:0422** obnovuje saved-underlay cez **04C7:044C** a následne zapisuje aktuálny token objektu cez **04C7:06A9**. Natívny scenár zachoval98 konkrétnych MOV pred/po párov:49 restore a49 occupancy zápisov. Z rámcov a26/28B záznamov sa potvrdili páry **GUARD24/actor168/tokenA5** a **GUARD25/actor174/tokenA4**.

Nový bounded PARTIAL rozsah má249 inštrukcií/683B v687B spane a6912 controlled replay prípadov. Katalóg je **146 rozsahov /6034 inštrukcií /15260B**,58034B typed file dát,1003217 riadených prípadov a26 original-EXE scenárov. Runtime record refinements sa zväčšili o108 už typovanýchB na4122B/16intervalov. Pribudlo12 caller-specific field-role evidence riadkov; celkovo26, nie26 nových jedinečných polí.

PASS320 sa nemení: **57118B PARTIAL /149B CLASSIFIED ONLY /28B UNKNOWN /0B DEEP VERIFIED**, presne57295B. Nové roly spresňujú existujúce record[350][28] aGUARD[100][26], nie nový typovaný byte union. Mapa `pass1_xms_move_request/noncode_intervals.csv` SHA497d10a11959dbae3d17f495e803569e229c13434658ec94c231d29784f47efe ostáva aktuálna.

## Natívny dôkaz po jednej inštrukcii

Breakpointy pre11 vybraných priamych ES BYTE+1 store kandidátov sa aktivovali až po map-init návrate0D29:09C4. Interpreter registrov vypočítal skutočnú adresu zo zachyteného ES aBX/DI; detailný záznam vznikol iba pre štyri požadované targety so skutočnou zmenou hodnoty. Pre každý pozitívny zásah:

1. CPU stojí na pôvodnom MOV pred vykonaním; zachová sa8192B mapy, celý14142B actor/guard/table blok a64B okolie SS:BP.
2. Nainštaluje sa code breakpoint na nasledujúcu inštrukciu a vykoná sa pôvodný MOV.
3. Post-breakpoint má rovnaké DS/ES/SS/SP/AX/BX/CX/DX a IP+4. Celá mapa sa musí líšiť presne v jednom targetBYTE a nová hodnota sa musí rovnať AL.
4. Actor/guard blok a stack frame sú medzi týmito dvoma bodmi byte-exact nezmenené. Post breakpoint sa odstráni a scenár pokračuje.

Nie je to priradenie writerPC podľa asynchrónneho BPLM cache eventu. Oba potvrdené opcode bloky sú **26 88 47 01 = MOV BYTE PTR ES:[BX+1],AL** a ich pôvodné bajty sa nezávisle porovnávajú s EXE. Debugger nevytvára tieto zápisy do hernej RAM. Natívny load0824 dáva writerCS0CEBh, DS=SS2F95h a record/map segment2A21h, alias canonical21FDh.

|Image target|Map byte offset|Zachytené meniace zápisy|
|---|---:|---:|
|2716Fh|6753|39|
|27171h|6755|49|
|271A5h|6807|1|
|2723Bh|6957|9|

98 zápisov vysvetľuje, prečo4 endpoint rozdiely neznamenajú iba4 interné zápisy: rutina dočasne obnovuje podklad a token vloží znovu aj vtedy, keď objekt ostáva v rovnakej bunke. Tieto prechodné stavy v koncovom súbore nevidno.

Scenár má340 candidate code stops,53 zachovaných startup/menu/init stavov a801 jedinečných raw capture súborov. Všetky23 zdroje a ich izolované kópie ostali hashovo nezmenené. Končí sa **04C7:06AD po poslednom požadovanom store**, teda uprostred funkcie pred lookup0176; nejde o dôkaz návratu poslednej celej GUARD aktualizácie alebo všetkých jej callee. Žiadny z98 one-MOV párov sám nemá iný raw mapový rozdiel.

Watch28 UNKNOWN zostal bez cached-value-change udalostí a zachoval sa aj finálny snapshot celých57295 NON-CODEB. Stále to nepozoruje reads/same-value writes. Vybraných11 store foriem nie je whole-program exhaustive writer dôkaz: samostatný static CSV ukazuje13 explicitných ES BYTE+1 store foriem dodaného inventára vrátane2WORX foriem, a iné indexované/alias/string cesty sa tým neuzatvárajú.

## Objektové argumenty a roly polí

Všetky98 zachované rámce majú caller return **04C7:0FBA**, po PUSHCS+NEARCALL04C7:0FB7 v otvorenej nadradenej funkcii04C7:0D80. Callee0422 má ENTER0Ah, uloží SI/DI a končí FAR RETF; caller odstraňuje8B dvoch FAR argumentov:

|Argument|Native hodnota|Význam v tomto calle |
|---|---|---|
|[BP+6,+8]|2A21:28BE alebo28D8|26B GUARD slot24 alebo25|
|[BP+0A,+0C]|2A21:1266 alebo130E|28B actor record168 alebo174|

Indexy sa nevymýšľajú podľa tokenu: GUARD `(offset-264Eh)/26`, actor `(offset-6)/28`, s rozsahmi100/350 podľa už doložených tabuliek. GUARD WORD+8 sa zhoduje s linked actor indexom168/174. TokenA4/A5 je actor BYTE0 uložený do mapBYTE1; nie je to jedinečné ID celého objektu ani dôkaz totožnosti konkrétneho monštra/bossa.

Najdôležitejšie spresnené caller-specific roly sú: GUARD+0D saved underlying mapBYTE1; GUARD+13/+14 signedBYTE coordinate deltas; GUARD+0B mode; actor+0C DWORD FAR current map cell; actor+10/+12 WORD coordinates; actor+03 animation phase; GUARD+0/+1 animation base/span; GUARD+0E low lookup result. Záznamy sú v `consumer_field_roles.csv`, spolu s presnými consumer inštrukciami a PARTIAL rozsahom.

Pri044C verifier kontroluje, že ES:BX je actor current-cell FAR a AL=GUARD+0D. Pri06A9 je AL=actor+0, GUARD+0D už zachytil pôvodný obsah novej bunky a actor FAR súhlasí s výpočtom zo súradníc. Napríklad prvý párA5 zachytáva coordinate0=3104 pred restore a3112 pred reinsert, coordinate1=3360; GUARD delta0=8,delta1=0. Druhý pár má zachytené signed deltas−8/−8. Neskoršie kolízie a celý pohybový plán sa neodvodzujú iba z týchto dvoch vektorov.

## Presný mapový výpočet

Pôvodný WORD výpočet na066A..0681 je:

```text
rowTerm = ((coord1 & FFC0h) * 2) & FFFFh
colTerm = arithmetic_shift_right(signed16(coord0 & FFDFh),5)
offset = (373Eh + rowTerm + colTerm) & FFFFh
segment = relocated21FDh
```

Pre bežné nezáporné súradnice v64×64 mape je to373Eh +128*floor(coord1/64)+2*floor(coord0/64). Tým sa mapové storage minor/major osi viažu na actor coordinate0/1 v tomto consumerovi; nepriraďuje sa geografický smer alebo všeobecné názvy sveta bez širšieho renderer kontraktu. Pri signed/overflow okrajoch sa musí zachovať presný WORD/AND/SAR algoritmus. Táto funkcia nemá vlastný všeobecný bounds guard pre každú vypočítanú adresu; replay používa výslovne normálne pozície s bezpečným okrajom aj pre signedBYTE velocity extremes.

## Celé riadiace telo0422: rekonštrukcia

Presné image hranice sú **[05092,05341)**. Zo687B spanu patrí683B do249 dekódovaných inštrukcií. Štyri bajty mimo entryCFG sú exportované v `cfg_unreached_bytes.csv`; nie sú automaticky padding ani bezpečné alternatívne vstupy. CFG nemá jump table.

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

Mode8 potláča **celý positional move blok**, ak je blokovaná aspoň jedna os; následné animation/motion bookkeeping ale nemusí byť preskočené. Mode6 pri oboch blokovaných osiach náhodne obráti jednu pôvodnú velocity BYTE; pozície sa v tomto calle následne neposunú znovu. Negácia−128 vytvorí local WORD+128, ale spätný BYTE zápis80h zostáva signed−128 pre ďalšie čítanie. Lookup skip je presne AXFFFFh, nie všeobecný signed-negative test.

Natívne pozorované2sloty majú mode8. Mode6 bounce, iné mode values a signed edge domény v tejto dávke preukazuje pôvodné telo v riadenom modeli, nie prirodzená dostupnosť týchto stavov u každého GUARD typu. Neboli pomenované ako konkrétna boss stratégia.

## Controlled replay a závislosti

6912 prípadov =2loady ×2pozície ×9signed velocity párov ×16collision response masks ×3mode hodnoty(0,6,8) ×2RNG parity ×2lookup výsledky(FFFF,1234). Volá sa celé pôvodné telo0422; kontroluje sa celý8192B mapový buffer a všetkých26/28B záznamov, poradie volaní, argumenty, BP/SI/DI/DS/SP. Pozície zahŕňajú stred a blízkosť cell boundary; animation seeds0/19/255 pokrývajú reset hranicu aj BYTE wrap. Underlay0 a52h sú modelové vstupy; nonzero underlay sa automaticky nevydáva za natívne pozorovanie tohto scenára.

Sedem závislých funkcií je **stubovaných**:083D:19E4 pre-update,04C7:0254 collision,0637:04B4 vector helper,0AEA:015E propagation,0FBA:01A0 RNG,04C7:00B0 motion helper a00F7:0176 cell lookup. Stub domain výslovne neprepisuje ďalšie record polia; pôvodné závislosti môžu mať širšie účinky. Preto výsledok uzatvára caller control/field kontrakt v danom modeli, nie celý AI alebo kolízny algoritmus. Autorstvo konkrétneho kompilátora/runtime knižnice sa z týchto C-style prologov neidentifikuje.

## Bounded DOS cross-version porovnanie

Reálne obrazy/inventáre DOS označení10/11/12/15/17/18/19/20 sú pripnuté SHA,7 unikátnych obrazov(18=19). Vo všetkých8 sa našiel unikátny0422 prologový vzor a zhodný celý normalizovaný687B layout aj CFG. Call/branch adresy, absolute displacements a MOVCX map segment sú maskované a pôvodné bindingy exportované. Record member offsets, signed operácie, podmienky mode6/8 a controlflow zostávajú v porovnaní zachované.

Je to bounded byte/CFG dôkaz; maskované segmentové/map/callee adresy nie sú automaticky sémanticky zviazané. Žiadny nový Win16 ekvivalent alebo prirodzená DOS/Win16 AI parity sa nepreukazuje. Raw rozdiely a normalizačné hash hodnoty sú v `guard_move_dos_versions/dos_version_comparison.csv`.

## Artefakty a reprodukcia

`runtime_watch_map_writers.py DOSBOXX GAMEFOLDER IMAGE RELOCS OUT WORK startup CDIMAGE` zachytí scénu bez gameplay key zásahov navyše. `verify_map_writer_capture.py IMAGE RELOCS CURRENT_MAP OUT WORK` overí všetkých98 one-MOV párov, argumenty, pointery, podklady a rodičovský callerFBA. `audit_guard_map_writer_fields.py IMAGE RUNTIME WORK INVENTORY OUT` exportuje native98row trace,108B/4record refinements,12field roles a vybrané static store formy.

`audit_replay_guard_cell_move.py IMAGE INVENTORY DECODER EMULATOR OUT` rekonštruuje celé telo/CFG a6912case matrix. `audit_guard_move_dos_versions.py` s rovnakýmCLI overí8DOS označení. Po `independent_decode_and_catalog.py ABS_DECODER OUTPUTS` tento writer a `render_campaign_status.py OUTPUTS pass1_xms_move_request GUARD_MAP_WRITER_REPORT.md` obnovia aktuálny stav. Raw801bin captures a pôvodnéEXE/assets sa nepublikujú; presné cesty/SHA a všetky harnesses sa zachovajú. Publikovanie novej dávky potvrdzuje samostatná receipt.

## Aktualizácia 13 oblastí

Nové sémantické percento = uzavreté jednotky/úplný inventár oblasti. Úplné menovatele stále chýbajú, preto N/A. Historické orientačné odhady sa nenahrádzajú odhadnutým číslom. Nové výsledky sú PARTIAL; UNKNOWN28B, CLASSIFIED ONLY149B a DEEP VERIFIED0 sa nemenia.

|Oblasť|Predošlý odhad|Nové % / metodika|Nový potvrdený dôkaz|Zostávajúce neznáme|Blokujúci problém|Najbližší krok|
|---|---:|---|---|---|---|---|
|Mapy a formáty|99 %|N/A,closure/inventár|všetky4targety majú presné BYTE1 writery;98zápisov|iné mapové cesty a alias writery|selected direct store formy nie exhaustive|šíriť trace cez ďalšie object/map operácie|
|Dátové typy a konštanty|95 %|N/A,closure/inventár|12caller-specific rolí,108B native rawrecord refinement|iné polia100/350records|iba2native GUARD sloty|zostávajúce record fields a consumers|
|Tabuľky a ukazovatele|93 %|N/A,closure/inventár|GUARD24→actor168 a25→174;FARcell pointer zcoord0/1|iné linky,lifecycle a invalidácia|2páry nie celá tabuľka|GUARD allocation/destruction/link callery|
|Funkcie / ASM / CFG|90 %|N/A,closure/inventár|0422whole controlbody683B/249instructions/6912replay|7mockcallee a4CFG gapB|callee effects neuzavreté|04C7:0254 a nadradená0D80|
|RNG|97 %|N/A,closure/inventár|mode6bothblocked parity branch staticky/replay|prirodzený mode6 RNG a global order|native bolmode8|native mode6 situácia a randtrace|
|Scheduler|96 %|N/A,closure/inventár|worldupdate vedie doGUARD callerFBA a98stores|cadence,inéstrategy/timer interactions|hustédebugstops|riedky multi-tick/strategy trace|
|DEMO a vstupy|96 %|N/A,closure/inventár|bez nového gameplay key input prebeholGUARDmove|DEMO a riadený pohyb/výstrel|iba no-input scéna|gameplay input a DEMOtrace|
|Renderer / VGA|94 %|N/A,closure/inventár|žiadny nový pixel parity dôkaz|renderer golden/clipping/scanout|storetrace nie pixel golden|object movement verzus spritedraw|
|GUARD / bossovia|93 %|N/A,closure/inventár|underlay restore/rebind,mode8 gate,mode6bounce model|0254collision,0D80AI,boss stratégia|2native mode8sloty a7stuby|0254validator a0D80strategy CFG|
|Zbrane / projektily|92 %|N/A,closure/inventár|žiadny nový damage dôkaz|projectile/collision/effects|bezvýstrelu|controlled projectile trace|
|Sprity / HUD / paleta|92 %|N/A,closure/inventár|actor phaseBYTEanimation base/span kontrakt|spriteID/phase timing a draw caller|framecounter nie celýrender|animation consumer a sprite selection|
|SAVE / LOAD|92 %|N/A,closure/inventár|4mapBYTE1writes označené dynamickéstate|serializácia actor/map underlay a rollback|metadata prefix nie celéSAVE|payload fields preactor/guard/map|
|Windows Win16|92 %|N/A,closure/inventár|8DOS normalized wholecallerCFG,žiadnyWin dôkaz|Winactor/collision equivalent|žiadnyWin16runtime|fixup-backed actor move mapping|

## Runtime testy na vykonanie

1. Rekonštruovať a testovať04C7:0254 bez collision stubu: presné tile/occupancy/player collision rules a návratové domény. Potom rozšíriť caller0422replay o pôvodnývalidator.
2. Nadradený04C7:0D80: spojiť native return0FBA s strategy/target states, type8 správaním a prirodzenými mode6/boss vetvami. Samotný map tokenA4/A5 nepomenovať za bossID.
3. GUARD allocator,underlay nezero/overlap,pre-update19E4,vector4B4/propagation15E/motion00B0 a lookup0176 sideeffects; korektne oddeliť caller model od celého AI.
4. UNKNOWN28 naďalej skúmať cez segmentové/indexované prístupy,staging a map boundaries. Tento recordrefinement nerobí z paragraph gaps dokázanýpadding. Pokračovať gameplay damage/DEMO/SAVE/Win16; PE32 sa nevykonáva.
