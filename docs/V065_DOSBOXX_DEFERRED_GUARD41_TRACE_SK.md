# Nitemare 3D — DOSBox-X Advanced History v3: odložený CPU trace (v0.65 draft)

**20. október 2026. Nástrojový patch, nie nové vykonanie hry.**

## Problém

Pôvodný N3D_TRACE_AUTOSTART=1 nahráva už od BIOS/DOS štartu. CPU stopa tak často vyčerpá 32 až 128 MB skôr, než sa spustí gameplay. Pri manuálnom DEBUGBOX / N3DTRACE START / RUN bolo v prostredí Linux Xvfb a PDCurses ovládanie okna nespoľahlivé. Nejde o dôkaz chyby pôvodného Nitemare 3D death handlera.

## Doplnok k upravenému DOSBox-X v3

Súbor tools/dosbox-x/n3dtrace_deferred_start_v3.patch sa aplikuje až PO pôvodnom N3D Advanced History v3 source patchi na src/debug/n3d_trace.cpp. Existujúci binárny formát N3DTRC01 a ručné príkazy START/STOP zostávajú bez zmeny.

Nové konfiguračné premenné:

| Premenná | Funkcia |
|---|---|
| N3D_TRACE_START_CSIP | Odložený štart len na zadanej runtime CS:IP |
| N3D_TRACE_START_OPCODE4 | Voliteľná kontrola prvých štyroch bajtov CPU kódu, napr. 26886410 |
| N3D_TRACE_START_ES_SI | Voliteľná kontrola aktuálneho ES a dolných 16 bitov ESI na identifikáciu GUARD aktéra |
| N3D_TRACE_INSTRUCTION_LIMIT | Po N skutočných CPU inštrukčných záznamoch zavrieť session; 0 = bez limitu |
| N3D_TRACE_STOP_BREAK | Pri pôvodnom STOP_CSIP: 1 = zastaviť debugger, 0 = len uzavrieť trace a pokračovať |

Pri START_CSIP má odložený štart prednosť pred AUTOSTART, takže sa neplní disk už počas bootu. Spustenie je jednorazové. Opcode kontrola používa len priamo mapovanú RAM cez TLB; pri nečitateľnom/opakovanom nesprávnom kóde trace neštartuje.

### Príklad pre pôvodný DOS V2.0 GUARD41 death

    export N3D_TRACE_DIR="$PWD/guard41-death-capture"
    export N3D_TRACE_AUTOSTART=0
    export N3D_TRACE_START_CSIP=0CEB:1333
    export N3D_TRACE_START_OPCODE4=26886410
    export N3D_TRACE_START_ES_SI=2A21:2A78
    export N3D_TRACE_INSTRUCTION_LIMIT=20000
    export N3D_TRACE_MEMORY=1
    export N3D_TRACE_READS=1
    export N3D_TRACE_IO=0
    export N3D_TRACE_VRAM=0
    export N3D_TRACE_VGA_REGS=0
    export N3D_TRACE_FRAME_EVERY=0
    export N3D_TRACE_RGB_EVERY=0
    export N3D_TRACE_STOP_BREAK=0
    export N3D_TRACE_LIMIT_MB=64

Spusť vlastnú pôvodnú DOS V2.0 hru s prirodzene vybraným DEMO.1 cez DOSBox-X s nainštalovaným v3 + overlay patchom. Záznam sa má začať AŽ pri overenom HP writeri. Po 20000 vykonaných CPU inštrukciách sa má automaticky uzavrieť s explicitným dôvodom INSTRUCTION_BUDGET bez ďalšieho RUN/STOP.

Pre N3D-UNFU.exe so SHA256 552d250ef773014a7f56ecdd7939559005fa990ebc7a6e435e6a7a49d372f301 je HP writer na MZ-load-image offsete 0x5FA3 (fyzický file offset 0x61A3) a jeho bajty sú 26 88 64 10. Runtime CS:IP 0CEB:1333 a ES:SI 2A21:2A78 sú len JEDNA predtým overená relokácia a identita aktéra, nie univerzálne adresy všetkých behov. Pri inej relokácii najprv vypíš aktuálne registre a uprav obe hodnoty.

## Acceptance gates pre GUARD41

- Overený pôvodný CPU writer HP 111→0 a GUARD identita, nie iný actor pri spoločnej funkcii.
- Volania RNG #16–18 s rejection/accept branch a následné skóre 0→100.
- MAP marker A5→00 a presný návrat z príslušného GUARD41 death handlera.
- V samostatnom ďalšom viac-tickovom meraní state 0→9→0x0A, RNG #19, nový scheduler a možný drop/pool cleanup.
- Porovnanie V1.2 ↔ V2.0 podľa normovaných aktérov, nie podľa rozdielnych DS offsetov.
- Originál versus moderný clean-room port je ďalšie osobitné zero-diff prijímacie kritérium.

## Dôkazy a stav implementácie

GPLv2-or-later testovací fixture tests/fixtures/dosboxx/n3d_trace_v3.cpp je priamo rekonštruovaný z používateľom dodaného v3 source patchu (586 riadkov), nie z komerčného Nitemare EXE. Automatizované testy kontrolujú aplikovateľnosť overlay cez git apply, odmietnutie poškodeného v3 základu, opakovanej aplikácie, poradie CSIP + ES:SI + opcode brány pred START a nepozastavujúci budget STOP.

**Neoverené:** zostavenie celého DOSBox-X, chod N3DTrace_Instruction() pri nepozastavenej originálnej hre, úspešný headless gameplay trace, konečné CPU poradie death handlera a celková 1:1 parita. Pretrvávajúci problém príkazu RUN nemožno považovať za automaticky odstránený len z úspešnej testovanej aplikácie patchu. Ak heavy-debug callback nie je v normálnom behu volaný, tento overlay sám o sebe nestačí.

Žiadne pôvodné komerčné EXE, súbory IMG/MAP/OBJECTS ani surové súkromné pamäťové dumpy nie sú súčasťou návrhu.
