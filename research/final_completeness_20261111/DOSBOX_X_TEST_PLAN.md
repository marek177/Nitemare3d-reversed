# DOSBox-X — plán dôkazových testov, zatiaľ nespustené

Každý test musí zaznamenať SHA-256 EXE a dát, DOSBox-X verziu/build, konfiguráciu CPU/cycles/memory, boot a mount postup, segment load map, vstupy, počiatočný save alebo snapshot, breakpoint/watchpoint definície, počet tickov, úplný log a výsledok expected/actual. Adresy z normalizovaného BIN mapovať na runtime CS:IP až po potvrdení load/relocation mapy. Zatiaľ nejde o hotové debugger príkazy.

| ID | Scenár | Zachytiť | Akceptácia |
| --- | --- | --- | --- |
| RT01 | Startup a prvé vykonanie knižničnej služby | DS/ES/SS/CS, inicializované rozsahy a prvé read/write | každá interpretácia má producenta a spotrebiteľa; neznáme aliasy zostanú otvorené |
| RT02 | Životný cyklus service49 z historického PASS321 | počítadlo CS:20C4, výsledok helpera, všetky prístupy k CS:21C8 | potvrdiť bežný počet úspechov a producentov callbacku; nedosiahnutie 63 v jednom teste nie je dôkaz nemožnosti |
| RT03 | Nepriamy INT63 dispatch a FLAGS | interrupt frame, handler a callback pred/po | zdokumentovať úpravy uložených FLAGS a presnú návratovú cestu |
| RT04 | Projektil do steny/GUARD/hráča, plný pool | sloty, damage, RNG a poradie scheduleru | prvá divergencia voči statickému kontraktu lokalizovaná |
| RT05 | GUARD a bossové transformácie | stav, HP, timer, resource/sound a prechody | dosiahnuteľné aj zlyhávajúce vetvy oddelené |
| RT06 | Dve prehratia identického DEMO | vstup/tick, RNG stav a caller, stav aktérov | totožné stopy z identického počiatočného stavu |
| RT07 | SAVE/LOAD v prechodovom stave | serializované polia, cache, RNG, prvý tick po LOAD | rozdiely klasifikované podľa uložených/obnovovaných/odvodených polí |
| RT08 | Hraničné clipping situácie a HUD | framebuffer 64000 indexov, 768 DAC hodnôt, VGA registre/plane stav | pri párovom porovnaní prvá pixelová/DAC divergencia a presné vstupy |
| RT09 | DOS2.0 versus Win1.10 | osobitné autentifikované prostredia, ekvivalentný vstup a normalizovaný stav | explicitné rozdiely algoritmov; bez tvrdenia totožnosti odlišných platformových backendov |

RT02 je návrh na preverenie historických tvrdení, nie nové potvrdenie uvedených offsetov. Umelé nastavenie počítadla na 63 je fault injection a nedokazuje prirodzenú dosiahnuteľnosť. Win16 beh vyžaduje zdokumentované Windows prostredie.
