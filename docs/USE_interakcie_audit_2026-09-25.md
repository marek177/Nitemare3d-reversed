# USE / interakcie — audit rekonštrukcie C++

Dátum: 25. 9. 2026

## Výsledok a hranica dôkazu

Pri kontrole zdrojov z `marek177/Nitemare3d-reversed` sa reprodukovala jedna
konkrétna chyba pri spoločnom použití dvoch hlavičiek. Minimálna lokálna oprava
odstraňuje druhú definíciu `hasAllPentagrams` a používa kanonickú implementáciu
z `InventoryRuntime.hpp`. Zachováva doterajšie hodnoty konštánt a správanie
existujúcich pomocných funkcií.

Toto je audit C++ rekonštrukcie a syntetických kontraktov, nie nová disassemblácia
NITE3W.EXE. Originálny EXE ani jeho úplný assemblerový export neboli v tomto behu
sprístupnené. Nevykonal sa beh pôvodnej hry, porovnanie trezorových kombinácií,
nové pomenovanie pôvodných FUN_* funkcií ani meranie pokrytia celého USE.
GitHub ani Google Drive sa nemenili.

## 1. Potvrdená integračná chyba: dvojitá definícia

`InventoryMask` je alias `std::uint8_t`. Tieto deklarácie preto nie sú dve
odlišné preťaženia:

```cpp
// InventoryRuntime.hpp
constexpr bool hasAllPentagrams(InventoryMask mask) noexcept;
// RecoveredInteractionFacts.hpp
constexpr bool hasAllPentagrams(std::uint8_t mask) noexcept;
```

V oboch hlavičkách je aj telo funkcie a obe sú v `nitemare3d::game`.
Ich vloženie do jednej prekladovej jednotky vyvolá `redefinition`.
`#pragma once` bráni opakovanému spracovaniu rovnakej hlavičky, nie konfliktu
dvoch samostatných hlavičiek.

Reprodukcia: GCC 14.2.0 a Clang 17.0.0, oba poradia `#include`: štyri zlyhania.
Po oprave: tie isté štyri kontroly prešli.

Oprava je v `01_fix_duplicate_pentagram.patch`. Mení iba
`src/game/RecoveredInteractionFacts.hpp`: pridáva include kanonickej hlavičky,
viaže `kPortalPentagramMask` na `kAllPentagramsMask` a odstraňuje duplicitné telo.
Nie je to tvrdenie, že pred opravou musel zlyhávať celý existujúci projekt:
chyba sa prejaví pri spoločnom vložení oboch hlavičiek.

## 2. Potvrdená hranica integrácie: hlavná akcia portu je len push

V skontrolovanom `src/main.cpp` vetva `input.actionPressed` vyberie smer a volá
`world.beginPush(...)`. V tejto vetve nie je volanie plného USE dispatchera pre
dvere, terminály, trezory alebo ponuky výťahov. `LevelState.cpp` poskytuje pohyb
posúvateľných objektov, ale toto volanie nie je všeobecná interakcia s bunkou.

Existencia dokumentácie a pomocných funkcií preto nedokazuje zapojenie všetkých
interakcií do aktuálneho SDL spustiteľného programu. Tento audit hlavnej slučky
nie je vyčíslením implementačného percenta.

## 3. Kartové masky: širšie API nie je automaticky herná chyba

Kanonický inventár používa bajt, zatiaľ čo `hasCard` v staršej hlavičke prijíma
16-bitovú masku a povoľuje indexy do 15. Napríklad `hasCard(0x0100, 8)` vráti
true. Takúto masku však nemožno získať z jediného 8-bitového inventárneho poľa.

Pre všetkých 256 bajtových masiek a všetkých 256 indexov sa overilo, že
staršia funkcia a kanonický bajtový model dávajú zhodné výsledky. Nenašiel sa
teda rozdiel v tomto platnom vstupnom rozsahu. Minimálna oprava zámerne nemení
verejné 16-bitové API bez kontroly jeho všetkých používateľov.

Samostatný voliteľný helper `use::hasRequiredCard` používa explicitne bajtový
kontrakt. Kontrola indexov mimo 0..7 je moderná ochrana; nie dôkaz toho, čo
originálny EXE robí s poškodenými dátami. Iba bitom 0/1 sú pridelené existujúce
názvy červená/žltá karta; helper nevymýšľa názvy ďalších predmetov.

## 4. Kľúčové brány: odčítanie triedy samo osebe nie je validácia

`warpKeyBitForClass` vypočíta `mappedWallType - 0x19` a výsledok zúži na bajt.
Zmysluplná rodina kľúčových brán je 0x19..0x1C. Pre 0x1D funkcia vráti 4;
chybný caller, ktorý vynechá kontrolu rodiny, by následne mohol prijať bit 0x10.

Toto je preukázaná vlastnosť pomocného API a podmienka jeho bezpečného použitia,
nie preukázaný chybný caller v pôvodnej hre alebo súčasnej hlavnej slučke.

Voliteľný `use::canUseColoredKeyGate` najprv overí rodinu a až potom príslušný
bit. Overených bolo všetkých 256 typov × 256 bajtových masiek proti explicitnej
štvorici pravidiel. Helper nevykonáva teleportáciu, zmenu mapy ani spotrebu kľúča.

## 5. Vstup USE: model spoločnej nábežnej hrany

Nový voliteľný `use::isRisingEdge` modeluje bit 0x0200 ako nový stisk:
aktuálne nastavený, predtým nenastavený. Overili sa všetky 16-bitové aktuálne
masky pri oboch hodnotách predchádzajúceho USE bitu; ostatné predchádzajúce bity
boli nastavené. Pridaný je aj syntetický priebeh držania dvoch klávesov, ktoré
predstavujú jednu akciu.

Skontrolované `SDLVideo.cpp` už filtruje klávesové opakovanie cez
`!event.key.repeat`. Každý samostatný nový stisk Space alebo E však generuje
`actionPressed`. Druhý kláves stlačený pri stále držanom prvom môže teda poslať
ďalšiu akciu, hoci zložený USE bit zostáva nastavený. Ide o staticky odvodenú
odlišnosť od modelu jedného spoločného bitu; živý SDL test neprebehol.
Tento balík nemení SDL obsluhu vstupu a netvrdí, že ju opravil.

## 6. SAFE/TRUNK: čo sa týmto krokom neuzavrelo

Skôr publikované `docs/USE_INTERACTION_RE.md` spája objektové typy 0x26/0x27
s `seg3:AD9E` a kombinačný prompt s typom 0x26. Aktuálne prečítaný register
`docs/UNKNOWN_SYSTEMS_AUDIT_2026-09-22.md` naďalej uvádza SAFE/TRUNK/radio/
special-station handlery ako otvorené.

V tomto kroku nepribudol priamy assemblerový dôkaz o výbere kombinácie,
stavoch po zlom/zrušenom/správnom zadaní, odmene, opakovanom použití ani
uložení príslušných stavov. Názov objektu nie je uzavretie jeho celého handlera.
Žiadne nové percento pôvodného USE sa z týchto C++ testov neodvodzuje.

## Overenie skutočne vykonané

| Kontrola | Výsledok |
|---|---|
| Git blob SHA-1 oboch prevzatých hlavičiek | Presná zhoda s GitHubom |
| Pôvodné hlavičky spolu: GCC/Clang × dve poradia | 4 reprodukované chyby |
| Opravené hlavičky spolu: GCC/Clang × dve poradia | 4 úspešné syntax-only kontroly |
| Test semantických kontraktov | 328 972 kontrol na jeden beh, 0 zlyhaní |
| GCC: Debug, Release s NDEBUG, UBSan | 3 úspešné behy |
| Clang: Debug, Release s NDEBUG, UBSan | 3 úspešné behy |
| Samostatný CMake/CTest harness, Release | 3/3 testy prešli |
| `git apply --check`, aplikácia na lokálnu kópiu, porovnanie výsledku | Prešlo |

Testovacie kontroly zostávajú aktívne aj pri NDEBUG; nepoužívajú runtime assert.
Počty kontrol nie sú počty pôvodných EXE vetiev. Logy sú v `logs/`.

Neoverené: celý pôvodný repozitár a všetky staršie testy, MSVC/Windows,
grafický SDL beh, originálne herné dáta a NITE3W runtime. Existujúce maskovanie
pentagramov s ľubovoľnými hornými bitmi sa iba zachováva; nejde o nový dôkaz
zhody s originálom pri umelo poškodenom inventári.

## Proveniencia zdrojov

Repozitár: https://github.com/marek177/Nitemare3d-reversed

| Súbor prečítaný cez GitHub | Git blob SHA-1 |
|---|---|
| src/game/RecoveredInteractionFacts.hpp | 0bfa63e3de9420d69609a4f939bd13dd981c2100 |
| src/game/InventoryRuntime.hpp | d94e5b56b63116b6fe19b023f3f326696c147e41 |
| src/game/RecoveredWallRuntime.hpp | 1c55ad8e5ce418acc92f0e237f57ede0737a5320 |
| tests/recovered_runtime_facts_test.cpp | 617e98fee0df477d67b20e57bbf47b378fb27a7c |
| src/game/LevelState.cpp | 1b248e5ea78145cfd14a4c94df4d090fe5a94a3a |
| src/main.cpp | 3c397fddf33204a3d771931abea2790f9a7707fc |
| src/platform/sdl/SDLVideo.cpp | d1d350d3ebba73aedfa0449b3eb0d466891c6d5d |

Pred testom sa lokálne kópie dvoch hlavičiek overili presným Git blob hashom.
Tieto dve hlavičky sú uložené v `before/`. Ostatné riadky sú proveniencia
zdrojového auditu, nie tvrdenie, že balík obsahuje alebo kompiluje celý projekt.
Manifest lokálnych hlavičiek je v `source_manifest.json`.