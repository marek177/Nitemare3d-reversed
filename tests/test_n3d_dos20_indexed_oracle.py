"""Copyright-free synthetic verification of the standalone, GitHub-safe VGA oracle."""
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from n3d_dos20_indexed_oracle import decode, to_rgb_cache, compare


class IndexedOracleTests(unittest.TestCase):
    def test_two_pages_and_last_pixel(self):
        mem = bytearray(2097152)
        mem[0] = 7
        mem[0x10000] = 12
        mem[0x10000 + 63999] = 99
        self.assertEqual(decode(mem, 0)[0], 7)
        self.assertEqual(decode(mem, 1)[0], 12)
        self.assertEqual(decode(mem, 1)[-1], 99)
        with self.assertRaises(ValueError): decode(mem[:64000], 0)
        with self.assertRaises(ValueError): decode(mem, 2)

    def test_dac_6bit_full_scale(self):
        pal = bytearray(768)
        pal[3:6] = bytes([63, 31, 16])
        rgb = to_rgb_cache(bytes([1])*64000, bytes(pal))
        self.assertEqual(len(rgb), 384000)
        self.assertEqual(rgb[:6], bytes([255, 125, 65, 255, 125, 65]))

    def test_original_cache_match_and_corruption(self):
        mem=bytes(2097152)
        pal=bytes(768)
        ppm=b'P6\n320 400\n255\n'+bytes(384000)
        good=compare(mem,pal,ppm,0)
        self.assertTrue(good['matches'])
        self.assertEqual(good['compared_rgb_components'], 384000)
        bad=bytearray(ppm)
        bad[-1]=1
        result=compare(mem,pal,bytes(bad),0)
        self.assertFalse(result['matches'])
        self.assertEqual(result['mismatched_rgb_components'],1)
        with self.assertRaises(ValueError): compare(mem,pal,ppm[:-1],0)

    def test_invalid_dac(self):
        with self.assertRaises(ValueError): to_rgb_cache(bytes(64000), bytes(767))
        with self.assertRaises(ValueError): to_rgb_cache(bytes(64000), bytes([64])*768)
        with self.assertRaises(ValueError): to_rgb_cache(bytes(63999), bytes(768))


if __name__=='__main__': unittest.main()
