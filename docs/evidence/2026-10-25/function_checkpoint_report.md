# Nitemare 3D — dôkazový checkpoint 25. 10. 2026

GOAL zostáva aktívny a neúplný. Toto je overiteľný inventarizačný a statický priechod, nie dokončená rekonštrukcia všetkých funkcií ani potvrdenie 1:1 parity.

## Overené v tomto priechode

- 13 analyzovaných obrazov má znovu vypočítaný SHA-256 z dostupných súborov. Názvy vydaní zostávajú prevzatými označeniami; číslo vydania nie je dokázané samotným názvom priečinka.
- 13431 kandidátnych vstupov pochádza z existujúcej analýzy. Pre každý vznikol Function Record, CFG, ASM a lokálne register/FLAGS informácie. Neznáma sémantika je výslovne UNKNOWN. Nejde o potvrdený počet funkcií.
- 609233 inštrukčných referencií bolo znovu dekódovaných Capstone 5.0.9 a dĺžkovo kontrolovaných iced-x86 1.21.0. Zistených rozdielov: 0. Referencie zahŕňajú zdieľané inštrukcie; nejde o unikátny kód ani coverage.
- 2425 miest nepriameho toku je evidovaných ako otvorených. Niektoré majú kandidátne ciele; to nepreukazuje úplnú cieľovú množinu.
- DOS 2.0 load image má 171360 B a SHA-256 `e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297`. Opakovaný sken potvrdil 22 doslovných CALL FAR 0FBA:01A0 vzorov zo staršieho censusu, vrátane 8860/886C. Toto je revalidácia známeho výsledku, nie nový objav ani úplný dynamický RNG callgraph.
- RNG wrapper 0FBA:01A0 volá 11EE:31F8. Stav DS:24B8/24BA sa násobí 214013 cez 11EE:3AD8, pripočíta sa 2531011 modulo 2^32, návrat je horných 15 bitov. Seed 1 dá stav 0x0029E2C0 a výstup 41. Overených 4101 syntetických vektorov nezávislých aritmetických formulácií. Nie je to runtime ani remake parity test.
- Existujúci DOSBox-X podporuje debugger, CPU trace a memory-change breakpointy. Originálny zabalený EXE bol spustený v oddelenej pracovnej kópii. Zachovaných je 16 po sebe idúcich krokov revízií 19–34, od 0823:0023 po 0823:0036; ide o štartovací stub. Registre a pamäťové odpovede sú uložené. Hashy prenesených pamäťových blokov boli prepočítané.

## Hranice dôkazov

CFG sa rekonštruoval iba v rámci prevzatého zoznamu inštrukcií. Nové nezávislé objavovanie všetkého kódu neprebehlo. Neznáme call-return/no-return správanie ani nepriamy JMP nie sú uzavreté. Koncový obal rozsahov nie je presná súvislá hranica funkcie. DOS segmenty sú relatívne k MZ load image; NE segmenty sú logické indexy, nie runtime selektory. NE fixupy používajú model prevzatej analýzy a syntetické importné selektory F000+modul; nezávislý audit loadera zostáva otvorený. Preto NE CFG zostáva INFERRED aj pri zhode dekodérov.

Memory mapa zachytáva explicitné dekódované operandy. Neobsahuje úplné implicitné string/stack prístupy, pointer aliasing, def-use, liveness ani absolútne identifikované globálne premenné. Segmentové xrefs sú symbolické závislosti. Cross-version CSV obsahuje podpisy kandidátnych inštrukčných prúdov, nie dôkaz rovnakého algoritmu. Register access a EFLAGS maska pochádzajú z dekodéra, nie z behového merania.

Runtime výpisy pôvodných reportov neboli povýšené na nové VERIFIED_RUNTIME. Úvodný 17-krokový probe mal chybu v názvoch logov, preto sa nepočíta medzi zachované jednotlivé kroky. Opravený logger zachoval ďalších 16 krokov. Pokus o druhú reláciu bol odmietnutý SESSION_BUSY a je evidovaný. Aktuálna relácia zostala pozastavená. Žiadne herné správanie ani percentá neboli menené.

## Repozitáre

Nitemare3d-reversed bol čítaný na commite `497c6fd6272d83509f0958f8042a4e87dee56fdf`; OpenNitemare3D na `1668039e5239e3b094a8302df183fd5cff315bdb`. Inventár obsahuje Git blob SHA pre dokumenty a testy. Obe aktuálne správy explicitne ponechávajú otvorený originál-vs-remake framebuffer/DAC test a P0 gameplay brány. Prístup umožňuje zápis. Verejný checkpoint má obsahovať iba metodiku, agregované výsledky a reproducer, bez EXE, herných dát a plných RAM dumpov.

## Ďalší presný postup

1. Doplniť pracovnú kópiu o všetky potrebné epizódové, SND a UIF dáta, zapísať ich hashy. Súčasný test nepreukazuje úspešný štart gameplayu.
2. Ukončiť/resetovať testovaciu RPC reláciu podľa dokumentácie konkrétneho buildu a zopakovať od MZ entry s opraveným loggerom; zachytiť rozbalenie a prevod runtime CS na hash-pinned load image.
3. Vziať najprv 48 otvorených DOS 2.0 nepriamych miest. Pre každý cieliť registrácie, zápisy pointerov, dispatch doménu, ABI a dosiahnuteľnosť; nevyhlasovať tabuľkový prefix za úplnú doménu.
4. Zachytiť pôvodný main-loop/OBJECT a seed-to-EOF DEMO ledger. Až s rovnakými vstupmi porovnávať remake, tick, slot generation a first-writer.
5. Riešiť renderer 64000+768, weapons/projectiles a prvý post-LOAD frame podľa parity_test_matrix.csv. Všetky P0 brány zostávajú otvorené.

Reprodukcia statického priechodu: Python 3 + Capstone 5.0.9 + iced-x86 1.21.0; `python build_evidence.py <source-checkpoint-root>`. Potrebný je lokálny predchádzajúci checkpoint s analysis JSON a hash-pinned binárkami. Finálny audit: `python finalize_evidence.py` v pôvodnom pracovnom priečinku. Zdrojový koreň a cesty sú v checkpoint.json. Manifest umožňuje kontrolu integrity balíka, nie potvrdenie všetkých sémantických tvrdení.

