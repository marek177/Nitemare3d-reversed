# Nitemare 3D DOS 1.0: hĺbková static batch 01

Date: 2026-09-28. Input: rozbalený `N3D-E-10.EXE`, SHA-256 `7035d185d27a4629664e9a300b77870577195205bbabcd17bbaf74a9ecf4cd04` (115 152 bytes), and dekompilovaný `N3D-E-10.EXE(4).c`, SHA-256 `ba11af55f759870e9153c2eabbf6e8eb68ab3b83349868b70e7db3d6d2dae194`. Match hash prefixu EXE with inventory z 2026-09-26 confirms identitu DOS 1.0. Lines below označujú dekompilovaný export, nie original source code. Addresses `1000:xxxx` are names z exportu; addresses data interpretujeme as offset up to after next check segment.

## Result

Preverených 8 susediacich functions `1000:0F6A` up to `1000:11B2`. Total related with dvojicou map ID on cell map and with odvodzovaním flag for 256 possible ID. Map uses dvojice bytes from `0x373E` and step `0x80` during prechode on next line; 64 × 64 buniek is doložených slučkami `1034`/`1088`. Meaning each ID classes and initialization tabuliek remain open.

| Function; lines exportu | Static finding | Confidence / obmedzenie |
|---|---|---|
| `0F6A`; 1207–1233 | Searches `param_1` v 256-byte table from `0xD154`, najprv from `param_2` after 255, then from 0 after 255; during nenájdení calls `func_0x0000f67a`. Druhé prehľadanie **is not** obmedzené on `param_2-1`. | Medium: exact loops v exporte; missing check original assembleru and terminácie error routines. |
| `0FB4`; 1235–1254 | Same dopredný lookup from `param_2` v `0xD254`, but **without** návratu on start tables. | Medium; nesymetria with `0F6A` is directly v exporte. |
| `0FEA`; 1256–1279 | iterate through records with krokom `0x1C`, count z `0x60C6`; compares byte on offset `+0x0C` with input and returns byte `+0x0A` zodpovedajúceho record; otherwise error routine. | Lower: dekompilátor uses holý pointer `0xC`; bázu segment and possible boundary needs to verify. |
| `1034`; 1281–1309 | Prejde 64 × 64 first bytes map dvojíc from `0x373E`; z tých, ktorých table value v `0xD154` corresponds to input, returns **najvyššie numeric ID**; during žiadnej match returns 0. | Medium: loop and maximum z exportu. Nula can be valid ID, so sama osebe does not have to označovať neprítomnosť. |
| `1088`; 1311–1339 | Analóg `1034` for second byte from `0x373F` and table `0xD254`. | Medium. |
| `10DC`; 1341–1357 | During zero cache `0x254A` calls `0F6A` with value `0x44` (export nevie spoľahlivo display second argument). If map input ID through `0xD154` gives `0x44` (`'D'`), returns difference ID and cache; otherwise `-1`. | Medium for condition, low for complete podpis and interpretáciu difference. |
| `1118`; 1359–1412 | Z tables 256 bytes `0xD154` odvodzuje after jednom flag byte to areas `0xCE52`. Specifically visible condition: bit 2 for `1..0x30`; bit 4 for `0x2E..0x2F`; bit 3 for `0x31..0x40`; bit 1 for `1..0x40`; bit 6 for `0x47..0x48`. Next operation on bitoch 0 and 5 depends from bitov 2/3. | Medium for listed intervaly; **low for entire result flag**, lebo `local_3` is v exporte neinicializované and jedna mask is neobvyklá. |
| `11B2`; 1414–1458 | Z tables 256 bytes `0xD254` odvodzuje flags to `0xCF52`: bit 0 for `0x06..0x3D`, bit 1 for `0x08..0x2D`, bit 2 for `0x2F..0x3D`, bit 3 for `0x08..0x25`, bit 5 during `0x2A`, bit 6 during `0x04`. | Medium for range; result byte neistý for neinicializované `local_3` and prekryv with dekompilovaným `1232`. |

## Krížové check

- `03FE` (lines 305–355) iterate through map from `0x373E` and test second map byte through `0xD254` proti class `3`; first byte through `0xD154` passes nasledujúcemu lookupu. To supports interpretáciu **dvoch rozličných map ID vrstiev**, nie so far their exact named.
- `12B6` (lines 1546–1588) reads oba bytes jednej map dvojice and test second flag table from `0xCF52` on bit 1. `switchD_1000_8285` (lines okolo 14359) test element flag table from `0xCE52` on bit 3. These two odbery podporujú, that `1118`/`11B2` create runtime klasifikačné flags.
- Listing call named `FUN_1000_*` ukazuje only explicit call `0F6A` z `10DC`. Missing other calls **nedokazujú nepoužitie**: export during next call states generické `func_0x...`, fragmenty and possible incorrect boundaries functions.

## Podporený model

```c
// Pseudokód podľa dekompilácie; names/types are provisional.
uint16_t find_first_layer_id(uint8_t class_id, uint8_t start) {
    for (uint16_t id = start; id < 256; ++id)
        if (first_class[id] == class_id) return id;
    for (uint16_t id = 0; id < 256; ++id)
        if (first_class[id] == class_id) return id;
    fatal_or_error(/* undecoded */);
}

uint8_t max_present_first_layer_id(uint8_t class_id) {
    uint8_t max_id = 0;
    for (uint16_t cell = 0; cell < 4096; ++cell) {
        uint8_t id = map_pairs[2 * cell];
        if (first_class[id] == class_id && id > max_id) max_id = id;
    }
    return max_id;
}
```

During `1118` and `11B2` sa pseudokód complete output flag intentionally neuvádza: export rozdelil `11B2`/`1232` podozrivo and premenná flag does not have v dekompilácii initialize.

## What needs to verify on confirmation

1. V IDA or inštrukčnom výpise for `1000:1118` up to `1000:1254` compare actual function boundaries, initialize local byte and mask bitov; `1232` can be incorrect create separate function in vnútri loops `11B2`.
2. For `0F6A`/`0FB4` zistiť call konvenciu, complete argumenty and whether `func_0x0000f67a` terminate program, or returns value.
3. On data `MAP.1` and corresponding ID table confirm, what physical mean first and second byte; compare several známych buniek with hrou.
4. Rozšíriť batch on source naplnenia tabuliek `D154/D254` and path, which call their flag odvodenie. Without toho cannot zodpovedne assign names specific class.

**Overall confidence:** medium for topológiu slučiek and map dvojíc, low for exact meaning class and complete logic flag. Is not eight plne uzavretých functions nor o percentuálny posun entire EXE.