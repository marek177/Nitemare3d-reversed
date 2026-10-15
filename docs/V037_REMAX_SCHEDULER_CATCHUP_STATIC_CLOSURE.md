# Nitemare 3D RE MAX v0.37 — FAST/FRAME časové brány a vynechané tick-y

**15. október 2026. Priama statická kontrola originálneho DOS v2.0.**

Vstup: používateľom vlastnený originál `N3D_DOS_v2.0_IDA.EXE`, MZ load image
**171 360 bajtov**, SHA-256
`e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297`.
Adresy v tomto reporte sú **offsety v obraze bez MZ hlavičky**; nie sú
adresami Win16 NE a priamo nepredstavujú CS:IP v DOSBox-X.

## Nové zistenie: preskakovanie zameškaných krokov

Nie je správne nahradiť pôvodný scheduler univerzálnym:
`while (simulationBehind) simulateOneTick();`

Pôvodný DOS v2.0 používa dve osobitné kvantizačné rutiny `BEB4` a `BEF4`.
Každá pri zmene svojho výstupného kvocientu inkrementuje uložený 32-bitový
čítač **presne raz**, aj keď medzi vzorkami prešiel viac než jeden časový
interval. Aj funkcia `C1A8` pre každú z dvoch vetiev
spracuje maximálne **jeden priamy FAST alebo frame pass na jedno vlastné
volanie**. Má iba dopredné podmienené skoky v auditovanom tele
`C1A8..C2B4`; žiadnu lokálnu catch-up slučku.

Tento dôkaz je **VERIFIED ORIGINAL STATIC pre tieto tri presné funkcie**.
Neuzatvára vnorené FAST volania iných funkcií ani prerušenia počas volania
`C1A8`. Nesmieme preto automaticky tvrdiť, že jeden event na jeden
renderovaný frame je globálny invariant celej hry.

### 1. Pomalé počítadlo — `BEB4`

Pôvodná aritmetika:

```cpp
uint32_t scaledSlow = uint32_t(uint32_t(clock) * 8) / 1000;
if (scaledSlow != DS_16FA_cachedScaledSlow) {
    DS_16FA_cachedScaledSlow = scaledSlow;
    ++DS_16F6_slowCounter;    // jeden 32-bitový INC, nie rozdiel kvocientov
}
return DS_16F6_slowCounter;
```

Relevantné strojové adresy:

- `BEB8`: vstupný 32-bitový clock a `SHL EAX,3`;
- `BEC0`: unsigned delenie tisícom;
- `BED0`: porovnanie proti `DS:16FA`;
- `BEDD–BEE9`: uloženie nového kvocientu a **jeden** `INC DWORD DS:16F6`;
- `BEEA`: návrat počítadla `DS:16F6`.

Výpočet je **32-bit wrap** pred delením, nie neobmedzené 64-bitové
násobenie. Zmena kvocientu späť na nižšiu hodnotu taktiež inkrementuje čítač,
pretože kód testuje **nerovnosť**, nie kladný rozdiel.

### 2. Frame počítadlo — `BEF4`

```cpp
uint32_t factor = uint32_t(int32_t(int16_t(DS_3CC2_calibration)));
uint32_t scaledFrame = uint32_t(factor * uint32_t(clock)) / 1000;
if (scaledFrame != DS_1702_cachedScaledFrame) {
    DS_1702_cachedScaledFrame = scaledFrame;
    ++DS_16FE_frameCounter;  // najviac jeden INC na toto volanie
}
return DS_16FE_frameCounter;
```

- `BEF8`: `MOVSX EAX,WORD DS:3CC2` (signed kalibračná hodnota);
- `BEFE`: 32-bit `MUL` s low-32-bit výsledkom;
- `BF02–BF0B`: unsigned delenie `1000`;
- `BF12`: porovnanie proti cache `DS:1702`;
- `BF1F`: uloženie a jeden `INC DWORD DS:16FE`.

Nie je preukázaná každá dosiahnuteľná kalibrácia či fyzikálna
frekvencia celého systému. Čítače však zodpovedajú tejto presnej
statickej aritmetike.

**Príklad skoku:** ak `slow.cachedKey=1` a `slow.count=8`, ďalšie
volanie zistí `scaledSlow=2000`, vráti sa s
`slow.cachedKey=2000` a `slow.count=9` — **nie 2007**.
Ďalšie volanie s rovnakým časovým kľúčom ho nezmení.

## 3. Vonkajší scheduler — `C1A8`

Vstupy a poradie:

```text
BE74 -> timeSnapshot          (clock; DS:081E môže byť aktualizovaný)
BDF8 -> legacySnapshot        (samostatná vzorka)

BEB4(timeSnapshot) -> slowCounter   // aktualizuje cache / +1, ak treba
if DS:1738 <= slowCounter:        // 32-bit unsigned high/low compare
    if DS:3CD6 == 0:             // bežný režim, nie DEMO
        FAST(slowCounter)         // site C1EA -> C150
    DS:1738 = slowCounter + 1    // site C1F0

BEF4(timeSnapshot) -> frameCounter
if DS:173C <= frameCounter:      // 32-bit unsigned high/low compare
    if DS:3CD6 != 0 && (DS:4540 & 1) != 0:
        FAST(slowCounter)         // site C22E -> C150, PRED renderom!
    MAIN()                       // site C235 -> C0D8
    BF36_render()                // site C239; increment DS:4540
    update_other_frame_systems()
    secret_panel_0AEA()          // C246
    projectile_update_8230()     // C24B
    ... additional frame callbacks ...
    DS:173C = frameCounter + 1   // site C274
    DS:1734 = legacySnapshot    // site C27E

if uint32_t(legacySnapshot - DS:1734) > 500:
    BDE4(1)                      // C29A
    BDE4(0)                      // C2A3
    DS:1734 = BDF8()            // C2AA/C2AD
```

**Zákerné rozdiely pri 1:1 implementácii:**

1. `DS:1738` a `DS:173C` sú *práh nasledujúceho povoleného
   spracovania*, nie počty zameškaných tickov. Pri due sa nastavia na
   `aktuálny_counter+1`. Kód nelúšti celý dlhý backlog.
2. Pri bežnej hre `C1EA` môže zavolať FAST v slow vetve. V DEMO režime
   sa slow počítadlo a nextSlow stále aktualizujú, ale tento FAST je
   potlačený a prípadný FAST beží na `C22E` vo frame vetve.
3. DEMO FAST gate vyhodnotí **starú** hodnotu `DS:4540 & 1` pred
   `BF36` inkrementom. Ak už je frame číslo párne, tento FAST sa
   nevykoná ani vtedy, keď následný render zmení číslo na nepárne.
4. **Obe FAST vetvy dostávajú ako argument slowCounter**, nie frameCounter
   ani renderGeneration. To ovplyvňuje interný `C150:C198` test
   `arg & 7 == 0` a podmienené druhé volanie `89A2`. Ide o **dve
   nezávislé brány**: DEMO odd-frame výber a slowCounter modulo-8.
5. V jednom *priamom* `C1A8` priechode nemôžu zároveň zavolať FAST
   normálna aj DEMO vetva, pretože kontrolujú opačné hodnoty
   `DS:3CD6==0` a `!=0`. Toto neobmedzuje možné vnorené invokácie.

`C235` MAIN sa volá **pred** `BF36` rendererom, potom nasleduje viac
explicitných frame callbackov a nakoniec `0AEA` a `8230`.
Nie je oprávnené prepísať globálne poradie tak, že projektily alebo
tajné panely musia vždy bežať pred kreslením.

## 4. Rare fallback: rozdiel viac než 500 a spätný skok hodín

Originál porovnáva 32-bitové **unsigned**
`uint32_t(legacySnapshot - DS:1734) > 0x1F4`.

- Rozdiel presne **500** obnovovaciu vetvu nespustí; **501** áno.
- Ak sa frame vetva vykonala, `DS:1734` sa najprv aktualizuje na
  `legacySnapshot`, a výsledný rozdiel je nula (bez iných zásahov).
- Ak sa frame nevykonala a epoch je starší, vetva po prekročení
  prahu volá `BDE4(1)`, `BDE4(0)`, znovu načíta `BDF8` a uloží nový epoch.
- Ak sa `legacySnapshot` vráti *pod* uložený epoch, unsigned
  odčítanie sa pretečie. Tým je staticky možné spustenie tejto vetvy
  aj pri *spätnom* skoku. Nie je preukázané, že sa tento skok
  skutočne stane v bežnej hre.

Význam všetkých efektov `BDE4` (časovač, vstupy alebo externé
ovládače) týmto lokálnym auditom **nie je kompletný**. Príčina
resynchronizácie je staticky presná, externé dôsledky sú OPEN.

## 5. Reprodukcia bez redistribúcie originálu

Read-only verifier používa pôvodný SHA-256 pred povolením offsetov.
Kontroluje **25 opcode windows, 13 krátkych skokov a 13 CALL hrán**:

```sh
python tools/n3d_v037_scheduler_gate_probe.py /private/N3D_DOS_v2.0_IDA.EXE
python -m unittest discover -s tests -p "test_n3d_v037_scheduler_gate_probe.py" -v
cmake -S . -B build -DN3D_ENABLE_SDL3=OFF
cmake --build build --target n3d_v037_scheduler_catchup_test
ctest --test-dir build -R "^n3d_v037_scheduler_catchup_test$" --output-on-failure
```

C++ test zahrnuje časové skoky, bežnú hru, DEMO, prenos slow-counter
argumentu, hranice 500/501, 32-bit wrap, podpis kalibrácie, vypnutý
frame tick pri hypotetickej kalibrácii nula a spätný legacy čas.

**STATICKY UZAVRETÉ:** kvantizačná aritmetika, jednorazové inkrementy,
32-bitové due porovnanie a posun threshold, dve vzájomne výlučné
priame FAST cesty, použitý slow argument a podmienka recovery.

**STÁLE OPEN:** časovanie reálneho BIOS/IRQ a DMA/sound volaní,
všetky nepriame/nested callbacky, presná frekvencia fyzických
časových vzoriek, DEMO seed1 RNG odber za odberom, LOAD návrat do
časovačov a pixel-perfect rendering. **Nový statický dôkaz sám
o sebe nemení percentá kompletnej 1:1 runtime parity.**
