# RE MAX v0.35 — SECRET/VEC cascade (15. október 2026)

Cieľ: preniesť úzke originálne statické zistenie do buildovateľného
C++ kontraktu bez vyhlasovania neoverenej runtime alebo pixel parity.

## Dôkazy a hranica istoty

- Win16 v1.10 SHA-256: 12fe5168783446275802e0e947898261b5eca6b88288f3a895fc1faa4c544481.
- Win16 v1.8 SHA-256: 144e96bb649c5463d440c343ad982ed8e5f143e788c9af08bbb890fcd1b3db22.
- Pôvodný cleanup blok je v týchto dvoch NE buildoch bajtovo totožný (164/164 B).
- SECRET panel má 22 B, VEC far pointery na +0,+4,+8,+C, MAP far pointer +10, state +14.
- Pri state=2 updater skúša jednotlivé VEC kroky unsigned 16-bit +2 bez clamping-u. Ak po cykle nenasleduje žiadny krok, spracuje kandidátov v poradí pôvodných panel recordov.
- Kandidát sa maže pri zhode aspoň jedného nenulového VEC far pointera v TOM ISTOM slote; poradie porovnania +0,+8,+4,+C. Zhodný pointer v odlišnom slote nestačí.
- Pri zhode sa všetkým nenulovým VEC kandidáta zruší bit 0 príznakov, následne sa v MAP vynuluje object, potom wall a napokon state; nevyžaduje sa predchádzajúca aktivácia kandidáta.
- Ak má aktívny panel všetky štyri VEC pointery NULL, v tomto lokálnom scan-e nenájde ani seba a jeho MAP wall/object sa touto vetvou nenulujú.
- Priamo pozorované Win16 NE4 explodable cleanup writery 4:3CB2 a 4:3CD2 nulujú iba wall. Nevyplýva z toho, že ďalšie nepriamo volané rutiny nikdy nemenia object.

Identifikované E1M9 bunky s WALL_EX1 + SECRET (zero-based X,Y):
(39,52), (40,52), (27,54), (27,55), wall ID 0x5B, object ID 0x62.
Či v retail runtime skutočne zdieľajú VEC far pointer v rovnakom slote,
zostáva **OPEN**.

## C++ kontrakt v0.35

src/re/N3DV035SecretCascade.hpp zachováva panelove sloty a plnú identitu
far pointera. VEC záznamy sú **zdieľané**, nie kopírované pre každý panel:
ak na jeden pointer odkazujú A aj B, ich coordinate/flags ukazujú na jeden
host-side VecRecord. Pôvodný samostatný syntetický v0.51 model udržiaval
per-panel polia coordinates, a preto nestačil na dôkaz aliasovaných zápisov.

tests/v035_secret_cascade_test.cpp obsahuje syntetické kontroly:
- cascade na neaktivovanom susednom paneli;
- nulové VEC a cross-slot odmietnutie;
- shared VEC koordináty;
- preskok nepárneho targetu, unsigned wrap;
- iba-wall EX cleanup verzus object-then-wall SECRET cleanup;
- nedotknutý state=1 a chýbajúci VEC referent.

Poznámka: hlavička nie je pôvodný packnutý Win16 22-B record,
nedereferencuje reálne NE far pointery, neobsahuje renderer, SFX,
full SAVE/LOAD, reentranciu ani originálne sekvencie tickov. Je to
**regresný statický referenčný kontrakt**, nie hotová implementácia hry.

## Test

    cmake -S . -B build -DN3D_ENABLE_SDL3=OFF
    cmake --build build --target n3d_v035_secret_cascade_test
    ctest --test-dir build -R n3d_v035_secret_cascade_test --output-on-failure

Test používa iba syntetické štruktúry; originálna hra a komerčné dáta nie
sú súčasťou repozitára.

## P0 na runtime uzavretie

1. Použiť konkrétny vyššie hashovaný Win16 build a rozlíšiť NE segmentové
   *logické* offsety od skutočných selektorov počas spustenia.
2. Na E1M9 pred aktiváciou oboch dvojíc zaznamenať panel records,
   štyri VEC far pointery, VEC flags/coords, state, MAP bytes.
3. Logovať Win16 v1.10 NE3:1B6A (aktivácia), 2000 (update), 20F5/2108/
   211D/2132 (slotové porovnanie), 217D (object clear), 2185 (wall clear),
   2189 (state), NE4:3CB2/3CD2 (EX write); pri zmene zaznamenať parent,
   call depth, hodiny, CPU registre, SFX, pôvodné config/DEMO vstupy.
4. Odlíšiť USE, shoot, USE→shoot, shoot→USE, SAVE/LOAD počas pohybu.
5. Vyžadovať dva reprodukovateľné original-game capture a prvý bod
   divergencie remake; samotná zhoda syntetického testu nestačí.

**Stav:** lokálna Win16 statická cesta potvrdená; nový zdieľaný VEC model
testovaný; dosiahnuteľnosť aliasu a originálny runtime OPEN; percentá parity
sa týmto commitom samy osebe nezvyšujú.
