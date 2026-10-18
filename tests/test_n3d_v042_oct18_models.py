import importlib.util,pathlib,unittest
TOOL=pathlib.Path(__file__).resolve().parents[1]/"tools"/"n3d_v042_oct18_models.py"
spec=importlib.util.spec_from_file_location("v042",TOOL);v042=importlib.util.module_from_spec(spec);spec.loader.exec_module(v042)
class T(unittest.TestCase):
 def test_damage(self):
  self.assertEqual(v042.damage_order("dos10_19"),"gate_before_calc");self.assertEqual(v042.damage_order("dos20"),"calc_before_gate");self.assertEqual(v042.rng_mask(0x14),31)
 def test_feedback(self):
  self.assertEqual(v042.feedback_step(0),{"timer_after":-1,"selector":3,"active":True});self.assertFalse(v042.feedback_step(-1)["active"])
 def test_save(self):
  self.assertEqual(v042.secret_save(17)["undefined_tail_bytes"],15);self.assertTrue(v042.io_success(0));self.assertFalse(v042.io_success(-1))
 def test_door(self):
  self.assertEqual(v042.door_load("dos")["runtime_prefix"],8);self.assertEqual(v042.door_load("win16")["runtime_prefix"],12)
 def test_queue(self):
  self.assertTrue(v042.win_mode4_ack(2)["forced_present"]);self.assertTrue(v042.win_mode4_ack(1)["end_message_mode"]);self.assertEqual(v042.win_mode4_ack(0)["count_after"],-1)
 def test_pools(self):
  self.assertEqual(v042.POOL_LAYOUTS["dos_dynamic_wall"],{"capacity":64,"stride":18});self.assertEqual(v042.POOL_LAYOUTS["win_class3_geometry"],{"capacity":32,"stride":22})
if __name__=="__main__":unittest.main()
