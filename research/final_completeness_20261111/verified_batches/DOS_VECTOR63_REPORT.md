# DOS 2.0 — skutočná inštalácia a obnova vektora 63h

11. 11. 2026. PARTIAL, nové DEEP VERIFIED 0 B, runtime testy 0. `audit_dos_vector63.py` reprodukovateľne overil presné bajty a nezávisle dekódoval tri **fragmenty**, spolu 43 inštrukcií / 81 B. Nie sú to tri uzavreté funkcie.

## Inštalačný kontrakt

Pri image18A8C kód nastaví AH=35h, AL=63h a na18A90 vykoná INT21. Výsledné BX a ES uloží na CS:2E11 a CS:2E13. Na18A9C nastaví AH=25h, AL=63h, DX=30E6h, cez PUSH CS/POP DS nastaví DS=CS a na18AA5 vykoná INT21. Podľa [Microsoft MS-DOS Encyclopedia, System Calls](https://www.pcjs.org/documents/books/mspl13/msdos/encyclopedia/section5/) ide o získanie pôvodného vektora cez ES:BX a inštaláciu nového cez DS:DX.

Pri CS15BF teda inštaluje handler15BF:30E6 = image18CD6, presne začiatok doteraz analyzovaného dispatchera. Označenie INT63 má teraz priamy strojový podklad a nie je len prevzatým názvom. Statický kód nepreukazuje vykonanie tejto inicializácie v konkrétnej relácii.

Vnútorný blok `[18A87,18AAC)` má symetrické PUSH/POP pre AX,BX,DS,DX,ES. Pri normálnom návrate z DOS volaní obnoví tieto registre a zásobník. FLAGS týmto blokom neukladá. Širší prefix na18A78 vykonáva CLI a na18A79 CLD; konečný IF/DF kontrakt celej inicializačnej rutiny zatiaľ uzavretý nie je.

## Dátový pointer a restore vetvy

`CS:2E11..2E15` = image `[18A01,18A05)` je 4-bajtový uložený predchádzajúci FAR vektor, little-endian offset WORD a segment WORD. Dátový katalóg obsahuje počiatočné bajty a hash. Nejde o nemenný pointer: uvedená inicializácia ho prepíše hodnotou z DOS.

Na image18B8B a18BD7 kód nastavuje AH=25h, AL=63h; načíta DX z CS:2E11 a DS z CS:2E13. INT21 na18B99, resp.18BE5 tak požaduje obnovu uloženého vektora. Oba ohraničené restore bloky ukladajú AX,DS,DX a symetricky ich obnovia. Prvý leží v širšej vetve končiacej RETF na18BBE, druhý pred NEAR RET na18BF3. Názvy fragmentov neznamenajú potvrdené hranice alebo všetkých callerov týchto rutín.

Lokálne restore bloky neoverujú, či vektor medzičasom zmenil ďalší používateľ, ani či uložený pointer bol predtým inicializovaný. Nie je tým dokázaný chybný životný cyklus: globálne poradie vstupov a externé TSR stále nie sú známe.

## Vzťah ku caller analýze

Predchádzajúci negatívny výsledok CD63 zostáva platný: celé statické telo kanonického obrazu túto dvojicu neobsahuje. Nový pozitívny dôkaz inštalácie ho nevyvracia; ide o odlišné otázky. Instalovaný handler môže zostať nepoužitý alebo byť zavolaný externým či nepriamym mechanizmom. Ani jedna možnosť sa tu nevyhlasuje za potvrdené správanie. Limity counter service49 ostávajú otvorené.

## Reprodukcia a pokrytie

`python audit_dos_vector63.py IMAGE ABSOLUTE_DECODER_DIRECTORY OUT_DIR` vytvára `dos_vector63/instructions.csv`, `data_intervals.csv`, `summary.json`. Následný `independent_decode_and_catalog.py` skontroloval hash pointerového poľa a neprítomnosť konfliktu s centrálnym kódom.

Centrálna partition po pridaní4 B: **534 B dát**,1 273 B lokálneho kódu,169 553 B v tejto kampani neposúdených,55 intervalov,spolu171 360 B. Fragmentových81 B sa zatiaľ nepripočítalo do funkčného katalógu: chýba uzavretie celých funkcií. Všetky nové dôkazy PARTIAL, členstvo PASS320 UNKNOWN, percentá N/A.

DOSBox-X ďalší krok: na INT21 zaznamenať AX=3563/2563 a výsledné či vstupné ES:BX/DS:DX; po inštalácii porovnať IVT slot0000:018C s load-adjusted handlerom; sledovať prvý vstup dispatchera a obidve restore vetvy. Treba rozlíšiť samotnú inštaláciu od prvého reálneho použitia a nezamieňať reálne adresy s nerelokovanými image offsetmi. Tieto testy neboli spustené.
