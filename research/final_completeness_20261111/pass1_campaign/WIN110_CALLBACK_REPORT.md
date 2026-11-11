# Win1.10 — callback sloty a segmentové predpoklady

11. 11. 2026. PARTIAL, nové DEEP VERIFIED 0 B, runtime testy 0. Skript `audit_win110_callback_slots.py` kontroluje originálny SHA-pinned EXE a explicitné bajty deviatich inštrukčných miest; nevyvodzuje globálny zoznam nepriamych cieľov.

## Dátové hranice

NE automatic data segment index = 10, initial SS segment index = 10, encoded SP = 0. Sú to indexy loadera; konkrétne runtime selektory a výpočet výsledného SP nie sú týmto uzavreté.

V súborom podloženom segmente 10 je `[20D0,20DC)` presne 12 nulových bajtov, file interval `[0x2E110,0x2E11C)`. V expandovanej tabuľke 6 082 relokačných miest nemá tento blok žiadny prekrývajúci sa loader zápis. To neznamená, že doň počas inicializácie alebo cez alias nezapisuje program či externá rutina.

| Relatívne pole | Statický typ podľa použitia |
|---|---|
| DS:20D0 | offset WORD nepriameho FAR pointera |
| DS:20D2 | selector WORD toho istého pointera, zároveň podmienka zapnutia |
| DS:20D4,20D6 | dva WORD argumenty prenášané do AX a DX pred prvým callbackom |
| DS:20D8,20DA | dva WORD argumenty prenášané do AX a DX pred druhým callbackom |

Mapovanie týchto DS-relatívnych polí na segment 10 vyžaduje príslušný runtime segmentový invariant. Počiatočná zhoda deklarovaného DS a SS ho nedokazuje pre všetky časy a všetkých callerov.

## Lokálny kontrakt troch callsites

`2:382F PUSH SS; 2:3830 POP DS` predchádza `2:3831 MOV CX,[20D2]`. `2:3835 JCXZ 3860` pri nule preskočí obe volania. Na vetve k prvému volaniu nie je medzi nastavením DS a `2:3849 CALL FAR [20D0]` iné volanie; DS tu teda označuje aktuálny SS. Prvý callback dostane BX=0, AX z DS:20D4, DX z DS:20D6 a SI načítané z ES:002C po načítaní ES z DS:0864. Význam týchto parametrov ostáva otvorený.

Po prvom callbacku rozhoduje `2:384D JAE 3852` o CF. Pri CF=1 vedie skok na 2:39CC; pri CF=0 kód načíta AX/DX z DS:20D8/20DA, nastaví BX=3 a na 2:385C volá znovu `[20D0]`. DS medzi oboma volaniami explicitne neobnovuje. **Ak prvý callback DS zmení, druhý pointer a argumenty môžu pochádzať z iného segmentu.** Bez ABI sa tieto dva ciele nesmú automaticky zlúčiť.

Na 2:396B sa testuje incoming DS:20D2; JCXZ na 2:396F pri nule preskočí volanie 2:3974. Pri nenulovej hodnote je BX=2 a vykoná sa CALL FAR [20D0]. Táto lokálna rutina pred volaním DS nenastavuje. AX/DX/SI kontrakt nie je uzavretý.

Zjednodušený pseudokód iba tejto lokálnej vetvy:

```text
DS = current_SS
if word(DS:20D2) != 0:
    ES = word(DS:0864)
    SI = word(ES:002C)
    AX = word(DS:20D4); DX = word(DS:20D6); BX = 0
    far_call(dword(DS:20D0))  // ABI aj clobbers otvorené
    if CF: goto 2:39CC
    AX = word(current_DS:20D8); DX = word(current_DS:20DA); BX = 3
    far_call(dword(current_DS:20D0))
goto 2:3860
```

Pseudokód zachováva možnú zmenu DS a neprezentuje nenájdený cieľ ako známu knižničnú funkciu. Nulový počiatočný blok by pri zachovaní hodnôt a segmentového invariantnu vetvu vypol; nejde o dôkaz, že všetky tri volania sú počas hry nedosiahnuteľné.

## Katalóg a ďalší krok

`win110_callbacks/indirect_sites.csv` katalogizuje všetkých 13 nepriamych control sites z ohraničeného CFG: 12 volaní a jeden skok. Zaznamenáva presné bajty, vlastnícke korene a segmentové obmedzenia; target sets zostávajú UNKNOWN. `summary.json` eviduje nulový blok, jeho hash, file offset a výsledok kontroly fixupov.

Reprodukcia: `python audit_win110_callback_slots.py WIN110_EXE CFG_DIRECTORY FIXUP_DIRECTORY OUTPUT_DIRECTORY`.

Najbližšie: hľadať producentov zápisov do 20D0..20DB v úplnom relevantnom CFG vrátane aliasov; pri runtime nastaviť watchpointy na výsledný SS/DS blok a zaznamenať DS pred/po prvom callbacku. Vynechané alebo neinicializované polia nesmú dostať názov podľa hypotetického runtime ABI.

DOSBox-X test vyžaduje bežiace Windows prostredie pre túto Win16 binárku: zaznamenať inicializáciu loadera, SS/DS, prvý zápis do slotu, cieľ callbacku, BX režimy 0/3/2 a návratové CF/DS. Tento test sa zatiaľ nespustil. DOS NON-CODE inventár ani percentá parity sa nemenia.
