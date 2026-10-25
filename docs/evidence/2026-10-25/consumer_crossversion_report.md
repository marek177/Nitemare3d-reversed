# Nitemare 3D — vykonaný nepriamy callback a cross-version resolver

## Nové overené výsledky

**VERIFIED_RUNTIME:** čistý beh `clean_run_b`, relácia `ses-1`, load base `0822`: originál zastal na `0F8A:07B0`, logicky `0768:07B0`. FAR CALL cez `2F93:350E` prešiel do `C3FF:0010` a vrátil sa na `0F8A:07B4`. SP sa zmenil `E7E6 → E7E2 → E7E6`; vrchol stacku po vstupe obsahuje návratové IP `07B4` a CS `0F8A`. Tak je doložená jedna vykonaná nepriama hrana aj jej návrat, nielen hodnota inicializovaného ukazovateľa. V tejto výzve AX=0800 a návrat AX=FA40, DX=FA40, BX=0000. Význam celej externej implementácie a ostatné command varianty tým nie sú rekonštruované. Dôkaz je v observed_indirect_invocations.json a v oddelenej runtime prílohe.

**VERIFIED_STATIC:** celá 37-bajtová lokálna rutina získania poskytovateľa bola porovnaná vo všetkých ôsmich dostupných DOS obrazoch. Po nahradení výlučne dvoch adresných displacementov symbolickým slotom a vyjadrení priamych branch cieľov relatívne k vstupu sú všetky inštrukcie, ich veľkosti, registre, ostatné konštanty a vetvy zhodné. Toto je ohraničená zhoda algoritmu inicializátora, nie celého DOS gameplayu ani externých interrupt handlerov.

| Obraz | Logický vstup | DS slot offset/segment |
|---|---|---|
| local_dos_12 | 0742:078C | 34A8/34AA |
| local_dos_cd | 0767:078C | 34BA/34BC |
| nite3d10 | 0739:05F0 | 33B2/33B4 |
| nite3d11 | 0742:0780 | 34AC/34AE |
| nite3d15 | 0747:078A | 347C/347E |
| nite3d17 | 0751:0786 | 3480/3482 |
| nite3d19 | 0767:078A | 350C/350E |
| nite3d20 | 0768:0784 | 350E/3510 |

Kanoničký version_function_mapping.csv teraz obsahuje sedem skutočných overených párov voči DOS 2.0; pôvodný index byte-stream podpisov je zachovaný oddelene vo version_function_signature_index.csv. Presné normalizované inštrukcie a hashy sú v crossversion_provider_mapping.json. Win16 zhoda sa týmto priechodom netvrdí.

**VERIFIED_RUNTIME:** po ďalšom úseku originálu bol v BIOS údajoch potvrdený režim 13h. Lokálne sa zachytilo 64000 bajtov A000 framebufferu, SHA-256 `986596cbf1af641a5d95f34bb15b41f0b94328ec576d6311c8ea67b53de2e302`, so šiestimi odlišnými indexmi. Záber nie je zarovnaný na hranicu frame; aktuálne herné/menu štádium nebolo identifikované. DAC sa nezachytil a chýba párovaný remake frame. Tento výsledok preto neuzatvára renderovaciu paritu.

## Reprodukovateľnosť a izolácia emulátora

Nový session.start v starom procese nedosiahol požadovaný rozbalený vstup v pozorovanom úseku. Po autoritatívnej kontrole bežiacej relácie a jej pozastavení bolo z IVT načítané INT08=`1DE2:4150` a INT09=`0ED3:0000`, teda adresy obslúh predchádzajúceho behu. To je priamy dôkaz pretrvávania platformového stavu cez session.stop/start. Príčinné priradenie konkrétneho neúspechu k týmto IRQ zostáva INFERRED.

Reštartovaná bola iba overená testovacia inštancia tohto chatu, nie iný DOSBox-X proces používateľa. Nová inštancia dostala oddelený pipe aj adresár dôkazov. Load base sa zmenil z predošlého 0823 na 0822; callback segmenty a dátový segment boli odvodené z nového vstupu. Spotrebiteľské breakpointy boli nastavené ešte pred rozbalením. Čistý replay následne vykonal uvedený FAR CALL a návrat. Nezávislé štarty sa odteraz nesmú považovať za čisté iba na základe session.stop.

## Čo zostáva otvorené

Ostatných päť consumer breakpointov bolo nastavených, ale v nasledujúcom ohraničenom úseku neboli dosiahnuté. Z toho nevyvodzujeme nedosiahnuteľnosť. Pre 0768:07B0 máme jednu pozorovanú adresu, nie úplnú cieľovú doménu vo všetkých prostrediach. Počet 48 otvorených DOS 2.0 nepriamych miest sa nemení. Ďalej treba sledovať allokáciu/prenos/uvolnenie provider pamäte, IRQ chaining, main-loop/OBJECT a seed-to-EOF RNG ledger; renderer stále potrebuje zarovnaný originál/remake indexed+DAC pár. Celý GOAL zostáva neúplný.

