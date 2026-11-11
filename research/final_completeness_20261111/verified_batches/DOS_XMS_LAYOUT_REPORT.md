# DOS 2.0 — XMS adaptér, move blok a skoré aliasovanie metadata

11. 11. 2026. Stav **PARTIAL**, nové DEEP VERIFIED 0 B. Statická analýza autentického rozbaleného obrazu; runtime testy 0. Pôvodné členstvo NON-CODE zostáva UNKNOWN.

## Identifikácia externého rozhrania

Rutina pri image 17E08 používa AX=4310h, INT 2Fh a uloží ES:BX do CS:21C8. Nasleduje AH=00h a AH=09h; úspech druhej funkcie testuje AX=1 a uloží DX do CS:21C6. Tieto strojové vzory spolu s nižšie uvedeným move blokom identifikujú **XMS adaptér**. Neidentifikujú výrobcu konkrétneho managera ani celú knižnicu.

Podkladom ABI je pôvodná spoločná Microsoft/Lotus/Intel/AST [XMS 3.0 špecifikácia, január 1991](https://ps-2.kev009.com/basil.holloway/ALL%20PDF/Microsoft_XMS_3%5B1%5D.0_Specification.pdf), strany 4–5 a 8–10 PDF. Dokument definuje získanie vstupu cez 4310h, alokáciu cez 09h a prenos cez 0Bh. Požaduje párnu dĺžku prenosu; pri nulovom handle používa offsetové DWORD ako konvenčný FAR pointer. Toto je kontrakt externého ABI, nie vykonaný test konkrétneho drivera.

Predchádzajúce reporty označovali callback opatrne ako neidentifikovaný. Táto dávka pridáva štrukturálny a primárny dokumentačný podklad pre názov XMS; neuzatvára všetky clobbers, inicializačné vetvy ani dostupnosť drivera. Špecifikácia 3.0 ako zdroj kontraktu neznamená, že program vyžaduje práve driver verzie 3.0.

## Presné polia

Všetky CS polia patria real-mode segmentu 15BF v nerelokovanom obraze. CSV obsahuje end-exclusive hranice aj range SHA.

| CS rozsah end-exclusive | Image rozsah | Typ / použitie |
|---|---|---|
| 20C4..20C6 | 17CB4..17CB6 | WORD počítadlo resource záznamov |
| 21C6..21C8 | 17DB6..17DB8 | WORD uložený XMS handle |
| 21C8..21CC | 17DB8..17DBC | FAR16 XMS entry offset:segment |
| 21CC..21D0 | 17DBC..17DC0 | DWORD move length |
| 21D0..21D2 | 17DC0..17DC2 | WORD source handle |
| 21D2..21D6 | 17DC2..17DC6 | DWORD source offset / konvenčný FAR pointer |
| 21D6..21D8 | 17DC6..17DC8 | WORD destination handle |
| 21D8..21DC | 17DC8..17DCC | DWORD destination offset / konvenčný FAR pointer |
| 2249..2349 | 17E39..17F39 | 256-bajtový read/transfer buffer |

Buffer je doložený nastavením ES=CS, DI=2249h a BX=0100h pred read312E. Nie je servisným poľom ani preukázaným paddingom. Deväť polí zaberá 280 B; tento súčet **nie je prírastok** do centrálnej partition, pretože niektoré polia už obsahovala. Aktuálny lokálny dátový katalóg tejto dávky sa drží oddelene, kým nebude aktualizovaná deduplikovaná únia.

Pri indexovaných operandov CS:[BX+20C6/20C8] ide o páry WORD reprezentujúce 32-bitové resource offsety. Priestor do nasledujúcej metadata hranice by mal aritmeticky 64 DWORD pozícií. **Nie je to dôkaz platného počtu položiek, kapacity ani dovolenej hodnoty indexu.**

## Service49 prenos a kontrola chýb

Na úspešnej vetve po helperi sa počítadlo zvýši. Kód nastaví source handle=0, source offset=15BF:2249, destination handle z CS:21C6 a destination offset z indexovaného záznamu. Každé kladné AX z read312E uloží do dolného WORD length, horný WORD nastavil na nulu pred slučkou. Na 17FAA nastaví AH=0Bh a na 17FAC zavolá XMS entry.

Po návrate na 17FB1 obnoví DS=CS a na 17FB3 **prepíše AX uloženou dĺžkou čítania**. Pred zvýšením destination offsetu a indexovaného záznamu netestuje návratové AX XMS operácie. Preto lokálna slučka posunie účtovaný offset aj v prípade, že driver ohlási neúspech. Správanie konkrétneho drivera a prirodzený výskyt takej chyby zostávajú runtime otázkou.

Z toho vzniká konkrétny test: short read nepárnej dĺžky, napríklad 255, sa bez lokálneho zaokrúhlenia dostane do XMS length. Špecifikácia takú dĺžku nepripúšťa. Nie je dokázané, že originálne resource dáta alebo normálny DOS priebeh túto situáciu vytvoria. Predchádzajúci read replay navyše ukázal, že AX a CF nemusia tvoriť jednoduchý all-or-error kontrakt; táto slučka rozlišuje len AX=0.

Pseudokód lokálneho jadra, s otvorenými externými účinkami:

```text
count = (count + 1) & 0xFFFF
move.source_handle = 0
move.source_far = CS:2249
move.dest_handle = allocated_handle
move.dest_offset = word_pair(CS:20C6 + 4*count)
write_word_pair(CS:20CA + 4*count, move.dest_offset)
while (n = read312E(max=256, destination=CS:2249)) != 0:
    move.length_low = n
    XMS_0B(DS:21CC)   // DS pred callom závisí od aktuálneho kontraktu
    DS = CS
    indexed_record_for_current_count += n
    move.dest_offset += n
return AX=count, DX=0
```

Kód počítadlo po callbacku načítava znovu, preto pseudokód netvrdí nemennosť count cez callback. Zachovanie DS pre prvé volanie vyžaduje caller/helper kontext; samotná LEA SI,21CC DS nenastavuje. Kontrola návratového AX chýba lokálne, nie je tým dokázaná globálna absencia error handlingu v celej hre.

## Metadata alias pred 16-bitovým wrapom

Adresy zapisované pri hodnote n sú `(20CA+4*n) mod 65536` a `(20CC+4*n) mod 65536`.

- n=62: zápis na 21C2/21C4, pred uloženým XMS handle.
- n=63: zápis na 21C6/21C8, teda XMS handle a **offset callbacku**. Tento zápis predchádza prvému XMS move volaniu v lokálnej vetve.
- n=64: zápis na 21CA/21CC, teda segment callbacku a dolný WORD move length.
- n=3FE9h: aritmetický alias na servisné WORD sloty 206E/2070, ako v historickom PASS320 zdroji.

Toto poskytuje skorší konkrétny bod pre count-bound analýzu než vzdialené wrap aliasovanie. **Nie je to preukázaná chyba originálnej hry:** dosiahnuteľnosť count=63, limity alokácie, úspešné opakované načítania a prípadné iné resety ešte nie sú uzavreté. Nulový init obrazu tiež nenahrádza životný cyklus počítadla.

## Reprodukcia a nasledujúce testy

`audit_dos_xms_layout.py IMAGE OLD_INSTRUCTIONS ABSOLUTE_DECODER_DIRECTORY OUT_DIR` overuje hash obrazu, prevzaté CS mapovanie, bajty a nezávislé dekódovanie. V relevantnom CS rozsahu našiel 71 pamäťových operandov: 59 fixných, 12 indexovaných. Výstupy `dos_xms_layout/data_fields.csv`, `cs_operand_xrefs.csv`, `counter_metadata_aliases.csv` a `summary.json` obsahujú dôkazy. Počty operandov nie sú počty funkcií ani celkové pokrytie všetkých aliasov.

DOSBox-X testy: zaznamenať INT2F vstup a konkrétny XMS entry; watchpointy na CS:20C4 a CS:21C6..21DB; pri každom 0Bh uložiť DS:SI, 16-bajtový descriptor a AX/BL návrat; overiť párne aj riadene nepárne short reads; sledovať skutočný rozsah counter a všetky jeho resety. Umelo nastavený count=63 je izolovaný test mechanizmu, nie dôkaz prirodzenej dosiahnuteľnosti.

Najbližší krok: uzavrieť callerov service49 a podmienky počtu úspešných resource loadov. Pôvodný PASS320 ledger ostáva chýbajúci; žiadny z týchto intervalov nebol spätne označený za jeho NON-CODE členstvo.
