"""Synthetic, data-free v0.58 tests (not original gameplay runtime tests)."""
import importlib.util
import json
import pathlib
import unittest

ROOT=pathlib.Path(__file__).resolve().parents[1]
import sys
sys.path.insert(0,str(ROOT))
sys.path.insert(0,str(ROOT/'tools'))
from model_v058 import (SCORE_08_20, DEATH_08_1F, STATE7_08_1F, LCG,
                        apply_score32, class_score, select_sound, sound_rule,
                        variant_select, after_nonfatal_hit, lethal_if_hp_le_damage, sfx_backend_initial_gate)
from verify_v058 import (EXPECT_SCORE,EXPECT_DEATH_SOUND,EXPECT_STATE7_SOUND,
                         decode_audio_case, signed16, win_seg3, require, SKIP)

class Tests(unittest.TestCase):
    def test_score_all_256_classes(self):
        for k in range(256):
            expected=EXPECT_SCORE[k-8] if 8<=k<=32 else 0
            self.assertEqual(class_score(k),expected)

    def test_all_death_sound_routes(self):
        for k in range(256):
            expected=EXPECT_DEATH_SOUND[k-8] if 8<=k<=31 else 0
            self.assertEqual(sound_rule(DEATH_08_1F,k),expected)

    def test_all_state7_sound_routes(self):
        for k in range(256):
            expected=EXPECT_STATE7_SOUND[k-8] if 8<=k<=31 else 0
            self.assertEqual(sound_rule(STATE7_08_1F,k),expected)

    def test_scores_negative_and_wrap(self):
        self.assertEqual(class_score(0x15),-1000)
        self.assertEqual(apply_score32(500,0x15),0xFFFFFE0C)
        self.assertEqual(apply_score32(1000,0x15),0)
        self.assertEqual(apply_score32(0xFFFFFFFE,0x20),48)

    def test_class20_only_score(self):
        self.assertEqual(class_score(0x20),50)
        self.assertEqual(sound_rule(DEATH_08_1F,0x20),0)
        self.assertEqual(sound_rule(STATE7_08_1F,0x20),0)

    def test_positive_hp_class15_zero_damage_not_lethal(self):
        for hp in range(1,256):
            self.assertFalse(lethal_if_hp_le_damage(hp,0))
        self.assertTrue(lethal_if_hp_le_damage(0,0))

    def test_byte_domain_checked(self):
        with self.assertRaises(ValueError):lethal_if_hp_le_damage(256,0)
        with self.assertRaises(ValueError):lethal_if_hp_le_damage(1,-1)

    def test_dos_audio_zero_selector_requires_runtime_slot(self):
        self.assertFalse(sfx_backend_initial_gate(0,1))
        self.assertFalse(sfx_backend_initial_gate(1,0))
        self.assertTrue(sfx_backend_initial_gate(1,123))

    def test_lcg_seed1(self):
        state=LCG(1)
        self.assertEqual([state.rand15() for _ in range(6)],[41,18467,6334,26500,19169,15724]);self.assertEqual(state.draws,6)

    def test_sound_rng_modulo(self):
        self.assertEqual(select_sound('rng%3+11',lambda:41),(13,1))
        self.assertEqual(select_sound('rng%2+54',lambda:41),(55,1))
        self.assertEqual(select_sound(70,lambda: (_ for _ in ()).throw(ValueError('should not call rng'))),(70,0))

    def test_variant_fast_branch_no_rng(self):
        self.assertEqual(variant_select(guard_plus12=0,high_flag=1,seven_low_bytes=(0,0,0,0,0,0,0),next_rng=lambda:1),(7,0))

    def test_variant_rejection_draw_count(self):
        draw=iter([0,1,6,2]);slots=(0,0,4,0,0,0,0)
        self.assertEqual(variant_select(guard_plus12=1,high_flag=1,seven_low_bytes=slots,next_rng=lambda:next(draw)),(2,4))

    def test_nonfatal_timer_forces_rng_path(self):
        slots=(1,)*7
        n=iter([13]);self.assertEqual(after_nonfatal_hit(strategy=2,seven_low_bytes=slots,high_flag=1,next_rng=lambda:next(n)),(6,1))
        n=iter([6]);self.assertEqual(after_nonfatal_hit(strategy=3,seven_low_bytes=slots,high_flag=1,next_rng=lambda:next(n)),(6,1))

    def test_strategy4_bypasses_selection_not_all_rng(self):
        self.assertEqual(after_nonfatal_hit(strategy=4,seven_low_bytes=(1,)*7,high_flag=1,next_rng=lambda: (_ for _ in ()).throw(Exception('not reached'))),(None,0))

    def test_missing_slots_instrumented_failure(self):
        with self.assertRaises(ValueError):variant_select(guard_plus12=8,high_flag=0,seven_low_bytes=(0,)*7,next_rng=lambda:0)

    def test_bounded_model_exhaustion(self):
        with self.assertRaises(ValueError):variant_select(guard_plus12=8,high_flag=0,seven_low_bytes=(0,1,0,0,0,0,0),next_rng=lambda:0,max_model_draws=3)

    def test_signed16(self):
        self.assertEqual(signed16(0xFC18),-1000)
        self.assertEqual(signed16(0x7fff),32767)
        self.assertEqual(signed16(0xffff),-1)

    def test_decode_audio_synthetic(self):
        b=bytearray(80);b[0:3]=b'\xbe\x46\x00'
        self.assertEqual(decode_audio_case(bytes(b),0,60),(70,'fixed_selector'))
        self.assertEqual(decode_audio_case(bytes(b),60,60),(0,'default_zero_selector'))
        b[0:16]=bytes.fromhex('9a 01 02 03 04 b9 03 00 99 f7 f9 8b f2 83 c6 0b')
        self.assertEqual(decode_audio_case(bytes(b),0,60),('rng%3+11','draw_rng_once_then_mod'))

    def test_reject_corrupt_audio_opcode(self):
        with self.assertRaises(AssertionError):decode_audio_case(bytes.fromhex('90')+bytes(64),0,60)

    def test_byte_witness_rejects_patch(self):
        self.assertEqual(require(bytes.fromhex('55 8b ec'),0,'55 8b ec','fixture')['bytes'],3)
        with self.assertRaises(AssertionError):require(bytes.fromhex('55 8b ed'),0,'55 8b ec','fixture')

    def test_operand_masks_do_not_hide_opcode_bodies(self):
        self.assertEqual(len(SKIP['score']),52)
        self.assertNotIn(0,SKIP['score'])
        self.assertNotIn(0,SKIP['fatal_variant'])
        self.assertIn(0x63,SKIP['nonfatal_variant'])

    def test_evidence_snapshot_route_counts(self):
        p=ROOT/'evidence_v058.json'
        if not p.exists():self.skipTest('read-only original-image verifier has not been run')
        j=json.loads(p.read_text())
        self.assertEqual(set(j['profiles']),{'dos20','win110','winalt'})
        for dat in j['profiles'].values():
            self.assertEqual(len(dat['tables']['score']['classes']),25)
            self.assertEqual(len(dat['tables']['death_sound']['classes']),24)
            self.assertEqual(len(dat['tables']['state7_sound']['classes']),24)
            self.assertEqual(dat['tables']['fatal_variant']['high_flag_offset'],'59')
            self.assertEqual(dat['tables']['nonfatal_variant']['high_flag_offset'],'49')

if __name__=='__main__':unittest.main()
