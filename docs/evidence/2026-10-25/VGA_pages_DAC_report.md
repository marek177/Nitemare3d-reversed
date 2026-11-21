# Nitemare 3D DOS 2.0 — stránky VGA, celý DAC zápis a dekódovaný pôvodný stav

## Nové runtime dôkazy

**VERIFIED_RUNTIME:** clean_run_c bol spustený v novej vlastnej inštancii DOSBox-X, bez zdedených obslúh predchádzajúcej hry. Load base je0823. Breakpoint0979:012A zachytil pôvodnú rutinu0156:012A pred zápisom palety. Z jej stacku sa získal near pointer DS:4A64, DS=2F94, a768 vstupných bajtov. Stopa obsahuje7164 CPU udalostí s neprerušenou sekvenciou a končí breakpointom na0979:014E pred RETF.

V stope je presne jeden OUT3C8 s indexom0 a768 OUT3C9. Všetky komponenty sa po poradí zhodujú so vstupným bufferom. Pri zastavení má CX=FFFF, AX=0 a SI/BP sú obnovené. RETF ešte nebolo vykonané, preto sa netvrdí zachytený návrat do volajúceho. Následný read-only odpočet skutočných768 hodnôt DAC emulátora sa presne zhoduje s portovou sekvenciou aj vstupným bufferom. Nejde iba o predpoklad zo súboru GAME.PAL.

## Read-only získanie kompletného VGA stavu

K nainštalovanému DOSBox-X existuje jeho PDB. Pomocou lokálneho DbgHelp sa z neho získali RVA globálneho VGA stavu a offsety presných typov: sequencer, graphics, CRTC, attribute, DAC a backing-memory pointer. EXE aj PDB sú označené SHA-256. Proces bol identifikovaný cez GetNamedPipeServerProcessId aktívneho debugger pipe; overila sa cesta hlavného modulu a hash EXE/PDB. Použili sa iba práva na čítanie/query a ReadProcessMemory, bez debug attach, bez injekcie a bez zápisu do hry alebo procesu.

[SymGetTypeInfo v primárnej dokumentácii Microsoftu](https://learn.microsoft.com/en-us/windows/win32/api/dbghelp/nf-dbghelp-symgettypeinfo) poskytuje informácie o typoch podľa indexu. V tomto postupe sa nepoužilo odhadované rozloženie iného buildu. Reproducer potrebuje presne príslušné lokálne EXE/PDB a Windows DbgHelp; ich absencia nie je dôvodom vymýšľať offsety.

Pri ďalšom zastavení, revision8, sa načítalo262144 bajtov backing VGA pamäte, príslušné registre a768 hodnôt DAC. Dve čítania a následný recheck sa zhodujú. Virtuálny CPU zostal stopped s rovnakou revision počas každej snímky. Chained=0 a sequencer memory_mode=6 potvrdzujú unchained stav. Obyčajné CPU čítanie64000 bajtov A000 sa presne zhoduje iba s rovinou0 vybranou každým štvrtým bajtom backing VRAM; roviny1–3 sú odlišné. Tým je pre tento nový beh runtime potvrdené, prečo raw A000 nie je celým obrázkom.

## Rekonštrukcia obrazu s explicitnými podmienkami

Dekóder akceptuje iba overený podprípad: width320, fyzických400 riadkov so zdvojením po2, address_add320, start/real_start0, bez panningu a splitu v obraze, byte-addressing a6-bit DAC s maskouFF. Obrazový index sa rekonštruuje ako:

`index(x,y)=VRAM[4*(80*y+(x>>2))+(x&3)]`, pre x=0..319 a y=0..199.

Pre tento layout sa teda všetky štyri roviny skladajú do64000 indexov. Všetkých256 DAC RGB trojíc sa po6→8-bit expanzii zhoduje s uloženou xlat32 tabuľkou toho istého emulátora; tým je skontrolované aj poradie kanálov. Výsledný PNG bol vizuálne skontrolovaný: ide o pôvodnú obrazovku Nitemare-3D V2.0 s výzvou PRESS A KEY. Je to rekonštrukcia z pozastaveného stavu, nie screenshot natívneho okna. Nie je zarovnaná na frame boundary a nie je spárovaná s remake.

Starý raw záber clean_run_b sa tým nepovyšuje na dekódovaný obraz. Jeho hardware-state dôkazy chýbajú; nový clean_run_c má samostatné snímky, hashy a rozsah platnosti. Dekóder odmieta nepodporované nenulové starty, panning a split namiesto toho, aby použil všeobecne nepreukázaný vzorec.

## Sedem ohraničených statických funkcií

Všetky nasledujúce miestne inštrukčné kontrakty sú **VERIFIED_STATIC** na rozbalenom DOS2 EXE5ad15f66a4478de21e4c74799a74d35d606f3bdb7406a5b40168cfbd5ba2c9a3. Neznamená to uzavretie všetkých caller invariants alebo časovania hardvéru.

| Vstup | Kontrakt |
|---|---|
| 0156:008E | Vymení DS:012C/012E a zapíše iba CRTC start-high index0C, odvodený z nového012C. Low byte sa tu nenastavuje. |
| 0156:00A8 | Rovnaká výmena; poll3DA bit0, CLI/CRTC zápis/STI, potom poll bit3. Entry IF sa neobnovuje a nejde všeobecne o úplný retrace-edge wait. |
| 0156:0A3A | Map mask0F, vybraná stránka,16000 aperture bajtov cez8000 STOSW; DF sa vymaže. |
| 0156:0A66 | BIOS13h plus následné sequencer/graphics/CRTC úpravy a vyčistenie oboch stránok. |
| 0156:088C | Jeden pixel: signed Y<200; adresa80*u8(Y)+(u16(X)>>2), raw maska11/22/44/88. Bez lokálneho X clipu a bez odmietnutia záporného Y. |
| 0156:012A | Index0 a presne768 DAC komponentov z near DS pointera; konečný CX=FFFF, nie0. |
| 0156:0150 | Jeden index a tri nízke bajty komponentov, bez lokálneho clamping. |

Počiatočné slová stránok DS:012C/012E sú A000/A400 a nie sú MZ relokácie. Pre320×200 viditeľných súradníc je64000 kombinácií aperture offsetu a roviny unikátnych. Tieto súradnicové kontroly sú syntetické, nie beh všetkých pixel-writer vstupov v origináli. Záporné Y a veľké X zostávajú caller-precondition otázkami; nenavrhuje sa neoverená oprava herného správania.

## Otvorené P0 a presný ďalší krok

Získať reprodukovateľný emulovaný vstup na odchod z copyright obrazovky a prejsť do E1M1. Prirodzene zachytiť main-loop/OBJECT, RNG ledger a frame/tick checkpoint. Nový originálny snapshot má64000 indexov+768 DAC, ale renderer parity gate zostáva OPEN: chýba rovnaký vstupný stav a porovnanie s remake. Ďalej treba podporiť druhú stránku, neštandardný CRTC start a prípadné zmeny palety počas scanoutu. Všetky dáta z hry, VRAM a PNG zostávajú lokálne; na GitHub ide metodika, hashy, výsledky a read-only verifikátory.

Offline dekóder bol overený na podporovanom snímku; odmietol nenulový štart aj poškodenú VRAM. Pred výstupom kontroluje hash backing VRAM, hash DAC a zhodu DAC blobu s uloženou DAC štruktúrou. Statický verifier overil sedem tiel na správnom EXE a odmietol zmenenú binárku. Ide o kontrolu ohraničených kontraktov a integrity, nie o parity PASS.

