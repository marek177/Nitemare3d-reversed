"""Synthetic fixtures for N3D RE trace tools; no original game data."""

import importlib.util
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / 'tools' / 'n3d_trace_audit.py'
spec = importlib.util.spec_from_file_location('n3d_trace_audit', SCRIPT)
probe = importlib.util.module_from_spec(spec)
spec.loader.exec_module(probe)


class FastEvidenceTests(unittest.TestCase):
    def test_modulo_gate_and_nested(self):
        rows = [{'invocation': 3, 'caller': 0xC150, 'target': target}
                for target in probe.FAST_DIRECT]
        rows.insert(3, {'invocation': 3, 'caller': 0x5F26, 'target': 0x9999})
        rows.insert(7, {'invocation': 4, 'caller': 0xC150, 'target': 0x1234})
        self.assertTrue(probe.audit_fast(rows, 3, 8)['ok'])
        self.assertEqual(probe.audit_fast(rows, 3, 7)['verdict'], 'divergent')
        without_last = rows[:-1]
        self.assertTrue(probe.audit_fast(without_last, 3, 7)['ok'])
        self.assertEqual(probe.audit_fast(without_last, 3, 8)['verdict'], 'incomplete')
        self.assertEqual(probe.audit_fast(rows, 100, 8)['verdict'], 'missing')

    def test_first_divergence(self):
        rows = [{'invocation': 5, 'caller': 0xC150, 'target': x}
                for x in probe.FAST_DIRECT]
        rows[1]['target'] = 0xDEAD
        error = probe.audit_fast(rows, 5, 0)
        self.assertEqual(error['index'], 1)
        self.assertEqual(error['expected'], 0x0A40)
        self.assertEqual(error['observed'], 0xDEAD)


class RngEvidenceTests(unittest.TestCase):
    def make_rows(self):
        state = 1
        rows = []
        for caller in (0x2478, 0x525E, 0x58A7):
            new_state = (state * 214013 + 2531011) & 0xFFFFFFFF
            rows.append({'caller': caller, 'before': state, 'after': new_state,
                         'result': (new_state >> 16) & 0x7FFF})
            state = new_state
        return rows

    def test_all_22_direct_callers_include_damage_site_pair(self):
        self.assertEqual(len(probe.RNG_DIRECT_CALLERS), 22)
        self.assertIn(0x8860, probe.RNG_DIRECT_CALLERS)
        self.assertIn(0x886C, probe.RNG_DIRECT_CALLERS)
        state = 1
        rows = []
        for caller in (0x8860, 0x886C, 0x887C):
            after = (state * 214013 + 2531011) & 0xFFFFFFFF
            rows.append(dict(caller=caller, before=state, after=after,
                             result=(after >> 16) & 0x7FFF))
            state = after
        self.assertTrue(probe.audit_rng(rows, seed=1, strict_callers=True)['ok'])
        rows[1]['caller'] = 0x7777
        self.assertEqual(probe.audit_rng(rows, seed=1, strict_callers=True)['error'],
                         'caller not in direct-call census')

    def test_seed_and_continuity(self):
        rows = self.make_rows()
        self.assertTrue(probe.audit_rng(rows, seed=1)['ok'])
        self.assertEqual(probe.audit_rng(rows, seed=2)['error'], 'seed mismatch')
        rows[1]['before'] += 1
        self.assertEqual(probe.audit_rng(rows, seed=1)['error'], 'RNG state discontinuity')

    def test_transition_and_result(self):
        rows = self.make_rows()
        rows[0]['after'] += 1
        self.assertEqual(probe.audit_rng(rows)['error'], 'LCG transition mismatch')
        rows = self.make_rows()
        rows[0]['result'] += 1
        self.assertEqual(probe.audit_rng(rows)['error'], 'RNG result mismatch')

    def test_unknown_caller(self):
        rows = self.make_rows()
        rows[0]['caller'] = 0xABCD
        self.assertTrue(probe.audit_rng(rows)['ok'])
        self.assertEqual(len(probe.audit_rng(rows)['unknown_callers']), 1)
        self.assertEqual(probe.audit_rng(rows, strict_callers=True)['index'], 0)

    def test_csv_reader_and_errors(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'trace.csv'
            path.write_text('caller,before,after,result\n0x2478,1,2745024,41\n', encoding='utf-8')
            rows = probe.read_csv(path, ('caller', 'before', 'after', 'result'))
            self.assertTrue(probe.audit_rng(rows, seed=1)['ok'])
            path.write_text('caller,before,result\n0x2478,1,41\n', encoding='utf-8')
            with self.assertRaises(ValueError):
                probe.read_csv(path, ('caller', 'before', 'after', 'result'))


if __name__ == '__main__':
    unittest.main()
