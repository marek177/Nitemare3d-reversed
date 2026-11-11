# PASS1: DOS commit wrapper a handle flagy

Obraz SHA-256 `e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297`. Default DS=2771h. Všetky nové interpretácie sú PARTIAL, bez runtime testu.

`11EE:28B0` má rozsah `[14790,147E9)`, FAR ABI s WORD handle v SS:[BP+6], caller odstráni argument. Zachová SI/DI/BP. Záporný handle alebo handle >= signed WORD DS:2128 nastaví WORD DS:2118 na 9 a vráti FFFFh. Počiatočný limit je 20.

Pri platnom handle načíta BYTE DS:2120 do AL a DS:2121 do AH, porovná AX signed s 031Eh. Pri menšej hodnote vráti 0. Verziový WORD pri štarte vzniká `XCHG AL,AH; MOV SS:[2120],AX` na 11F37/11F39; konkrétne runtime hodnoty verzie v tejto dávke neboli odmerané. Porovnanie sa preto dokumentuje presne ako signed WORD, nie ako univerzálna verzionovacia politika pre všetky budúce DOS implementácie.

Pri vyššej/rovnakej hodnote vyžaduje bit 01h v BYTE DS:[212A+handle]. Ak chýba, nastaví CRT error 9 a vráti FFFFh. Inak volá `11EE:39D4`, obraz `[158B4,158C1)`: načíta BX=handle, nastaví AH=68h a vykoná INT 21h, potom skočí do spoločnej CF vetvy. Bez CF sa AX vynuluje. Pri CF sa volá spoločný mapovač chyby; celý jeho kontrakt zatiaľ nie je uzavretý. Wrapper uloží nenulový výsledok do WORD DS:2126, nastaví CRT error 9 a vráti FFFFh. Úspech je 0. Nejde o zatvorenie handle: primitív explicitne používa AH=68h.

| DS pole | Obraz, end-exclusive | Typ / počiatočný stav |
|---|---|---|
| 2118 | 29828..2982A | WORD CRT error, 0 |
| 2120 | 29830..29832 | minor BYTE + major BYTE, počiatočne 0 |
| 2126 | 29836..29838 | WORD native error, 0; spoločný mapovač zapisuje aj BYTE alias |
| 2128 | 29838..2983A | WORD handle limit, 20 |
| 212A | 2983A..2984E | počiatočné BYTE flagy pre 20 handles |

Presná veľkosť počiatočnej flagovej oblasti vyplýva z limitu a jednotkového indexovania, nie z veľkosti stream slotov. Neznámi writeri limitu môžu runtime rozsah zmeniť. Význam ostatných bitov sa touto dávkou neuzatvára.

Reprodukcia: `audit_pass1_crt_commit.py IMAGE PRIOR_MAP DECODER_DIR OUT`. Skript overuje SHA obrazu a predošlej mapy, rozhodujúce bajty a dekóduje wrapper, primitív, spoločnú vetvu a verziový zápis. CSV obsahuje 20 jednobajtových slotov a päť dátových polí. Výstup `pass1_crt_commit/` má **PARTIAL 12 191 B, CLASSIFIED ONLY 9 242 B, UNKNOWN 35 862 B, DEEP VERIFIED 0 B**. Prírastok 28 B pochádza z CLASSIFIED ONLY; súčet je presne 57 295 B.

DOSBox-X plán: platný/neplatný handle, verziové vetvy, bit 01h zapnutý/vypnutý, CF úspech/chyba po AH=68h a zmeny oboch error slotov. Ďalší krok: spoločný mapovač chyby a writeri handle flagov. Počet nových runtime testov je 0; úplný kontrakt wrappera a cleanup zostáva otvorený.

## Aktualizácia 13 oblastí

Nové sémantické percento všade N/A: chýba úplný inventár kontraktov/polí/vetiev. Metodika je uzavreté jednotky / úplný inventár danej oblasti, runtime parity osobitne. Historické percentá sú orientačné odhady.

| Oblasť | Predošlý odhad | Nové % | Nový dôkaz | Neznáme / blokátor | Ďalší krok |
|---|---:|---|---|---|---|
| Mapy a formáty | 99 % | N/A | bez nového dôkazu | mapový scan | tvorba objektov |
| Dátové typy a konštanty | 95 % | N/A | 28 B CRT globálov PARTIAL | error mapovanie | 11EE:05CA |
| Tabuľky a ukazovatele | 93 % | N/A | 20 počiatočných handle flagov | runtime limit | writeri 2128/212A |
| Funkcie / ASM / CFG | 90 % | N/A | AH=68h wrapper a verziové vetvy | mapovač chýb | spoločná CF cesta |
| RNG | 97 % | N/A | bez nového dôkazu | caller inventár | RNG ledger |
| Scheduler | 96 % | N/A | bez nového dôkazu | tick ordering | PIT spotrebitelia |
| DEMO a vstupy | 96 % | N/A | bez nového dôkazu | determinizmus | párová stopa |
| Renderer / VGA | 94 % | N/A | bez nového dôkazu | clipping/VGA stav | framebuffer/DAC |
| GUARD / bossovia | 93 % | N/A | bez nového dôkazu | lifecycle | helper 04C7:1692 |
| Zbrane / projektily | 92 % | N/A | bez nového dôkazu | kolízie | kolízne vetvy |
| Sprity / HUD / paleta | 92 % | N/A | bez nového dôkazu | resource binding | draw xrefs |
| SAVE / LOAD | 92 % | N/A | bez nového dôkazu | pointer restore | tabuľky po LOAD |
| Windows Win16 | 92 % | N/A | bez nového dôkazu | runtime selektory | DS callbacku |
