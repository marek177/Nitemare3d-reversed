# DOS 2.0 — riadený replay DSP probe a BIOS wait

11. 11. 2026. **PARTIAL**, deväť riadených instruction replay prípadov; skutočný hardware/DOSBox-X runtime0, DEEP VERIFIED0 B.

## Presný model experimentu

`replay_dos_dsp_probe.py` používa celé pôvodné hash-pinned image bajty. Vykonáva probe1B768 a jeho skutočný wait helper18A31. Neobchádza helper ani ručne nenastavuje výsledný CF/bázu. Hooks poskytujú iba explicitný externý model: IN vracia pripravené status/data BYTE, OUT sa zaznamenáva, INT1Ah/AH0 vracia rastúce syntetické DX tick hodnoty, CX0 a AL0. Pamäť, stack a počiatočné registre sú syntetické. Žiadne fyzické porty sa nevykonajú.

Code hook zastaví normálny NEAR návrat na pripravenú adresu. Pri probe sa kontroluje konečný CF, globálna báza, SP, zachovanie DS/ES/BP/SI/DI, presné reset zápisy a počty poll/data čítaní. Stopy a native-library identita sú v `dos_dsp_probe_replay/evidence.json`.

## Šesť probe výsledkov

| Adapter scenár | Výsledná báza / CF | Status čítania spolu | Data čítania | Reset OUT |
|---|---|---:|---:|---:|
| všetky porty bez ready bitu | 0300h /1 | 3200 | 0 | 32 |
| 0220h ready hneď, replyAAh | 0220h /0 | 401 | 1 | 6 |
| 0220h reply55h,0230h replyAAh | 0230h /0 | 402 | 2 | 8 |
| 0220h ready až na200. poll | 0220h /0 | 600 | 1 | 6 |
| readyAAh až na poslednej báze02F0h | 02F0h /0 | 3001 | 1 | 32 |
| všetky bázy ready, vždy nesprávny reply55h | 0300h /1 | 16 | 16 | 32 |

Všetky assertions prešli. Test s200. poll dokladá, že posledná povolená pripravená odpoveď sa prijme pred ďalším LOOP decrement. Nesprávna reply vedie k ďalšej báze bez opakovania200 pollov na tej istej báze. Po neúspechu sa hodnota0300h nevymaže. Žiadny z týchto adapter scenárov nepreukazuje, že takto odpovie skutočný hardvér.

## Tri wait výsledky

| Počiatočný DX / vstupBX | WORD cieľ | Pozorovanie pri synteticky rastúcom ticku |
|---|---|---|
| 000Ah /1 | 000Bh | INT1A hodnoty10,11,12; návrat po striktne väčšej hodnote |
| FFFEh /3 | 0001h | hodnotyFFFEh,FFFFh; skorý návrat pred prechodom cez wrap |
| FFFEh /1 | FFFFh | bez návratu pri1000 inštrukciách /332 INT1A volaniach |

Posledný beh je riadne ukončený inštrukčným budgetom; loguje presne1000 code hookov, konečný IP2E4Bh a neobnovený aktívny stack stav. Nie je to čakajúci proces ani normálny návrat. Lokálna unsigned JBE slučka pri cieliFFFFh nemá v16-bitovom DX väčšiu hodnotu. Tento záver je podmienený bežným návratom z INT1Ah; skutočné IRQ/BIOS interakcie model nepokrýva.

Wrapped-target prípad ukazuje konkrétny rozdiel medzi low-WORD porovnaním a elapsed-time čakaním. Neoznačuje sa ako prirodzený hang hry, kým sa nepreukáže relevantný vstupný tick, BX, caller a správanie reálneho BIOS modelu.

## Reprodukcia a pokrytie

```text
python replay_dos_dsp_probe.py IMAGE UNICORN_DIRECTORY OUT_DIR
```

Použitý Unicorn2.1.4 a hash natívnej DLL sú uložené v JSON. SMC problém sample IRQ sa týmto netestuje; tieto probe/wait inštrukcie neprepisujú svoj vykonávaný kód.

Centrálne byte counts sa nemenia:27 kandidátnych funkcií,867 inštrukcií/1 978 B,812 dátových B. Prijaté riadené replay prípady teraz32 =23 predchádzajúcich+6 probe+3 wait. Nie je to32 DOSBox-X testov ani sémantické percento. Nové percentá N/A; pôvodný PASS320 ledger a jeho členstvo ostávajú neoverené.

Nasledujúci konkrétny krok: caller reakcia na CF1 a bázu0300h po probe, potom prirodzený DOSBox-X trace s nastavenou/neprítomnou kartou a s watchpointom naCS:2DF0. Do globálneho uzavretia zostávajú BIOS ABI, hardvérové časovanie a indexed/alias writeri.
