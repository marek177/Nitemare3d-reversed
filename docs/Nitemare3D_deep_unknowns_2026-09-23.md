# Nitemare3D: hlboká analýza neznámej logiky

**Dátum:** 23. 9. 2026  
**Typ:** doplnenie auditu Nitemare3D; statická analýza kódu a dát  
**Rozsah:** DOS v2.0, Win16 1.10, kontrolne Win16 1.8; aktuálne dodané MAP, WALLS, OBJECTS a IMG dáta

## Čo sa podarilo uzavrieť

Z 1 486 rozpoznaných funkcií je 519 v DOS a 967 vo Win16. Párovanie medzi verziami podporuje identitu 1 358 položiek, teda 91,4 %. Všetky funkcie sú priradené k oblastiam, ale detailná ručná analýza doteraz pokrývala iba prvých 200 funkcií z každej platformy. Párovanie je dôkazom podobnosti funkcií; úplné správanie potvrdzuje až ich telo a volania.

Najvýraznejší posun v tomto doplnení:

| Oblasť | Teraz priamo potvrdené | Zostáva otvorené |
|---|---|---|
| GUARD AI a percepcia | kostra automatu, LOS a rozsah 8 buniek; strategy-3 tabuľka mapuje osem facingov na štyri kardinálne kroky, stav 0x15 po zásahu vracia uložený stav; `GUARD+0x12` je staticky potvrdený smerový cache key, ktorý damage invaliduje hodnotou 8; prechody sú rovnaké vo Win16 1.8/1.10 | triedový výber reakčnej animácie, úplné writers stavov, viditeľné runtime obnovenie cache a DOS parity |
| Časovače a animácie | časová základňa DOS/Win16; IMG adresáre, obe 90 B SEQDEF banky, polia, aliasy a všetky frame streamy v troch IMG; interval ide priamo do ms deadline | presné EXE/epizóda párovanie, runtime väzba selectorov a alternatív, cross-build obrazové správanie |
| Projektily a hazardy | 8-záznamový pool, typy projektilov, kolízny reťazec, frekvencia strelby v simulačných krokoch, oheň 100/10/2 HP | presná rýchlosť v súradniciach/s, úplná projektilová damage tabuľka |
| Špeciálne triedy | číselné wall/object class ID priradené k názvom; Win16 1.10 TRIGGER1/2 staticky spárované s epizódou, levelom, bunkami, flagmi a textami; E1 SPECIAL1 poistková skrinka a interval sekvencie chalkboardu čiastočne trasované | runtime potvrdenie markerov/animácie; ONE_SHOT a SPECIAL1 boli doplnené 24. 9. v samostatnom reporte; LOAD tabule a wall class 03–06 v iných mapových verziách zostávajú otvorené |
| USER.SAV | všetky bloky vrátane 94 B na 0x2035; interné offsety, priame čítania/zápisy, odvodené pointery a rebase po load-e sú rozmapované v samostatnom reporte | niekoľko bajtov 94 B bez priameho C xrefu, nepriame/raw prístupy, runtime diff testy, 51A9/51AA a selector rozsah naprieč WALLS buildmi |

Nasledujúce tvrdenia sú zo statického kódu alebo surových dát. Označenie „potvrdené“ znamená, že operácia je viditeľná priamo v kóde; jej príbehový názov môže byť stále neznámy.

## 1. GUARD AI a percepcia

### Záznam strážcu

Win16 uchováva až 100 strážcov v záznamoch dlhých 26 bajtov. FUN_1010_80aa prejde všetky aktívne záznamy a zavolá FUN_1010_7b56. Dôležité polia:

| Offset | Pozorovaný význam |
|---:|---|
| +0x06 | odpočítavací časovač stavu |
| +0x0A | stratégia |
| +0x0B | aktuálny stav |
| +0x0C | nasledujúci stav |
| +0x10 | HP |
| +0x11 | smer/facing v 8 smeroch |
| +0x12 | smerový cache key: reader porovnáva očakávanú hodnotu 0–7; damage path zapisuje 8 ako invalidáciu, nie ako odpočet bolesti |
| +0x13, +0x14 | bočné a čelné pohybové posuny v pomocných stavoch |
| +0x16 | režim výberu percepcie |
| +0x17 | výsledok ray-trace / videnia |
| +0x18 | blízkosť hráča |

Stavový časovač sa znižuje pri volaní AI aktualizácie; nie je to priamo počet milisekúnd. Názvy nižšie opisujú vykonané operácie, nie pôvodné vývojárske názvy stavov.

### Čo robia hlavné stavy

| Stav | Priamo pozorovaný tok |
|---:|---|
| 0 | prehráva snímky zvolenej sekvencie; po vypršaní +0x06 prepne aktuálny stav na +0x0C |
| 1 | odpočítava časovač, potom prejde do stavu 2 |
| 2 | inicializuje sekvenciu upozornenia a prejde do stavu 3 |
| 3 | vykoná percepciu; pri výsledku videnia prejde do 4, inak do 5 |
| 4 | znovu kontroluje percepciu a spúšťa útokové/kolízne spracovanie; pri strate podmienky pokračuje do 5 |
| 5 | zavolá plánovanie podľa stratégie |
| 6 | vykonáva pohyb; po vyčerpaní časovača sa vracia do kontroly v stave 3 |
| 7–8 | pohyb a opakované kontroly hráča; jedna vetva závisí od stratégie 3 |
| 9 | spracuje špeciálnu interakciu objektu a prípadné súvisiace presuny |
| 0x0B | stav nemá vlastnú vetvu v hlavnom switchi; pomocník FUN_1010_80ea ho nastavuje napríklad pri vyradení strážcu |
| 0x0C–0x0D | volajú spoločný pohybový/animačný pomocník; presné herné meno nie je dokázané |
| 0x0E–0x0F | časovaná Cannon AI vetva riadená `DAT_1048_51A5`; pri zapnutí pokračuje do stavu 0x10 s perception/damage testom; pri vypnutí sa vracia medzi 0x0E/0x0F |
| 0x10–0x11 | útokový pokus po perception teste a následný pohyb/recovery; presná zdieľaná vetva závisí od class a stavu |
| 0x12–0x15 | samostatné časované animačné a pohybové vetvy; stav 0x15 prehráva snímky a potom preberie ďalší stav |

Stavy 0x0E/0x0F používajú DAT_1048_51A5 v špeciálnej AI triedy `0x19`; mapová class tabuľka ju priraďuje objektom `0xCC–0xCF`, teda štyrom smerovým variantom Cannon. Pri zapnutom flagu sa prejde do časovanej vetvy, ktorá v stave 0x10 overí videnie/blízkosť hráča a potom môže zavolať damage helper `FUN_1010_8c0a`. Pri vypnutom flagu sa automat vracia medzi stavmi 0x0E/0x0F bez tohto útokového prechodu. `51A5` sa resetuje na 1 pri level init-e a príkazy panelového menu `0x20/0x21` ho preklápajú. Statický tok teda potvrdzuje Cannon attack-enable flag; presná kadencia a viditeľná animácia ostávajú na runtime overenie.

### Percepcia: rozsah, smer a prekážky

FUN_1010_7494 najprv prevedie polohu hráča a strážcu na bunky mapy posunom doprava o 6 bitov. Ak je rozdiel v X alebo Y väčší než 8 buniek, kandidáta odmietne. V bežnom režime smeru zostaví bitovú masku troch susedných smerov: smer strážcu a po jednom smere na obe strany. Pri ôsmich smeroch to tvorí približne 135° kužeľ, čiže tri sektory po 45°.

Následne FUN_1010_d50a vykoná Bresenhamov prechod najviac cez 8 buniek. Stena s príslušným blokovacím flagom ukončí kontrolu. Niektoré bunky s dynamickými objektmi sa vyhodnocujú cez door/object tabuľky; stav otvorenia teda môže meniť priechodnosť lúča. Volajúci nastaví výsledok do poľa +0x17.

FUN_1010_7594 počíta aj blízkosť: obe absolútne súradnicové odchýlky musia byť menšie než 0x41, teda 65 interných jednotiek. Jedna bunka má 64 jednotiek. Režim +0x16 s hodnotou 0 vracia blízky výsledok; hodnoty 1 a 2 v tejto vetve vracajú LOS výsledok. Správanie ďalších hodnôt zatiaľ nie je pomenované.

Tento kód dokazuje zrakový test cez geometriu a blokujúce bunky. Kompletný model sluchu alebo reakcie na zvuk sa nepodarilo potvrdiť.

### Stratégie

- Stratégia 1 pri HP pod 0x7F volá FUN_1010_1394. Tá prechádza 22-bajtové záznamy na adrese 0x9DD6 (door tabuľka), počíta vzdialenosť v mapových bunkách, odmieta ciele bez LOS a vyberá najbližší viditeľný záznam. Potom strážcu pošle pohybovou vetvou k tomuto cieľu. Presný dizajnový zámer tejto stratégie ostáva neistý; jej bezprostredný cieľ je najbližší viditeľný door záznam.
- Stratégia 2 nastaví náhodné čakanie 8–15 krokov a potom pokračuje pohybovou vetvou.
- Stratégia 3 má osobitnú vetvu zo stavu 7. FUN_1010_7a06 nastaví náhodné čakanie 8–87 krokov a bočné/čelné posuny podľa facing smeru.
- Stratégia 0 používa všeobecný výber smeru podľa polohy hráča a uložených výsledkov percepcie. Jej úplné pravidlá pre všetky typy strážcov ešte treba rozobrať.

### Doplnenie: strategy-3 pohyb a reakcia na zásah

Win16 1.10 stav 7 po úspešnom výsledku perception predicate prechádza do stavu 0x13, ak má strážca stratégiu 3. **Oprava a doplnenie 24. 9. 2026:** ide o výstup chrliča triedy `0x12/0x13` z ONE_SHOT stenového obrazu. `7A06` nastaví `rand()%80+8` a smerový pohyb. `7A44` pri novej hodnote časovača 8 volá `4:3876` (vyhľadanie wall class 7 podľa bunky a smeru) a `4:392C` (wall frame 0→1), nie zvukový helper. Pohybové pokusy prebiehajú pri nových hodnotách 7…0, teda osemkrát; pri všetkých úspešných krokoch je posun 64 world units, celá bunka. Blokovanie cieľovým objektom/hráčom nezastaví odpočet. Pri starom časovači 0 sa stratégia vymaže a nastaví stav 2. Hraničný prípad: počiatočný timer 8 sa zníži na 7 a stenový trigger v tejto vetve preskočí. Priame NE bajty a relocations opravujú starší opis „sedem krokov/56 jednotiek/zvuková vetva“. Dodaný MAP má 65 chrličov týchto tried a všetky sú na ONE_SHOT stenách. Detaily a runtime hranice: `Nite3W_ONE_SHOT_SPECIAL1_analysis_2026-09-24.md`.

Pri damage reakcii kód odčíta HP a zapíše 8 do GUARD+0x12. Čítač smerového cache helpera na `3:6F1E` očakáva iba kľúč 0–7 a pri nezhode ho prepíše na `3:6F2F`; preto 8 funguje ako invalidácia cache, nie ako pain timer. Bežná vetva vyberie reakčnú sekvenciu cez triedovú tabuľku, nastaví jej počiatočný frame vo VEC, uloží pôvodný stav do +0x0C a prejde do stavu 0x15. Tento stav posúva frame až po posledný frame sekvencie, potom obnoví stav uložený v +0x0C. Stavy 3, 4 a 0x0B majú osobitnú damage vetvu a stratégia 4 môže návratom preskočiť bežný hit reaction.

Win16 1.8 má rovnaký dispatcher v FUN_1010_7ab2, strategy-3 entry v FUN_1010_7962 a pohyb/timer v FUN_1010_79a0. State-13 a state-15 prechody sa zhodujú s 1.10; surové movement bytes tu boli dekódované z dostupného 1.10 EXE. Ide o statické porovnanie, nie o runtime verifikáciu; DOS parity a class-to-animation väzba ostávajú otvorené. Podrobný rozpis je v `analysis/nite3w_guard_reaction_2026-09-23.md`.

### Poškodenie hráča pri kontakte

FUN_1010_a1ea počíta vzdialenosť medzi hráčom a strážcom cez celú odmocninu z dx²+dy² v mapových bunkách. Základ je 100 / vzdialenosť; pri vzdialenosti pod 1 použije 100. Trieda strážcu ho nahradí alebo upraví:

| Object class strážcu | Poškodenie pred obtiažnosťou |
|---:|---|
| 0x08 | náhodne 0–7 |
| 0x09–0x0A | náhodne 0–15 |
| 0x0B | štvrtina základu |
| 0x0C, 0x1D, 0x1E | základ |
| 0x11–0x14 | náhodne 0–31 |
| 0x16 | 33 pri podmienke level ≠ 3 a DAT_51A6 = 0; inak 100 |
| 0x19 | 100 |
| ostatné vetvy | polovica základu |

Nastavenie obtiažnosti DAT_1048_4C14 potom násobí poškodenie dvomi pri hodnote 2 alebo delí dvomi pri hodnote 0. Toto je guard-to-player kontaktné poškodenie. Projektilové aj hitscan poškodenie hráča na strážcu ide cez spoločný damage výpočet: `OBJECT+0x18` je projekčný screen row; odčíta sa DAT_53EE, násobí ôsmimi a pripočíta RNG remainder modulo 25 pred class/weapon vetvami. Hitscan kandidát má current-generation GUARD stamp; projectile collision taký stamp gate v kontrolovanom call path nemá, takže aktuálnosť `OBJECT+0x18` pri projektilovom zásahu je runtime otázka. DOS v2.0 číta rovnaký typ poľa a zdieľa damage aritmetiku; DOS writer/order nie je uzavretý.

## 2. Časovače a seqdef animácie

### Časová základňa

**Oprava z 24. 9. 2026, priamo overená v EXE Win16 1.3/1.6/1.8/1.10:** FUN_1010_d6c6 v 1.10 číta GetTickCount/timeGetTime. Slow helper D70A používa ((uint32(ms)<<3) modulo 2^32)/1000 a pri zmene bucketu zvýši logický counter len raz. V bežnej vetve mode 0 tak D9C6 volá D974 nominálne 8-krát/s, bez dobiehania zmeškaných bucketov. Frame/pohyb používa samostatný kalibrovaný counter D74A; pri nenulovom mode sa slow update volá na nepárnej render generácii. D7D0 meria päť render/present behov D7C0, nie päť AI update-ov. Do 53F2 uloží surový priemer PRED obmedzením lokálnej efektívnej hodnoty na minimum 40 ms; samotné 53F2 sa späť na 40 neprepíše. Adresy ostatných verzií a bajtové dôkazy: Nitemare3D_Win16_all_available_versions_audit_2026-09-24.md. Runtime potvrdenie nebolo vykonané.

Dôsledok: GUARD časovače a weapon cooldowny sú počítané v simulačných krokoch. Animácie s termínom GetTickCount používajú milisekundy.

DOS v2.0 FUN_1000_241e porovnáva aktuálny 32-bitový čas na 0x81E/0x820 s termínom v zázname +8/+10. Po termíne vykoná presne jeden krok snímky a nastaví nový termín na aktuálny čas + seqdef interval. Pri oneskorení nespustí dobiehaciu slučku. DOS FUN_1000_bdf8 používa čas BIOS ticku ×0x37 (približne 55 ms), alebo DOS čas v sekundách a milisekundách; preto je jeho presnosť podľa zdroja času odlišná.

### Win16 seqdef mechanika

### IMG adresáre a banky seqdef

Win16 1.10 číta dva 0x400-bajtové adresáre: 256 wall offsetov od `0x0000`, 256 object offsetov od `0x0400`. Za nimi ležia obe SEQDEF banky: low/wall `0x0800 + 90*id`, high/object `0x6200 + 90*id`; frame dáta začínajú na `0xBC00`. Tento výpočet potvrdzuje Win16 1.8 aj DOS v2.0. Oprava staršieho auditu: výraz `+'\b'` v dekompilovanom kóde zvyšuje horný bajt selectoru o `0x08`; low bank preto neprekrýva adresáre a offset nie je `8+90*id`.

Všetky 512 selectorov v každom z troch dodaných IMG sú uložené v úplnom inventári. Každý nenulový image offset bol parsovaný cez jeho SEQDEF frame count a overený proti ďalšiemu unikátnemu streamu; nulové streamy, aliasy, rozmery a payloady sú zachované samostatne. Všetky streamy prešli bez chyby a dekódovaný frame count sa rovná byte `+2`.

90 B SEQDEF: `+0` u16 interval; `+2` frame count; `+3` extension flag; `+4..+33` tri 8-word facing/phase tabuľky; `+34/+36/+38` state 2/3/4 slová; `+3A..+47` a `+4A..+57` dve sedem-word alternate tabuľky; `+49` a `+59` selector-7 shortcut flagy. `+48` a `+58` nemajú v C exporte priamy nájdený reader. Loader rozšírené recordy kopíruje, runtime čítače volia facing/state/alternate hodnoty a updater posúva snímku. Detail poľa a validačný inventár: `Nitemare3D_save_animation_closure_2026-09-23.md` a `Nitemare3D_IMG_SEQDEF_frame_inventory_2026-09-23.csv`.

Frame stream je 10 B disk header + `width*height` pixelov. Počty všetkých sekvenčných snímok sú potvrdené naprieč IMG. `DAT_4746` ide priamo do ms deadline; updater vykoná najviac jeden frame krok na expiráciu, state 1 loopuje a state 2 je one-shot cesta. Presná EXE/epizóda väzba a runtime výber každej alternatívy zostávajú otvorené.
## 3. Projektily, zbrane a hazardy

### Zbrane a streľba

OBJECTS dáta označujú ID 0x25 plasma bolt, 0x26 wand, 0x27 pistol a 0x28 multi-bolt plasma. FUN_1010_aae6 nastaví index 2 ako hitscan režim; indexy 0, 1 a 3 používajú projektily. V poradí ide o jednu plazmovú strelu, spell-stars z wandu, hitscan z pištole a viacnásobnú plazmovú strelu.

Streľba sa bráni bez munície. FUN_1010_a97c znižuje príslušný ammo counter pri pokuse o výstrel. Tabuľka na DS offsete 0x1F6 obsahuje prahy [2, 1, 3, 1] slow krokov pre weapon index 0–3; vlastný saturujúci counter je na 0x1FA. Index 3 má v bráne streľby osobitnú výnimku, ktorá mu umožňuje opakovanú streľbu pri držaní vstupu. Oprava 24. 9. 2026: counter 01FA zvyšuje pomalý update D974; v bežnom mode 0 je jeho nominálne tempo 8 Hz, nezávislé od raw DAT_53F2. Prahy teda zodpovedajú nominálnym 250/125/375/125 ms, no fáza vstupu, ammo/pool a zbraňová animácia môžu zmeniť reálnu kadenciu. Nejde o odmerané intervaly výstrelov.

### Projektilový runtime

FUN_1010_9aac vyberie jeden z ôsmich slotov. Každý záznam má 42 bajtov; pool je priamo zapísaný do USER.SAV. Sekvenčné indexy v FUN_1010_a930/FUN_1010_a956 vyberajú pre wand skupinu flying/exploding spell-star animácií a pre ostatné projektilové zbrane skupinu plasma animácií.

FUN_1010_9d30 integruje pohyb v podkrokoch DAT_1048_53FA a pri každom kroku volá FUN_1010_9b64. Pri kolízii sa zmení aktívny záznam na nárazový stav a vyberie sa impact sekvencia. Guard hit-test používa absolútne rozdiely súradníc najviac 9 a menej než 10 interných jednotiek. Pri prekročení 20 jednotiek na jednej osi od polohy hráča sa slot uvoľní. Ide o herné súradnice; prevod na metre alebo presnú sekundu nie je doložený.

Kolízny kód rozpozná dynamické objekty a guard záznamy. Stena s príznakom 0x10 pre explóziu spustí zvukovú udalosť 0x29, vyhľadá wall objekt v bunke a nastaví jeho explóznu sekvenciu a časovanie. Presný význam jednotlivých grafických variantov a damage pre každý wall/object typ ostáva otvorený.

### Oheň: poškodenie potvrdené v bajtoch

Win16 inicializované DS dáta obsahujú na offsete 0x1FC bajty 0x64, 0x0A, 0x02. FUN_1010_be62 vyberie object class 7 a indexuje túto tabuľku podľa poradia CAUSTIC assetov. OBJECTS súbor dáva poradie 0x3B veľký, 0x3C stredný, 0x3D malý:

| Object ID | Asset | Poškodenie |
|---:|---|---:|
| 0x3B | veľký oheň | 100 HP na simulačný update |
| 0x3C | stredný oheň | 10 HP na simulačný update |
| 0x3D | malý oheň | 2 HP na simulačný update |

Update prebehne v FUN_1010_d974, ak hráč nie je v príslušnom invulnerable stave. Pri 100 HP je veľký oheň smrteľný v jednom prijatom damage update. Oprava 24. 9. 2026: v bežnom mode 0 ide nominálne o 8 slow update-ov/s, nie o 1000 / DAT_53F2. Odvodené tempo stredného/malého ohňa je pri plynulom plánovaní 80/16 HP/s. Vynechané buckety sa nedobiehajú a nenulový mode má inú vetvu, preto tieto hodnoty nie sú univerzálnym runtime meraním.

## 4. Wall a object triedy

Overil som surový MAP súbor: 2-bajtový počet levelov, dve 256-bajtové class mapy a 11 máp po 0x2000 bajtov; súčet 90 626 bajtov. Číselnú triedu z hlavičky som spojil s ID a názvom z WALLS/OBJECTS dát. Každá tabuľka obsahuje 39 rôznych bajtových hodnôt vrátane nuly; v dodanom MAP sa nepoužívajú wall triedy 0x03–0x06. Toto tvrdenie platí pre tento 11-level súbor.

### Wall triedy, ktoré riadia špeciálne správanie

| Wall class | Názov v dátach | Reálne wall ID |
|---:|---|---|
| 0x02 | REVWALL | 15 panelových ID, párované skryté steny |
| 0x07 | ONE_SHOT | 0x54 a 0x55, miznúce chrliče |
| 0x08 | SPECIAL1 | 0x12 poistková skrinka; 0x56 meniaca sa tabuľa |
| 0x09–0x0A | LEVEL_UP / LEVEL_UP2 | 0x9F a 0xA0 |
| 0x0D–0x24 | WARP a keyed/portal varianty | schody, dvere s kľúčmi, zrkadlá a prechody |
| 0x2D | WALL_EX | 0xFF generická explodovateľná stena |
| 0x2E | WALL_EX1 | 0x53 explodovateľné dvere; 0x5B cieľ; 0xFE živý plot |
| 0x30–0x34, 0x39–0x3A | jamb, vertikálne/horizontálne dvere, zamknuté a transportné dvere | priame kódy v WALLS dátach |
| 0x3F–0x40 | DOORVC / DOORHC | závesy/dverové závesy |
| 0x41–0x43 | TURN / RETREAT / FLEE | smerovníky pre strážcov |
| 0x44–0x45 | FLOOR / SAFESPOT | podlahové značky a kombinácie trezorov |
| 0x46 | ACTIONSPOT | 0xB7 označí tancujúcich strážcov v leveli 9 |
| 0x47–0x48 | TRIGGER1 / TRIGGER2 | 0xB8 a 0xB9 |

ONE_SHOT a SPECIAL1 sú pevne priradené k mapovým tile ID. SPECIAL1 wall 0x12 na E1 level index 6 je staticky trasovaný ako poistková skrinka, ktorá po dark evente obnoví svetlo. Wall 0x56 je podľa WALLS „Morphing chalkboard“; jeho E1 level-index 1 vetva mení per-wall interval sekvencie a prehráva SFX 0x44, ale viditeľný výsledok nie je uzavretý. Doplnenie 24. 9. uzatvára ONE_SHOT trigger/frame tok a SPECIAL1 dispatch: E1M9 nemá USE vetvu, tabuľa E1M2 loopuje pri 150 ms; jej cache interval má osobitnú LOAD otázku. Pozri nový report.

### Object triedy

| Object class | Použitie potvrdené v OBJECTS dátach |
|---:|---|
| 0x03 | SECRET panel, ID 0x62 |
| 0x04 | IMPACT efekt projektilu, ID 0x61 |
| 0x05 | MISSILE: ID 0xFB/0xFC plasma fly/impact; 0xFD/0xFE spell-star fly/impact |
| 0x07 | CAUSTIC oheň, ID 0x3B–0x3D |
| 0x08–0x21 | rodiny strážcov; class 0x21 je GUARD26 Dancers, ID 0x8C |
| 0x26–0x2B | SAFE, TRUNK, PUSH, ACTION rádio, PERMEABLE, DUMB |
| 0x2E | ELEVATED predmety pri strope |
| 0x2F–0x3E | kľúče, karty, jedlo, zbrane, munícia, magické predmety a scroll/UI objekty |

Secret panel class 0x03 má aj runtime štruktúru: FUN_1010_16d6 prehľadá mapu, vytvorí panelový záznam a priradí až štyri priľahlé door/wall záznamy. FUN_1010_1a22 pri aktivácii mení ich posun/otvorenie a prehrá zvuk 0x27. Najviac 32 per-panel bajtov na offsete +0x14 sa samostatne ukladá v save súbore. To prepája názov SECRET, panelovú logiku a samostatný 32-bajtový USER.SAV blok.

Wall class a object class sú odlišné indexové priestory. Napríklad wall class 0x07 znamená ONE_SHOT; object class 0x07 znamená CAUSTIC oheň.

## 5. USER.SAV: rozloženie anonymných blokov

Win16 zapisovač FUN_1010_5466 a načítavač FUN_1010_574c súhlasne používajú slot s dĺžkou 0xD6E7 bajtov. Nasledujúce adresy sú offsety v jednom slote; rozsahy končia bajt pred ďalším riadkom.

| Offset | Veľkosť | Nové pomenovanie / dôkaz |
|---:|---:|---|
| 0x0000 | 4 | sentinel dĺžky slotu: 0xD6E7 |
| 0x0004 | 0x29 | 41-bajtová hlavička; zapisovaná z parametra slotu |
| 0x002D | 2 + 2 + 4 | DAT_7E52, DAT_7E54 a 32-bitový čas |
| 0x0035 | 0x2000 | aktuálna 64×64 mapa |
| 0x2035 | 0x5E | 94 bajtov od DAT_4BE8; zmiešaný hráčsky/herne stav |
| 0x2093 | 28 000 | 1000 × 28-bajtové VEC záznamy |
| 0x8DF3 | 9 800 | 350 × 28-bajtové object záznamy |
| 0xB43B | 2 600 | 100 × 26-bajtové guard záznamy |
| 0xBE63 | 1 408 | 64 × 22-bajtové door záznamy |
| 0xC3E3 | 32 | aktivácia každého z až 32 SECRET panelov; kópia poľa +0x14 |
| 0xC403 | 336 | 8 × 42-bajtové projektilové záznamy |
| 0xC553 | 8 | DAT_51A4 až DAT_51AB, globálne flagy |
| 0xC55B | 72 | 12 × 6-bajtové push záznamy |
| 0xC5A3 | 4 096 | 64×64-bajtová automap raster/index plocha |
| 0xD5A3 | 64 | DAT_A65E: saved one-shot guard wake cache, keyed by nonzero class-D wall selector |
| 0xD5E3 | 256 | DAT_8094: farebná remap lookup tabuľka |
| 0xD6E3 | 1 | DAT_7E62 |
| 0xD6E4 | 1 | DAT_7E63 |
| 0xD6E5 | 2 | DAT_7E60, render/shade parameter |

Potvrdené detaily anonymných dát:

- Panelový blok 0xC3E3 je samostatný od 64 door záznamov pred ním. Zapisovač kopíruje presne +0x14 z každého panelového recordu a načítavač bajt vracia.
- Projektile blok 0xC403 je presne 0x150 bajtov, rovnaký rozsah ako osem runtime slotov po 42 bajtov.
- Automap blok 0xC5A3 je 4096-bajtová 64×64 plocha; FUN_1010_b1a4 ju kreslí, maže, upravuje aktuálnu pozíciu a značky guardov. Zostáva rozlúštiť význam všetkých hodnôt a farieb tejto plochy.
- DAT_A65E je one-shot gate podľa posledného selectoru steny triedy DOOR: prvý úspešný výstrel pre nenulový selector označí príslušný bajt a môže prebudiť strážcov stratégie 0 v stave 7/8 s rovnakým selectorom. Timer je rand()%8 a nový stav 1; slučka nefiltruje vzdialenosť ani LOS. Selector je odvodený od wall ID, nie od bunky či podlažia.
- DAT_8094 je pixelová farebná remap tabuľka používaná rendererom; jej 256 bajtov sa ukladá.
- DAT_51A4 je bitová maska stavu `SECRET` panela a jeho prepojenej skupiny wall entít; dodané mapy používajú kanál 0. DAT_51A5 prepína časovanú útočnú vetvu AI `Cannon`. DAT_51A6–51AA majú v Win16 1.10 zmapované priame event callsite-y: A6/A7 sú one-shot brány, A8 sa číta v Escape vetve a A9/AA nemajú nájdeného priameho funkčného readera. DAT_51AB vplýva na farebný/shade režim.
- 94-bajtový blok od DAT_4BE8 je staticky rozmapovaný po offsetoch vrátane HUD, ammo, key, charge a pohybových polí; úplná tabuľka a residual unknowns sú v `Nitemare3D_save_animation_closure_2026-09-23.md`. Niekoľko bajtov nemá priamy C xref a vyžaduje raw disassembly/runtime save diff.

## Čo sa oplatí analyzovať ďalej

Najvyššiu hodnotu prinesú tieto konkrétne kroky:

1. Spárovať tri staticky parsované IMG súbory s presnými EXE/epizóda/MAP buildmi a dynamicky zaznamenať facing/state/alternate/selector-7 voľbu pre reprezentatívne wall/object/guard sekvencie.
2. Pri `DAT_A65E` overiť runtime reakciu a zámer zoskupovania podľa wall ID; statický selector, reset a save/load tok sú teraz zmapované. Pri `51A9/51AA` sa v exporte nenašiel ďalší funkčný reader.
3. Zrekonštruovať triedovú a weapon damage cestu FUN_1010_9fa2 po jednom operandovi a porovnať výstup s FUN_1010_80f8. Samostatne rozobrať hitscan a osemslotový projektilový pool.
4. TRIGGER1/2, E1 level 7 poistková skrinka a časť E1 level 2 chalkboard cesty sú staticky zmapované nižšie. ONE_SHOT a SPECIAL1 boli ďalej staticky rozobrané 24. 9.; nasleduje runtime kontrola timeru 8, animácie mimo pohľadu, E1M9 USE a LOAD tabule podľa nového reportu.
5. Zostaviť úplnú tabuľku guard state × strategy × timer × animation × movement × sound a overiť ju vo Win16 1.8 a DOS 2.0.
6. Rozlíšiť kódové vetvy wall class 0x03–0x06 od object class 0x03–0x06. Dodaný MAP ich ako wall classes nepoužíva, no iné buildy alebo mapy ich môžu mať.
7. Po statickom dokončení urobiť riadený runtime trace niekoľkých situácií: guard zorný kužeľ, otvorené/zatvorené dvere, každý projektil, oheň na troch veľkostiach a save/load panelu.

## Podklady a obmedzenia

Analýza používa priamo dekompiláty nite3w110.exe.c, N3D-DOS-UNFULL-v20.exe.c a NITE3W18.EXE(1).c, plus aktuálne súbory IMG, MAP, WALLS a OBJECTS. Použité kľúčové funkcie: FUN_1010_4b86, FUN_1010_4c8a, FUN_1010_7494, FUN_1010_7594, FUN_1010_76fc, FUN_1010_7b56, FUN_1010_80aa, FUN_1010_80f8, FUN_1010_9aac, FUN_1010_9b64, FUN_1010_9d30, FUN_1010_9e20, FUN_1010_a1ea, FUN_1010_be62, FUN_1010_5466, FUN_1010_574c a DOS FUN_1000_241e.

Výsledok je ďalší krok k pochopeniu logiky, nie dôkaz úplného správania každého z 1 486 funkčných blokov. Neznáme miesta sú v texte pomenované podľa toho, čo treba zmerať alebo sledovať ďalej.

## 6. TODO resolution pass — USER.SAV flagy a farebné bajty

**Rozsah tohto doplnenia:** statická kontrola Win16 1.10 exportu `nite3w110.exe.c`. Toto doplnenie nemení DOS závery. Hodnoty pri globálnych premenných sú priame operácie v kóde; príbehový názov udalosti zostáva otvorený, ak ho kód nedokazuje.

### Uzavreté alebo spresnené položky

| Premenná / rozsah | Nové potvrdené správanie | Zostávajúca hranica |
|---|---|---|
| `DAT_1048_7E62` | Bajt farby používaný pri vyplnení jednej plochy framebufferu. `FUN_1010_c5e2` nastaví predvolene `0x0C`; pri `DAT_1048_51AB != 0` nastaví `0`. `FUN_1010_3612` rozšíri jeho hodnotu na oba bajty 16-bitového zápisu. | Presné pomenovanie kreslenej plochy a všetci používatelia mimo tejto fill cesty. |
| `DAT_1048_7E63` | Druhý fill-color bajt; predvolene `0x11`, v tmavom stave `0`. V `FUN_1010_3612` vypĺňa prvú oblasť pred druhou oblasťou `7E62`. | Presný názov grafickej oblasti nie je dokázaný. |
| `DAT_1048_7E60` | Index úrovne stmavenia. `FUN_1010_29be` indexuje tabuľku `[0,4,8,12,16,20,30,40]`; následne násobí vybranú hodnotu štyrmi pri odčítaní RGB kanálov. Predvolený index je `2`, špeciálny tmavý stav používa `6`. | `DAT_1048_4698` sa kopíruje ako voľba, keď je nezáporná. Úplná validácia rozsahu načítanej/zadanej hodnoty stále nie je potvrdená; index mimo 0–7 by prekročil tabuľku. |
| `DAT_1048_4698`, `469A`, `469C` | `FUN_1010_0e9e` ich inicializuje na `0xFFFF`; `FUN_1010_c5e2` potom pri záporných hodnotách používa defaulty shade index `2` a fill bajty `0x0C/0x11`. | V exporte sa nenašiel iný priamy zapisovateľ. Zdroj prípadného nenulového override a jeho prípustné hodnoty by vyžadovali nepriamych/raw XREF alebo runtime overenie. |
| `DAT_1048_51A5` | Inicializuje sa na `1`; panelové príkazy `0x20/0x21` ju preklápajú XOR-om s `1`. AI triedy `0x19` (`Cannon`, object IDs `0xCC–0xCF`) používa stavy `0x0E/0x0F`; pri `1` pokračuje do časovanej vetvy a po perception teste môže zaútočiť cez `FUN_1010_8c0a`, pri `0` sa vracia do čakacej vetvy. | Runtime kadencia, SFX/rendering výsledok a cross-build potvrdenie. |
| `DAT_1048_51AB` | Pri udalosti Episode 1, level index `6`, marker `G`, sa nastaví na `1`. `FUN_1010_c5e2` prepne shade index na `6`, oba framebuffer fill bajty na `0` a prepočíta farebnú remap tabuľku. Kým je flag aktívny, zdieľaný door-state helper `FUN_1010_188a` hneď vracia bez svojich bežných zmien. Vetva `FUN_1010_c0a2` po `51A6==1` nastaví `51A6=2`, vynuluje `51AB` a obnoví predvolenú alebo konfigurovanú shade/fill cestu. | Ľudsky čitateľný text udalosti a jej presná dĺžka/časovanie treba potvrdiť v hre. Level index `6` je siedmy level pri číslovaní od 1. |
| `DAT_1048_51A6` | Inicializuje sa na `0`; funguje ako viacfázový latch `0→1→2` v Episode 1 level index `6`. Ten istý bajt bráni opakovaniu viacerých levelových udalostí. V damage vetve entity class `0x16` ovplyvňuje poškodenie. | Je to zdieľaný, pri vstupe do levelu nulovaný event/progres stav, nie jeden globálny príbehový bit. Callsite-y sú rozpísané nižšie; presné texty a runtime priebeh ostávajú otvorené. |
| `DAT_1048_51A4` | Osem bajtov `51A4–51AB` sa serializuje spolu. `51A4` je bitová maska stavu `SECRET` panela: jeho index sa uloží v `DAT_40F8`, ten istý bit riadi menu `0x1E/0x1F` a v týchto príkazoch sa nastavuje/maže po zmene zodpovedajúcich wall entít. V aktuálnych mapách je index panela `0`, teda používa sa bit 0. | Runtime význam výsledného vzhľadu/stavu cieľových stien a prípadné ďalšie kanály v iných dátových balíkoch. Safe/combo objekty sú samostatná vetva. |
| `DAT_1048_51A7`, `51A8` | `51A7` je one-shot brána pre marker `H` na Episode 1, level index `9`. `51A8` sa nastaví pri marker-i `G` na tom istom leveli; Escape handler ju skutočne číta. | Pôvodný text udalostí ostáva nerozparsovaný. |
| `DAT_1048_51A9`, `51AA` | `51A9` sa nastaví po časovanej udalosti Episode 2, level index `9`; `51AA` pri spracovaní záznamu s class `0x16` vo vetve `FUN_1010_a0ee`. | Okrem serializácie nebol nájdený priamy funkčný reader. Uloženie je potvrdené, no funkčný účel po zápise nie. |

### Druhá skupina vyriešená staticky: eventy a flagy `51A6–51AA`

**Spúšťací reťazec pre mapové značky:** `FUN_1010_84f4` kontroluje vlastnosti dvoch buniek v `DAT_1048_7E94`. Ak má bunka bit `0x40`, zavolá `FUN_1010_bfd8` s indexom danej bunky. Dispatcher číta jej marker z mapy (`DAT_1048_8196[cell]`) a vetví podľa epizódy, level indexu a znaku `G/H`. Ide o mapovú/collision cestu; samotný marker ešte neodhaľuje pôvodný názov udalosti.

`FUN_1010_0ef6` vynuluje `51A6–51AA` (zároveň `51A4` a `51AB`) a nastaví `51A5=1`. Volá sa pri level setup-e `FUN_1018_09f2` a pri ďalších prechodoch/setup vetvách. Preto ide o hodnoty s resetom pri inicializácii levelu, nie o monotónny progres platný bez resetu cez celú hru. Zapisovač `FUN_1010_5466` a načítavač `FUN_1010_574c` ukladajú/obnovujú súvislý 8-bajtový blok `51A4–51AB` v USER.SAV; reset pri level setup-e treba odlišovať od save/load obnovy.

**Číselný účinok dark eventu:** `FUN_1010_c5e2` pri `51AB=1` nastaví `DAT_7E60=6`, `DAT_7E62=0` a `DAT_7E63=0`, potom zavolá `FUN_1010_29be`. Tá používa odtiene `[0,4,8,12,16,20,30,40]`; index `6` teda dáva zníženie `30×4=120` na každý RGB kanál pred orezaním na nulu a výberom najbližšej dostupnej farby do remap tabuľky. Po inicializácii `FUN_1010_0e9e` je bežný default index `2`, ktorý odpočítava `8×4=32`; blackout preto zvyšuje odpočet o ďalších `88` na kanál oproti defaultu. V exporte sa nenašli iné priame zápisy do `4698/469A/469C` než nastavenie `0xFFFF`, takže override nie je potvrdený. Súčasne `DAT_7E62/63=0` nastaví obe framebuffer fill oblasti na farbu `0`.

Flag má aj nefarebný efekt. `FUN_1010_188a` kontroluje `51AB` hneď pri vstupe a pri nenulovej hodnote vracia pred zmenou stavu wall-pair záznamov. Táto spoločná rutina sa volá z interakčnej vetvy, z pohybovej/AI cesty a z príkazov `0x1E/0x1F` pre steny ovládané cez `SECRET` panel. Kód teda potvrdzuje, že počas dark fázy tieto callsite-y neprevedú steny cez bežnú state rutinu. `FUN_1010_66b0` zároveň prestane nahrádzať shade index nulou pre vybrané aktívne object stavy, takže tieto objekty dostanú dark shade. Tieto účinky vyplývajú zo statického toku; presný obraz a dĺžka udalosti zostávajú na runtime overenie.

### `51A4`: bitová maska `SECRET` panela

`DAT_1048_51A4` nie je safe/combo progres. V `FUN_1010_1a22` ide objekt s class byte `3` do `FUN_1018_21d8`; tá preberá jeho class-relative byte `+1` do `DAT_1048_40F8`. Objekt z tabuľky `MAP(8).1` s class `3` je ID `0x62` (`SECRET`, Secret panel). `FUN_1010_d1a2` zostavuje object record tak, že byte `+1` je rozdiel medzi ID objektu a prvým ID s rovnakou triedou (`FUN_1010_2398`). V dodanej tabuľke je `0x62` jediným ID triedy `3`, preto panel nastavuje `DAT_40F8=0`. Všetkých 11 máp obsahuje tento objekt; zo zdrojových máp je priamo doložený bit 0, nie samostatné bity pre každý panel.

| Class byte v mapovej tabuľke | Object ID a označenie v `OBJECTS(10).1` | Class-relative byte `+1` | Význam pre `51A4` |
|---:|---|---:|---|
| `0x03` | `0x62` — `SECRET`, Secret panel | `0` | Zdroj `DAT_40F8`; vyžaduje credential bit 0 z `DAT_4C29`. |
| `0x3B` | `0x19` — `MAGICEYE`, Magic eye | `0` | Trieda cieľových wall-pair záznamov; zodpovedá kanálu 0. |
| `0x3C` | `0x1F–0x22` — `PENTAGRAM`, štyri farebné varianty | `0–3` | Druhá cieľová trieda; na kanál 0 sedí prvý variant `0x1F`. |
| `0x26` | `0xD2–0xD7` — `SAFE`, šesť safe variantov | `0–5` | Samostatná kombináciová vetva (`FUN_1010_ad9e`), nie `51A4`. |

`DAT_4C29` sa pri class `0x30` (ID card) nastavuje bitom `1 << object_record[+1]`. Objektové ID `0x09` a `0x0A` sú v mapovej tabuľke triedy `0x30`, s indexmi `0` a `1`; `OBJECTS(10).1` ich označuje ako červenú a žltú ID kartu. Panel s indexom `0` preto kontroluje bit 0, teda červenú kartu. Pri chýbajúcom bite `FUN_1010_bcea(0)` zobrazí požiadavku na credential; pri splnenom bite sa pripraví menu.

`FUN_1018_2146` používa bit `1 << DAT_40F8` na nastavenie stavov menu pre príkazy `0x1E/0x1F`. Ich handler `FUN_1018_27de` prejde najviac 64 wall-pair záznamov, vyberie class `0x3B/0x3C` záznamy s rovnakým byte `+1` a stavom `1/3` (príkaz `0x1E`) alebo `0/2` (príkaz `0x1F`), nastaví príznak záznamu a zavolá `FUN_1010_188a`. Potom preklopí/aktualizuje bit `51A4`. To dokazuje class, index, credential gate a riadiacu väzbu; názov príkazov ako „otvor“/„zatvor“ a ich presný viditeľný výsledok nechávam otvorené, kým sa neoveria v runtime.

`SAFE` je oddelené: object IDs `0xD2–0xD7` majú mapovú class `0x26` (`&`) a dispatcher ich posiela do `FUN_1010_ad9e`, kde sa spracúva kombinácia. Pôvodný „safe/combo“ výklad `51A4` sa tým vyvracia. `51A4` má kapacitu 8 bitov; generický kód maskuje index cez `& 0x1F`, ale dostupný mapový class byte `3` dáva index `0` a zapisuje sa iba bit 0 cez túto cestu.

### `51A5`: povolenie útočnej vetvy Cannon AI

`DAT_1048_51A5` a `DAT_1048_51A4` sa menia z toho istého menu pripraveného cez `FUN_1018_21d8`; menu riadky s kódmi `0x20/0x21` zobrazujú aktuálny stav `51A5`. Handler `FUN_1018_27de` pri oboch príkazoch vykoná `51A5 ^= 1` a vráti ovládanie do hry. `FUN_1010_0ef6` ho pri level setup-e nastavuje na `1`.

Mapová object-class tabuľka priraďuje class `0x19` objektom `0xCC–0xCF`; `OBJECTS(10).1` ich označuje ako `GUARD18 Cannon N/E/S/W`. `FUN_1010_b02c` pre class `0x19` vyberá stratégiu `4` a stav `0x0E`; ak sú uložené bočné/čelné posuny nenulové, neskoršia spoločná kontrola presmeruje záznam do stavu `0x08`. Preto flag riadi Cannon záznamy, ktoré vstupujú do dvojice stavov `0x0E/0x0F`, nie nevyhnutne ich prvý frame po spawn-e. V `FUN_1010_7b56` stav `0x0E` prejde do `0x0F` iba pri nenulovom `51A5`; stav `0x0F` sa pri nule vracia do `0x0E`. Pri zapnutom flagu časovač vedie do stavu `0x10`, ktorý po úspešnom teste `FUN_1010_7594` zavolá `FUN_1010_8c0a` a potom naplánuje ďalší prechod cez 8 simulačných krokov. `FUN_1010_8c0a` odpočíta vypočítané poškodenie od HP hráča; pri prechode sa tiež môže vyvolať class-dependent SFX helper.

Staticky je teda `51A5` Cannon attack-enable prepínač dostupný v tom istom credential-gated panelovom menu ako `51A4`. Presné trvanie medzi útokmi a ich viditeľný/auditívny prejav treba zmerať v runtime.

`DAT_1048_51A4` sa resetuje na `0` vo `FUN_1010_0ef6` a uloží/obnoví sa spolu s bajtmi `51A5–51AB` vo `FUN_1010_5466`/`FUN_1010_574c`. `DAT_40F8` je pracovný selector znovu odvodený pri interakcii; save obsahuje stavový bit, nie samostatný selector. Tieto závery sú pre dodané Win16 1.10 kódové a mapové dáta; správanie iných episode balíkov a runtime animácia ešte nie sú overené.

| Flag | Potvrdená udalosť alebo podmienka | Čítania a dôsledok |
|---|---|---|
| `51A6` | Episode 1, index `6`, marker `G`: `FUN_1010_bef4` pri hodnote `0` vykoná event helper, nastaví `51A6=1`, `51AB=1`, obnoví shade režim/časovanie a odošle textový záznam `DAT_016E`. Episode 1, index `9`, `G`: `FUN_1010_bf20` prehrá udalosť `0x12`, nastaví `51A6=1`, `51A8=1`, `DAT_4BE8=1`, `DAT_4BE5=0` a odošle `DAT_0182/0186/018A`. Ďalšie one-shot markery: Episode 2, index `9`, `G` → `DAT_01C6`; Episode 3, index `0`, `G` → `DAT_01D2`; Episode 3, index `9`, `G` → `DAT_019A`. | Každý z týchto callsite-ov testuje `51A6==0`, takže bráni opakovaniu v rámci aktuálneho levelu. V Episode 1, index `6`, dispatcher typu `8` volá `FUN_1010_c0a2`: pri `51A6==1` prejde na `2`, vynuluje `51AB` a odošle `DAT_0172`; inak odošle `DAT_0176`. Damage výpočet class `0x16`: pri epizóde inej než 3 a `51A6==0` použije `33` HP; inak `100` HP pred modifikátorom obtiažnosti. |
| `51A7` | Episode 1, index `9`, marker `H`: `FUN_1010_bf70` pri hodnote `0` nastaví `1` a odošle `DAT_018E`. | Jediný nájdený reader je táto one-shot brána. |
| `51A8` | Episode 1, index `9`, marker `G`: nastaví sa v `FUN_1010_bf20` spolu s `51A6`. | Escape handler ju číta, keď `DAT_46B6==7`: ak `51A8==0` alebo hráčske HP `DAT_4C1D` nie je nula, ide cez `FUN_1010_e2fa` a `FUN_1018_2f6c`; inak zobrazí špeciálnu vetvu `FUN_1018_0ab0(10)`. Je teda funkčne čítaná, nie iba uložená. |
| `51A9` | Episode 2, index `9`: `FUN_1010_c356` vedie do `FUN_1010_c2b8`, ktorá pri každom 20. čítači `DAT_0202` vykoná časovanú sekvenciu, odošle `DAT_01CA/01CE`, nastaví `DAT_46B4=3` a nakoniec `51A9=1`. Cesta sa aktivuje z `FUN_1010_9b64` pri vlastnosti `0x40` v druhej (object-property) tabuľke `DAT_7F94`. | Priamy funkčný reader okrem uloženia/obnovenia 8-bajtového bloku sa v C exporte nenašiel. Zápis nasleduje dokončenie sekvencie, preto je „completion latch“ vierohodný výklad, ale nie je dokázaný ďalším správaním. |
| `51AA` | `FUN_1010_a0ee`, volaná z guard AI stavu `9`, pri zázname s poľom class `+6 == 0x16` spustí udalosť `0x12`, odošle `DAT_0196`, nastaví `DAT_46B4=0` a `51AA=1`. | Priamy funkčný reader okrem uloženia/obnovenia 8-bajtového bloku sa v C exporte nenašiel. Kód dokazuje zápis pri tomto spracovaní entity, nie neskorší účinok flagu. |

**Čo je týmto uzavreté:** v Win16 1.10 sú známe všetky nájdené priame zapisovacie vetvy, epizóda/level/marker podmienky, priame funkčné čítania `51A6–51A8`, one-shot brány `51A6/51A7` a reset/save rozsah. `51A9/51AA` nemajú priameho funkčného readera v exporte; ich význam po zápise sa nedá dokázať bez iného build-u alebo runtime trace. Literály pre event pointery sú dekódované v §7; story interpretácia a runtime priebeh zostávajú otvorené.

### Cache 0xA65E — selector a prebudenie guardov

Funkcia FUN_1010_247A klasifikuje wall ID aktuálnej mapovej bunky tabuľkou DAT_1048_8196. Ak trieda je D, vráti wall ID mínus prvé ID triedy D; inak vráti -1. Pri zmene DAT_1048_7E52 prepočíta základ cez FUN_1010_2334(0x44,0), ktorá nájde prvú položku s triedou D. Raw ASM segmentu 3 na 0x247A potvrdzuje odovzdanie argumentu 0x44 a nulového počiatočného indexu. Dodané WALLS dáta začínajú triedu DOOR pri ID 0x70.

WALLS metadáta obsahujú 24 DOOR ID: 0x70–0x77, 0x79–0x80, 0x82–0x83, 0xA3–0xA6 a 0xAD–0xAE. Po odčítaní 0x70 vychádzajú riedke hodnoty 0–7, 9–16, 18–19, 51–54 a 61–62. Rozsah 64 bajtov je teda dostatočný pre dodané dáta, hoci FUN_1010_247A selector neorezáva a tento predpoklad treba preveriť v iných WALLS buildoch. Selector 0 zodpovedá wall ID 0x70, ale FUN_1010_7664(0) je no-op; selector 63 sa v dodanom WALLS nepoužíva. WARP_L*, WARP_S* a WARP_* nie sú class D.

FUN_1010_8A20 aktualizuje DAT_1048_4C1C podľa playerovej aktuálnej mapovej bunky len vtedy, keď je trieda D. Pohyb cez iné triedy starý selector nemaže. FUN_1010_71DC robí rovnaký zápis do guard record +0x0E po pohybe guardu; aj tam ne-dverová bunka hodnotu nemaže. Obe polia preto nesú posledný zaznamenaný DOOR wall selector, nie unikátnu pozíciu. Rovnaké porovnanie sa objaví v guard state 0x0F; pri zhode volá class-dependent helper FUN_1010_B5E4.

FUN_1010_7664 má tri vetvy:
- argument 0: návrat bez akcie;
- argument -1: vymazanie 16 dwordov, teda presne 64 bajtov od runtime 0xA65E;
- nenulový selector: adresa cache je 0xA65E + selector; ak bajt už nie je nula, rutina sa vráti. Inak ho nastaví na 1 a prejde aktívne guard záznamy.

Pri prvom nenulovom selector-e rutina zmení iba guardov so stratégiou +0x0A = 0, selectorom +0x0E zhodným s DAT_1048_4C1C a stavom +0x0B v {7,8}. Do časovača +0x06 zapíše rand()%8 a stav zmení na 1. Stav 1 odpočítava tento počet simulačných krokov pred stavom 2. Wake loop nemá test vzdialenosti ani LOS a cache bajt označí ešte pred skenovaním strážcov, takže neskorší výstrel s rovnakým selectorom guardov znovu neskenuje.

Win16 1.10 attack path FUN_1010_8B06 po úspešnej hitscan alebo projectile streľbe vloží DAT_1048_4C1C na stack a zavolá FUN_1010_7664; raw ASM na 0x8BED to potvrdzuje. Potom samostatne volá FUN_1010_B594 na výber a prehratie zvuku. Tento wake handler teda reaguje priamo na streľbu; zvuková vzdialenosť, útlm ani percepcia sa v tejto slučke nepočítajú. To nevylučuje iné zvukové cesty inde.

Win16 1.8 používa rovnaký mechanizmus pod menami FUN_1010_75C0 (cache), FUN_1010_8A62 (útok) a FUN_1010_242E (selector). Cache, filtre guardov aj náhodný timer 0–7 sa zhodujú.

USER.SAV+0xD5A3 obsahuje tých istých 64 bajtov, ktoré save writer/loader kopírujú z/na runtime 0xA65E. Level setup FUN_1018_09F2 cache vynuluje. Ak load cesta spustí level setup, FUN_1010_574C sa vykoná po ňom a obnoví bajty zo slotu; reader ich obnoví aj bez zmeny levelu. Nový level cache resetuje, pokračovanie zo save obnoví predchádzajúce markery.

Zostáva runtime potvrdiť zamýšľaný dôvod zoskupovania podľa wall ID, správanie selectoru 0 a to, či každá podporovaná WALLS tabuľka dodrží rozsah 0–63.

### Aktualizovaný zoznam zostávajúcich TODO

| Stav | TODO | Ďalší konkrétny dôkaz potrebný |
|---|---|---|
| STATIC HOTOVO / RUNTIME OPEN | `51A4` stavová maska `SECRET` panela | Win16 1.10: source selector `0`, credential bit 0, target class/index, menu príkazy a reset/save/load sú rozmapované vyššie. Runtime stav stien, presný text menu a cross-build/ďalšie episode dáta zostávajú otvorené. |
| STATIC HOTOVO / RUNTIME OPEN | `51A5` povolenie AI Cannon | Win16 1.10: init `1`, panelové príkazy `0x20/0x21`, trieda `0x19`, stavy `0x0E/0x0F/0x10`, perception gate a damage call sú rozmapované vyššie. Runtime kadencia a porovnanie buildov zostávajú otvorené. |
| STATIC HOTOVO / RUNTIME OPEN | `51A6–51AA` event flagy | Win16 1.10: callsite-y, priame C reader-y a texty triggerov `51A6–51A8` rozmapované nižšie. Zostáva potvrdiť runtime priebeh, porovnať DOS/Win16 1.8 a zistiť použitie `51A9/51AA` po zápise; ich neprítomnosť medzi priamymi reader-mi sama osebe nedokazuje, že sú nepoužívané. |
| STATIC HOTOVO / RUNTIME OPEN | TRIGGER1/TRIGGER2 v troch dodaných MAP/WALLS pároch | Názvy G/H, wall ID, polohy, dispatch `FUN_1010_BFD8`, event flagy aj texty Win16 1.10 sú rozmapované nižšie. Overiť, kedy pohybový scanner aktivuje bunku, prehratie textov a správanie v DOS/Win16 1.8. |
| PARTIAL / RUNTIME OPEN | SPECIAL1 `0x12` a `0x56` v E1 | Fuse box po dark evente je zmapovaný; chalkboard na indexe 1 mení cache interval cez prvú class-8 runtime entitu, ktorej bounds obsahujú bunku (entity[+4] je selector), na `0x96` a prehrá SFX `0x44`. Raw NE lookup je potvrdený; zmerať animáciu/časovú jednotku a vysvetliť druhú inštanciu na indexe 8. |
| STATIC HOTOVO / RUNTIME OPEN | `51AB` dark event | Spúšťač, reset, shade výpočet, nulové fill farby a blokovanie door-state helpera sú zmapované. Zmerať dĺžku a viditeľný výsledok v E1 level index 6; preveriť save/load uprostred fázy. |
| PARTIAL | `7E60/7E62/7E63` | Dark-event override a číselný shade výpočet sú potvrdené; `4698/469A/469C` majú len priamu inicializáciu na `0xFFFF` v C exporte. Ešte overiť prípadné nepriame/raw zapisovatele, rozsah uloženého `7E60` a pomenovať framebuffer oblasti `7E62/63`. |
| STATIC MAPA / RUNTIME OPEN | `0xA65E` guard wake cache | Selector, callsite, indexový rozsah v dodaných WALLS dátach, reset a save/load tok sú zmapované; overiť zámer grouping-u, selector 0 a všetky podporované WALLS buildy. |
| STATIC HOTOVO / RUNTIME OPEN | Párové wall/door pole `DS:9DD6` | Kapacita, stavy 0–3, auto-close 32/4 tickov, movement step a map-cell guard potvrdené staticky; writer stavu 4 a runtime obraz/SFX otvorené. |
| STATIC HOTOVO / RUNTIME OPEN | Pushable entity a sloty `DS:A616` | Pointer lookup, 8-krokový posun, podmienky blokovania a aktualizácia mapy zmapované; presné jednotky vektora/assets/runtime pocit otvorené. |
| PARTIAL / RUNTIME OPEN | Class-3 group-motion pole `DS:A356` | Štyri komponenty, phase 2 a cleanup bunky potvrdené; asset a viditeľný/gameplay význam neznámy. |
| STATICALLY CLOSED / RUNTIME OPEN | `OBJECT+0x12`, `OBJECT+0x18`, `GUARD+0x12` | Win16 1.10 reader/writer sites a význam sú zmapované v `Nite3W_OBJECT_GUARD_field_read_write_closure_2026-09-23.md`; zostáva impact-time freshness pre projektily, render/shot order, DOS parity a class overlays. |
| OPEN | ostatné polia OBJECT/GUARD/DOOR/PANEL/PUSH/VEC | Pokračovať v offsetovom reader/writer audite; zmeny v globálnych flagoch nenahrádzajú rozpis štruktúr. |
| STATICALLY CLOSED / RUNTIME OPEN | IMG/SEQDEF a tick | Obe banky, všetkých 90 B polí, stream hranice, aliasy, frame count a intervaly v troch IMG sú staticky overené; low bank je za adresármi. Otvorené: EXE–epizóda–IMG pairing, runtime selector/facing/alternate výber a kalibrácia 53F2/53FA. |
| OPEN | guard, combat a class skripty | Dokončiť state × strategy × timer × sound; zbrane/damage/hazardy a class `0x2D`; ONE_SHOT/SPECIAL1 statické doplnenie je v reporte z 24. 9., runtime overenie otvorené. |
| OPEN | renderer a DOS porovnanie | Pixelový test renderera; raw DOS potvrdenie cleanup-u wall class `0x2D` a oprava chybných funkčných hraníc. |

**Poznámka k istote:** priame priradenie fill bajtov, event podmienok a zápisov je potvrdené v exporte NITE3W 1.10. Príbehový význam názvov udalostí, runtime index cache a zhodné správanie DOS build-u z toho automaticky nevyplýva.

## 7. Win16 1.10 TRIGGER1/TRIGGER2 — dispatch, mapové polohy a texty

### Cesta od bunky po event

`FUN_1010_24BC` nastaví marker bit `0x40` pre wall image ID `G`/`H`. Pohybový/collision scanner `FUN_1010_84F4` kontroluje tento bit a volá `FUN_1010_BFD8`; handler prečíta image ID cez `DAT_1048_8196[wall ID]` a podľa epizódy a indexu levelu vyberie vetvu. Tým je staticky potvrdený per-level dispatcher, nie univerzálny odkaz triggera na vzdialené dvere. Skutočné načasovanie pri prejdení bunkou ešte potrebuje runtime trace.

MAP súbory ukladajú v hlavičke preklad wall-ID → image-ID. E1 používa `0xB8 → G` a `0xB9 → H`; E2 a E3 používajú `0xBE → G` a `0xBF → H`. Súradnice nižšie sú zero-based `(x,y)`; označenie levelu je one-based, index dispatchera je zero-based.

| Dáta | Level / index | Triggerové bunky | Staticky potvrdený účinok a text |
|---|---:|---|---|
| E1 / `MAP(20260921-103303).1` | 7 / 6 | G wall `0xB8`: `(54,36)`, `(55,36)`, `(56,36)` | Ak `51A6==0`: SFX event `0x42`, `51A6=1`, `51AB=1`, aktualizácia shade/palety; text `DAT_1048_016E`: “Oh dear! The storm seems to have fused the lights!” |
| E1 | 9 / 8 | G `0xB8`: `(6,45)`, `(7,45)`; H `0xB9`: `(3,35)`, `(4,35)`, `(10,47)` | G nastaví latch `4C2E=1`; H ho vynuluje; obe vetvy prehrávajú SFX event `0x44`. Pri pokuse o streľbu s aktívnym latchom hra zobrazí “Your weapon appears to be jammed!” cez `FUN_1018_2508`. |
| E1 | 10 / 9 | G `0xB8`: `(23,27)`; H `0xB9`: `(27,29)` | G, ak `51A6==0`, prehrá SFX `0x12`, nastaví `51A6=1`, `51A8=1`, `4BE8=1`, `4BE5=0`, a zaradí texty `DAT_1048_0182`, `0186`, `018A`: “So! You have discovered me!”, “Fool! Did you really think you could defeat me? You have no idea of my power!”, a “Bid farewell my friend! 'Tis the end for you!”. H, ak `51A7==0`, nastaví `51A7=1` a zobrazí `DAT_1048_018E`: “Look over there! It's Penelope and the evil Dr. Hamerstein!”. |
| E2 / `MAP(8).2` | 10 / 9 | G wall `0xBE`: `(45,36)`, `(45,37)`, `(45,39)`, `(45,40)` | Ak `51A6==0`, nastaví `51A6=1` a zobrazí `DAT_1048_01C6`: “QUICK! Destroy the plasma core!” |
| E3 / `MAP(8).3` | 1 / 0 | G wall `0xBE`: `(45,37)`, `(46,37)`, `(46,38)`, `(45,39)`, `(46,39)` | Ak `51A6==0`, nastaví `51A6=1` a zobrazí `DAT_1048_01D2`: “You recover to witness the defunct plasma core's residual radiation slowly decaying. When the plasma core imploded into another dimension the blast jammed the automatic doors shut and scattered your posessions. There does not appear to be any way out!” (pravopis `posessions` je zachovaný podľa binárky). |
| E3 | 10 / 9 | G wall `0xBE`: `(52,16)` | Ak `51A6==0`, nastaví `51A6=1` a zobrazí `DAT_1048_019A`: “Look! It's Penelope! Where's Dr. Hamerstein?” |

V dodaných E2/E3 MAP súboroch sa wall image `H` nevyskytuje. Súradnice a výskyty sú priamo spočítané zo surových máp, nie odvodené z názvov levelov. E1 level 7 poistková skrinka je wall `0x12` / image ID `8` na `(27,26)`. Interakcia prejde cez `FUN_1010_C0A2`: pri `51A6==1` prehrá SFX `0x32`, zmení `51A6` na `2`, vynuluje `51AB`, obnoví shade/paletu a zobrazí `DAT_1048_0172` (“Well done! You fixed the power!”); iný stav zobrazí `DAT_1048_0176` (“You already fixed it!”). Statický kód ukazuje, že `51AB` sa nastaví triggerom a vymaže poistkovou skrinkou alebo level initom; trvanie a obrazový výsledok stále vyžadujú runtime test.

Ďalšia čiastočne uzavretá vetva SPECIAL1: WALLS.1 pomenúva wall `0x56` ako „Office - Morphing chalkboard“. E1 level 2 (dispatch index 1) ho umiestňuje na `(32,50)` a `(33,50)`; level 9/index 8 má druhú dvojicu na `(46,42)` a `(46,43)`. MAP hlavička prekladá `0x56 → image ID 8`, takže `FUN_1010_1A22` posiela interakciu do `FUN_1010_C0A2`. V indexe 1 handler nastaví `0x96` do sequence-cache intervalu vybratej položky a prehrá SFX event `0x44`. `FUN_1010_66B0` používa rovnaký selector a volá updater `FUN_1010_65A6`; cache sharing znamená, že zásah môže ovplyvniť viac než jeden wall segment.

Raw disassembly teraz uzatvára selector lookup, ktorý dekompilácia nechávala nejasný. V NE segmente `1018`, funkcii `3844` (file offset `0x28AA4`), kód prevedie far pointer mapovej bunky na tile `x/y` a zavolá `37A0(x,y,8)`. `37A0` prechádza 28-bajtové runtime entity v poradí, vyžaduje byte `+6 == 8` a testuje ich bounding box cez `3736`; pri prvom matchi vracia far pointer entity v `DX:AX`, inak nulu. Hoci export deklaruje `3844` ako `void`, raw epilóg po volaní `37A0` zachová `AX/DX`. Volateľ `1010:C0A2` (file offset `0x22062`) hneď použije `ES:BX = DX:AX`, načíta byte entity `+4` a zapíše `0x96` na `0x51AE + 8*entity[+4]`. Tým je staticky potvrdené, že cache selector pochádza z prvej class-8 entity, ktorej bounds obsahujú použitú bunku; nie je to priamo wall ID.

Presné runtime entity/selector závisia od naplnenia a poradia object listu. Doplnenie 24. 9.: `0x96` je 150 ms; IMG wall 56 má šesť snímok a všeobecný updater loopuje. Index-8 SPECIAL1 handler nemá vetvu. Vizuálny runtime výsledok, dôvod druhej mapovej inštancie a správanie pri LOAD zostávajú otvorené; podrobný dôkaz je v novom reporte.

Ďalší priamo dekódovaný event text: class `0x16` death vetva vo `FUN_1010_A0EE` zaradí `DAT_1048_0196` (“You've won! You've won!”), nastaví `51AA=1` a vynuluje `DAT_1048_46B4`. `51AA` nemá v tomto exporte priamy funkčný reader, takže následný herný účinok nie je uzavretý.

**Rozsah dôkazu:** Win16 NITE3W 1.10 SHA-256 `12fe5168783446275802e0e947898261b5eca6b88288f3a895fc1faa4c544481`; MAP E1 SHA-256 `de4eb9cd58fc8e969af4076c1a19e5aa4b70f409205c93f8578b71cbd496200c`, E2 `938b7e79c9881eab71fdef4b7afa9b0482c870c808785f599a4ba52093d44756`, E3 `0008775106854b3e9302f36fbcd7001607bcf2fd26cc9d8db6bccc732ead4217`; WALLS E1/E2/E3 `9fbbf889440cf7200c7c2dad271f47c79652baf237c27f1bbb354ee1e8b1cf84`, `23f9cb3757ad92876d8f43a8ad9987cecc596e3c2d9a9ebb09b10ce0a2af59fe`, `abf6c2bc6779e6261998bc26bd03bbbce7e3ea608f28ddc4d78a13fd80a39cae`. Statická analýza neoveruje prejdenie triggerom, časovanie dialógov ani DOS/Win16 1.8 parity.

## 8. Win16 1.10 paired-wall a pushable-object controllery

### Oprava staršieho pomenovania

`FUN_1010_133A` porovnáva offset a segment far pointera bunky s entity fields `+0x6D72/+0x6D74`. Nie sú to hráčske world súradnice. `DS:A616` sloty indexujú 28-bajtové entity označené byte `+6 == '('`; `133A` vyhľadá taký slot podľa mapovej bunky.

### Tri odlišné runtime polia

| DS rozsah | Kapacita | Úloha potvrdená kódom |
|---|---:|---|
| `9DD6–A355` | 64 × 22 B | Paired-wall/door controllery vytvorené `14A8` pre wall-property bit `0x08`. |
| `A356–A615` | 32 × 22 B | Class-3 group-motion records: štyri entity pointery, cell pointer a phase. |
| `A616–A65D` | 12 × 6 B | Indexy pushable runtime entities s markerom `(`. |

`A65E–A69D` je oddelená guard-wake cache; `A69E–C69D` je 64×64 mapa po dvoch bajtoch. Rovnaký stride prvých dvoch polí neznamená rovnaký record layout.

### Paired-wall lifecycle

`14A8` vytvára record pri property bit `0x08`, pripája dve 28-bajtové entity a nastaví state `1`. Record ukladá ich far pointery na `+0/+4`, cell pointer na `+8`, state `+0x0C`, timer `+0x0E`, cieľové world súradnice `+0x10/+0x12` a helper byte `+0x14`. Interakcia cez `188A` preklopí zatváranie/otváranie; `1E00` hýbe oboma časťami po dvoch jednotkách za update. States 1/0 sú zavreté/otvorené, 2/3 sú pohyb; `1476` pokladá za priechodný stav 0 alebo 4, ale bežný writer stavu 4 sa nenašiel.

Po dokončení otvorenia sa odpočet nastaví na 32 update-ov. `1D4E` zatvorí len po odpočítaní v stave 0 a len ak druhý byte mapovej bunky je nula a hráč stojí inde. Inak opakuje kontrolu po 4 update-och. Entity ID `0x3B–0x3C` túto auto-close vetvu preskakujú. `700A` má aj osobitnú vetvu pre ID `0x33–0x3C`, preto tieto predicate pravidlá neplatia bez výnimky pre každý wall.

### Class-3 skupina a pushable objekty

`16D6` vytvára odlišné pole pre bunky, ktorých druhá class table vracia `3`. Record má štyri entity pointery rozlíšené byte `+7` = 0–3, cell pointer `+0x10` a phase `+0x14`. Interakcia `1A22` nastaví phase 2 a upraví ciele jednotlivých komponentov o ±1; `1E00` ich posúva o dva world units/update. Po dokončení vymaže collision bit 0, oba map-cell bytes a phase. Asset/herný význam zostáva neznámy.

`181C` registruje najviac 12 entít s markerom `(`. Pri USE `21B6` vyhľadá slot cez far pointer bunky objektu, vyžaduje neaktívny slot a cieľovú wall-property bez bitu `0x02`, uloží player-state signed bytes `+0xA4/+0xAC` a nastaví 8 krokov. `2210` skúša pohyb v každom simulačnom update. Pri prechode bunkou vyžaduje `DAT_1048_7F94[object_id] & 0x06 == 0`; potom presúva druhý byte mapy, aktualizuje world súradnice a renderer ordering cez `C9A6`. Blokovaný krok nemení pozíciu ani čítač a skúša sa znovu v ďalšom ticku.

**Istota a otvorené otázky:** adresy, kapacity, maskové testy a zápisy sú staticky potvrdené pre Win16 NE `nite3w(10).exe`, SHA-256 `12fe5168783446275802e0e947898261b5eca6b88288f3a895fc1faa4c544481`; push call chain `1A22 → 21B6 → 133A`, update chain `d974 → 2210`. Neznáme sú presná škála smerového vektora, názov/identita class-3 a push assets naprieč epizódami, mask semantics mimo priamo pozorovaných testov, runtime vizuál/zvuk, writer stavu 4 a DOS/Win16 1.8 zhoda. WALLS/OBJECTS sa používajú len ako ID→názov slovník.


## Doplnenie 24. 9. 2026: ONE_SHOT, SPECIAL1 a LOAD

Samostatný primárny audit: `Nite3W_ONE_SHOT_SPECIAL1_analysis_2026-09-24.md`; reprodukčné dôkazy: `Nite3W_ONE_SHOT_SPECIAL1_evidence_2026-09-24.zip`.

- **Confirmed/High:** strategy 3/state 13 spája chrliče object class 12/13 s wall class 7. `4:392C` aktivuje wall frame 0→1. Animátor drží idle 0 a finálny frame 4; IMG wall 54/55 majú päť snímok pri 200 ms. Táto vetva sama neodstráni stenovú geometriu.
- **Confirmed/High:** osem pohybových pokusov po 8 jednotiek; timer 8 preskočí aktivačné volanie. Kontrolný odvodený model preveril 640 timer×facing prípadov, nie behov pôvodnej hry.
- **Confirmed/High:** tabuľa wall 56 v E1M2 aktivuje interval 150 ms a šesťsnímkovú slučku; E1M9 nemá v `C0A2` príslušnú USE vetvu. Staršia otázka časovej jednotky je uzavretá.
- **Inferred/Medium:** cache interval tabule nie je v kontrolovanom save layoute; pri novom načítaní levelu sa obnoví 0 z IMG, pri LOAD v tej istej inštancii levelu môže prežiť 150. Presné viditeľné správanie vyžaduje tri kontrolované LOAD scenáre v novom reporte.
- **Rozsah:** Win16 1.10 EXE hash `12fe5168783446275802e0e947898261b5eca6b88288f3a895fc1faa4c544481`. Relevantný strategy-3 tok podporuje aj C export Win16 1.8. V tomto doplnení sa neoverovala DOS parity a nevykonal sa runtime beh.


## Win16 medziverziové doplnenie — 24. 9. 2026

Nový priamy audit štyroch EXE je v `Nitemare3D_Win16_all_available_versions_audit_2026-09-24.md`. Popri oprave časovania vyššie potvrdil: render v frame vetve predchádza projektilom aj vstupu; cache OBJECT+18 však zapisuje iba podmienená projekčná vetva, takže univerzálna freshness ostáva otvorená. Win16 1.10 mení paletový upload/realizáciu oproti 1.8; 1.8 pridáva obnovenie úspešne načítaných MIDI/wave hlasitostí oproti 1.6. V dodaných shareware dátach je MAP.1 1.3/1.6 totožný, kým 1.8 presúva E1M5 objekt D8 z (26,35) na (26,34), súradnice od nuly. IMG.1, DEMO.1, SND.DAT, UIF.DAT a GAME.PAL sú v tejto trojici totožné. GAME.PAL je PCX s úplnou 256-farebnou paletou. Tieto nové dôkazy sú statické a nemenia stav runtime potvrdení na hotový ani nedokazujú úplné pochopenie všetkých funkcií.


## Doplnenie 24. 9. 2026: analýza všetkých 40 Win16 oblastí

Podrobný pokračujúci audit je v `Nitemare3D_Win16_40_oblasti_hlbkovy_audit_2026-09-24.md`; dôkazy a strojový register obsahuje `Nitemare3D_Win16_40_oblasti_evidence_2026-09-24.zip`. Rozsah tvoria štyri dodané EXE 1.3/1.6/1.8/1.10, C exporty a dostupné shareware assety 1.3/1.6/1.8. Každá zo 40 oblastí má konkrétny statický nález, verziový rozsah, adresy, implementačný dôsledok a zostávajúci rozlišujúci test. Nejde o dokončenie všetkých subsystémov ani o runtime potvrdenie.

Nové priame opravy oproti staršej hlavnej referencii:

- Raw score tabuľka je overená pre 25 tried vo všetkých 4 EXE: 8/26→25, 9→75, 10/32→50, 11/15/16/23/27/28→100, 12/29/30→250, 13/18/19→150, 14/20/24/31→200, 17/25→0, 21→−1000, 22→1000. DOS score parity tým nie je potvrdená.
- Kontaktné poškodenie guard→player pri difficulty 2 sa zdvojnásobuje, pri 0 sa aritmeticky delí dvoma; štyri EXE potvrdené raw. Tento hlboký audit mal smer už správny, hlavná referencia ho mala obrátene.
- `3:8CD2` prijíma virtuálne klávesy: 0x71/0x72 sú F2/F3, 0x73 je F4; vetva Alt+F4 posiela WM_CLOSE 0x0010.
- GUARD+0x0D uchováva podkladový objektový bajt mapovej bunky. `3:80F8` ho cez OBJECT+0x0C vracia do mapCell[1], nie do OBJECT+1. Nevyplýva z toho význam rovnakého offsetu v projektilovom slote.
- `3:7B56`, case 9, obsahuje writer door state 4. `3:A0EE` zapisuje AI state 0x0A; význam terminálneho stavu je interpretácia, writer je priamy dôkaz. State 0x0B ostáva otvorený.
- DEMO timestamp sa zapisuje z generation counter a porovnáva s ním vo všetkých štyroch EXE. Mode 8 môže generáciu posunúť bez normálneho renderu; nejde všeobecne o milisekundy ani vždy o počet zobrazených snímok. Dodané DEMO.1 má 203 udalostí (19…1157), jeho EOF/ukončenie vyžaduje beh originálu.
- OBJECT+0x18 dostáva uložený baseline riadok projection>>4 pred ďalším sprite-slot clippingom (`3:CCBB–CCC2`, `3:CE5B–CE5E`). Sprite bypass v `3:3F80` číta OBJECT+5 bit 0x10, nie VEC+5.

Ďalšie nálezy: cooldown sa v `3:AA90` resetuje pred výsledkom pokusu o výstrel; hitscan slučka v `3:8B06` nemá break po prvom úspešnom damage; HUD clamp reálne mení stav; RNG odbery sú previazané aj s animáciami viditeľných objektov; loader `3:574C` obnovuje pointery a rebazuje VEC/world OBJECT deadline, kým lokálna projektilová slučka taký rebase neukazuje. To posledné nie je samo osebe dôkaz chyby a potrebuje rozlišujúci save/load test. Všetky tri BSF boli dekódované a porovnané; bloky 0/2 sú zhodné, rozdiely sú v distributorovi a manuáli. Čítače CONFIG kontrolujú a čítajú 20 bajtov.

Overenie: 100 score položiek, 12 raw byte kontrol, 3 DEMO súbory a 9 BSF blokov prešli. Katalóg 424 extrahovaných verzionovaných funkčných okien nie je tvrdenie o ručnom preverení každej inštrukcie. Rozsah jednotlivých potvrdení určuje detailný 40-oblastný report. Aktuálna revízia hlavnej referencie je 1.5; skoršie konfliktné formulácie sú týmito presnými opravami prekonané. Existujúce doplnenie ONE_SHOT a ostatné nezávislé zistenia zostávajú zachované.