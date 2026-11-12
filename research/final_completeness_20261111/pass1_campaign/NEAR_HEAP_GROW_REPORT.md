# CRT: near-heap grow, posledný blok a resize integrácia

Stav PARTIAL. Dva nové lokálne funkčné rozsahy, bez novej byte reklasifikácie. Pôvodný grow aj finder sú vykonávané spolu s už analyzovaným pôvodným resize helperom 11EE:2270; modelovaný je iba DOS INT21/AH4A. Nejde o celý malloc, OS memory manager ani prirodzený game runtime.

| Rutina | CS:IP | Image interval [start,end) | Inštrukcie / bajty |
|---|---|---|---:|
|near_heap_grow|11EE:21E4|[140C4,14150)|68 / 140|
|near_heap_last_block|11EE:22C1|[141A1,141C1)|17 / 32|

Všetky začiatky a bajty boli nezávisle dekódované a porovnané s kanonickým obrazom aj dodaným inventárom. Exporty majú pôvodné ASM a samostatné CFG hrany. Ani platné statické CFG neznamená prirodzenú dosiahnuteľnosť každej vetvy.

## ABI, segmenty a bloky

Grow je NEAR register ABI: BX=near root v DS, CX=požadovaná veľkosť. Ukladá a obnovuje CX/DI, CF nesie výsledok. Zachovanie BX v testoch vyplýva aj z resize helpera. DS drží root a bloky; **WORD kroku 2344h sa číta cez ES po PUSH SS/POP ES**, teda zo SS, nie všeobecne z DS. Testy zámerne dávajú DS:2344 inú hodnotu než SS:2344. Stack je samostatný segment. Ďalšie pracovné registre a ES sa nemajú považovať za zachované.

Root +2 obsahuje BYTE flags (bit0 povoľuje grow, bit2 mení resize kontrakt); +4 aktuálnu veľkosť, +6 dolný blokový offset, +8 kurzor a +0A offset sentinel hlavičky. V tejto matici je root DS:20E2, limit pre bit2 je root-2. Bloková WORD hlavička používa dolný bit ako free tag, zvyšok posun na ďalšiu hlavičku cez LODSW + očistenú dĺžku. Sentinel je FFFEh. Celý layout predchádzajúcich či poškodených heap reťazí sa tým neuzatvára.

## Algoritmus findera

Začne na root+8; ak kurzor ukazuje priamo na sentinel, použije root+6. Číta WORD, porovná FFFEh, inak uloží adresu za hlavičkou, zruší bit0 a posunie sa o veľkosť na ďalšiu hlavičku. Pri sentineli vráti v SI adresu poslednej skutočnej hlavičky. DI zachová. Testovaná reťaz má jeden skutočný blok a sentinel; obe východiskové polohy kurzora sú pokryté. Viacblokové, cyklické alebo poškodené reťaze zostávajú otvorené. Prázdna reťaz by mohla použiť predchádzajúce DI; jej prirodzenú prípustnosť treba doložiť callerom.

## Grow a zaokrúhľovanie

Ak bit0 flags nie je nastavený, CF=1 bez resize. Inak vyhľadá posledný blok a uloží jeho hlavičku. Ak je voľný, od požiadavky odpočíta jeho označenú dĺžku a 1; potom pripočíta dva bajty novej hlavičky a aktuálnu veľkosť root+4. Všetky operácie sú 16-bitové. Pri carry a nenulovom low výsledku zlyhá; presný prechod na 0000h má osobitnú cestu resize veľkosti0.

Bežná cesta používa quantum zo SS:2344. Hodnota2000h má priamu cestu. Inak sa hľadá mocnina dvojky podľa porovnávania s quantum a pri malých/neudržateľných hodnotách padne na 16 B. Pre testované quantum 0/8/9/16 dáva 16 B; 1000h a2000h príslušnú veľkosť. Pre FFFFh sa 16-bitový krok pretočí na nulu; nevydáva sa to za prirodzený konfiguračný stav. Následný add/AND krok sa pri carry nastavuje na veľkosť0.

```text
candidate = rounded_needed_size
try native resize_or_accept(candidate)
if failure and pôvodná maska != FFF0h:
    candidate = rounded_needed_size_with_16_byte_step
    try native resize_or_accept(candidate)
if failure: CF=1
else:
    delta = candidate - old_current mod 65536
    root.current = candidate
    root.cursor = last_header
    old_sentinel.word = delta - 1 mod 65536
    root.sentinel += delta mod 65536
    root.sentinel.word = FFFEh
    CF=0
```

Pôvodný resize môže prijať hodnotu bez DOS volania podľa bit2/limit; grow preto nemá zaručené jedno AH4A na každú úspešnú vetvu. Posledný existujúci free blok sa tu priamo neprepisuje ani nezlučuje s novou časťou; nový označený blok sa zapisuje na starý sentinel. Neskorší allocator scan môže mať vlastnú coalescing logiku, ktorá nie je predmetom tejto dávky.

## Kontrolovaná emulácia a reprodukcia

21 504 prípadov = 2 load bázy × 4 flags × 8 požiadaviek × 2 current veľkosti × 2 posledné tagy × 7 quantum × 3 DOS politiky × 2 limity × 2 polohy kurzora. Flags 0,1,4,5; request0,1,15,16,17,32,FFF0h,FFFFh; current4014h/FFF0h; posledný blok allocated16/free17; quantum0,8,9,16,1000h,2000h,FFFFh; policy success, prvé volanie fail a ďalšie success, vždy fail; limit0/FFFFh. Mnohé seedované stavy iba skúmajú aritmetické hranice, nie prirodzenú hru.

Nezávislý model kontroluje počet a presné ES/BX argumenty DOS volaní, CF, celý root+limit, poslednú existujúcu hlavičku, starý/nový sentinel a SP/CX/DI/DS. Nulové odchýlky. DOS model zachováva DX a ostatné nedeklarované registre; nemožno z neho odvodiť všetky vlastnosti skutočného DOS. Natural DOSBox-X runtime0.

Reprodukcia: audit_replay_near_heap_grow.py IMAGE INVENTORY DECODER EMULATOR OUT. Pôvodný obraz SHA e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297, iced-x861.21.0/Unicorn2.1.4. cases.csv obsahuje celú maticu a summary hash dôkazu. Predchádzajúca dávka PASS1_NEAR_HEAP_FLAGS_REPORT.md samostatne opisuje resize helper a jeho modelové limity.

## Meranie

PASS1 ostáva **57 102 B PARTIAL, 149 B CLASSIFIED ONLY, 44 B UNKNOWN, 0 B DEEP VERIFIED**. Nové funkčné rozsahy sa neprepočítavajú na percento celej CRT alebo hry. Táto nová lokálna dávka ešte nie je v publikovanej analytickej snímke ba27379dd28c9a689d15233b0fd7017867f50114.

SHA cases `6d6b2a312173d5e67f9524040bf32d995c61cc509d220d75830af3b2967ecdd4`.

## Aktualizácia 13 oblastí

Nové % = uzavreté jednotky / úplný inventár oblasti. Menovatele chýbajú, preto N/A; historické orientačné hodnoty sa nemenia z test count ani partition integrity.

| Oblasť | Predošlý odhad | Nové % | Nové potvrdenie | Zostávajúce neznáme / blokátor | Najbližší konkrétny krok |
|---|---:|---|---|---|---|
| Mapy a formáty |99 %|N/A|bez nového dôkazu|loader hranice|map closure|
| Dátové typy a konštanty |95 %|N/A|bez novej promócie|149 B iba klasifikované|susedné alias polia|
| Tabuľky a ukazovatele |93 %|N/A|SS quantum a sentinel zápisy|viacblokové invarianty|allocator scan|
| Funkcie / ASM / CFG |90 %|N/A|2 rozsahy,172 B/85 inštrukcií|celý malloc|2168 scan integrácia|
| RNG |97 %|N/A|bez nového dôkazu|prirodzené poradie|DEMO trace|
| Scheduler |96 %|N/A|bez nového dôkazu|prirodzené callery|call graph|
| DEMO a vstupy |96 %|N/A|bez nového dôkazu|driver ABI|input closure|
| Renderer / VGA |94 %|N/A|bez nového dôkazu|setup|VGA init CFG|
| GUARD / bossovia |93 %|N/A|bez nového dôkazu|selector doména|descriptor flag8|
| Zbrane / projektily |92 %|N/A|bez nového dôkazu|damage callery|effect producer|
| Sprity / HUD / paleta |92 %|N/A|bez nového dôkazu|resource identity|resource parser|
| SAVE / LOAD |92 %|N/A|CRT memory oddelená|prirodzené I/O|stream trace|
| Windows Win16 |92 %|N/A|bez nového Win dôkazu|iný heap model|Win kontrakt|

## Runtime testy na vykonanie

V DOSBox-X logovať skutočné heap reťaze, flags a SS:2344 pred grow. Overiť fallback po reálnej AH4A chybe a následné použitie novej hlavičky skenom2168. Zvlášť zistiť prirodzenú prípustnosť prázdnych reťazí, veľkosti0 a vysokého quantum; modelové hraničné stavy to nedokazujú. PE32 sa nevytvára.
