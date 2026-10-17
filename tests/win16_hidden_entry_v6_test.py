#!/usr/bin/env python3
"""Artifact and binary regressions. Run with unittest discovery or directly.
Set N3D_WIN16_BINARIES to check all emitted instructions against original EXEs.
"""
import csv, hashlib, importlib.util, json, os, unittest
from collections import Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'analysis/win16_hidden_v6'
spec=importlib.util.spec_from_file_location('hidden_v6',ROOT/'tools/win16_hidden_entry_v6.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)

def csvrows(name):return m.readcsv(OUT/name)

class HiddenEntryRegression(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.d=[json.loads(x) for x in (OUT/'machine_dossiers.jsonl').read_text().splitlines()]
        cls.g=csvrows('callgraph.csv');cls.r=csvrows('cross_version_relations.csv')
        cls.s=json.loads((OUT/'summary.json').read_text())
    def test_high_only_and_exact_counts(self):
        self.assertEqual(Counter(d['version'] for d in self.d),{'1.3':9,'1.6':18,'1.8':19,'1.10':24})
        self.assertEqual(len(self.d),70)
        self.assertEqual(self.s['medium_or_medium_high_promoted'],0)
        self.assertTrue(all(d['entry_confidence']=='High' and d['incoming_evidence'] for d in self.d))
        self.assertTrue(all(r['status']=='promoted' for r in csvrows('promotion_audit.csv')))
    def test_closed_boundaries_and_runtime_address_discipline(self):
        for d in self.d:
            a=m.number(d['start_offset']);end=m.number(d['end_offset_exclusive'])
            ins={m.number(x['offset']):{'offset':m.number(x['offset']),'bytes':bytes.fromhex(x['bytes']),'mn':x['mnemonic'],'op':x['operand']} for x in d['assembly']}
            self.assertEqual(set(ins),m.reachable(ins,a))
            self.assertEqual(end,max(p+len(x['bytes']) for p,x in ins.items()))
            self.assertTrue(d['return_sites']);self.assertIsNone(d['runtime_va'])
            self.assertEqual(d['semantic_status'],'Unknown')
            self.assertEqual(sum(len(x['bytes']) for x in ins.values()),d['reachable_bytes'])
            ordered=sorted(ins)
            for p,q in zip(ordered,ordered[1:]):self.assertLessEqual(p+len(ins[p]['bytes']),q)
    def test_call_site_uniqueness_and_counts(self):
        keys=[(r['version'],r['source_segment'],r['call_site_offset']) for r in self.g]
        self.assertEqual(len(keys),len(set(keys)))
        expected={'1.0':2794,'1.3':2788,'1.6':2800,'1.8':2803,'1.10':2791}
        self.assertEqual(Counter(r['version'] for r in self.g),expected)
        for s in self.s['callgraph']:
            g=[r for r in self.g if r['version']==s['version']]
            self.assertEqual(s['direct_total'],len(g))
            self.assertEqual(s['direct_total'],s['near']+s['far_internal']+s['far_import'])
            self.assertEqual(s['indirect'],212)
    def test_exact_targets_and_parent_not_substituted(self):
        for d in self.d:
            for r in d['callers']:
                self.assertEqual(r['callee'],d['function'])
                self.assertEqual(r['target_offset'],d['start_offset'])
                self.assertEqual(r['target_selector'],d['selector'])
                self.assertEqual(r['target_exact_start'],True)
            self.assertTrue(d['callers'])
            for r in d['callees']:
                self.assertEqual(r['caller'],d['function'])
                if r['call_kind'].startswith('far'):
                    self.assertTrue(r['record_bytes']);self.assertTrue(r['source_fixup_offset'])
    def test_reference_mapping_does_not_promote_candidates(self):
        self.assertEqual(len(self.r),350)
        by={(d['version'],d['entry']) for d in self.d}
        for r in self.r:
            self.assertEqual(r['semantic_equivalence'],'not claimed')
            if r['to_entry']:
                self.assertEqual(r['to_has_promoted_dossier']=='True',(r['to_version'],r['to_entry']) in by)
                self.assertTrue(r['to_body_sha256']);self.assertTrue(r['to_file_offset'])
        for d in self.d:
            r=next(r for r in self.r if r['from_version']==d['version'] and r['from_entry']==d['entry'] and r['to_version']==d['version'])
            self.assertEqual(r['to_entry'],d['entry'])
    def test_operand_entry_regression_and_stateful_not_thunk(self):
        d=next(d for d in self.d if d['version']=='1.10' and d['entry']=='1010:D7D0')
        self.assertTrue(any('FUN_1010_d7cc' in s for s in d['boundary_notes']))
        self.assertFalse(any(r['caller']=='FUN_1010_d7cc' and m.number(r['call_site_offset'])>=0xd7d0 for r in self.g if r['version']=='1.10'))
        for d in self.d:
            if d['entry'] in {'1010:D78C','1010:D56A','1010:D6DE'}:
                self.assertNotEqual(d['classification'],'call-wrapper')
    @unittest.skipUnless(os.getenv('N3D_WIN16_BINARIES'),'Original EXEs not supplied')
    def test_original_binary_bytes_fixups_and_mapping(self):
        binaries={v:m.Binary(Path(os.environ['N3D_WIN16_BINARIES'])/name,v) for v,name in m.VERSIONS.items()}
        for d in self.d:
            b=binaries[d['version']];seg=d['segment_ordinal'];raw=b.segments[seg]['bytes'];a=m.number(d['start_offset']);end=m.number(d['end_offset_exclusive'])
            self.assertEqual(hashlib.sha256(raw[a:end]).hexdigest(),d['body_sha256'])
            for x in d['assembly']:
                p=m.number(x['offset']);bs=bytes.fromhex(x['bytes']);self.assertEqual(raw[p:p+len(bs)],bs)
            for f in d['incoming_evidence']:
                actual=b.fixups[(f['source_segment'],m.number(f['opcode_site_offset']))]
                self.assertEqual(actual['target_segment'],seg);self.assertEqual(actual['target_offset'],d['start_offset'])
                for k in ('record_index','record_file_offset','record_bytes','chain_index','source_fixup_offset'):self.assertEqual(actual[k],f[k])
        for r in self.g:
            b=binaries[r['version']];seg=int(r['source_segment']);p=m.number(r['call_site_offset']);bs=bytes.fromhex(r['instruction_bytes'])
            self.assertEqual(b.segments[seg]['bytes'][p:p+len(bs)],bs)
            if r['call_kind'].startswith('far'):
                f=b.fixups[(seg,p)]
                for k in ('record_file_offset','record_bytes','source_fixup_offset','chain_index'):self.assertEqual(str(f[k]),r[k])
        for r in self.r:
            if not r['to_entry']:continue
            b=binaries[r['to_version']];sel,off=r['to_entry'].split(':');seg=next(k for k,v in m.SELECTORS.items() if v==sel);a=int(off,16);end=m.number(r['to_end_offset_exclusive'])
            self.assertEqual(hashlib.sha256(b.segments[seg]['bytes'][a:end]).hexdigest(),r['to_body_sha256'])

if __name__=='__main__':unittest.main()
