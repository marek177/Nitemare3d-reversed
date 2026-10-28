# Nitemare 3D — GUARD41 DOS V1.2 ↔ V2.0 interrupt-normalized fatal CPU trace

**Dátum:** 20. 10. 2026 · **Originálne runtime**, dva nezávislé nepatchované DOS buildy, autentické a SHA-256 overené N3DTRC01 záznamy. **Žiadna** originál-versus-remake 1:1 parita a žiadne nové zistenie o ukončení death animácie.

## Dva súkromné pôvodné dôkazy

* DOS V1.2 GUARD41: pôvodný 3642 CPU stop trace, SHA256 `da9f242b783e4ff607d54f51facecb283e2135449aad206f826fec6a6df07d1c`; súkromný ZIP `N3D_GUARD41_DEATH_SCORE_ADVANCED_V3_20261019.zip`.
* DOS V2.0 GUARD41: nový automatický, pôvodný 20000 CPU trace, SHA256 `b73a47225c9d869f90ce02d48088133a65fe9960fc3593e2aa13a633e609de17`; súkromný ZIP `N3D_GUARD41_DOS20_DEATH_V065_20261020.zip`.
* **Nový offline Python verifier** a súhrnný event CSV: `N3D_GUARD41_CROSSDOS_FATAL_ORDER_20261020.zip`, SHA256 `ab9b7209275bce2834b69b588cc80c691dc1e1dadf93b7a0d6d3f905821a2da3`. Tento malý balík je dodaný používateľovi oddelene, pôvodné CPU tracey ani komerčné herné súbory sa necommitujú.

## Behaviorálna chronológia v dvoch originálnych buildoch

| Pozorovaný stav | CPU ordinal DOS1.2 | CPU ordinal DOS2.0 | Výsledok |
|---|---:|---:|---|
| GUARD41 HP 111→0 | 1 | 1 | MATCH |
| RNG #16–18 state writes | 52/53,105/106,158/159 | rovnaké | MATCH |
| varianty `1→6→0`, reject/reject/accept | 74,127,180 | rovnaké | MATCH |
| GUARD header / linked WORLD frame | 215,218 | rovnaké | MATCH |
| timer / next-state / state | 223,225,227 | rovnaké | MATCH |
| Score 0→100 + carry high word | 256/257 | rovnaké | MATCH |
| Linked MAP marker A5→00 | 3642 | 4016 | MATCH effect; 374 extra CPU in V2 |

V oboch originálnych traceoch bol presne zachytený rovnaký priebeh 15 normalizovaných zápisov, width/previous/new a poradie. Death-selector RNG volania majú rovnaké CPU ordinals `22,75,128`, návratové AX `491,2995,11942`, rovnaké dve odmietnutia + akceptáciu. Rozdiel fyzických DOS segmentov/offsetov nie je behaviorálny rozdiel.

## Prečo má V2.0 pred MAP zápisom 374 CPU inštrukcií navyše

**Nový vykonaný výsledok: všetkých 374 krokov patrí jednej vloženej obsluhe prerušenia.**

* Pôvodný DOS V2.0 vykoná `OUT DX,AL` na `097A:0935` (CPU #1147); zodpovedajúci DOS V1.2 `OUT DX,AL` je `0979:0937` (#1147).
* DOS V2.0 potom vykoná presne **374 CPU inštrukcií** na segmente `1DE3` od `1DE3:4150` (CPU #1148) až po skutočné `IRET` na `1DE3:41B2` (#1521).
* DOS V2.0 obnoví prerušený parent na `097A:0936` (#1522), čo zodpovedá ďalšej pôvodnej DOS1.2 inštrukcii `0979:0938` (#1148).
* Po **odstránení týchto 374 ISR krokov len z porovnávacej projekcie**, zostáva presné párovanie **3642:3642 CPU inštrukcií**, v **7 správne párovaných kódových segmentoch**.
* Prvý opcode byte sa rovná v **3641/3641 čitateľných pároch**; pri CPU #209 má V2 `code_valid=0` (TLB code-lookahead unavailable), takže ho neoznačujeme za rozdiel ani ho nedopĺňame odhadom.
* `FLAGS` je úplne rovnaké v 3482 pároch; zostávajúcich 160 párov sa líši **výhradne Parity Flag bitom 0x04**, nie všetkými príznakmi.

**Hranica dôkazu:** vykonaná extra sekvencia, jej IRET a návratový bod sú preukázané. **Presný IRQ vektor/zariadenie zostáva OPEN.** CPU stopy sa fyzicky nerovnajú (jedna obsahuje ISR); prvý opcode byte nestačí na dôkaz rovnakých všetkých registrov, efektov, emulačných cyklov alebo game-pixel parity.

## Verifikátor

Súkromný ZIP `N3D_GUARD41_CROSSDOS_FATAL_ORDER_20261020.zip` obsahuje `verify_crossdos.py` (iba Python stdlib), `normalized_events.csv`, `verification.json`, SHA256 manifest a slovenskú správu. Overovač číta a kontroluje **pôvodné bytes oboch surových traceov**, súvislosť CPU/event seq, memory R/W previous-value, ISR IRET aj všetkých 15 normalizovaných eventov. Zámerné zmeny HP/score/branch/MAP/IRET boli zamietnuté **5/5** s vypnutou hash bránou počas negatívnych skúšok.

## Otvorený P0

1. DOS V2.0 po death handleri: pôvodný `GUARD state0→9→0x0A`, RNG #19 a neskoršie tick-y.
2. Item drop/slot lifecycle a všetky možné neinstrumentované/aliasované zápisy.
3. IRQ zariadenie/vektor a prípadný vplyv na DEMO timing; potom **original-versus-clean-room** normalizovaný state/VRAM/DAC zero-diff.

Globálne percentá 1:1 parity **nemeníme**. Toto je silný, ale presne ohraničený **original-versus-original** GUARD41 death-path dôkaz.
