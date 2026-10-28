# Nitemare 3D DOS — Ghidra 12.2 pass 2, 2026-10-28

## Finding

Obnovených 74 predtým zlyhaných dekompilácií; počet zlyhaní 107 → 33, bez novej zlyhanej dekompilácie a bez zmeny počtu detegovaných funkcií. Úspešný dekompilát stále nie je dôkaz úplnej správnosti typu, hraníc alebo sémantiky.

## Coverage

| Obraz | Predtým | Teraz | Obnovené | Zostávajúce zlyhania |
|---|---:|---:|---:|---:|
| 1.0 | 557/575 | 569/575 | 12 | 6 |
| 1.1 | 559/577 | 570/577 | 11 | 7 |
| 1.2 | 555/578 | 570/578 | 15 | 8 |
| 1.5 | 563/579 | 575/579 | 12 | 4 |
| 1.7 | 566/580 | 577/580 | 11 | 3 |
| V1.9 (vstupy 1.8/1.9) | 561/579 | 574/579 | 13 | 5 |

## Evidence

| Status | Zistenie | Zdroj | Confidence |
|---|---|---|---|
| Confirmed | 112 guarded prepínacích tabuliek, 2009 položiek; 2345 emulovaných rozhodnutí vrátane troch indexov mimo rozsahu na tabuľku. | evidence/DOS*/switch_proofs.json; evidence/switch_emulation.json | High pre testovaný dispatch |
| Confirmed | Opravených 55 near-call referencií podľa zachovania CS a signed rel16; všetky sú overené v konečnom exporte referencií. | evidence/DOS*/near_specs.json, near_repairs.tsv; evidence/validation.json | High pre inštrukčnú referenciu pri doloženom CS |
| Confirmed | Pri damage gate sa AH nuluje, HP byte sa porovná s AL. HP ≤ AL vynuluje HP; HP > AL prejde do druhej vetvy. | evidence/damage_gate_emulation.json; audit/DOS*/instructions.tsv | High pre testovaný prefix |
| Inferred | Rutiny gate patria k aplikovaniu damage a death/pain rozhodovaniu. | obnovený dekompilát a staršie klasifikácie | Medium pre pomenovanie |
| Unknown | Celý vzorec damage, reachability zo skutočnej hry, renderer parita a presné časovanie. | v tomto passe sa netestovali | Neuzavreté |

## Method

Pracovné projekty sú kópie projects_clean z prvého passu. Kód EXE sa nemenil; opravovali sa referencie a override tabuliek v databáze Ghidry. Pri tabuľkách sa overila súvislá sekvencia CMP AX,max → JA default → zdvojenie AX → XCHG AX,BX → JMP CS:[BX+table]. Pri variante ADD AX,DX bez doloženej kópie AX do DX sa kandidát vynechal. Segment tabuľky sa musí vyskytovať aj ako operand dekódovaného far-call. Bajty okna sa porovnávajú s rekonštruovaným EXE.

112 tabuliek nepredstavuje 112 odlišných herných mechaník: ide o inštancie naprieč šiestimi odlišnými obrazmi. Duplicitný vstup označený 1.8 je stále V1.9, ako bolo potvrdené v prvom passe.

Ghidra dostala výslovné ciele z tabuliek; staré chybné flow referencie zo zdrojov sa odstránili. Výsledné ciele všetkých 112 tabuliek a 55 volaní boli porovnané s exportom po uložení projektu.

Následný samostatný N3DFlowExport zapisuje celé flow exporty cez Files.writeString a marker počtu inštrukcií. Nahrádza aj neúplne dopísaný priebežný TSV pri DOS11. Konečné súbory sú z overeného samostatného exportu, nie z priebežného stavu počas dekompilácie.

## Damage gate behavior model

```c
// Tested prefix; damage producer is replaced by injected AX.
damage = AX & 0xff;
if (record.byte_10 <= damage) {
    record.byte_10 = 0;
    // Continue into branch consistent with death handling.
} else {
    // Continue into nonlethal branch; prefix leaves HP unchanged.
}
```

Testovalo sa všetkých 256 hodnôt HP proti damage {0,1,127,128,254,255}, v šiestich obrazoch: 9216 prípadov. Vstupné AH bolo 0xAB; rutina ho v testovanom prefixe vynuluje. Zahrnuté sú HP=0/damage=0 a rovnosť 255/255. Výpočet damage, následná aktualizácia skóre, animácie a audio sa v tejto emulácii nevykonávali.

Príklad obnoveného tela: V1.9 `14c7:1304`; producent hodnoty `183c:01c6`. Reťazec volania a obnovený dekompilát podporujú interpretáciu, ale názvy polí a význam celočíselnej návratovej hodnoty producenta vyžadujú ďalšiu analýzu.

## Remaining failures

- 1.0: `1000:0ae0`, `17f5:05ca`, `1cdc:209a`, `1f85:0736`, `219b:1744`, `2dec:1cb0`
- 1.1: `1000:0ae0`, `1d00:207e`, `1fa7:048e`, `21bc:1648`, `2e21:19d0`, `2e21:1b14`, `2e21:1b78`
- 1.2: `1000:0ae0`, `1818:05c6`, `1d00:2080`, `1fad:048e`, `21c2:1648`, `2e27:19d0`, `2e27:1b14`, `2e27:1b78`
- 1.5: `1000:0aea`, `181c:05d8`, `1d05:207e`, `21c7:164c`
- 1.7: `1000:0aea`, `1d0f:207a`, `21d1:1648`
- V1.9: `1000:0aea`, `183c:05d8`, `1d25:20ae`, `21ea:164c`, `2d0b:2e0e`

## Next discriminating tests

1. `1000:0ae0/0aea`: samostatný segmentový pohľad a kontrola far-data symbolov; neopravovať bajty hry kvôli AddressOutOfBounds v dekompilátore.
2. Zvyšné renderer near skoky: potvrdiť skutočný CS, porovnať zachovanie IP s Ghidra pcode a až potom navrhnúť override.
3. CRT funkcia `*:1648/164c` (1.0 `219b:1744`): zistiť preconditions indexu tabuľky vrátane XLAT; nezahrnúť nepodložené ciele.
4. `2d0b:2e0e` a podobné vstupy: preveriť, či ide o falošné funkcie vytvorené pôvodným chybným cieľom near call. Samotná oprava referencie ich automaticky neodstránila.
5. Damage producent: sledovať všetky vstupné record polia, náhodné vetvy a možné vrátené AL; až potom hodnotiť presný damage a 1:1 paritu.

## Reproduction

Spúšťače v koreni balíka vyžadujú úpravu miestnych ciest k Ghidre 12.2 a Java 25. Skripty používajú pracovný koreň ako rodiča scripts. Presný postup: scripts/prepare_pass2.py → run_pass2.py → run_flow_export.py → scripts/validate_pass2.py. prepare_pass2 potrebuje inventár a projekty prvého passu. Balík obsahuje aj baseline audit pre porovnanie a rekonštruované EXE.

```bash
python3 scripts/verify_switch_dispatch.py
python3 scripts/verify_damage_gate.py
python3 scripts/validate_pass2.py
```

Emulácia používa Unicorn 2.1.4. Nejde o DOSBox runtime ani test celej hry. Dôkazy o uložení sú v pass2/DOS*.log a flow_DOS*.log.

## Confidence

High pre konkrétne opravené flow referencie a emulačné modely v uvedenom rozsahu. Úplná sémantická analýza všetkých neznámych rutín, samostatná DOS 1.8 a 1:1 herná parita zostávajú otvorené.
