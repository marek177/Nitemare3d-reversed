# Nitemare 3D — hodiny, zmenové počítadlá a oprava rozsahu VGA dôkazu

## Overené časovacie funkcie DOS 2.0

Na EXE SHA-256 `5ad15f66a4478de21e4c74799a74d35d606f3bdb7406a5b40168cfbd5ba2c9a3` boli znovu dekódované a inštrukčne rekonštruované tieto ohraničené telá. **VERIFIED_STATIC** označuje miestnu sémantiku; závislosti, dosiahnuteľnosť a všetky okrajové runtime cesty zostávajú samostatné otázky.

| Funkcia | Doložený kontrakt |
|---|---|
| 0BCC:0002 | IRQ obsluha nastaví relokované DS, INC dword DS:081E, vykoná portový sled 70/71/A0/20, obnoví registre a IRET. |
| 0BCC:0074 | Podľa parametra inštaluje/obnovuje vektor70, vybrané registre a bit masky na porte A1; má guard DS:16F0. |
| 0BDE:0018 | Vyberá BDA vetvu low32((ticks-baseline)*55) alebo fallback helper-buffer výpočet low32(dword*1000+word). Úplný význam fallback helpera zostáva otvorený. |
| 0BDE:0094 | Pri DS:3CCF=0 obnoví cache cez 0018; inak vracia cache DS:081E/0820. |
| 0BDE:00AE | Vytvorí 32-bit deadline z času a unsigned word parametra; unsigned now>=deadline ukončuje čakanie vrátane rovnosti. |
| 0BDE:00D4 | q=((time<<3) mod2^32)/1000; pri q!=predošlé_q zvýši sekvenciu presne o1. |
| 0BDE:0114 | q=low32(u32(sign_extend16(rate))*time)/1000; pri zmene q zvýši sekvenciu presne o1. |

Zmenové počítadlá **nedobiehajú všetky preskočené pásma**. Napríklad 00D4 pri time=1000, old_q=0, old_seq=7 vráti q=8 a seq=8, nie15. Posun/multiplikácia pred unsigned delením má 32-bit truncation. Pri time=20000000h sa ľavý posun o3 zmení na0; neobmedzená aritmetika by dala iný výsledok. Rutina0114 vykoná MOVSX pre rate, potom unsigned MUL a po vymazaní EDX unsigned DIV. Negatívny word nemožno svojvoľne interpretovať ako signed delenie. Tieto okrajové prípady sú syntetické matematické kontroly, nie injektované situácie v origináli.

Čakanie 00AE končí pri rovnosti, na rozdiel od predtým analyzovanej 15BF:2E41, ktorá pri rovnosti ešte opakuje. Ani jedna sa nesmie bez dôkazu nahradiť všeobecným modulárnym elapsed-time testom. Jednotky a presná rýchlosť všetkých zdrojov času sa nevyvodzujú iba z konštanty1000.

## Pôvodný runtime zápis a watchpoint

**VERIFIED_RUNTIME:** clean_run_b/ses-1, loadbase0822. Na 13EE:000F bolo zachytené `INC dword DS:081E`, DS=2F93, s prechodom `0000370A→0000370B`. Stopa má24 CPU udalostí: zahŕňa portové inštrukcie a IRET späť do časovacieho volajúceho. Po prerušení sa ešte vráti už pred IRQ odčítaná hodnota370A; ďalšie čítanie cache načíta370B. Ide o poradie vzorkovania, nie dokázaný torn-read pri pretečení.

Samostatný platný memory-change watchpoint na linear0003014E zastavil ďalší zápis s PC13EE:0014 a prechodom `00003A18→00003A19`. Vytvorenie s once=true bolo výslovne odmietnuté CAPABILITY_UNAVAILABLE; once=false fungovalo a watchpoint bol následne odstránený. Odmietnutý pokus sa nepočíta ako watchpoint hit. Správny reproducer musí kontrolovať odpoveď create pred pokračovaním. Nie je tým zmeraná frekvencia IRQ ani uzavreté všetky zápisy.

## Oprava predchádzajúceho označenia framebufferu

Zachytených64000 bajtov A000 je reálny runtime obsah CPU pamäťového okna, **nie zatiaľ overený kompletný lineárny obraz**. BIOS byte13h sám nestačí. Statický inicializátor0156:0A66 po INT10h s AX=13h mení sequencer index4 výrazom `(AL&F7h)|04h`, ďalšie graphics registre a CRTC. Iné kresliace rutiny zároveň posúvajú X o2 bity doprava, vyberajú masku na3C4/3C5 a používajú stride50h. Pred použitím raw A000 dát ako pixelov treba zachytiť mapovanie rovín, display start/pitch a DAC.

[Primárna dokumentácia DOSBox-X](https://github.com/joncampbell123/dosbox-x/blob/master/README.source-code-description) uvádza, že VGA stav určuje podľa registrov, nie iba podľa INT10 režimu. To podporuje potrebu uvedenej kontroly; nie je to meranie registrov konkrétneho uloženého záberu. Jeho dekódované obrazové usporiadanie preto zostáva UNKNOWN. Pôvodné raw bajty a hash sa zachovávajú. Tvrdenie o64000 dekódovaných pixeloch sa nepoužíva na parity gate.

## Ďalší postup

Zachytiť prirodzené vstupy a výstupy 00D4/0114 v hlavnej slučke, poradie ich konzumentov a následné OBJECT/RNG operácie. Doplniť úplný fallback helper0018→11EE:2AEA. Pri novom VGA meraní získať skutočné registre/roviny/DAC alebo overený renderovaný výstup. P0 main-loop, timing a renderer zostávajú otvorené.

