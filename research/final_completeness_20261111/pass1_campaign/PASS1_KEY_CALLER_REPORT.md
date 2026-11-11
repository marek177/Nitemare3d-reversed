# PASS1 — ohraničenie známej key-label caller cesty

11. 11. 2026. PARTIAL; sedem nových riadených replay prípadov. Byte statusy sa nemenia, pretože ide o posilnenie kontraktu už klasifikovaných objektov, nie o nové objekty.

## Dve priame hrany

Nezávislá kontrola všetkých35 648 položiek hash-pinned historického inventára našla tieto priame encoded callsites:

| Zdroj image | Cieľ | Úloha |
|---|---|---|
| 0143Dh | 0D29:1E1A = image0F0AAh | dispatcher→wrapper |
| 0F0B9h | 083D:1F36 = image0A306h | wrapper→key-label selector |

V danom inventári je pre každý z týchto dvoch cieľov jedna priama hrana. Nepriame, externé a dodatočne generované callsites tým nie sú vylúčené.

Dispatcher začína00F7:0484 = image013F4h. Typ načíta doSI zoSS:[BP+0Ah], cezLES zo stacku získa FAR pointer na vstupný záznam a z neho BYTE. Pred key vetvou používa signed porovnaniaSI s19h a1Ch. Pri typoch25..28 prejde na1436; iné hodnoty túto konkrétnu vetvu nepoužijú.

Do wrappera vloží najprvSI (typ), potom zero-extended BYTE záznamu. Wrapper načíta typ zoSS:[BP+8] doDI, vytvorí `AX=DI-19h`, vloží ho ako argument a priamo volá selector. Pred vstupom selectoru nie je na tejto route ďalšie externé volanie.

Pre túto cestu je preto index presne0..3. Toto ohraničenie pochádza z predchádzajúceho dispatchera, **nie z ochrany v samotnom selectore**, ktorý naďalej nemá lokálny bounds check.

## DS kontrakt

Na analyzovanej route sa incoming DS explicitne nemení. LES meníES, nieDS. Wrapper ho takisto nenastavuje; selector následne číta pointerové premenné z aktuálnehoDS. Doložená startup báza2771h je vhodný očakávaný default kontext, ale tento bounded route dôkaz nepreukazuje, s akýmDS prišiel nadradený prirodzený caller.

Nie je preto prípustné uzavrieť globálneDS iba preto, že lokálna cesta DS zachováva. Ani platný index nezaručuje správny text pri nesprávnom vstupnom segmente.

## Sedem riadených replay prípadov

`replay_pass1_key_callers.py` vykonáva pôvodné inštrukcie od013F4h cez reálny FAR wrapper call až po vstup selectoru. Synteticky pripraví iba entry stack, záznam a segmenty; index na selector stack nevkladá priamo.

| Vstupný typ | EntryDS | Pozorovanie |
|---:|---:|---|
| 24 | 2771h | zastavenie pred iným dispatcher callom1424h |
| 25 | 2771h | selector index0, DS2771h |
| 26 | 2771h | selector index1, DS2771h |
| 27 | 2771h | selector index2, DS2771h |
| 28 | 2771h | selector index3, DS2771h |
| 29 | 2771h | zastavenie pred iným dispatcher callom1453h |
| 25 | 2222h | selector index0, **DS zostane2222h** |

Všetky assertions prešli. Posledný prípad cielene potvrdzuje inherited-DS precondition; po príchode selectoru sa zastaví a nesnaží sa čítať nesprávne texty. Susedné dispatcher vetvy sa nevykonávajú celé. Nejde o sedem prirodzených gameplay testov.

## Artefakty, pokrytie a pokračovanie

`audit_pass1_key_caller_paths.py IMAGE HISTORICAL_INSTRUCTIONS ABSOLUTE_DECODER_DIRECTORY OUT_DIR` vytvára `pass1_key_caller_paths/direct_calls.csv`, `bounded_instructions.csv` a summary s presnými guard/argument oknami. `replay_pass1_key_callers.py IMAGE UNICORN_DIRECTORY OUT_DIR` vytvára `pass1_key_caller_replay/evidence.json` s inštrukčnými stopami, konkrétnym stack argumentom, segmentmi a native-library hashom.

Aktuálna PASS1 mapa zostáva306 B PARTIAL,9649 B CLASSIFIED ONLY,47340 B UNKNOWN,0 B DEEP VERIFIED. Centrálny code/data katalóg sa nerozširuje o neuzavreté prefix fragmenty. Prijaté controlled replay prípady sú47 =40 predchádzajúcich+7 tejto dávky; pôvodný DOSBox-X/runtime0. Percentá13 oblastí N/A.

Ďalší krok: nadradený dispatcher entry DS/caller kontrakt, potom dve ID-card label premenné priDS:0D46h a0D5Ah a ich spotrebiteľ. Globálne writeri a nepriame vstupy zostávajú otvorené; tento výsledok neudeľuje DEEP VERIFIED užitočným, ale podmieneným lokálnym zisteniam.
