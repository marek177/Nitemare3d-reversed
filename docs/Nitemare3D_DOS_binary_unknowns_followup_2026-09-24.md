# Nitemare 3D — new findings z DOS binary file

Date: 24. 9. 2026

This record continues v analysis unclosed DOS areas. Compares rozbalené load images versions 1.0, 1.7, 1.9 and 2.0. DOS V1.8 as separate build was not confirmed. Analysis is static; original game sa v this kroku nespúšťala.

## usage binary obrazy

SHA-256 are directly prekontrolované relative to predchádzajúcemu registru rozbalených image. Addresses below are offset v these image, nie offset v zabalenom EXE.

| DOS build | SHA-256 obrazu |
|---|---|
| V1.0 | `113ea529e4247a5991f9dde2bd49e04b61f5714a8ea838d027014cac261e004a` |
| V1.7 | `df85d457e752860dc8fc8c39c4c36ba1c62f03b0e704f1365ee618d8ed8447ff` |
| V1.9 | `e29a8d058fdf3033241f4f711bca273fb168d750f8f972047e1be8f3d946529e` |
| V2.0 | `e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297` |

## 1. Switch `-b` zapína diagnostic prehľad

Parser prijme `-b` and sets local flag. After process argumentov ho pass štartovacej function. That flag skontroluje and during zapnutom state calls format routine with viacerými text and count. Is one štartovací listing, nie o slučku v game ticku.

| Build | Miesto, where parser sets flag | Condition štartovacieho výpisu |
|---|---:|---:|
| V1.0 | `0x48B4` | `0x4705` |
| V1.7 | `0x49F6` | `0x480F` |
| V1.9 | `0x4B5A` | `0x4973` |
| V2.0 | `0x4B5A` | `0x4973` |

Format strings v dátovom segment určujú content prehľadu:

| Build | Data in výpise |
|---|---|
| V1.0 | Count vector and object; count strážcov; frames for sekundu and milisekundy; využitie near, far and extended heapu; štatistiky tile and sound slotov including reloadov, thrashov, XMS and disku |
| V1.7 | Vector, objects and strážcovia v jednom row; frame frekvencia; near/far/extended heap; tile, object and sound sloty |
| V1.9 | Same skupiny as V1.7 |
| V2.0 | Same skupiny as V1.7 |

Extended heap line is condition flag extended-memory branches. From V1.7 is add line `Object slots`; V1.0 has separate lines for overall counts vector/object and strážcov. Text „Frame rate“ contains four numeric arrays, but their exact assign k interným timer nebolo v this kroku rozobraté.

**Conclusion:** functional behavior `-b` is teraz supported as štartovací diagnostic/benchmarkový prehľad o count, výkone and memory cache. Meaning itself písmena `b` and exact output kanál (screen, stdout or presmerovaný output) remain unconfirmed.

## 2. Switch `-o` zapína write to `debug.txt`

For DOS V1.7, V1.9 and V2.0 parser sets global flag during `-o`. Separate logovacia function sa naň pozerá before každým record. If is vypnutý, function sa returns without write. If is zapnutý, opens `debug.txt`, send format message, then file zavrie.

| Build | Parser `-o` | Logovacia function | Name and modes file |
|---|---:|---:|---|
| V1.7 | `0x4A50` sets `DS:0x3C40=1` | `0x4674` | `debug.txt`; modes `w` and `a` |
| V1.9 | `0x4BB4` sets `DS:0x3CD0=1` | `0x47D8` | `debug.txt`; modes `w` and `a` |
| V2.0 | `0x4BB4` sets `DS:0x3CD0=1` | `0x47D8` | `debug.txt`; modes `w` and `a` |

During element record sa call mode `w`; additional calls call `a`. If sa file cannot open, code references on text `Error opening file %s`. Logovacia function uzatvára file after zapísaní each record.

**Conclusion:** from V1.7 is `-o` static confirmed as zapnutie diagnostic logovania to `debug.txt`. This is different from `-b`: `-b` pripraví súhrnný prehľad, `-o` allow logovacie calls rozmiestnené v programe. Nepotvrdzuje sa, that `-b` writes to `debug.txt`. V1.0 has during `-o` other target branch and its meaning so far is not closed. Itself file sa during static analysis nevytváral.

## 3. Array `CONFIG.SAV +0x02` does not have find priameho čitateľa

Array is druhé 16-bit word 16-byte block `CONFIG.SAV`. Its build-relatívna address sa changes according to DOS versions:

| Build | DGROUP | Start block | Unknown array `+0x02` | Instruction initialization |
|---|---:|---:|---:|---:|
| V1.0 | `0x2360` | `DS:0x3F9C` | `DS:0x3F9E` | `0x32F1` |
| V1.7 | `0x2754` | `DS:0x40B4` | `DS:0x40B6` | `0x33E1` |
| V1.9 | `0x276D` | `DS:0x4144` | `DS:0x4146` | `0x33DF` |
| V2.0 | `0x2771` | `DS:0x4144` | `DS:0x4146` | `0x33DF` |

Initialize instruction writes DWORD `0x00000130` on start block, so during defaultoch is `+0x00 = 304` and `+0x02 = 0`. V each from four zostavení sa našli priame references on start block or its first word, but **none priamy operandový reference on address `+0x02`** v provided CFG inštrukčných inventory. Block sa loads and serializuje as 16 bytes.

Známa výpočtová path image výrezu odvodzuje height as `width >> 1`, therefore array `+0x02` does not have evidence, that by určovalo height viewportu.

**Najlepšie podložená klasifikácia:** probably rezervované or historical preserved WORD array without priameho spotrebiteľa v skúmaných DOS image. This is not define evidence, that ho none aliasovaný pointer nikdy nečíta; complete uzavretie all indirect prístupov still missing.

## What remains open

- remain 31 indirect call miest on each DOS build still is not klasifikovaných.
- During `-b` remains output kanál and exact meaning all numeric fields rámcovej frekvencie on confirmation.
- V1.0 branch `-o` potrebuje separate track; its flag cannot without evidence stotožniť with neskorším `debug.txt` loggerom.
- `CONFIG.SAV+0x02` potrebuje close through complete track únikov pointer and case runtime watchpoint.
- None z these finding nepotvrdzuje prirodzené game behavior nor output on hardvéri.

**Level evidence:** confirmed static z raw 16-bit instructions, dátových string, priamych odkazov and row toku. Without runtime confirm.
