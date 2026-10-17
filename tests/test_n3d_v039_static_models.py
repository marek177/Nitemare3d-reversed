import importlib.util
import pathlib
import unittest

TOOL = pathlib.Path(__file__).resolve().parents[1] / "tools" / "n3d_v039_static_models.py"
spec = importlib.util.spec_from_file_location("v039", TOOL)
v039 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(v039)


class V039ModelsTest(unittest.TestCase):
    def test_cannon_rng_then_zero(self):
        self.assertEqual(v039.class19_weapon_damage(), {"damage": 0, "rng_draws": 1})

    def test_e2m10_property40_impact(self):
        r = v039.e2m10_property40_collision()
        self.assertTrue(r["collision_accepted"])
        self.assertFalse(r["dda_budget_reread"])
        self.assertTrue(r["impact"])

    def test_radio_state14_boundary(self):
        timer = 0x70
        for _ in range(16):
            r = v039.radio_state14_tick(timer)
            timer = r["timer"]
            self.assertEqual(r["action"], "none")
        r = v039.radio_state14_tick(timer)
        self.assertEqual((r["timer"], r["action"]), (0x5F, "move"))
        self.assertEqual(v039.radio_state14_tick(0)["action"], "global_stop")

    def test_fire_cadence(self):
        self.assertFalse(v039.fire_cadence_input(1, 0, True)["accepted"])
        self.assertTrue(v039.fire_cadence_input(2, 0, True)["accepted"])
        self.assertFalse(v039.fire_cadence_input(2, 0, False)["accepted"])
        self.assertTrue(v039.fire_cadence_input(1, 3, False)["accepted"])
        self.assertFalse(v039.fire_cadence_input(10, 0xFF, True)["valid_weapon_index"])
        self.assertEqual(v039.fire_cadence_fast_tick(0xFF), 0xFF)

    def test_clock_routing(self):
        self.assertEqual(v039.cached_clock_source(True), "rtc_cache")
        self.assertEqual(v039.cached_clock_source(False), "backend")
        self.assertEqual(v039.backend_clock_source(False, True), "bios_bda_x55")
        self.assertEqual(v039.backend_clock_source(True, True), "system_datetime")
        b = v039.bios_clock55(1000, 0)
        self.assertEqual(b, {"value": 0, "origin": 1000})
        b = v039.bios_clock55(1010, b["origin"])
        self.assertEqual(b["value"], 550)

    def test_angle_one_turn(self):
        cases = {-360: 0, -1: 359, 0: 0, 359: 359, 360: 0, 719: 359, 720: 360}
        for source, expected in cases.items():
            self.assertEqual(v039.normalize_angle_one_turn(source), expected)
        self.assertTrue(v039.angle_input_statically_safe(-360))
        self.assertTrue(v039.angle_input_statically_safe(719))
        self.assertFalse(v039.angle_input_statically_safe(720))


if __name__ == "__main__":
    unittest.main()
