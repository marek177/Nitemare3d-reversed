import importlib.util
import pathlib
import unittest

TOOL = pathlib.Path(__file__).resolve().parents[1] / "tools" / "n3d_v040_projectile_reentry.py"
spec = importlib.util.spec_from_file_location("v040", TOOL)
v040 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(v040)


class V040ProjectileReentryTest(unittest.TestCase):
    def test_state1_no_collision_stays_flying(self):
        r = v040.visit_flying_slot(False)
        self.assertEqual(r["state_after_visit"], v040.FLYING)
        self.assertFalse(r["falls_through_to_impact_expiry"])
        self.assertFalse(r["allocator_can_reuse"])

    def test_state1_collision_becomes_impact_not_free(self):
        r = v040.visit_flying_slot(True)
        self.assertEqual(r["state_after_visit"], v040.IMPACT)
        self.assertFalse(r["falls_through_to_impact_expiry"])
        self.assertFalse(r["allocator_can_reuse"])

    def test_20th_then_21st_counter(self):
        a = v040.e2m10_counter_step(19)
        b = v040.e2m10_counter_step(20)
        self.assertEqual(a, {"after": 20, "enters_nested_wait": True})
        self.assertEqual(b, {"after": 21, "enters_nested_wait": False})

    def test_one_level_direct_aba_negative(self):
        for collision in (False, True):
            r = v040.one_level_self_reentry(collision)
            self.assertFalse(r["same_nested_invocation_can_free"])
            self.assertFalse(r["same_nested_invocation_can_reallocate"])
            self.assertFalse(r["same_property40_hit_immediately_nests_again"])
            self.assertFalse(r["direct_one_level_aba_possible"])


if __name__ == "__main__":
    unittest.main()
