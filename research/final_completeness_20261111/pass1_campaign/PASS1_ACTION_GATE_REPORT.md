# DOS 2.0: selektorový prahový gate a saturujúci čítač

## Presné dáta a funkcia

| Pole | DS | Obrazový interval, koniec exclusive | Obsah |
|---|---|---|---|
| Prahy selektorov | 143E | [28B4E,28B52) | BYTE 2,1,3,1 |
| Čítač | 1442 | [28B52,28B53) | počiatočný BYTE 0 |

Spolu **5 B**, každý interval má konkrétne čítania/zápisy a SHA v `data_fields.csv`. Nominálna doména selektora je 0..3; v samotnom gate nie je guard tejto hranice ani test FFh. Úplný inventár writerov a prirodzená platnosť selektora DS:418F zostávajú otvorené.

FAR rutina **083D:0C56** má obalový rozsah `[09026,0907C)`, 86 B. CFG od vstupu dosiahne **33 inštrukcií / 85 B**; bajt 0C6Dh po skorom RETF sa nezapočítava a automaticky sa neoznačuje za padding. Všetky dosiahnuté bajty a hranice sú nezávisle dekódované a porovnané s obrazom. Rutina nemá ďalšie CALL, interrupt ani nepriamy skok; lokálny výsledok nečíta RNG.

## Presný kontrakt

WORD mode je na SS:[BP+6]. Len mode=0 číta druhý argument, a to iba jeho BYTE na SS:[BP+8]. Vrátený výsledok je **AL**, nie garantovaný celý WORD AX.

```text
result = 0
if mode == 0:
    selector = BYTE DS:418F
    if BYTE DS:1442 >= THRESHOLD[selector]:   # unsigned BYTE porovnanie
        result = selector == 3 ? 1 : BYTE second_argument
    if result != 0:
        BYTE DS:1442 = 0
else if mode == 1:
    if BYTE DS:1442 < FFh:
        BYTE DS:1442++
return AL = result
```

Mode=1 inkrementuje najviac na FFh, bez pretečenia na nulu. Vráti AL=0. Ostatné mode hodnoty tiež vrátia AL=0 a čítač nemenia. Pri mode=0, nedosiahnutom prahu alebo nulovom result sa čítač nemení. Pre selektory 0..2 môže result obsahovať ľubovoľný nenulový BYTE vrátane FFh, nie iba boolean 1. Vstup 0100h sa správa ako nulový druhý argument, 0101h ako 1. Selektor 3 po dosiahnutí prahu druhý argument ignoruje a povolí result=1.

BP a lokálny stack sa obnovia, argumenty odstraňuje caller. DS/ES/SS sa explicitne nemenia; BX/AX/FLAGS sa používajú ako pracovné registre. Caller sa nemá spoliehať na AH: napríklad nepodporovaný mode môže ponechať nenulové AH pri AL=0. Predpoklad platného DS a rámca patrí do vstupného kontraktu.

## Doložené call sites a gameplay hranica

Na **06B0:0B4F** sa odovzdáva mode=0. Druhý argument vytvára `CMP BYTE DS:0B5E,1; SBB AL,AL; NEG AL`: jeho low BYTE je 1 práve pri DS:0B5E=0, inak 0. Pred volaním je podmienka nenulového lokálneho agregátu. Po návrate sa testuje AL a pri nenulovom výsledku sa volá **0637:05FC**. Celá vstupná vetva a telo následnej akcie tu nie sú uzavreté; pomenovanie akčného/cooldown gate je lokálna rola, nie potvrdenie konkrétnej zbrane či projektilového algoritmu.

Na **0BDE:03B1** sa odovzdáva iba mode=1. Druhý argument v tejto vetve nie je potrebný, pretože ho gate nečíta. Frekvencia tohto call site, jeho zaradenie do schedulera a počet inkrementov za sekundu zostávajú otvorené. Z prahov preto nemožno vypočítať potvrdenú kadenciu v Hz. `caller_context.csv` uchováva byte-exact overené okná oboch miest, nie dôkaz úplného inventára všetkých priamych/nepriamych callerov.

## Controlled replay a reprodukcia

`audit_replay_pass1_action_gate.py IMAGE INVENTORY DECODER_DIR EMULATOR_DIR OUT` overí kanonický SHA, dáta, CFG začiatky a caller okná. Pôvodná funkcia sa vykoná bez mock callees pri load bázach 0 a 1000h:

- Mode=0: všetky 4 nominálne selektory × všetkých 256 čítačov × event WORDy 0,1,255,256,257.
- Mode=1: všetkých 256 čítačov; selektor nie je čítaný.
- Mode 2/FFFFh: vybrané čítače a eventy pre staticky spoločnú neaktívnu vetvu.

Spolu **10 768 prípadov, 0 odchýlok** v AL, čítači, DS, BP a SP po RETF. Prirodzené game state dáta a call schedule sa neseedujú zo zachyteného behu, preto je to controlled test. Nepodporované mode hodnoty sa netestujú exhaustívne cez celý WORD priestor; ich spoločná vetva je doložená statickým CFG.

Výstupy `pass1_action_gate/`: `instructions.csv`, `caller_context.csv`, `data_fields.csv`, `cases.csv`, `summary.json`, nová CSV/JSON mapa, promotion summary a nezávislá partition kontrola.

## Pokrytie

5 B prešlo z CLASSIFIED ONLY do PARTIAL. Aktuálne: **54 982 B PARTIAL, 2 269 B CLASSIFIED ONLY, 44 B UNKNOWN, 0 B DEEP VERIFIED**, spolu presne 57 295 B. Nezávislá kontrola 678 intervalov potvrdila SHA, presné členstvo a nulové diery/prekryvy.

Centrálny katalóg: **55 rozsahov, 1 944 inštrukcií / 4 727 B kódu**, 55 828 B typovaných dát celého obrazu a 54 980 B historických NON-CODE dát. Rozdiel 2 B voči PARTIAL zostáva neuzavretá relokácia. Controlled replay súčet je 24 761 plus osobitne 65 548 normalizačných prefixových prípadov. Prirodzené runtime testy zostávajú 0.

Lokálny gate je reprodukovateľne potvrdený v uvedenej doméne, ale širší gameplay/caller kontrakt zostáva PARTIAL. Najnovšia overená GitHub snímka 52924ebf849dd79d15af9d7c164b8304f50cae87 túto dávku ešte neobsahuje.

## Aktualizácia 13 oblastí

Metodika sémantického percenta: uzavreté jednotky / úplný inventár oblasti. Menovatele chýbajú; nové percentá sú N/A a predošlé orientačné.

| Oblasť | Predošlý odhad | Nové % | Nové potvrdenie | Neznáme / blokátor | Konkrétny ďalší krok |
|---|---:|---|---|---|---|
| Mapy a formáty | 99 % | N/A | bez nového dôkazu | prirodzené stavy | serializačná stopa |
| Dátové typy a konštanty | 95 % | N/A | 4 prahy + saturujúci BYTE | writeri a selektorová doména | DS:418F invariant |
| Tabuľky a ukazovatele | 93 % | N/A | unsigned prahové indexovanie | bounds mimo 0..3 | caller guardy |
| Funkcie / ASM / CFG | 90 % | N/A | 85 B / 33 inštrukcií, 10 768 prípadov | všetci calleri | priame/nepriame volania |
| RNG | 97 % | N/A | gate sám RNG nepoužíva | širšia akcia | 0637:05FC |
| Scheduler | 96 % | N/A | konkrétny inkrementačný caller | frekvencia a tick ordering | 0BDE:03B1 kontext |
| DEMO a vstupy | 96 % | N/A | input low BYTE gating | význam DS:0B5E | jeho writeri |
| Renderer / VGA | 94 % | N/A | bez nového dôkazu | clipping | render stopa |
| GUARD / bossovia | 93 % | N/A | bez nového dôkazu | AI/lifecycle | inicializátory |
| Zbrane / projektily | 92 % | N/A | lokálny akčný gate a následný call | identita a kadencia | telo 0637:05FC |
| Sprity / HUD / paleta | 92 % | N/A | bez nového dôkazu | asset identity | descriptor producer |
| SAVE / LOAD | 92 % | N/A | counter je file-backed mutable BYTE | reset/obnova po LOAD | serializačné rozsahy |
| Windows Win16 | 92 % | N/A | bez nového Win dôkazu | gate parity | Win ekvivalent |

## Runtime testy na vykonanie

Zachytiť oba call sites, mode, event low BYTE, selektor a counter pred/po prirodzenej akcii; sledovať, kedy sa vykoná 0637:05FC. Zmerať počet mode=1 volaní za tick/sekundu a správanie po LOAD/DEMO. Osobitne overiť prirodzené držanie/opakovanie vstupu pre selektor 3 oproti ostatným. Seedované selektory ani counter hodnoty nie sú dôkaz ich prirodzenej dostupnosti. DOSBox-X vykonanie zatiaľ chýba.
