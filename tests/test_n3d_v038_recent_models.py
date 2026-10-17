import importlib.util
import pathlib
import unittest

TOOL = pathlib.Path(__file__).resolve().parents[1] / "tools" / "n3d_v038_recent_models.py"
spec = importlib.util.spec_from_file_location("v038", TOOL)
v038 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(v038)


class RecentModelsTest(unittest.TestCase):
    def test_joystick_clamp(self):
        self.assertEqual(v038.joystick_calibration(0, 50)["v110"], 1)
        self.assertEqual(v038.joystick_calibration(49, 50)["v110"], 1)
        self.assertEqual(v038.joystick_calibration(50, 50)["v110"], 1)
        self.assertEqual(v038.joystick_calibration(32768, 1)["v18"], 32768)
        self.assertEqual(v038.joystick_calibration(32768, 1)["v110"], 1)
        self.assertTrue(v038.joystick_calibration(1, 0)["divide_error"])

    def test_magic_eye_budget(self):
        self.assertEqual(v038.magic_eye_budget(1)["direct_rng_calls"], 1000)
        self.assertEqual(v038.magic_eye_budget(7)["direct_rng_calls"], 2)
        self.assertEqual(v038.magic_eye_budget(8)["direct_rng_calls"], 0)
        self.assertTrue(v038.magic_eye_budget(0)["divide_error"])

    def test_door_completion_difference(self):
        d1 = v038.normal_door_step(0, 4)
        d2 = v038.normal_door_step(d1["coord"], 4, d1["state"])
        self.assertTrue(d2["completed"])
        p1 = v038.four_vector_panel_step(0, 4)
        p2 = v038.four_vector_panel_step(p1["coord"], 4, p1["state"])
        self.assertFalse(p2["completed"])
        p3 = v038.four_vector_panel_step(p2["coord"], 4, p2["state"])
        self.assertTrue(p3["cleanup"])

    def test_hamerstein_local_damage_contracts(self):
        self.assertEqual([v038.class16_player_hit_damage(1, d) for d in range(3)], [0, 0, 0])
        self.assertEqual([v038.class16_player_hit_damage(3, d) for d in range(3)], [6, 3, 1])
        self.assertEqual([v038.class16_to_player_amount(1, 0, d) for d in range(3)], [16, 33, 66])
        self.assertEqual([v038.class16_to_player_amount(1, 1, d) for d in range(3)], [50, 100, 200])

    def test_signed_counter_and_low16_mean(self):
        self.assertTrue(v038.signed_every20_after_increment(19))
        self.assertTrue(v038.signed_every20_after_increment(0xFFEB))
        self.assertFalse(v038.signed_every20_after_increment(18))
        self.assertEqual(v038.low16_average(4, 5), 0)
        self.assertEqual(v038.low16_average(327680, 5), 0)


if __name__ == "__main__":
    unittest.main()
