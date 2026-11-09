#!/usr/bin/env python3
"""PASS153 conservative FAR-pointer / segment-block structural audit.
Input: PASS150 published JSON. Does not reconstruct original EXE or runtime state.
"""
import json, re, pathlib
p=pathlib.Path('/mnt/data/files/N3D_PASS150_evidence.json')
x=json.loads(p.read_text())
report={'pass':153,'source':p.name,'method':'reanalysis of PASS150 evidence, not new original-binary disassembly','builds':{},'paired':{},'limits':[]}
for label,v in x['direct_references'].items():
 refs=v['references']
 jump=[r for r in refs if r['instruction'].lower().startswith('ljmp ')]
 cx=[r for r in refs if r['instruction'].lower().startswith('mov cx,')]
 es=[r for r in refs if r['instruction'].lower().startswith('mov es,')]
 assert len(refs)==53 and len(jump)==len(cx)==1 and len(es)==51
 def addr(r):
  a,b=r['address'].split(':');return (int(a,16),int(b,16))
 j=jump[0]; c=cx[0]; seg,ip=addr(j); cseg,cip=addr(c)
 assert seg==cseg
 target=int(j['fields'][0],16); cxvar=int(c['fields'][0],16)
 assert cxvar==target+2
 # 16-bit indirect FAR pointer: m16:16 = offset word followed by segment word
 report['builds'][label]={'references':len(refs),'segment_load_reads':len(es),'cx_reads':len(cx),'indirect_far_jumps':len(jump),'far_pointer':{'offset_word':f'{target:04X}','segment_word':f'{target+2:04X}','size_bytes':4,'instruction':j['instruction'],'address':j['address'],'cx_read':c['address'],'cx_word':f'{cxvar:04X}','address_delta_from_cx':ip-cip,'possible_intervening_bytes':max(0,ip-cip-4)},'distinct_segment_slots':sorted(set(r['fields'][0] for r in es)),'static_zero_block':x['builds'][label]['all_30_bytes_zero']}
old=report['builds']['DOS_1.8']; new=report['builds']['DOS_2.0']
assert int(new['far_pointer']['offset_word'],16)-int(old['far_pointer']['offset_word'],16)==2
assert int(new['far_pointer']['segment_word'],16)-int(old['far_pointer']['segment_word'],16)==2
report['paired']={'segment_reads_51_plus_2_special_reads':53,'field_shifts_all_plus_2':all(int(b['fields'][0],16)-int(a['fields'][0],16)==2 for a,b in zip(x['direct_references']['DOS_1.8']['references'],x['direct_references']['DOS_2.0']['references'])),'same_function_kinds':all(a['instruction'].split('[')[0]==b['instruction'].split('[')[0] for a,b in zip(x['direct_references']['DOS_1.8']['references'],x['direct_references']['DOS_2.0']['references']))}
report['limits']=['Only 53 candidate explicit reads per build are analyzed; the scan is not comprehensive for pointer writes, aliasing, relocation and copies.','MOV CX and LJMP instruction starts are 6 bytes apart. Without the two intervening bytes there is no proof that CX still contains the FAR-pointer segment at jump time.','Static zeros do not imply zero during runtime; indirect JMP target cannot be determined.','The DOS_1.8 label is contested by an older audit attributing the same normalized-image digest to DOS 1.9.']
path=pathlib.Path('/mnt/data/N3D_PASS153_evidence.json');path.write_text(json.dumps(report,indent=2,ensure_ascii=False))
md=f'''# Nitemare 3D — PASS 153: FAR ukazovateľ a hranice dôkazu

Dátum: 2026-11-09. Zdroj: `N3D_PASS150_evidence.json`. Metóda: samostatná štruktúrna kontrola už publikovaných inštrukcií; **bez novej disassemblácie EXE a bez runtime testu**.

## Kontrolovaný výsledok

- Pre každý z dvoch obrazov existuje v 53 explicitných referenciách **51 čítaní segmentu do ES, jedno čítanie do CX a jeden nepriamy FAR `LJMP`**.
- Starší obraz: `11EA:397E mov cx,[2552h]` a `11EA:3984 ljmp [2550h]`.
- DOS 2.0: `11EE:397A mov cx,[2554h]` a `11EE:3980 ljmp [2552h]`.
- Pre 16-bitový `LJMP m16:16` predstavujú štyri bajty od adresy operandu dvojicu `IP` (nižší WORD) a `CS` (vyšší WORD). Čítanie `CX` v oboch obrazoch referuje presne na **horný WORD** tohto FAR ukazovateľa.
- Rozdiel medzi začiatočnými adresami `mov cx` a `ljmp` je v oboch prípadoch **6 bajtov**. Keďže `mov cx,[disp16]` má typicky štyri bajty, medzi inštrukciami zostávajú **dva neanalyzované bajty**. Nedá sa preto tvrdiť, že CX pri skoku nevyhnutne obsahuje segment cieľa, pokiaľ nepoznáme vloženú inštrukciu.
- Všetkých 53 odvodených párov zachováva posun operandov o +2; to nie je dôkaz presného dôvodu posunu ani iniciátora zápisov.

## Layout známy z použitých operandov

| Obraz | FAR offset (IP) | FAR segment (CS) | Čítanie segmentu do CX |
|---|---|---|---|
| Starší (v archíve DOS_1.8, identita sporná) | DS:2550 | DS:2552 | 11EA:397E |
| DOS 2.0 | DS:2552 | DS:2554 | 11EE:397A |

Tento layout je **interpretácia inštrukcie**, nie dôkaz, že celá oblasť obsahuje iba ukazovatele. V DOS 2.0 `DS:2550` nie je v úzkom súpise explicitne referované, ale to neimplikuje nepoužiteľnosť ani absenciu zápisu.

## Čo zostáva neznáme

1. Obsah dvoch medziľahlých bajtov medzi `mov cx` a `ljmp` a ich účinky na CX, DS, FLAGS a zásobník.
2. Producent 4-bajtovej hodnoty v `DS:2552–2555` (DOS 2.0): priamy zápis, pamäťová kópia, relokácia alebo aliasovaný ukazovateľ.
3. Cieľový `CS:IP` v runtime a dosiahnuteľnosť skoku.
4. Inicializácia susedných segmentových premenných a validita pred LOAD a pri prvom snímku.
5. Overenie identity staršieho normalizovaného obrazu podľa skutočného EXE, nie podľa názvu priečinka.

## Ďalší cielený krok

Získať pôvodný normalizovaný EXE alebo kompletný ASM úsek `11EE:397A–3983`, dekódovať medzibajty; následne hľadať def-use a všetkých writerov rozsahu `DS:2552..2555`, vrátane implicitných zápisov a relokácií. Pri DOSBox-X trace logovať posledný writer pre každý zo 4 bajtov a adresu cieľa v momente skoku.

Záver: **preukázané prekrývanie čítania CX s druhým WORD nepriameho FAR cieľa**, nie ešte producent ani runtime hodnota.
'''
path2=pathlib.Path('/mnt/data/N3D_PASS153_far_pointer_audit.md');path2.write_text(md)
print(json.dumps({'report':str(path2),'evidence':str(path),'builds':report['builds'],'paired':report['paired']},indent=2))