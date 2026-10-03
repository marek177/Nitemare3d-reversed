# Nitemare 3D DOS — identify kandidáta „v1.8"

Date: 2026-09-24  
Range: provided files `N3D(5).EXE`, `N3D-E-18(1).EXE`, `N3D-UNP.EXE` and `N3D-E-18.EXE(1).i64`.  
Metóda: static analysis bytes, DOS MZ/DIET headers, hashov, reťazcov and krátkeho bitstream dekódera. Program was not spúšťaný.

## Conclusion

V dodanej skupine is not confirmed DOS build V1.8.

- `N3D-E-18(1).EXE` also `N3D-UNP.EXE` are byte-identické with referenčným `N3D-E-18.EXE`/`N3D-E-19.EXE` and vnútri contain `V1.9`.
- `N3D(5).EXE` is DIET-komprimovaný EXE obraz. Its dekomprimovaný start sa zhoduje with V1.9 obrazom and its header states original length exactly `0x1C74C` = 116 556 bytes, therefore size V1.9 file.
- `.i64` databáza is IDA databáza for `L:\nd-3-18\N3D-E-18.EXE`, with load range `0x0000–0x1C74C`.

For next audit sa therefore these files have mark as **DOS V1.9 / E18–E19 image**, nie as V1.8.

## Binary register

| File | Size | SHA-256 | Version / status |
|---|---:|---|---|
| `N3D-E-18(1).EXE` | 116 556 | `1cbb55c193b75424ee6b287f3a902a0a3c243a392d034086d040b07c99994be8` | DOS MZ, strings `V1.9`; identický with referenciou E18/E19 |
| `N3D-UNP.EXE` | 116 556 | `1cbb55c193b75424ee6b287f3a902a0a3c243a392d034086d040b07c99994be8` | exact copy E18/E19 |
| `N3D(5).EXE` | 74 426 | `ea9cbea5896a304cf6851f90d6b2559295a0d596fec657e5a1d11a50042d1462` | DIET-packed EXE; version is v komprimovanom obraze |
| `N3D-E-18.EXE(1).i64` | 819 513 | — | IDA databáza for E18; is not DOS EXE |

Priame evidence for nekomprimovaný obraz:

- `Nitemare-3D -- Demo Mode` on file offsete `0x1A84E`.
- `Nitemare-3D` on `0x1A88E`.
- `V1.9` on `0x1A89A` and `0x1AA1C`.
- DOS MZ image start: 512 bytes; entry file offset `0x1B900`.

## `N3D(5).EXE`: DIET header

File starts 32-byte MZ hlavičkou and identify `diet` on offsete `0x1C`. Charakteristický DIET v1.44 bootstrap odtlačok is on offsete `0x48`; DLZ header starts on `0x6B`:

```text
64 6c 7a 31 34 21 3c 92 04 4c c7
```

Z headers vyplýva:

- compressed stream: `0x76–0x121AA`, length `0x12134` = 74 036 bytes;
- original size obrazu: `((0x04 >> 2) << 16) | 0xC74C = 0x1C74C` = 116 556 bytes;
- value sedí with size `N3D-E-18.EXE` and with range load v `.i64` databáze.

Krátky bitstream probe (without tvrdenia, that is hotový univerzálny UNDIET tool) emitoval first code:

```text
55 8b ec 57 b8 f9 21 8e d8 33 c9 b8 76 30 8c da
8b d8 8e c2 39 0e 00 00 7e 1c 8b 7e 06 8b 46 08
```

This prefix is identical with začiatkom E18/E19 obrazu. Probe sa zastaví during prvej segmentovej/EXE spätnej referencii (`offset 113`, so far only 58 výstupných bytes); on complete rozbalenie needs to add DIET EXE IDATA/segment-refresh rekonštrukciu. To is limit dekódera, nie evidence different versions.

## Status evidence

| Tvrdenie | Status | Confidence |
|---|---|---|
| `N3D-E-18(1).EXE` is V1.9 | confirmed embedded strings + SHA | high |
| `N3D-UNP.EXE` is tá istá binárka | confirmed identickým SHA | high |
| `N3D(5).EXE` is DIET-packed EXE | confirmed MZ/DIET odtlačkom and DLZ hlavičkou | high |
| `N3D(5).EXE` is packed forma E18/V1.9 | silno podporené original size, `.i64` cestou and dekódovaným prefixom | high, complete byte-for-byte evidence čaká on completion unpacku |
| provided files contain actual V1.8 release | unconfirmed; available evidence smerujú on V1.9 | high |

## Consequence for audit

Results z doterajšieho DOS auditu, which use these files, needs to viesť pod identify **V1.9 (E18/E19)**. For separate V1.8 audit needs to dodať EXE with verify `V1.8` reťazcom or známym SHA-256. Name file `N3D-E-18` itself o sebe is not enough, because dodaná binárka contains `V1.9`.
