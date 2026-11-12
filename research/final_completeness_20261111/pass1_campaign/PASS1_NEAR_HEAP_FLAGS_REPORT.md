# PASS1: near-heap flags a resize/accept helper

Jeden nový bajt PARTIAL: image **[297F4,297F5)**, DGROUP offset **20E4**, počiatočná hodnota 05h. Explicitné konzumenty testujú BYTE [BX+2] s koreňom BX=20E2. Bit0 testuje grow helper 21E4, bit2 testuje tento resize helper. Susedný nulový BYTE 20E5 nemá touto dávkou potvrdený WORD prístup: ostáva CLASSIFIED ONLY a neoznačuje sa padding. Žiadny DEEP VERIFIED.

## Funkcia a ABI

11EE:2270..22C1, image [14150,141A1), span 81 B, 39 inštrukcií / 80 B. Jeden span byte nepatrí k dosiahnutému lokálnemu CFG. ASM a CFG exportujú near_heap_resize_or_accept.csv a cfg_edges.csv. Všetky začiatky aj pôvodné bajty sú nezávisle overené proti kanonickému obrazu a inventáru.

NEAR register ABI: AX=požadovaná veľkosť, BX=near heap root v DS. Výsledok CF=0 pri prijatí/úspešnom resize, CF=1 pri DOS chybe. Pri úspechu AX=požadovaná veľkosť; pri DOS chybe ostáva AX z DOS. BX/CX sú zachované pomocou stacku okolo interruptu, DI sa v tele nepoužíva, SI/DX/ES sa menia. SS môže byť odlišný od DS. Toto zachovanie závisí aj od skutočného DOS kontraktu; model nemení DX/BP/SI ľubovoľne.

## Rekonštruovaný algoritmus

```c
// unsigned 16-bit výpočty
dx = desired;
if (root.flags_byte & 4) {
    dx = (desired - 1) & 0xFFFF;
    if (dx > ((root.word4 - 1) & 0xFFFF) && root.word_minus2 >= dx)
        return CF_clear; // AX=desired, DX=desired-1; bez INT21
    dx = (dx + 1) & 0xFFFF;
}
paragraphs = desired >> 4;
if (paragraphs == 0) paragraphs = 0x1000;
ES = DS;
if (root.flags_byte & 4) {
    paragraphs = (paragraphs + DS - DS.word[0x211E]) & 0xFFFF;
    ES = DS.word[0x211E];
}
INT21_AH4A(ES, paragraphs);
if (CF) return; // AX z DOS
AX = dx;
if (root.flags_byte & 4) {
    dx = (dx - 1) & 0xFFFF;
    root.word_minus2 = dx;
}
return CF_clear;
```

Pri BX=20E2 je word_minus2 práve 20E0 a word4 je 20E6, ktoré startup už inicializuje. Bit2 preto v tejto ceste vyberá PSP/limit variant memory resize; úplné meno alebo význam každého možného flag bitu sa nedopĺňa. Bit0 je potvrdený len statickým testom v 21E4, jeho vetva sa touto emuláciou nevykonáva. Vyššie flag bity sa v tomto helperi nespotrebujú.

Výpočet paragraphov zaokrúhľuje doprava bez pridania 15. Caller 21E4 pripravuje požadovanú hodnotu osobitne; samostatný helper nie je dôkaz bezpečnosti nevyrovnaného priamého vstupu v prirodzenej hre. Desired=0..15 dáva po SHR nulu a následný špeciálny počet 1000h paragraphov. Current=0 má po odčítaní SI=FFFFh, čím fast vetva v tejto matici neprejde. Všetky tieto stavy sú explicitné modelové vstupy, nie automaticky prirodzené stavy.

## Kontrolovaná emulácia

8 192 prípadov = 2 load bázy × 8 flag WORD seedov × 8 veľkostí × 4 current × 4 limit × 2 výsledky DOS × 2 incoming CF. Flag seed používa aj nenulový horný BYTE, ale konzument je BYTE a iba dolný BYTE sa typuje. Veľkosti 0,1,15,16,17,1000h,8000h,FFFFh; current 0,1,1000h,FFFFh; limit 0,1,0FFFh,FFFFh. DOS resize je jediný modelovaný interrupt, úspech aj chyba. Žiadna skutočná OS alokácia alebo zmena hostiteľskej pamäte.

Kontroluje sa presný počet/ES/BX argument resize volaní, AX/DX/CF, celý 8 B stav okolo limit/root/flags/current, SP/BX/CX/DI/DS. Model vracia pri chybe AX=8 a pri úspechu odlišnú dočasnú AX hodnotu, ktorú helper nahradí. Nulové odchýlky. Prirodzený DOSBox-X runtime0, kompletný heap lifecycle otvorený.

Reprodukcia: audit_replay_pass1_near_heap_flags.py IMAGE INVENTORY DECODER EMULATOR OUT; promote_pass1_fields.py s mapou pass1_fcb_prefix; verify_pass1_partition.py. Canonical image SHA e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297; iced-x861.21.0/Unicorn2.1.4. root_and_flag_context.csv dokladá BX koreň v malloc ceste a bit0 test. Nie je to celý malloc kontrakt.

## Meranie

**57 102 B PARTIAL, 149 B CLASSIFIED ONLY, 44 B UNKNOWN, 0 B DEEP VERIFIED**, spolu 57 295 B. Nezávislá kontrola 888 intervalov potvrdila presné členstvo, hash hodnoty, nulové diery/prekryvy. Táto integrita neznamená úplnú sémantiku. Publikovaná analytická snímka ba27379dd28c9a689d15233b0fd7017867f50114 má predchádzajúcu mapu; táto nová lokálna dávka v nej ešte nie je.

SHA mapy `3021969d4e4348715816361fa387631e7d6cfd9fc9dcc136e26073f0f9984d1b`; SHA cases `23a80d8cf166a78cdaceff170efa2e421a03483ab5c0efc87aa8b4534cf2d0eb`.

## Aktualizácia 13 oblastí

Nové % = uzavreté jednotky / úplný inventár oblasti. Menovatele chýbajú, preto N/A; historické percentá zostávajú orientačné.

| Oblasť | Predošlý odhad | Nové % | Nové potvrdenie | Zostávajúce neznáme / blokátor | Najbližší konkrétny krok |
|---|---:|---|---|---|---|
| Mapy a formáty |99 %|N/A|bez nového dôkazu|loader hranice|map closure|
| Dátové typy a konštanty |95 %|N/A|1 BYTE flags PARTIAL|149 B iba klasifikované|susedné alias polia|
| Tabuľky a ukazovatele |93 %|N/A|root+2 BYTE a PSP variant|ostatné flag bity|grow kontrakt|
| Funkcie / ASM / CFG |90 %|N/A|80 B / 39 inštrukcií|celý heap lifecycle|21E4 grow replay|
| RNG |97 %|N/A|bez nového dôkazu|prirodzené poradie|DEMO trace|
| Scheduler |96 %|N/A|bez nového dôkazu|prirodzené callery|call graph|
| DEMO a vstupy |96 %|N/A|bez nového dôkazu|driver ABI|input closure|
| Renderer / VGA |94 %|N/A|bez nového dôkazu|setup|VGA init CFG|
| GUARD / bossovia |93 %|N/A|bez nového dôkazu|selector doména|descriptor flag8|
| Zbrane / projektily |92 %|N/A|bez nového dôkazu|damage callery|effect producer|
| Sprity / HUD / paleta |92 %|N/A|bez nového dôkazu|resource identity|resource parser|
| SAVE / LOAD |92 %|N/A|CRT pamäť oddelená|prirodzené I/O|stream trace|
| Windows Win16 |92 %|N/A|bez nového Win dôkazu|odlišný heap model|Win kontrakt|

## Runtime testy na vykonanie

V DOSBox-X sledovať prirodzené flags20E4, desired/current/limit pri 2270, skutočné AH4A výsledky a caller alignment. Zachytiť flag0 vetvu 21E4 a následný allocator retry. Bez takejto trace sa nevyhlasuje celý heap za uzavretý. PE32 sa nevytvára.
