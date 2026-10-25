# Nitemare 3D — nadväzujúci checkpoint: nepriame ciele a časovanie

Tento priechod nadväzuje na function_checkpoint_report. Celý GOAL zostáva neúplný. Počty kandidátov a otvorených nepriamych miest sa neznižujú.

## Konkrétne nové dôkazy

1. **VERIFIED_STATIC:** sedem DOS 2.0 nepriamych volaní má inštrukčne doložený pôvod ukazovateľa. Šesť je zásobovaných návratom ES:BX z INT 2Fh AX=4310, jedno používa uložený vektor 9 získaný cez INT 21h AH=35. Zahŕňa aj ES override pri dočasnej zmene DS v 0768:0810. Podmienky a hranice dôkazu sú v indirect_provenance_report.md a indirect_target_provenance.json.
2. **VERIFIED_RUNTIME:** v relácii ses-3 je na PC 0F8B:079D, DS=2F94 uložený poskytovateľ `C3FF:0010`; hodnota sa zhoduje s návratom ES:BX. Na PC 0ED3:015B je v 2F94:3F52 uložený predchádzajúci vektor `F000:E987`, zhodný s DX:AX. Dôkaz sa vzťahuje na inicializačné zápisy, nie na vykonané spotrebiteľské volania. Tieto runtime adresy nie sú univerzálne pre iné behy alebo emulátory.
3. **VERIFIED_RUNTIME:** päť krátkych vzoriek programu sa zhoduje s DOS 2.0 rozbaleným load image po aplikácii MZ relokácií pri load base 0823. Rozbalený MZ vstup bol dvakrát zachytený na 1A11:0018, zodpovedajúcom logickému 11EE:0018. Nejde o byte-for-byte audit celého RAM obrazu.
4. **VERIFIED_RUNTIME:** pôvodná textová obrazovka preukázala `Error opening file nite3d.bsf.` Pracovná kópia tento súbor neobsahovala; po jeho doplnení s SHA-256 `565e504e17f8b8ddc14a1bb8b71d41c6465ac2f9f5589db4b57e54f83ccb6291` originál dosiahol ďalšie inicializačné breakpointy. Predchádzajúci BIOS wait preto nebol dôkazom dokončeného štartu hry. Textový buffer po ďalšom štarte môže obsahovať starý výstup; stará obrazovka sa nepoužíva na hodnotenie nového behu.
5. **VERIFIED_STATIC + obmedzené VERIFIED_RUNTIME:** funkcia 15BF:2E41 je 21-bajtová NEAR rutina s 15 inštrukciami. Uloží AX/BX/CX/DX, zavolá INT 1Ah s AX=0, vypočíta target16=(BX+DX) modulo 65536 a opakuje INT 1Ah, kým unsigned DX<=target16. Potom obnoví registre a vykoná RET. Stok CPU udalostí v relácii ses-3 zachytáva vnútornú slučku a BIOS obsluhu pri runtime CS=1DE2; vstup a výstup funkcie zachytené neboli. Dvojsekundový continue/pause zaznamenal šesť BIOS tickov; toto nie je požadovaná normálna rýchlosť originálu ani kalibrácia parity.

## Dôsledky pre rekonštrukciu

Pri časovači je porovnanie prísne: DX==target ešte opakuje slučku. Aj BX=0 teda v lokálnom modeli vyžaduje neskorší dolný tick. Používa sa iba DX, nie celé CX:DX ani modulárny rozdiel uplynulého času. Pri target16=FFFF neexistuje 16-bit DX spĺňajúci ukončenie DX>target; tento lokálny záver nepreukazuje dosiahnuteľnosť takej situácie v bežnej hre. Porovnávací model bol vyčerpávajúco skontrolovaný pre všetkých 65536 DX a šesť cieľových hodnôt, spolu 393216 syntetických porovnaní. Nie je to originálny edge-case runtime ani remake parity test.

Statický import, skutočný pointer pri inicializácii a vykonaný indirect CALL sú tri odlišné dôkazové kroky. Tretí zatiaľ chýba. Callback breakpointy boli pridané po inicializačných zápisoch a v krátkom nasledovnom úseku neboli dosiahnuté; nevyvodzujeme z toho nedosiahnuteľnosť. Ďalší replay ich má nainštalovať ešte pred rozbaleným vstupom.

## Nadväzujúci experiment

Zopakovať štart so zachovaným úplným vstupným manifestom a consumer breakpointmi už pred vstupom 11EE:0018. Zachytiť aspoň jeden skutočný FAR CALL cez provider slot a jeho návrat. Potom prejsť na main-loop/OBJECT a seed-to-EOF DEMO ledger. Runtime adresy odvodzovať od nového load base, nie slepo prebrať C3FF/F000 z tohto behu. Zostáva 48 otvorených DOS 2.0 nepriamych miest a všetky P0 parity brány.

