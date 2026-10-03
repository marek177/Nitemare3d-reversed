# Výsledky testov — N3W Runtime Lab 0.1.0

Dátum: **25. september 2026**. Prostredie tvorby: Linux x86-64. Cieľové binárky: **Windows x64 GUI**.

## Čo bolo skutočne vykonané

| Kontrola | Výsledok | Rozsah dôkazu |
|---|---|---|
| Kompilácia oboch Windows EXE cez Clang/LLD | Úspešná, bez upozornení kompilátora. | Zdroj sa preložil a nalinkoval; nejde o vykonanie na Windows. |
| Prenositeľné jadro pod AddressSanitizer + UndefinedBehaviorSanitizer | 75 kontrolných tvrdení; 100 000 deterministických stresových vstupov. Bez zistenej chyby sanitizéra. | Číselné parsery, unsigned porovnania, príkazová allowlist, rámce protokolu, CS:IP a registrové tokeny, CRC32 a SHA256. |
| Krížové testy s Pythonom | 50 038 náhodných a hraničných porovnaní prešlo. | Parsovanie a overflow, little-endian dekódovanie, SHA256 a CRC32 vrátane blokových hraníc. |
| Streaming ZIP pod sanitizérmi | Prešiel. | Text, prázdny súbor, 100 000 binárnych bajtov, UTF-8 názov; odmietnutie cesty s traversal. |
| Nezávislé načítanie ZIP cez Python zipfile | Dáta a CRC všetkých položiek súhlasia. | Prenositeľný ZIP zapisovač; nie celá Windows GUI exportná cesta. |
| Dodaný syntetický LOGCPU | 6 adresných riadkov, 5 jedinečných adries, 2 nerozpoznané riadky. | Kontrolovaná umelá vzorka. |
| Statické kontroly Win32 ABI a PE hlavičiek | Prešli. | PE32+ x86-64, GUI, ASLR/NX a veľkosti/alignment použitých štruktúr. Nie funkčné overenie API. |

Stresové a náhodné testovanie nie je formálny dôkaz bezchybnosti. Presný počet úspešných kontrol nevyjadruje percento otestovania celého programu.

## Čo sa v tomto prostredí NESPÚŠŤALO

Windows 11 grafické rozhranie, ReadProcessMemory a reálny scan, register capture a suspend/resume, PDH/GPU čítače, snímanie okna, skutočný DOSBox-X control klient, import reálneho nite3w trace a OTVDM. Nebol spustený ani Windows syntetický testovací cieľ. Nie je potvrdená kompatibilita s konkrétnou používateľovou zostavou emulátora.

V žiadnom prípade sa úspešné preloženie EXE nemá čítať ako potvrdenie úspešného behu týchto integrácií.

## Reprodukcia prenositeľných testov

Z koreňa zdrojového balíka na Linuxe s C kompilátorom a Pythonom 3:

```sh
mkdir -p test-build
cc -std=c11 -g -O1 -fsanitize=address,undefined -fno-omit-frame-pointer \
  src/core.c tests/test_core.c -o test-build/test_core
ASAN_OPTIONS=detect_leaks=1 ./test-build/test_core

cc -std=c11 -D_POSIX_C_SOURCE=200809L -g -O1 \
  -fsanitize=address,undefined src/core.c src/zipstore.c tests/test_zip.c \
  -o test-build/test_zip
ASAN_OPTIONS=detect_leaks=1 ./test-build/test_zip test-build/fixture.zip

cc -std=c11 -O2 -fPIC -shared src/core.c -o test-build/libcore.so
python tests/test_properties.py test-build/libcore.so
```

Zostavenie Windows bináriek vyžaduje Clang a lld-link v PATH alebo adresár určený LLVM_BIN:

```sh
python build_llvm.py
```

## Prvý Windows smoke test

Použite postup s `N3W_Test_Target.exe` v README_SK.md: vybrať presný PID, zadať jeho zobrazenú adresu, zachytiť A, zásah 100 -> 93, zachytiť B, porovnať a exportovať ZIP. Overte aj scan u32 a zachovanie zmeny v CSV. Až potom prejdite na emulátor.

Pri chybe priložte opis kroku, Windows chybový kód z events.csv a export bez citlivých údajov. Nesprávny výsledok sa nemá označiť za nové zistenie o hre, kým nie je overený samotný nástroj.