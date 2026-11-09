import zipfile,re,json,hashlib,collections
ZIP='/mnt/data/files/N3D_FUNCTIONS_PASS100_NATIVE_OBJECT_EFFECTS_AND_RECORD_LOOKUP.zip'
BASE='pass019/analysis/DOS_2.0/'
FIELDS=['2556','2558','255E','256A']
with zipfile.ZipFile(ZIP) as z:
 img=z.read(BASE+'normalized_image.bin')
 records=[]
 for n in z.namelist():
  if not n.startswith(BASE+'functions/') or not n.endswith('.asm'):continue
  for line in z.read(n).decode(errors='replace').splitlines():
   m=re.match(r'^([0-9A-Fa-f]{4}):([0-9A-Fa-f]{4})\s+([0-9a-f]+)\s+(.*)$',line)
   if not m:continue
   seg,off,hexbytes,op=m.groups()
   targets=[f for f in FIELDS if ('[0x'+f.lower()+']') in op.lower()]
   if not targets:continue
   raw=int(seg,16)*16+int(off,16)
   match=img[raw:raw+len(hexbytes)//2]==bytes.fromhex(hexbytes)
   records.append({'function':n.split('/')[-1],'address':seg+':'+off,'raw':hex(raw),'bytes':hexbytes,'opcode':op,'fields':targets,'byte_match':match,'classification':('read' if 'mov es' in op else 'other')})
 r={'source':ZIP,'image_sha256':hashlib.sha256(img).hexdigest(),'image_bytes':len(img),'scope':'direct operand reads in candidate DOS 2.0 ASM files; indirect writers not covered','records':records,'count_by_field':{f:sum(f in x['fields'] for x in records) for f in FIELDS},'verified':sum(x['byte_match'] for x in records),'all_match':all(x['byte_match'] for x in records)}
 open('/mnt/data/N3D_PASS149_evidence.json','w').write(json.dumps(r,indent=2))
 report=['# Nitemare 3D – PASS149: audit segmentových premenných','', '## Zdroj',f'Normalizovaný DOS 2.0 obraz: SHA-256 `{r["image_sha256"]}`; {len(img)} bajtov.','', '## Priame prístupy','', '| Globálna adresa | Výskyty | Interpretácia dostupných inštrukcií |','|---|---:|---|']
 labels={'2556':'segment pre počítadlo a väzby 18-bajtových mapových záznamov','2558':'segment čítania tried mapových buniek','255E':'segment pre pomocnú kontrolu a lookup objektov','256A':'segment používaný GUI/SAVE zoznamami; 18-bajtové indexovanie v 0D29:2204'}
 for f in FIELDS:report.append(f'| `DS:{f}` | {r["count_by_field"][f]} | {labels[f]} |')
 report+=['','## Overené inštrukcie','']
 for x in records:report.append(f'- `{x["address"]}`: `{x["opcode"]}`; bajty `{x["bytes"]}`; EXE '+('ZHODA' if x['byte_match'] else 'NESÚLAD'))
 report+=['','## Obmedzenia dôkazu','- Porovnanie potvrdzuje miestne opcode bajty, nie úplnú dosiahnuteľnosť funkcií.','- V kandidátnych ASM výpisoch nebol nájdený priamy explicitný zápis na uvedené adresy; to **nevylučuje** inicializáciu dátového segmentu, nepriamu adresáciu, segmentové aliasy alebo kopírovanie.','- `DS:256A` nie je automaticky identické s `DS:2556`/`2558`, ani keď všetky obsahujú 18-bajtové záznamy.','- Pre dokázanie platnosti pri LOAD je potrebný register hodnôt segmentov pred LOAD, po zmene mapy a prvom frame.','- Kompletný Win16 binárny diff a runtime test sa v tomto priechode nevykonali.']
 open('/mnt/data/N3D_PASS149_segment_provenance.md','w').write('\n'.join(report)+'\n')
 print(json.dumps({'sha':r['image_sha256'],'counts':r['count_by_field'],'verified':r['verified'],'total':len(records),'all_match':r['all_match']}))