import importlib.util
import pathlib
import unittest

TOOL = pathlib.Path(__file__).resolve().parents[1] / "tools" / "n3d_v041_latest_static_models.py"
spec = importlib.util.spec_from_file_location("v041", TOOL)
v041 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(v041)


class V041LatestStaticModelsTest(unittest.TestCase):
    def test_radio_clears_wall_not_object(self):
        self.assertEqual(v041.clear_radio_wall_only(0xB7, 0x91), (0, 0x91))

    def test_split_clock_torn_witness(self):
        torn = v041.projectile_rearm_deadline(0xFFFF, 0x0002, 50)
        coherent = 0x00020000 + 50
        self.assertEqual(torn, 0x00030031)
        self.assertEqual(coherent, 0x00020032)
        self.assertEqual(torn - coherent, 65535)

    def test_nested_tail_uses_global_scratch_and_outer_local_epoch(self):
        self.assertEqual(
            v041.outer_tail_after_nested(13, 100),
            {"next_frame": 14, "legacy_epoch": 100},
        )

    def test_damage_and_projectile_threshold(self):
        self.assertEqual(v041.preclass_damage(101, 100, 0), 8)
        self.assertEqual(v041.preclass_damage(100, 100, 24), 24)
        self.assertTrue(v041.projectile_proximity(9, -9))
        self.assertFalse(v041.projectile_proximity(10, 0))

    def test_pool_and_asset_facts(self):
        self.assertEqual(v041.POOL_FACTS["secret"]["reserve"], 0)
        self.assertEqual(v041.POOL_FACTS["door"]["source_max"], 62)
        self.assertEqual(v041.E1M9_GROUPS["skeleton"], 9)


if __name__ == "__main__":
    unittest.main()
