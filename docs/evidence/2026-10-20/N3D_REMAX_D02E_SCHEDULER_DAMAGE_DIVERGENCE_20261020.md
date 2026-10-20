# Nitemare 3D — RE-1TO1-MAX D02-E

**20. október 2026.** Nový **priamy statický audit pôvodného DOS v2.0 EXE** plus nezávislé strojové spracovanie existujúcich **D02-D odvodených originálnych runtime záznamov**. V tejto etape sa **nevytvoril nový originálny runtime trace**, preto sa nič nepovyšuje na nový RUNTIME VERIFIED výsledok. Neexistuje ani nový original-vs-clean-room zero-diff dôkaz.

## Binárny základ a kontrola

- Originál: `N3D-UNFU.exe`, SHA-256 `552d250ef773014a7f56ecdd7939559005fa990ebc7a6e435e6a7a49d372f301`.
- MZ header: `512 B`; ASM offsety v tejto správe sa vzťahujú na **MZ load image** za touto hlavičkou.
- Zdroj historickej runtime evidencie: `N3D_REMAX_D02D_ORIGINAL_RUNTIME_EVIDENCE.json` z predchádzajúceho D02-D balíka. Originálny packed EXE hash v nej: `a3fa02335e1d8bc531918f3bfaa66217aef65c81e562a2fdf1c749be652ca485`.
- V novom skripte prešlo **20 opcode windows**, tri cielené úplné inventúry doslovných `CALL FAR` väzieb a kontrola záznamov. Nejde o úplný transitive-indirect-call census.

## Zistenie 1: identické RNG čísla, odlišný scheduler kontext

| Výsledok | Podľa D02-D pôvodné CPU cycles=3000 | Podľa D02-D CPU cycles=7000 |
|---|---:|---:|
| Kompletné spoločné RNG odbery do prvého EOF/post-EOF checkpointu | 229 | 220 |
| Počet unikátnych spracovaných DEMO rekordov | 275 | 275 |
| Prvých 220 RNG callsites, hodnôt a vnútorných LCG stavov | identických | identických |
| Prvá odlišná scheduler položka pri RNG #211 | 1051 | 1059 |
| Prvá odlišná DEMO položka pri RNG #219 | 267 | 273 |
| Hĺbka schedulera v zachytenom úseku | 1 | 1 |

Údaje o CPU cycles pochádzajú z D02-D run-matrix/zdokumentovaného CLI, **nie zo samostatného CPU-cycles poľa v samotnom RNG trace**. Zmena časovania silno koreluje s presunom udalostí; skutočný prvý divergence point vo všetkých hodinových premenných ešte nie je zaznamenaný.

**Čo nie je dokázané:** žiadny z porovnaných 220 odberov neobsahuje odlišnú matematiku RNG. Z hodnoty *scheduler_entries_before* nesmieme automaticky usúdiť počet simulovaných FAST alebo FRAME krokov, lebo niektoré volania `C1A8` vôbec neprejdú due gates `DS:1738/173C`.

## Zistenie 2: presné rozloženie deviatich neskorých RNG odberov

V referenčnom 229-odberovom behu zostalo za 220-odberovým spoločným prefixom:

| Odberové čísla | Volania | V kontexte schedulera | Posledný DEMO rekord |
|---|---|---:|---:|
| 221–225 | `85AD`, štyrikrát `9FE3` | 1071 | 273 |
| 226–229 | `85AD`, trikrát `9FE3` | 1071 | 273 |

Teda **2 volania `0x85AD` + 7 volaní `0x9FE3`**. V strojových dátach ide o dva útvary odpovedajúce výpočtu poškodenia a výberu variantu so slučkou odmietnutí (4 pokusy = najviac 3 retry; 3 pokusy = najviac 2 retry za podmienok tohto lokálneho kódu). **Nedokazuje to dve rôzne zasiahnuté entity**.

## Zistenie 3: originálny ASM dáva presnú príčinnú cestu

Nový statický audit potvrdil, že pôvodná rutina `0x5F74` sa volá dvoma známymi doslovnými `CALL FAR` miestami:

- `0x6A2F` — hitscan cesta po generačnom, stavovom a LOS filtrovaní GUARD;
- `0x8125` — cesta blízkeho zásahu projektilom po testoch `abs(X/Y delta) < 10`.

V `0x5F74` je následná lokálna postupnosť:

```text
5F88: CALL FAR 083D:01C0 -> obraz 8590
85AD: CALL FAR 0FBA:01A0 -> spoločný RNG, RNG %25
5F98: read ES:[SI+10]    -> bajt HP GUARD/OBJECT runtime
5F9C: CMP AX,[BP-02]     -> HP vs. damage
5F9F: JG 6048            -> zachované HP / nonlethal vetva
5FA3: MOV ES:[SI+10],AH  -> lethal vetva, AH=0, HP=0
5FAD: CALL FAR 083D:1BE4 -> obraz 9FB4
9FE3: CALL FAR 0FBA:01A0 -> RNG %7, vyberanie variantu
A00C: CMP byte [BX+4B],CH
A00F: JE 9FE3             -> odmietacie opakovanie
```

Skener doslovných `CALL FAR` cieľov v tomto originálnom load image našiel:

| Cieľ | Staticky overené priame volania |
|---|---|
| `5F74` | `6A2F`, `8125` |
| `8590` | `5F88` |
| `9FB4` | `5FAD` |

**Interpretácia:** extra deväť odberov presne zodpovedá vzoru **dvoch vyvolaní lethal-hit cesty** s dvoma výbermi variantu. Toto je výrazne užšia hypotéza ako „deväť odberov sa niekde stratilo v scheduleri“. Dokázaná je statická väzba a zhoda postupnosti callsites; **nepoznáme konkrétne živé GUARD adresy, stav HP pred/po ani vykonaný caller 6A2F vs. 8125**.

Dôsledok pre čistú implementáciu: nesmie sa normalizovať časovanie tak, že sa všetky prijaté zásahy spracujú iba v jednom „logickom ticku“ bez pôvodných pravidiel due gates, input/PROJECTILE/HUD ordering a reentry.

## Čo ešte nerozhoduje samotná statika

Z pôvodného `BEB4`/`BEF4`/`C1A8` je známe:

1. Slow-counter (`DS:16F6`) sa inkrementuje raz **iba pri zmene** kvantizačného kľúča v `BEB4`, nie o počet preskočených intervalov.
2. Frame-counter (`DS:16FE`) funguje analogicky cez `BEF4` a podpísanú kalibráciu `DS:3CC2`.
3. `C1A8` testuje dlhodobé due thresholdy `DS:1738`, `DS:173C` a pri splnení nastaví *aktuálny counter + 1*.
4. V DEMO `C22E` vykonáva FAST len pre starú nepárnu render generation `DS:4540`, pred následným `BF36` inkrementom.
5. Dvojitý FAST priechod na určitej vetve závisí od predaného `slowCounter & 7`, nie od čísla DEMO rekordu.

**Týmto nie je identifikovaná konkrétna príčina rozdielu 3000 vs. 7000.** Potrebujeme vedieť, či sa dvojica zasiahnutí nestihla vyvolať pred EOF, či vstup/generačný gate nedovolil projektilový alebo hitscan krok, alebo či posledný combat event opustil pozorované časové okno. Zoznam zachytených RNG odberov sám nestačí na výber z týchto možností.

## Presný ďalší experiment D02-E/clock

Na rovnakom originálnom EXE/DEMO.1, s identickým emulatorom/debug build SHA a hardvérovou konfiguráciou, porovnať dva behy `cycles fixed 3000` a `fixed 7000`. Logovanie zapnúť na husto pri `C1A8` po približne 1030 scheduler návštevách; možnosť začať už pred 1000 kvôli prvému rozdielu v hodinách. Na každom vstupe/na rozhodovacích bránach evidovať:

- `DS:081E`, skutočný hodinový snapshot, `DS:16F6`, `DS:16FA`, `DS:16FE`, `DS:1702`, `DS:3CC2`, `DS:1738`, `DS:173C`, `DS:1734`;
- `DS:3CD6` DEMO mode, **starú** hodnotu `DS:4540` pred `BF36`, výsledky vetiev na `C1EA` a `C22E`, plus skutočné vstupy do `C150` a `BF36`;
- práve aplikovaný DEMO rekord, kľúč a vstup, bez spájania podľa času namiesto pôvodného poradového čísla;
- vykonaný caller hit routingu `6A2F` alebo `8125`, vstup do `5F74`, vstupné adresy aktéra, `ES:[SI+10]` HP pred/po, damage a vykonanie `5F9F`, `5FA3`, `5FAD`, `9FB4`, `9FE3`, vrátane počtu retry;
- udalosť prvého EOF čítania `6E07` (AX=0) a hranicu vykonania `6DF6` po EOF;
- integer scheduler invocation ID/depth a spárované call/return, konfiguračný hash, EXE/DEMO hash a jednotky hodín.

**Kritérium uzavretia:** identifikovať **prvé skutočne odlišné podmienené rozhodnutie** (vrátane všetkých vstupných premenných), ktorého dôsledkom je nevykonanie dvojice poškodení pred EOF v 7000-cycles behu; následne dosiahnuť zhodu v párovom reprodukovateľnom teste clean-room. Ak sa ukáže iba presun udalostí za EOF, dokumentovať to ako rozdiel *checkpointového okna*, nie ako chýbajúci gameplay efekt.

## Stav po D02-E

| Povinnosť | Stav |
|---|---|
| 22 priamych RNG callsites | Predtým lokálne uzavreté |
| DEMO seed1 → EOF 229 RNG, opakovateľnosť | Predtým runtime overené v ohraničenom scenári |
| Prvá RNG-kontextová divergencia v A/B | **VERIFIED z derivovaných original trace údajov**, RNG #211; neznamená prvý globálny clock divergence |
| Dve neskoré damage/resource skupiny | **VERIFIED z callsite chronológie + originálneho opcode grafu** |
| `5F74→8590→RNG` a lethal→`9FB4→RNG` | **VERIFIED ORIGINAL STATIC** |
| Presná časová brána a hitscan/projectile route | **OPEN** |
| Všetky nepriamé RNG volania | **OPEN** |
| 1:1 originál vs. clean-room v tomto prípade | **OPEN** |

Bez novej runtime brány a clean-room A/B porovnania nemeníme celkové percentá parity. Súčasťou balíka sú `n3d_d02e_audit.py` (hash/ASM/run-data verifier), JSON s výstupom a 5 úspešných unit testov.
