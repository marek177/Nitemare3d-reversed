#!/usr/bin/env python3
"""Nitemare 3D PASS154: read-only original DOS2 EXEPACK + bounded byte audit.
Requires user-owned all-nite3d.zip and verify_v040.py unpacker from previous audit.
Does not execute original game or persist its unpacked bytes.
"""
from pathlib import Path
import zipfile,hashlib,importlib.util,json
BASE=Path('/mnt/data')
Z=BASE/'files/all-nite3d.zip'
V=BASE/'files/verify_v040.py'
S=importlib.util.spec_from_file_location('original_unpacker',str(V))
v=importlib.util.module_from_spec(S);S.loader.exec_module(v)
with zipfile.ZipFile(Z) as z:
  raw=z.read('nite3d/dos/N3D-Dos/N3D-UNFU.exe')
  older18=z.read('nite3d/dos/nd-3-18/N3D-E-18.EXE')
  older19=z.read('nite3d/dos/nd-3-19/N3D-E-19.EXE')
assert hashlib.sha256(raw).hexdigest()==v.EXPECTED_SHA256
assert hashlib.sha256(older18).digest()==hashlib.sha256(older19).digest()
image=raw[512:]
mem,runs,counts=v.unpack_mz_image(image)
_,relocations=v.custom_relocations(image)
# Verified 16-bit code bytes, expanded image file-linear addresses.
checks={
  'caller_argument_gate':(0x15526,'83 7e 06 02 75 12'),
  'caller_target':(0x15533,'9a 7a 39 ee 11'),
  'guard_and_jmp':(0x1585a,'8b 0e 54 25 e3 04 ff 2e 52 25'),
  'fallback':(0x15864,'b8 ff ff c7 06 18 21 16 00 e9 27 cc'),
  'callback_range_1':(0x120c1,'be 52 25 bf 52 25 e8 a1 00'),
  'callback_range_2':(0x12113,'be 52 25 bf 52 25 e8 4f 00'),
  'callback_scan':(0x1216b,'3b f7 73 0e 83 ef 04 8b 05 0b 45 02 74 f2 ff 1d eb ee c3')
}
for k,(at,h) in checks.items():
  expected=bytes.fromhex(h)
  assert mem[at:at+len(expected)]==expected,(k,mem[at:at+len(expected)].hex())
needles={'direct_call_11EE_397A':'9a 7a 39 ee 11',
         'indirect_far_jmp_DS_2552':'ff 2e 52 25',
         'SI_2552':'be 52 25','DI_2552':'bf 52 25',
         'mov_CX_DS_2554':'8b 0e 54 25'}
counts_by={}
for label,needle in needles.items():
 b=bytes.fromhex(needle); at=0; hits=[]
 while True:
  i=mem.find(b,at)
  if i<0:break
  hits.append(f'0x{i:05X}');at=i+1
 counts_by[label]=hits
p=0x21fd*16+0x2552
r={
 'pass':154,
 'scope':'static original DOS 2.0 from all-nite3d.zip (EXEPACK expansion); no game execution',
 'original_exe_sha256':hashlib.sha256(raw).hexdigest(),
 'normalized_image_sha256':hashlib.sha256(mem).hexdigest(),
 'exact_byte_checks':{k:{'offset':f'0x{a:05X}','bytes':h,'verified':True} for k,(a,h) in checks.items()},
 'decoded_guard':{
  'mov_CX':'11EE:397A mov cx,word ptr ds:[2554h]',
  'conditional':'11EE:397E jcxz 11EE:3984',
  'far_jump':'11EE:3980 jmp far ptr ds:[2552h]',
  'fallback':'11EE:3984 mov ax,0FFFFh; mov word ptr ds:[2118h],0016h; jmp common 0x12497 (image-linear)'
 },
 'direct_caller':{'image_linear':'0x15533','address':'11EE:3653', 'gate':'cmp [bp+06],2; jne bypass', 'argument_pushes':3},
 'static_far_pointer':{'linear':f'0x{p:05X}','bytes':bytes(mem[p:p+4]).hex(),'relocation_intersects_any_byte':any(s<p+4 and s+2>p for s in relocations),'reloc_exact_word_start':[hex(s) for s in relocations if s in [p,p+2]]},
 'whole_image_raw_signature_occurrences':counts_by,
 'older_distribution_binary_identity':{'dos18_exe_sha256':hashlib.sha256(older18).hexdigest(),'dos19_exe_sha256':hashlib.sha256(older19).hexdigest(),'byte_identical':older18==older19},
 'limitations':['Byte pattern hits are not complete disassembly or writer census.', 'No runtime pointer target or last-writer trace.', 'Range-walker helper checks 4-byte entries and can invoke them; does not prove writes to callback slot.', 'Expanded image is unrelocated; memory initialization after loader remains unobserved.']
}
out=BASE/'N3D_PASS154_evidence.json';out.write_text(json.dumps(r,indent=2,ensure_ascii=False),encoding='utf8')
print(json.dumps({'verified_checks':len(checks),'normalized_sha256':r['normalized_image_sha256'],'signatures':counts_by,'pointer_relocation_intersects':r['static_far_pointer']['relocation_intersects_any_byte'],'older_same':older18==older19},indent=2))