# Izolácia samomodifikácie ADC — syntetická diagnostika

11. 11. 2026. Táto dávka **nie je vykonaním Nitemare3D**, neprepisuje pôvodné EXE a nezvyšuje jeho pokrytie. Slúži na vysvetlenie neprijatého sample IRQ replay.

## Experiment

`diagnose_unicorn_smc_adc.py UNICORN_DIR OUT_DIR MODE` vytvorí krátky samostatný 16-bitový program. Jediná ADC pripočíta1 a vstupný CF do WORD200h. Tri ciele zápisu: displacement budúceho MOV v prekladanom kóde, obyčajné dáta na rovnakej stránke a dáta na inej stránke. Štyri CF kombinácie oddeľujú starší stav od bezprostredného vstupu ADC. Cieľ future_operand sa počíta z dĺžky generovaného programu, nie ručne podľa očakávaného výsledku.

| Režim | Príprava CF | Počet prípadov | Odchýlky od WORD(200h+1+CF) |
|---|---|---:|---:|
| explicit_flags | STC/CLC pred ADC | 12 | 0 |
| memory_add | CMP/JAE a memory ADD pred ADC | 12 | 2 |
| flags_barrier | rovnaký memory ADD, potom PUSHF/POPF | 12 | 0 |

V memory_add režime obidve odchýlky patria future_operand cieľu pri ADC vstupnom CF=0: očakávané0201h, pozorované0202h. Pri CF=1 je výsledok0202h zhodný. Všetkých osem kontrolných zápisov mimo budúceho operanda prešlo. Po pridaní PUSHF/POPF do **syntetického programu** prešli aj štyri future_operand prípady.

PUSHF/POPF sa nevkladalo do originálneho handlera a nijaký výsledný register, carry ani cieľový WORD sa počas vykonávania manuálne neopravoval. Diagnostický variant mení experimentálnu inštrukčnú sekvenciu, preto nie je náhradným runtime dôkazom hry.

## Záver a obmedzenie

Tento kontrolovaný rozdiel reprodukuje triedu nesúladu bez IRQ frame, DOS, portových hookov či pôvodných herných dát. Podporuje vysvetlenie interakciou translation/self-modification a reprezentácie FLAGS v danom emulátore; presné interné miesto chyby v Unicorn/QEMU zdroji ešte nie je identifikované. Nie je podkladom pre tvrdenie o všetkých verziách Unicorn ani o správaní fyzického x86/prefetch.

Použitý Unicorn2.1.4, natívna DLL SHA-256 `010d85dce84b8f6ffaec3d5420f1b5f7768f859eb831be574c7da23e656ee8f1`. Každý JSON obsahuje presné generované bajty a ich hash, vstupy, očakávaný/pozorovaný výsledok a inštrukčnú stopu. Výstupy sú `unicorn_smc_explicit_flags/`, `unicorn_smc_memory_add/`, `unicorn_smc_flags_barrier/`. Skoršie názvy minimal/lazy_flags sú historické snímky a nepoužívajú sa ako ďalšie nezávislé prípady.

Všetkých36 syntetických experimentov sa vykonalo a skončilo; nejde o36 prijatých game replay testov. Súčet prijatých read/PIT replay zostáva23. Pôvodný sample IRQ replay zostáva neprijatý. DOSBox-X runtime testy0, DEEP VERIFIED0 B; centrálna bajtová mapa sa nemení.

Ďalší krok: overiť pôvodný handler druhým CPU modelom alebo DOSBox-X s pripravenými operandmi a následne s prirodzeným herným vstupom. Samotný workaround FLAGS v diagnostike sa do hry ani portu neprenáša.
