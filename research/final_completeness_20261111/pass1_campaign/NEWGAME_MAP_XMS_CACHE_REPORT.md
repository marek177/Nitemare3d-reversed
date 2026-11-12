# DOS2: načítaná mapa a prechod zvukového adresára na XMS offsety

Nový prirodzený beh **vrátil map-init call0277:0B72** a dosiahol0D29:0A31, s epizódou1, level index0 a difficulty1. Celých8192B mapového bufferu sa zhoduje s prvým payloadom reálneho MAP.1. Pribudli dve bounded PARTIAL funkcie490B/167 inštrukcií,806 riadených replay prípadov a22. zachovaný original-EXE runtime scenár.

**Oprava významu staršieho markeru:**0D29:0A31 je CALL na083D:288C, už známy music selector, nie vstup do samotnej hernej slučky. Starší názov `game_loop_entry` vo frozen runtime harness/snapshots je iba legacy marker. Tento report a verifier ho interpretujú ako **pre_music_select_call**. Ani nový beh nepotvrdzuje prvý gameplay frame, celý scheduler, AI ani damage. Predošlý report XMS uvádzal tento endpoint ako plánovaný loop entry; tento predpoklad je vyvrátený kontrolou cieľa.

PASS320 je nezmenený: **57118B PARTIAL /149B CLASSIFIED ONLY /28B UNKNOWN /0B DEEP VERIFIED**, spolu57295B. Všetkých28 UNKNOWN bajtov ostalo v tomto scenári bez cached-value-change udalosti; čítanie ani zápisy rovnakej hodnoty tým nie sú vylúčené. Stav0nových DEEP VERIFIED ostáva.

## Natívny záznam a oprava chybnej kontrolnej podmienky

23 izolovaných súborov zahŕňalo pôvodný packed DOS2 EXE a explicitne pridaný CD DSTOPEN.IMG. AUTOTYPE3SPACE+3ENTER prešiel intro, main menu1, episode menu15→1 a difficulty menu19→1. Všetky pôvodné zdroje a ich kópie sú hashovo nezmenené.53 zachovaných code-breakpoint stavov obsahuje:

|Bod|Dôkaz|
|---|---|
|0D29:095A|pôvodný FAR caller frame: return0D29:281A, level0, episode1|
|0D29:09C4|návrat0277:0B72 pred zápisom DS:3CD4=1|
|0D29:0A31|po clock/input príprave, pred music selector call083D:288C|

Po odstránení16B XMS descriptoru z watch setu vznikol V2 beh bez udalostí a dosiahol všetky tri body, ale zlyhal v záverečnej kontrole: starý harness očakával `sound_directory==SND.DAT[192:666]`. Tento predpoklad platil pri skoršom startup zázname, no nie po cachovaní zvukov. V2 má runtime_tests0 a neimportuje sa ako úspešný scenár.

V3 zachoval pôvodný endpoint aj28B watch set, odstránil túto nesprávnu nemennosť tabuľky a zachoval raw dáta. Nezávislý verifier nižšie vyžaduje presnú rekonštrukciu celej zmenenej tabuľky, nie iba ľubovoľnú odlišnosť. Má runtime_tests1. Zostal zachovaný213 raw capture súborov; ich cesty a SHA sú v manifeste. Hra sa po captures ukončila riadeným zastavením testového procesu.

Finálny snapshot pokrýva všetkých57295 NON-CODE B aj57392B DGROUP.10963 NON-CODE bajtov sa líši od pôvodného relokovaného obrazu; tento počet nie je počet zápisov ani percento sémantického closure. Watch28 bol kalibrovaný na počiatočné nuly a všetky BPLIST cache hodnoty sú overené. Hook candidate4B sa iba dumpoval. Žiadne CPU registre či herná RAM sa debuggerom neprepisovali. Paused VGA plane readback používa explicitný GC read-map zásah a obnovu; nie je to host screenshot alebo nový renderer pixel golden.

## Mapový payload a stav

File-backed interval **[2570E,2770E)** sa zhoduje bajt za bajtom s `MAP.1[514:8706]`,8192/8192B. Offset vychádza zo známeho level loadera514+levelIndex*8192, nie z hľadania podobnej oblasti. DS:626A=1, DS:626C=0, DS:4180=1. DS:626E má hodnotu0250h, ale jej význam táto dávka neurčuje; historický filename `episode_level_counts` nie je dôkaz typu tretieho WORD.

Vo finále DS:1C9C=0, DS:3CD1=0, DS:3CD4=1. XMS control DS:3506/3508/350A=(handle1,limit2048KiB,used1074KiB). Mapový readback aj DGROUP údaje overuje `verify_newgame_map_capture.py`. Neznamená to uzavretie všetkých interných map-init callee alebo správania mapy.

## Zvuková tabuľka: pôvodný offset sa mení na záporný token

79 záznamov po6B sa nachádza v DGROUP `[3F64,413E)`,474B mimo file image. Každý záznam má WORD length a DWORD disk offset, pričom cache prepíše offset dvojkovým záporom XMS byte offsetu. Všetkých79 length WORD ostalo nezmenených;68 DWORD offset polí sa zmenilo,272 odlišných bajtov. Nepridáva sa nových474B do PASS1 ani do už započítaných4054B runtime BSS tabuliek.

Toto je reprezentácia závislá od fázy: pôvodný kladný DWORD označuje súborový offset, po prijatom cachovaní záporná hodnota označuje XMS uloženie. Nula má osobitne neuzavretý okraj: negácia XMS offsetu0 je tiež0; ďalšie consumer domény sa týmto reportom neuzatvárajú. Cache read consumer0768:0684 má signed test offsetu a opačný XMS helper, ale celý nie je v tejto dávke rekonštruovaný.

## Pôvodná funkcia0768:0580–0684

Presný image interval **[07C00,07D04)** má260B/99 inštrukcií, FAR RETF. WORD argument je index záznamu; index nemá vlastný rozsahový guard. Funkcia používa DS tabuľku, scratch FAR z DS:34F4 a source+6. Vykonáva čítanie cez0277:008A a XMS append0768:0294; externé účinky týchto callee sú v jej replay explicitne stubované. BP/SI/DI/DS a caller-cleanup SP sa kontrolujú; výstup AX nie je deklarovaný success ABI.

```c
record = sound[index];
if (record.length == 0) return;
for (k = 0; k < index; ++k)
    if (sound[k].offset == record.offset &&
        sound[k].length == record.length) return;
if (record.length > 8192) { rejected_word++; return; }
file_read(scratch_far + 6, record.offset, record.length);
start = xms_append(scratch_far + 6, record.length);
if ((int32_t)start < 0) { rejected_word++; return; }
accepted_word++;
for (k = index + 1; k < 79; ++k)
    if (sound[k].offset == record.offset)
        sound[k].offset = (uint32_t)(-start);
sound[index].offset = (uint32_t)(-start);
```

`rejected_word` je DS:E026, `accepted_word` DS:E028. Oba sú16-bitové a wrap sa kontroluje cez syntetický seedFFFFh. Predošlé duplicate porovnanie vyžaduje offset aj length, ale propagácia do neskorších aliasov porovnáva iba offset: rôzna dĺžka aliasu sa nemení a nezabráni zmene tokenu. To je potvrdená vetva pôvodného kódu, nie odporúčaná oprava. Nepriraďuje sa jej prirodzená dostupnosť mimo reálneho SND datasetu.

158 reálnych-sekvenčných replay invokácií predstavuje všetkých79 záznamov pri2load bázach. File stub kopíruje skutočný payload cez scratch, append stub vracia modelované offsety. Ďalších360 prípadov pokrýva2loady ×5lengthov(0,1,8192,8193,65535) ×3indexy(0,1,78) ×4append výsledky(0,1024,7FFFFFFFh,FFFFFFFFh) ×3duplicate domény. Celkom518 prípadov,0 rozdielov. Skutočnú XMS implementáciu ani audio výstup tento model nenahrádza dôkazom.

Rekonštrukcia celej474B natívnej tabuľky sa začína na **742KiB, odvodených z prvého zmeneného offsetu**. Je to inferovaný vstup modelu, nie nezávisle zachytený allocator stav pred sound fázou. Následne66 append operácií a4 oversized skips presne vytvorí celú tabuľku a konečný used1074KiB; tento endpoint a counters(4,66) sú nezávisle zachované v DGROUP.68 changed records oproti66 allocations vysvetľujú propagované offset aliasy. Výsledok je silnejší než označiť zmeny za korupciu, ale nepreukazuje celý source-to-XMS payload copy.

## Pôvodná orchestrace0D29:095A–0A40

Image **[0DBEA,0DCD0)** má230B/68 inštrukcií. FAR argumenty sú level index `[BP+6]`, episode `[BP+8]`. Celé telo je nezávisle dekódované a hranice zodpovedajú pôvodnému inventáru. CFG aj ASM sú v `game_start_replay`.

Algoritmus: ak DS:1C9C=0 zavolá0D29:080E; potom znovu číta flag a ak je nenulový nastaví globálnu epizódu na0. Flag vždy vynuluje a zapíše level argument. Pri DS:4152=0 vyčistí BYTE4192/4193, inak ich ponechá. Inicializuje progress, query4 a progress arguments0. Pri odlišnej epizóde volá0277:0336. Zapíše mode3CD4=0, volá map init0277:0B72 a potom mode=1. Nasledujú explicitné init callee0000:0212/03FE/052A, audio idFFFF, progress finish, tri samples do3CB2/3CB6/3CBA,083D:143C s DWORD2, clock init0BDE:019A, vyčistenie3CD1 a music selector083D:288C. Progress text pointery postupne1C9D,1CAB,1CB9,1CC7.

288 prípadov:2loady ×3počiatočné flagy ×2intro-stub flag výsledky ×2pôvodné epizódy ×3episode argumenty ×2level argumenty ×2mode hodnoty. Všetkých18 callee sú stubované; intro/episode zmeny sú explicitné modelové kontrakty. Overuje sa poradie, argumenty, vetvy, lokálne zápisy a obnovenie BP/SP/DS v DS=SS doméne. Tri return sample seeds kontrolujú zachovanie AX do príslušných WORD; nevyhlasuje sa tým skutočný význam všetkých troch sample rutin. Intro-stub mutation môže zmeniť druhý flag test, preto nestačí zlúčiť oba testy do jediného vstupného booleanu.

## Katalóg a reprodukcia

Aktuálne **143 funkčných rozsahov, 5708 inštrukcií /14344B kódu**,58034B typovaných file dát,994017 kontrolovaných replay prípadov a22 natural original-EXE scenárov s uvedenými debugger zásahmi. Typed NON-CODE zostáva57116B;2B PARTIAL relocation WORD DS2358 je naďalej typovo otvorený. Žiadny nový executable kód sa nenašiel v pôvodnom NON-CODE.

`audit_replay_game_start.py IMAGE INVENTORY DECODER EMULATOR OUT` a `audit_replay_sound_xms_cache.py` reprodukujú celé dve telá, ASM/CFG a modelové príklady. SND aj native474B výpis sú pripnuté cestou a SHA v druhom summary. `runtime_watch_newgame_map_v3.py DOSBOXX GAMEFOLDER IMAGE RELOCS OUT WORK startup CDIMAGE` reprodukuje zachytenie; `verify_newgame_map_capture.py IMAGE RELOCS CURRENT_MAP OUT WORK` overí mapu, zmenenú tabuľku, cache watch a manifest. Frozen V2 a starší44B watch pokus ostávajú neúspešné a nepočítajú sa ako runtime scenáre.

Katalóg sa obnoví cez `independent_decode_and_catalog.py ABS_DECODER OUTPUTS`, tento report cez `write_newgame_map_report.py OUTPUTS`, súhrn cez `render_campaign_status.py OUTPUTS pass1_xms_move_request NEWGAME_MAP_XMS_CACHE_REPORT.md`. Raw pamäťové výpisy, EXE a celé SND/MAP assets sa nepublikujú. GitHub stav potvrdzuje iba samostatná publication receipt; táto veta opisuje stav pri generovaní dávkového reportu.

## Aktualizácia 13 oblastí

Nové sémantické % = uzavreté jednotky / úplný inventár oblasti. Pre všetkých13 oblastí chýba úplný menovateľ, preto N/A; historické orientačné percentá sa nenahrádzajú vymysleným číslom. Nové výsledky sú PARTIAL. CLASSIFIED ONLY149B a UNKNOWN28B ostávajú; DEEP VERIFIED0B. Nasledujúci stav sa opiera o túto dávku, nie o domnelé vykonanie hernej slučky.

|Oblasť|Predošlý odhad|Nové % / metodika|Nové potvrdenie|Zostávajúce neznáme|Blokujúci problém|Konkrétny ďalší krok|
|---|---:|---|---|---|---|---|
|Mapy a formáty|99 %|N/A, closure/inventár|8192/8192B MAP1 level0 a map-init návrat|ostatné levely, init callee a gameplay význam|iba jedna prirodzená mapa|ďalšie levely a prvý gameplay frame|
|Dátové typy a konštanty|95 %|N/A, closure/inventár|79length WORD a68 zmenených offset DWORD, signed XMS token|zero token a index domény|consumer0684 neuzavretý|read cache consumer a0offset doména|
|Tabuľky a ukazovatele|93 %|N/A, closure/inventár|celá474B sound tabuľka rekonštruovaná;alias propagácia|4scratch cache sloty a životnosť|iba prvý cache fill|0768:0684 a invalidácia|
|Funkcie / ASM / CFG|90 %|N/A, closure/inventár|2telá490B/167inštrukcií,806replay|18stubovaných init callee, index guard|ABI závislosti nie sú closure|rozšíriť call graph z riadiaceho caller|
|RNG|97 %|N/A, closure/inventár|žiadny nový RNG dôkaz|prirodzené srand/rand a DEMO|prvý gameplay frame chýba|RNG trace po init návrate|
|Scheduler|96 %|N/A, closure/inventár|mode3CD4 0→1 pred music select;markerA31 opravený|skutočný loop a timer interaction|music selector nie je scheduler|sledovať0BDE:03C8 až po init|
|DEMO a vstupy|96 %|N/A, closure/inventár|prirodzený Newgame/episode1/difficulty1 až po init|DEMO a input v hre|iba menu vstupy|frame+input po scheduler vstupe|
|Renderer / VGA|94 %|N/A, closure/inventár|žiadny nový renderer parity výsledok|prvý frame a scanout|map loaded nie je frame|prvý world-draw a viditeľný flip|
|GUARD / bossovia|93 %|N/A, closure/inventár|žiadny nový AI dôkaz|actor init a boss vetvy|žiadny AI trace|actor dispatch pri gameplay|
|Zbrane / projektily|92 %|N/A, closure/inventár|žiadny nový damage dôkaz|kolízie a effect caller domény|žiadny damage trace|riadený input a projectile entry|
|Sprity / HUD / paleta|92 %|N/A, closure/inventár|žiadny nový closure dôkaz|HUD frame a text metrics|endpoint je pred hudbou|HUD/world frame capture|
|SAVE / LOAD|92 %|N/A, closure/inventár|žiadny nový SAVE dôkaz|payload54709B a rollback|metadata nie je celý formát|0277:1176 a izolovaný SAVE|
|Windows Win16|92 %|N/A, closure/inventár|žiadny nový Win dôkaz|Win cache/runtime ekvivalent|žiadny Win16 beh|fixup-backed cache porovnanie|

## Runtime testy na vykonanie

1. Po prekročení0D29:0A31 najprv zachytiť návrat inicializačného caller0D29:281A a následný vstup0BDE:03C8. Scheduler breakpoint aktivovať až po init, aby sa nechytil starší menu/prefix výskyt. Neoznačiť samotný vstup za dokončený tick/frame.
2. Sledovať remaining UNKNOWN28 počas prvých herných tickov a world-draw; descriptor16B zachovávať len vo fixných snapshot bodoch. Naďalej rozlišovať cached-change od read/write prístupu.
3. Zachytiť stav usedKiB bezprostredne pred prvým sound cache fill, aby inferred742KiB nahradil priamy dôkaz; preveriť XMS destination payload cez samostatný manager readback.
4. Overiť cache consumer0768:0684 pri hit/miss, signed disk/XMS vetve a four-slot replacement; nula token a index79+ ostávajú iba neuzavreté domény.
5. Oddelené sound output, ďalšie epizódy/levely, gameplay damage, SAVE/LOAD a Win16 parity; PE32 sa nevykonáva.
