#!/usr/bin/env python3
"""Ordered gameplay-state CSV diff; equal snapshots never prove original execution."""
import argparse
import csv
import hashlib
import json
import sys
from pathlib import Path

FIELDS = ('sample','tick','x','y','direction','input_mask','hp','ammo','weapon','object_count','guard_count','projectile_count','render_count')
NONNEG = {'sample','tick','hp','ammo','weapon','object_count','guard_count','projectile_count','render_count','input_mask'}

class TraceError(ValueError):
    pass

def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def read(path):
    with Path(path).open(encoding='utf-8-sig',newline='') as f:
        reader=csv.DictReader(f,strict=True)
        if reader.fieldnames is None or len(set(reader.fieldnames))!=len(reader.fieldnames):
            raise TraceError('missing or duplicated header')
        if tuple(reader.fieldnames)!=FIELDS:
            raise TraceError('wrong CSV field order')
        result=[]
        for lineno,r in enumerate(reader,2):
            if None in r:
                raise TraceError(f'line {lineno}: extra columns')
            row={}
            for field in FIELDS:
                token=r[field]
                if token is None or not token.strip():
                    raise TraceError(f'line {lineno}: empty {field}')
                token=token.strip()
                try:
                    if field=='input_mask' and token.lower().startswith('0x'):
                        value=int(token,16)
                    elif token.isascii() and token.lstrip('-').isdigit():
                        value=int(token,10)
                    else:
                        raise ValueError()
                except ValueError:
                    raise TraceError(f'line {lineno}: invalid {field}') from None
                if field in NONNEG and value<0:
                    raise TraceError(f'line {lineno}: negative {field}')
                if field=='input_mask' and value>65535:
                    raise TraceError(f'line {lineno}: mask exceeds uint16')
                if field=='direction' and not 0<=value<360:
                    raise TraceError(f'line {lineno}: direction outside [0,359]')
                row[field]=value
            if row['sample']!=len(result):
                raise TraceError(f'line {lineno}: noncontiguous sample sequence')
            if result and any(row[f]<result[-1][f] for f in ('tick','render_count')):
                raise TraceError(f'line {lineno}: tick/render_count went backwards')
            result.append(row)
    if not result:
        raise TraceError('empty trace')
    return result

def envelope(meta,csv_path,rows,kind):
    if meta is None:
        return None
    obj=json.loads(Path(meta).read_text(encoding='utf-8'))
    required=('schema','kind','build','capture_id','begin','end','closed','row_count','csv_sha256')
    if not isinstance(obj,dict) or any(k not in obj for k in required):
        raise TraceError('incomplete manifest')
    if obj['schema']!='n3d.gameplay-state.v1' or obj['kind']!=kind:
        raise TraceError('manifest schema or kind mismatch')
    if any(not isinstance(obj[k],str) or not obj[k].strip() for k in ('build','capture_id','begin','end')):
        raise TraceError('empty manifest identity')
    if obj['closed'] is not True or type(obj['row_count']) is not int:
        raise TraceError('capture must be declared closed with integer row_count')
    if obj['row_count']!=len(rows) or obj['csv_sha256']!=sha(csv_path):
        raise TraceError('row_count or SHA256 mismatch')
    return obj

def compare(ref,cand):
    for i in range(max(len(ref),len(cand))):
        if i>=len(ref) or i>=len(cand):
            return dict(equal=False,sample=i,classification='capture_length')
        delta={f:dict(reference=ref[i][f],candidate=cand[i][f])
               for f in FIELDS[1:] if ref[i][f]!=cand[i][f]}
        if delta:
            return dict(equal=False,sample=i,classification='tick_alignment' if 'tick' in delta else 'state_mismatch',fields=delta)
    return dict(equal=True,samples=len(ref))

def run(ref_csv,cand_csv,ref_manifest=None,cand_manifest=None):
    ref,cand=read(ref_csv),read(cand_csv)
    rm=envelope(ref_manifest,ref_csv,ref,'original')
    cm=envelope(cand_manifest,cand_csv,cand,'remake')
    boundaries=bool(rm and cm and all(rm[k]==cm[k] for k in ('capture_id','begin','end')))
    result=compare(ref,cand)
    verdict=('matched_attested_captures' if result['equal'] and boundaries
             else 'matched_unattested' if result['equal'] else 'first_divergence')
    return dict(schema='n3d.gameplay-diff.v1',comparison=result,verdict=verdict,
                reference_samples=len(ref),candidate_samples=len(cand),
                reference_sha256=sha(ref_csv),candidate_sha256=sha(cand_csv),
                boundaries_verified=boundaries,reference_manifest_verified=bool(rm),
                candidate_manifest_verified=bool(cm),
                original_runtime_verified=False,parity_proven=False)

def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('original_csv',type=Path)
    p.add_argument('remake_csv',type=Path)
    p.add_argument('--original-manifest',type=Path)
    p.add_argument('--remake-manifest',type=Path)
    p.add_argument('--output',type=Path)
    a=p.parse_args(argv)
    try:
        report=run(a.original_csv,a.remake_csv,a.original_manifest,a.remake_manifest)
    except (OSError,ValueError,csv.Error) as exc:
        print(f'gameplay-diff: {exc}',file=sys.stderr)
        return 2
    output=json.dumps(report,indent=2,sort_keys=True)+'\n'
    if a.output:
        a.output.write_text(output,encoding='utf-8')
    else:
        print(output,end='')
    return 0 if report['comparison']['equal'] and report['boundaries_verified'] else 1

if __name__=='__main__':
    sys.exit(main())
