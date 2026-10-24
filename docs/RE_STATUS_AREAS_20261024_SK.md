# Nitemare 3D — stav oblastí a dôkazov (24. 10. 2026)

> Táto správa sumarizuje súčasný výskumný stav; nepridáva novú pôvodnú runtime stopu, potvrdenie 1:1 parity ani nové dekódované bajty. Percentá sú orientačné expertné odhady, **nie** code coverage, byte coverage ani úspešnosť regression testov.

## Agregovaný odhad

| Metrika | Odhad | Interpretácia |
| --- | ---: | --- |
| Statická/semantická znalosť | 99–99,5 % | Pracovný odhad rozsahu preskúmania, bez úplného dôkazu všetkých vetiev |
| Behaviorálna znalosť | 97–98 % | Mnohé originálne mechaniky sú opísané, neznamená tick-exact reprodukciu |
| Pripravenosť na implementáciu 1:1 | 96–97 % | Výskumná pripravenosť, nie hotovosť portu |
| Celková parita remaku | 89–92 % (historický odhad) | **Neoverené end-to-end meraním**; nesmie sa prezentovať ako test-pass rate |

## Odhady po oblastiach — porozumenie originálu, nie stav implementácie

| Oblasť | Odhad |
| --- | ---: |
| Mapy a dátové formáty | 98–99 % |
| RNG a determinismus | 96–98 % |
| Hlavná slučka a OBJECT scheduler | 94–97 % |
| DEMO/vstup | 94–97 % |
| Renderer, steny, VGA | 92–96 % |
| GUARD AI/bossovia | 90–96 % |
| Zbrane a projektily | 89–94 % |
| Sprity, HUD, paleta | 89–95 % |
| SAVE/LOAD/cache | 89–94 % |
| Win16 gameplay | 89–94 % |

## Dôkazové hranice

- Originál DOS 2.0 má zachytené runtime merania vstupov, pohybu, vybraných projektilových/RNG sekvencií a renderovacích komponentov. Pozri existujúce dátované dokumenty a príslušný evidence registry.
- Aktívny renderer v `Nitemare3d-reversed` stále používa diagnostické DDA. Nenahrádza overenú pôvodnú VEC/owner/span pipeline.
- Žiadny kompletný synchronizovaný **originál ↔ remake** test framebufferu 320×200 (64 000 indexed pixelov) spolu so všetkými 768 DAC hodnotami nebol vykázaný ako PASS.
- OpenNitemare3D je samostatný clean-room bootstrap, nie 89–92 % hotová implementácia. Agregované RE odhady sa nesmú prenášať na jeho programovú dokončenosť.
- Príprava diagnostického ZIP balíka a návrhu funkcií pre Codex/OpenAI je projektová dokumentácia, **nie nový RE dôkaz**; nemení percentá.

## Prioritné akceptačné brány

1. **P0 renderer:** párovaný pôvodný framebuffer a DAC vs remake, prvá divergencia, zdokumentovaný vstupný stav; potom až náhrada DDA.
2. **P0 projektily/weapon:** presné poradie scheduleru, slot lifecycle, stale-depth, DAMAGE a RNG rejection branch.
3. **P0 SAVE/LOAD:** prvý gameplay frame po LOAD, objektové cache a deterministický návrat.
4. **P0 scheduler/DEMO:** vstup/tick/frame ordering, RNG caller ledger, viacaktérové modifikácie v rámci ticku.
5. **P1 Win16:** samostatný runtime a prvá DOS-vs-Win divergencia.
6. **P1 GUARD/bossovia:** špeciálne transformácie, útoky a death flow.

## Politika ďalších aktualizácií

- Zvýšiť percento iba pri novom, identifikovateľnom dôkaze: SHA-pinned binárka, trace/offset, reprodukčný príkaz, expected/actual, výsledok nezávislého testu.
- Rozlišovať `original_runtime`, `static_evidence`, `synthetic_test` a `original_vs_remake_parity`.
- Nespájať pokrytie binárnych bajtov, pochopenie semantiky, implementáciu a paritu do jediného čísla.
- Neoznačovať syntetický PASS za dôkaz hernej 1:1 parity.

Súvisiace podklady: [RE konsolidácia](RE_CONSOLIDATION_20261022_24_SK.md), [akceptačná matica](RE_IMPLEMENTATION_ACCEPTANCE_20261024_SK.md), [evidence registry](RE_EVIDENCE_REGISTRY_20261022.json).
