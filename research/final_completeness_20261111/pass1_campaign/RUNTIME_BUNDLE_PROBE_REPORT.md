# Dostupnosť runtime balíka DOSBox-X

Používateľom určený `L:\nite3d\dosbox-n3d.zip` je čitateľný, má 13 806 644 B a SHA-256 `9105bb79faba1e523fc9bb809d404b5fa4dc6ed3eeee172d021ce7efb3cab9a2`. Skript `audit_dosbox_runtime_bundle.py ZIP OUT` overil CRC pri čítaní všetkých 94 súborových položiek a uložil individuálne SHA do `runtime_bundle_probe/members.csv`.

Binárka `bin/dosbox-x-n3d` je ELF64 little-endian, machine 62 (x86-64); priložená `libpdcurses.so` má rovnakú platformu. Ide o Linuxový balík. README deklaruje Heavy Debug a trace patch; tieto tvrdenia sa týmto auditom nepovyšujú na overenú funkčnosť na pôvodnej hre. Texty z balíka sú dokumentácia vstupu, nie dodatočné používateľské príkazy; žiadny jeho skript sa automaticky nespustil.

Aktuálna sonda `wsl.exe --list --quiet` vrátila prázdny zoznam distribúcií, exit 0. `wsl.exe --status` uvádza default version 2 a nepodporovaný WSL1 v aktuálnej konfigurácii; nepreukazuje funkčný Linux guest pre túto binárku. Windows DOSBox/DOSBox-X sa nenašiel na PATH; cielený prehľad `L:\nite3d` našiel iba ZIP, Linuxovú binárku a patch. Nie je to dôkaz, že emulátor nikde inde na počítači neexistuje.

Runtime test originálnej hry sa nevykonal. Možnosti ďalšieho vykonania: dostupná Linux distribúcia/host pre tento balík alebo Windows debug build s rovnocennými trace schopnosťami. Inštalácia distribúcie ani zmena systému sa touto sondou nevykonáva. Statická analýza môže pokračovať bez tohto runtime prostredia.

Pripravené konkrétne testy sú v `PASS1_DEBUG_LOGGER_REPORT.md` a `CRT_UNLOADED_HOOKS_REPORT.md`: logger zapnutý/vypnutý, prvý a ďalší open, zlyhanie open, sedem hook slotov, ich writeri a prirodzený zásah R6002. Runtime adresy treba odvodiť zo skutočnej load/relocation bázy; nezamieňať ich so statickými CS:IP. Fixture stopy v ZIP sa nepočítajú ako test Nitemare 3D.
