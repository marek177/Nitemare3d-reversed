"""Synthetic BSF fixture tests; no copyrighted game binaries/data required."""
from __future__ import annotations

from contextlib import redirect_stderr, redirect_stdout
from io import StringIO
from pathlib import Path
import json
import struct
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
import n3d_bsf_audit as bsf  # noqa: E402


CHUNKS = (
    b"Exit screen: %o249%\r\n",
    "Manual %o19% %o249% café #".encode("cp437"),
    b"Episode one completed.\r\n",
)


def assemble(exe_data: bytes, map_data: bytes, *, registered: bool = False) -> bytes:
    """Build an artificial archive obeying the documented 54-byte header layout."""
    header = bytearray(bsf.HEADER_BYTES)
    header[1] = bsf.xor_bytes(exe_data, 0x7B)
    header[2] = bsf.xor_bytes(map_data, 0x7B)
    header[3] = 1 if registered else 0
    header[4:4 + len(b"Fixture Distributor")] = b"Fixture Distributor"
    cursor = bsf.HEADER_BYTES
    for i, data in enumerate(CHUNKS):
        struct.pack_into("<I", header, 36 + 4 * i, cursor)
        struct.pack_into("<H", header, 48 + 2 * i, len(data))
        cursor += len(data)

    # The initial plaintext correction byte is 0. Flipping it by the XOR of
    # the provisional encrypted header makes XOR(all ciphertext) become 0.
    header[0] = bsf.xor_bytes(bsf.transform(bytes(header)))
    assert bsf.xor_bytes(bsf.transform(bytes(header))) == 0
    return bsf.transform(bytes(header)) + b"".join(bsf.transform(d) for d in CHUNKS)


def replace_header_field(raw: bytes, offset: int, replacement: bytes) -> bytes:
    """Mutate synthetic plaintext metadata and recompute its ciphertext XOR."""
    header = bytearray(bsf.transform(raw[:bsf.HEADER_BYTES]))
    header[offset:offset + len(replacement)] = replacement
    header[0] = 0
    header[0] = bsf.xor_bytes(bsf.transform(bytes(header)))
    return bsf.transform(bytes(header)) + raw[bsf.HEADER_BYTES:]


class BSFAuditTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.exe_data = b"unrelated artificial executable"
        self.map_data = b"unrelated artificial level"
        self.exe = self.root / "N3D.EXE"
        self.map1 = self.root / "MAP.1"
        self.path = self.root / "NITE3D.BSF"
        self.exe.write_bytes(self.exe_data)
        self.map1.write_bytes(self.map_data)
        self.path.write_bytes(assemble(self.exe_data, self.map_data))

    def test_header_and_independent_buffer_key_phase(self) -> None:
        archive = bsf.parse_bsf(self.path.read_bytes())
        self.assertEqual(archive.distributor, "Fixture Distributor")
        self.assertFalse(archive.registered)
        self.assertTrue(archive.contiguous)
        self.assertEqual([archive.decoded_chunk(i) for i in range(3)], list(CHUNKS))
        self.assertEqual(archive.chunks[0].offset, bsf.HEADER_BYTES)
        for chunk in archive.chunks:
            # Each chunk is decoded with KEY[0], not file_offset % KEY_SIZE.
            first_byte = self.path.read_bytes()[chunk.offset]
            self.assertEqual(first_byte ^ bsf.KEY[0], CHUNKS[chunk.index][0])
        self.assertEqual(bsf.manual_image_ids(archive.decoded_chunk(1).decode("cp437")),
                         [275, 505])

    def test_correction_byte_must_make_cipher_header_xor_zero(self) -> None:
        raw = bytearray(self.path.read_bytes())
        raw[7] ^= 0x01
        with self.assertRaisesRegex(bsf.BSFError, "ciphertext header XOR"):
            bsf.parse_bsf(bytes(raw))

    def test_truncation_and_overlap_are_rejected(self) -> None:
        raw = self.path.read_bytes()
        with self.assertRaisesRegex(bsf.BSFError, "Truncated BSF"):
            bsf.parse_bsf(raw[:50])
        with self.assertRaisesRegex(bsf.BSFError, "outside BSF"):
            bsf.parse_bsf(raw[:-1])
        overlapped = replace_header_field(raw, 40, struct.pack("<I", bsf.HEADER_BYTES))
        with self.assertRaisesRegex(bsf.BSFError, "Overlapping"):
            bsf.parse_bsf(overlapped)

    def test_dos_checks_exe_and_shareware_map(self) -> None:
        archive = bsf.parse_bsf(self.path.read_bytes())
        lines = bsf.verify_installation(archive, "dos", exe=self.exe, map1=self.map1)
        self.assertEqual(len(lines), 2)
        self.exe.write_bytes(self.exe_data + b"\x01")
        with self.assertRaisesRegex(bsf.BSFError, "expected XOR"):
            bsf.verify_installation(archive, "dos", exe=self.exe, map1=self.map1)
        self.exe.write_bytes(self.exe_data)
        self.map1.write_bytes(self.map_data + b"\x01")
        with self.assertRaisesRegex(bsf.BSFError, "MAP.1"):
            bsf.verify_installation(archive, "dos", exe=self.exe, map1=self.map1)

    def test_win16_ignores_exe_and_registered_skips_map(self) -> None:
        archive = bsf.parse_bsf(self.path.read_bytes())
        self.exe.unlink()  # Win16's BSF policy does not enforce this checksum.
        lines = bsf.verify_installation(archive, "win16", exe=None, map1=self.map1)
        self.assertIn("not enforced", lines[0])

        registered_blob = assemble(self.exe_data, self.map_data, registered=True)
        registered = bsf.parse_bsf(registered_blob)
        self.map1.unlink()
        lines = bsf.verify_installation(registered, "win16", exe=None, map1=None)
        self.assertIn("skipped", lines[-1])
        with self.assertRaises(bsf.BSFError):
            bsf.verify_installation(registered, "dos", exe=None, map1=None)

    def test_cli_json_and_manual_refs(self) -> None:
        stdout = StringIO()
        with redirect_stdout(stdout):
            status = bsf.main(["info", str(self.root), "--json"])
        self.assertEqual(status, 0)
        info = json.loads(stdout.getvalue())
        self.assertEqual(info["expected_dos_exe_xor"],
                         f"0x{bsf.xor_bytes(self.exe_data, 0x7B):02X}")
        self.assertEqual(info["distributor"], "Fixture Distributor")

        stdout = StringIO()
        with redirect_stdout(stdout):
            status = bsf.main(["text", str(self.root), "1", "--image-ids"])
        self.assertEqual(status, 0)
        self.assertEqual(stdout.getvalue().strip(), "275 505")

    def test_cli_bad_checksum_is_nonzero(self) -> None:
        self.map1.write_bytes(self.map_data + b"\x10")
        with redirect_stderr(StringIO()):
            result = bsf.main(["verify", str(self.root), "--platform", "dos"])
        self.assertEqual(result, 2)


if __name__ == "__main__":
    unittest.main()
