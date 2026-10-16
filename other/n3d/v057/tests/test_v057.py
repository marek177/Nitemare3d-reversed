#!/usr/bin/env python3
"""Synthetic/no-original-bytes regression suite for v0.57 local contracts."""
from __future__ import annotations
import pathlib, sys, unittest
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parents[1]))
from model_v057 import (Tile, geometry_line, damage_scalar, CLASS_PATH,
    STATE_MAP_3_TO_21, guard_hit_local_branch, s16, u16, sar16)
from verify_v057 import (DAMAGE_CASE_REL, GEO_MUTABLE, GEOMETRY_SIZE,
    DAMAGE_SIZE, DAMAGE_MUTABLE, normalized_masked_equal)

class GeometryLocalTests(unittest.TestCase):
    def empty(self,*args): return Tile()
    def test_exact_endpoint_not_tested_for_walls(self):
        calls=[]
        def reader(x,y): calls.append((x,y)); return Tile(0x06 if (x,y)==(23,21) else 0,0)
        r=geometry_line(20,20,3,1,16,True,reader)
        self.assertTrue(r.reached)
        self.assertEqual(r.reason,'endpoint_before_collision')
        self.assertEqual(r.traversed,((21,20),(22,21),(23,21)))
        self.assertEqual(calls,[(21,20),(22,21)])
    def test_first_step_wall_block(self):
        r=geometry_line(20,20,3,1,16,True,lambda x,y:Tile(6 if (x,y)==(21,20) else 0,0))
        self.assertFalse(r.reached)
        self.assertEqual(r.reason,'wall_flags_02_and_04')
    def test_object_gate_enabled_vs_disabled(self):
        b=lambda x,y:Tile(0,0x02)
        self.assertEqual(geometry_line(20,20,3,1,16,True,b).reason,'object_flags_02_without_20')
        self.assertTrue(geometry_line(20,20,3,1,16,False,b).reached)
    def test_object_flag_20_overrides_02(self):
        self.assertTrue(geometry_line(20,20,3,1,16,True,lambda x,y:Tile(0,0x22)).reached)
    def test_object_without_bit02_passes(self):
        self.assertTrue(geometry_line(20,20,3,1,16,True,lambda x,y:Tile(0,0x20)).reached)
    def test_wall_flags_without_bit02_pass(self):
        self.assertTrue(geometry_line(20,20,3,1,16,True,lambda x,y:Tile(0x04,0)).reached)
        self.assertTrue(geometry_line(20,20,3,1,16,True,lambda x,y:Tile(0x08,0)).reached)
    def test_dynamic_wall_true(self):
        seen=[]
        r=geometry_line(20,20,3,1,16,True,lambda x,y:Tile(0x0A,0),
                        lambda x,y:seen.append((x,y)) or True)
        self.assertTrue(r.reached);self.assertEqual(r.wall_callbacks,2)
        self.assertEqual(seen,[(21,20),(22,21)])
    def test_dynamic_wall_false(self):
        r=geometry_line(20,20,3,1,16,True,lambda x,y:Tile(0x0A,0),lambda x,y:False)
        self.assertEqual(r.reason,'special_wall_callback_false')
        self.assertEqual(r.wall_callbacks,1)
    def test_wall_04_priority_over_08(self):
        seen=[]
        r=geometry_line(20,20,3,1,16,True,lambda x,y:Tile(0x0E,0),
                        lambda x,y:seen.append((x,y)) or True)
        self.assertEqual(r.reason,'wall_flags_02_and_04')
        self.assertEqual(seen,[])
    def test_wall_gate_runs_before_object_gate(self):
        r=geometry_line(20,20,3,1,16,True,lambda x,y:Tile(0x06,0x02))
        self.assertEqual(r.reason,'wall_flags_02_and_04')
    def test_zero_or_negative_step_limit(self):
        for n in [0,-1,-32768]:
            r=geometry_line(20,20,3,1,n,True,lambda x,y: self.fail('read not allowed'))
            self.assertEqual(r.reason,'limit_nonpositive')
            self.assertEqual(r.traversed,())
    def test_limit_exactly_distance(self):
        self.assertTrue(geometry_line(20,20,16,0,16,True,self.empty).reached)
        self.assertFalse(geometry_line(20,20,17,0,16,True,self.empty).reached)
        self.assertEqual(geometry_line(20,20,17,0,16,True,self.empty).reason,'step_limit_reached')
    def test_guard_8_vs_hit_16(self):
        self.assertFalse(geometry_line(20,20,9,0,8,False,self.empty).reached)
        self.assertTrue(geometry_line(20,20,9,0,16,False,self.empty).reached)
    def test_zero_delta_does_not_instant_accept(self):
        r=geometry_line(20,20,0,0,16,False,self.empty)
        self.assertFalse(r.reached)
        self.assertEqual(r.traversed[0],(19,19))
    def test_all_short_cardinal_diagonals(self):
        for dx in range(-10,11):
            for dy in range(-10,11):
                if not (dx or dy): continue
                r=geometry_line(20,20,dx,dy,16,True,self.empty)
                self.assertTrue(r.reached,(dx,dy,r.reason,r.traversed))
                self.assertEqual(len(r.traversed),max(abs(dx),abs(dy)))
                self.assertEqual(r.traversed[-1],(20+dx,20+dy))
    def test_no_target_object_test_when_adjacent(self):
        calls=[]
        def fail_if_target(x,y):
            calls.append((x,y));return Tile(6,2)
        r=geometry_line(20,20,1,0,16,True,fail_if_target)
        self.assertTrue(r.reached)
        self.assertEqual(calls,[])
    def test_wrap_arithmetic_example(self):
        self.assertEqual(u16(65535+1),0)
        self.assertEqual(s16(65535),-1)
        self.assertEqual(s16(sar16(65535,8)),-1)

class DamageMatrixTests(unittest.TestCase):
    def test_case_count(self):
        self.assertEqual(len(CLASS_PATH),20)
        self.assertEqual(set(CLASS_PATH),set(range(0x0C,0x20)))
        self.assertEqual(len(DAMAGE_CASE_REL),20)
    def test_draw_even_if_damage_is_zero(self):
        for cls in [0x15,0x19,0x16]:
            r=damage_scalar(cls,0,1,100,100,0,special_626a=0)
            self.assertEqual(r.rng_draws_direct,1)
            self.assertEqual(r.consumed_damage_byte,0)
    def test_class15_extra_callback(self):
        for mode in range(4):
            r=damage_scalar(0x15,mode,1,110,100,24)
            self.assertTrue(r.special_callback)
            self.assertEqual(r.consumed_damage_byte,0)
    def test_class16_global_gate(self):
        self.assertEqual(damage_scalar(0x16,0,1,110,100,24,3).consumed_damage_byte,3)
        self.assertEqual(damage_scalar(0x16,0,1,110,100,24,2).consumed_damage_byte,0)
    def test_three_difficulties(self):
        # default class: scalar 8*(3)+0=24; easy doubles, medium unchanged, hard halves
        self.assertEqual([damage_scalar(0x08,0,d,103,100,0).consumed_damage_byte for d in range(3)],
                         [48,24,12])
    def test_mode_1_vs_2_special_case_0e(self):
        self.assertGreater(damage_scalar(0x0e,2,1,110,100,0).consumed_damage_byte,
                           damage_scalar(0x0e,1,1,110,100,0).consumed_damage_byte)
    def test_mode1_harder_class_0f(self):
        self.assertLess(damage_scalar(0x0f,1,1,110,100,0).consumed_damage_byte,
                        damage_scalar(0x0f,2,1,110,100,0).consumed_damage_byte)
    def test_negative_has_no_lower_clamp(self):
        r=damage_scalar(0x0c,0,1,99,100,0)
        self.assertEqual(r.value_after_class,-1)
        self.assertEqual(r.returned_ax,65535)
        self.assertEqual(r.consumed_damage_byte,255)
    def test_upper_clamp(self):
        self.assertEqual(damage_scalar(0x08,0,0,300,100,24).returned_ax,255)
    def test_all_256_class_and_modes_model_properties(self):
        for cls in range(256):
            for mode in range(4):
                for difficulty in range(3):
                    for random_byte in [0,1,24,25,32767]:
                        r=damage_scalar(cls,mode,difficulty,110,100,random_byte,special_626a=3)
                        self.assertEqual(r.rng_draws_direct,1)
                        self.assertEqual(r.special_callback,cls==0x15)
                        self.assertEqual(r.consumed_damage_byte,r.returned_ax&255)
                        self.assertTrue(0<=r.returned_ax<=65535)
    def test_rng_domain(self):
        with self.assertRaises(ValueError):damage_scalar(0x0c,1,1,0,0,-1)
        with self.assertRaises(ValueError):damage_scalar(0x0c,1,1,0,0,32768)

class HitWrapperTests(unittest.TestCase):
    def test_state_table_19(self):
        self.assertEqual(len(STATE_MAP_3_TO_21),19)
        for s in [3,4,11]:self.assertEqual(STATE_MAP_3_TO_21[s-3],'return')
        for s in [7,8,21]:self.assertEqual(STATE_MAP_3_TO_21[s-3],'special_animation')
    def test_hp0_damage0_is_terminal_comparison(self):
        self.assertTrue(guard_hit_local_branch(0,0,1,3)['terminal'])
    def test_hp_positive_damage0_no_updates(self):
        r=guard_hit_local_branch(10,0,1,3)
        self.assertFalse(r['terminal']);self.assertFalse(r['pain_timer_written'])
        self.assertEqual(r['hp_after'],10)
    def test_damage_equal_hp_is_terminal(self):
        self.assertTrue(guard_hit_local_branch(10,10,1,7)['terminal'])
        self.assertFalse(guard_hit_local_branch(10,9,1,7)['terminal'])
    def test_strategy2(self):
        self.assertEqual(guard_hit_local_branch(10,1,2,7)['transition'],'strategy_2_effect')
    def test_strategy4_returns_after_subtract(self):
        r=guard_hit_local_branch(10,1,4,7)
        self.assertEqual(r['hp_after'],9);self.assertTrue(r['pain_timer_written'])
        self.assertEqual(r['transition'],'return_strategy_4')
        self.assertTrue(r['pre_state7_callback'])
    def test_special_state7_handler_nonlethal_only(self):
        self.assertTrue(guard_hit_local_branch(10,1,1,7)['pre_state7_callback'])
        self.assertFalse(guard_hit_local_branch(10,10,1,7)['pre_state7_callback'])

class VerificationContractTests(unittest.TestCase):
    def test_geometry_operand_only_mask(self):
        a=bytes([0]*GEOMETRY_SIZE);b=bytearray(a)
        for i in GEO_MUTABLE:b[i]=1
        self.assertTrue(normalized_masked_equal(a,bytes(b),GEO_MUTABLE))
        b[5]=1
        self.assertFalse(normalized_masked_equal(a,bytes(b),GEO_MUTABLE))
    def test_damage_operand_only_mask(self):
        a=bytes([0]*DAMAGE_SIZE);b=bytearray(a)
        for i in DAMAGE_MUTABLE:b[i]=5
        self.assertTrue(normalized_masked_equal(a,bytes(b),DAMAGE_MUTABLE))
        b[6]=7
        self.assertFalse(normalized_masked_equal(a,bytes(b),DAMAGE_MUTABLE))


class MovingWallNestedTests(unittest.TestCase):
    def test_states_0_and_4_only(self):
        from model_v057 import moving_wall_gate_dos20,MovingWallRecord
        for state in range(16):
            record=[MovingWallRecord(0x1234,0x5678,state)]
            self.assertEqual(moving_wall_gate_dos20(record,0x1234,0x5678), state in (0,4))
    def test_far_pointer_requires_both_words(self):
        from model_v057 import moving_wall_gate_dos20,MovingWallRecord,MissingMovingWallRecord
        records=[MovingWallRecord(0x1234,0x5678,0)]
        with self.assertRaises(MissingMovingWallRecord):
            moving_wall_gate_dos20(records,0x1235,0x5678)
        with self.assertRaises(MissingMovingWallRecord):
            moving_wall_gate_dos20(records,0x1234,0x5679)
    def test_first_match_wins(self):
        from model_v057 import moving_wall_gate_dos20,MovingWallRecord
        records=[MovingWallRecord(0x2222,0x7777,1),MovingWallRecord(0x2222,0x7777,4)]
        self.assertFalse(moving_wall_gate_dos20(records,0x2222,0x7777))
    def test_miss_not_silent_pass(self):
        from model_v057 import moving_wall_gate_dos20,MissingMovingWallRecord
        with self.assertRaises(MissingMovingWallRecord):moving_wall_gate_dos20([],0,0)

if __name__=='__main__':unittest.main()
