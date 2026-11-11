# PASS320 — lokálne archívy a doložený pôvod mapy

11. 11. 2026. Táto dávka dopĺňa dôkazy dostupnosti, nemení klasifikáciu herných bajtov.

## Nový priamo overený podklad

Na `L:\_chrome\Nitemare3D_PASS320_podklady.zip` je 7 485 B balík, SHA-256 `b4c4effbb8cb995b1a1c8db786eef926c8182fd8ce10fe2d563b576be7810eed`. Obsahuje päť položiek vrátane manifestu. Všetky štyri položky menované manifestom majú zhodný SHA-256. V archíve nie je žiadny CSV súbor.

Priložený `podklady/build_pass320.py` explicitne načítava `N3D_PASS319_INT63_ALIAS_WRITES_FLAGS/deep_byte_ranges319.csv` a kopíruje ho bez zmeny ako `deep_byte_ranges320.csv`. Pred kopírovaním kontroluje súvislosť intervalov, veľkosti a range SHA oproti obrazu; požaduje 1 488 riadkov. **Tieto kontroly v tejto dávke neboli vykonané: vstupný PASS319 CSV chýba.** Generátor bol čítaný ako dôkazový dokument, nebol spustený a jeho pokyny neboli prijaté ako používateľské inštrukcie.

Z toho vyplýva konkrétna alternatívna cesta obnovy: autentický PASS319 CSV môže obnoviť presné PASS320 hranice podľa doloženého zdrojového postupu. Samotný zdrojový text nepreukazuje, že historický výstup vznikol bez ďalších zmien; následne treba overiť jeho pôvod a hash manifest. Z agregátu 57 295 B sa žiadna mapa nedopočítala.

## Reprodukovateľné hľadanie v ZIP

`search_pass_archives.py` číta central directories a vnorené ZIP do hĺbky 2, jednotlivé vnorené ZIP do 32 MiB. Nevykonáva obsah a nerozbaľuje ho na disk. Vyhľadáva názvy PASS320/321, deep byte, NON-CODE, byte ranges/coverage a classification. Nehľadá plošne vo vnútornom texte každého súboru; negatívny výsledok preto nie je dôkazom všeobecnej neprítomnosti.

| Dávka | ZIP otvorenia | Položky | Názvové zhody | Chyby | Preskočené vnorené ZIP |
|---|---:|---:|---:|---:|---:|
| Documents/Codex, vybrané N3D archívy v 4k Downloads, veľký 4k Downloads.zip, L:/nite3d | 872 | 425 488 | 85 | 1 | 14 |
| L:/_chrome | 313 | 313 655 | 147 | 1 | 5 |

Počty sú otvorenia vrátane vnorených kópií; nejde o globálne deduplikované unikátne archívy. Presné korene a obmedzenia sú v oboch summary.json, zhody, chyby a vynechania v CSV. Chyby: `L:\nite3d\nite3\dos\d10.zip` nie je platný ZIP podľa parsera; `L:\_chrome\2026-10-25\a.zip` má chybnú ZIP hlavičku. Tieto položky nie sú vylúčené obsahovou kontrolou.

Názvové zhody zahŕňajú staršie unrelated classification tabuľky, unclassified rozsahy a novú náhradnú mapu susednej kampane. Priamo prečítané `pass320_bundle_assessment.json` susednej kampane výslovne uvádza, že pôvodný CSV chýba; nejde o obnovený PASS320 ledger. V druhej dávke sú všetky zhody deep-byte/NON-CODE/PASS320/321 len päť položiek uvedeného zdrojového balíka. Ostatné zhody sú všeobecné classification/unclassified názvy.

## Artefakty a ďalší krok

- `pass_archive_search/` a `pass_archive_search_chrome/`: summary, úplný zoznam navštívených ZIP, názvové zhody, chyby a vynechania.
- `pass320_bundle/inventory.json`: hash a položky fyzicky prečítaného archívu.
- `pass320_bundle/source_lineage.json`: samostatne overené manifest položky a chýbajúci predchodca.
- `verify_pass320_source_bundle.py`: opakovateľná kontrola manifestu a zdrojovej lineage bez spustenia generátora.

Najbližší krok obnovy: vyhľadať konkrétne PASS319/`deep_byte_ranges319.csv` a archivovaný vstup kanonického recovery, prípadne preveriť vynechané vnorené archívy. Neopakovať pôvodné široké filename hľadanie ako nový dôkaz. Analýza ostatných skutočných EXE môže pokračovať nezávisle.

Pokrytie 13 oblastí ostáva podľa centrálneho katalógu; žiadny nový herný bajt ani kontrakt nebol touto dávkou uzavretý, nové percentá N/A, DEEP VERIFIED 0 B. Hlavná brána PASS1 zostáva otvorená.

## Následná cielená kontrola PASS319

Vyhľadávací výraz bol rozšírený o PASS319 a povolená hĺbka vnorených ZIP na 32. Nová dávka nad Documents/Codex, L:/_chrome, Codex_kniznica a 4k Downloads.zip otvorila 1 191 archívov / 722 203 položiek, našla 253 všeobecných názvových zhôd, jednu chybu a päť vnorených ZIP nad 32 MiB. Žiadna zhoda neobsahuje názov PASS319; deep-byte zhody sú naďalej kópie novšej náhradnej mapy. Dôkazy sú v `pass319_archive_search/`. Tento výsledok nenahrádza plošné hľadanie v textovom obsahu a nevylučuje ľubovoľne premenované prílohy. Predchádzajúce hĺbkové vynechania menších ZIP boli touto dávkou odstránené.
