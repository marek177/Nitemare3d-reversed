"""Synthetic robustness checks; fixtures are not original CPU evidence."""
import copy
import importlib.util
from pathlib import Path
import unittest

TOOL = Path(__file__).resolve().parents[1] / 'tools/n3d_d02e_audit.py'
spec = importlib.util.spec_from_file_location('d02e', TOOL)
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


def fixture():
    rows, state = [], 1
    for ordinal in range(1, 230):
        after = (214013 * state + 2531011) & 0xffffffff
        site = '0xA047'
        if ordinal in (221, 226): site = '0x85AD'
        elif ordinal > 220: site = '0x9FE3'
        rows.append(dict(ordinal=ordinal, callsite=site, state_before=f'0x{state:08X}',
                         state_after_lcg=f'0x{after:08X}', return_lcg=(after >> 16) & 0x7fff,
                         original_instruction_complete=True,
                         scheduler_entries_before=1000 if ordinal <= 210 else 1071,
                         last_demo_record_ordinal=263 if ordinal <= 218 else 273))
        state = after
    def run(r):
        return dict(rng_rows=copy.deepcopy(r), rng_entries=len(r),
                    complete_original_rng_outcomes=len(r), scheduler_max_depth=1,
                    scheduler_unmatched_returns=0, original_demo_unique_applied_records=275)
    old, new = run(rows), run(rows[:220])
    for row in new['rng_rows'][210:]: row['scheduler_entries_before'] += 8
    for row in new['rng_rows'][218:]: row['last_demo_record_ordinal'] += 1
    evidence = dict(source_original_exe_sha256=m.EXPECTED_ORIGINAL_PACKED_SHA,
                    source_demo_sha256=m.EXPECTED_DEMO_SHA,
                    runs=[{} for _ in range(5)] + [new, old])
    image = bytearray(0x10000)
    for site, seg, off in [(0x6A2F,0x04C7,0x1304),(0x8125,0x04C7,0x1304),
                           (0x5F88,0x083D,0x01C0),(0x5FAD,0x083D,0x1BE4)]:
        image[site:site+5] = b'\x9a'+off.to_bytes(2,'little')+seg.to_bytes(2,'little')
    return image, evidence


class Robustness(unittest.TestCase):
    def test_synthetic_supported_shape(self):
        image, evidence = fixture()
        report = m.audit(image, evidence)
        self.assertEqual(report['common_exact_rng_prefix'], 220)
        self.assertEqual([g['total_rng_draws'] for g in report['remaining_reference_only_rng_groups']], [5,4])
        self.assertFalse(report['raw_original_runtime_recaptured_in_this_audit'])
        self.assertEqual(report['closure']['D02E_exact_clock_gate'], 'OPEN')

    def reject(self, change):
        image, evidence = fixture()
        change(image, evidence)
        with self.assertRaises((ValueError, AssertionError)):
            m.audit(image, evidence)

    def test_identical_corruption_in_both_runs_is_rejected(self):
        def change(_, e):
            for run in e['runs'][5:]: run['rng_rows'][4]['state_after_lcg']='0xDEADBEEF'
        self.reject(change)

    def test_invalid_result(self):
        self.reject(lambda _,e: e['runs'][5]['rng_rows'][0].update(return_lcg=0))

    def test_duplicate_ordinal(self):
        self.reject(lambda _,e: e['runs'][5]['rng_rows'][3].update(ordinal=3))

    def test_incomplete_instruction(self):
        self.reject(lambda _,e: e['runs'][6]['rng_rows'][0].update(original_instruction_complete=False))

    def test_wrong_asset(self):
        self.reject(lambda _,e: e.update(source_demo_sha256='wrong'))

    def test_missing_outcome(self):
        self.reject(lambda _,e: e['runs'][5].update(complete_original_rng_outcomes=219))

    def test_extra_group_crosses_context(self):
        self.reject(lambda _,e: e['runs'][6]['rng_rows'][221].update(scheduler_entries_before=0))

    def test_changed_literal_call(self):
        def change(image, _): image[0x5F88]=0
        self.reject(change)

    def test_no_context_difference_fails_cleanly(self):
        def change(_,e):
            for old,new in zip(e['runs'][6]['rng_rows'],e['runs'][5]['rng_rows']):
                new['scheduler_entries_before']=old['scheduler_entries_before']
                new['last_demo_record_ordinal']=old['last_demo_record_ordinal']
        self.reject(change)

    def test_far_call_at_last_complete_position(self):
        self.assertEqual(m.far_call_targets(bytes.fromhex('009a34120010'),0x11234), [1])

if __name__ == '__main__': unittest.main()
