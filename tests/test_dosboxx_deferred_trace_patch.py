#!/usr/bin/env python3
"""Applicability/safety-shape tests for the optional DOSBox-X v3 overlay.

Tests do NOT compile or execute DOSBox-X or the original Nitemare 3D executable.
"""
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
PATCH = ROOT / "tools" / "dosbox-x" / "n3dtrace_deferred_start_v3.patch"
FIXTURE = ROOT / "tests" / "fixtures" / "dosboxx" / "n3d_trace_v3.cpp"


def setup_source(temp_dir, damaged=False):
    root = Path(temp_dir)
    target = root / "src" / "debug" / "n3d_trace.cpp"
    target.parent.mkdir(parents=True)
    content = FIXTURE.read_text(encoding="utf-8")
    if damaged:
        content = content.replace(
            "bool stop_enabled = false;", "bool stop_enabled = true;", 1
        )
    target.write_text(content, encoding="utf-8")
    subprocess.run(
        ["git", "init", "-q"], cwd=root, check=True, capture_output=True
    )
    return target


def git_apply(directory, *extra):
    return subprocess.run(
        ["git", "apply", *extra, str(PATCH)],
        cwd=directory,
        check=False,
        text=True,
        capture_output=True,
    )


class TestDosboxXDeferredTraceOverlay(unittest.TestCase):
    def test_patch_applies_without_fuzz_to_exact_v3_source(self):
        with tempfile.TemporaryDirectory(prefix="n3d-v3-overlay-") as dirname:
            path = setup_source(dirname)
            self.assertEqual(git_apply(dirname, "--check").returncode, 0)
            self.assertEqual(git_apply(dirname).returncode, 0)
            patched = path.read_text()
            self.assertIn('N3D_TRACE_START_CSIP', patched)
            self.assertIn('N3D_TRACE_START_ES_SI', patched)
            self.assertIn('N3D_TRACE_START_OPCODE4', patched)
            self.assertIn('N3D_TRACE_INSTRUCTION_LIMIT', patched)
            self.assertIn('N3D_TRACE_STOP_BREAK', patched)
            self.assertIn('StopUnlocked("INSTRUCTION_BUDGET")', patched)
            self.assertIn('start_armed = false; // One-shot;', patched)

    def test_patch_refuses_mutated_v3_anchor(self):
        with tempfile.TemporaryDirectory(prefix="n3d-v3-invalid-") as dirname:
            setup_source(dirname, damaged=True)
            self.assertNotEqual(git_apply(dirname, "--check").returncode, 0)

    def test_patch_is_not_silently_applied_twice(self):
        with tempfile.TemporaryDirectory(prefix="n3d-v3-double-") as dirname:
            setup_source(dirname)
            self.assertEqual(git_apply(dirname).returncode, 0)
            self.assertNotEqual(git_apply(dirname, "--check").returncode, 0)

    def test_actor_guard_is_before_start(self):
        with tempfile.TemporaryDirectory(prefix="n3d-v3-guard-") as dirname:
            path = setup_source(dirname)
            self.assertEqual(git_apply(dirname).returncode, 0)
            patched = path.read_text()
            dispatch = patched[patched.index("bool N3DTrace_Instruction(void) {"):]
            self.assertLess(dispatch.index("SegValue(es)!=start_es"), dispatch.index("StartUnlocked()"))
            self.assertLess(dispatch.index("start_guard_bytes"), dispatch.index("StartUnlocked()"))

    def test_budget_stops_without_debugger_pause(self):
        with tempfile.TemporaryDirectory(prefix="n3d-v3-budget-") as dirname:
            path = setup_source(dirname)
            self.assertEqual(git_apply(dirname).returncode, 0)
            patched = path.read_text()
            dispatch = patched[patched.index("bool N3DTrace_Instruction(void) {"):]
            self.assertIn(
                'StopUnlocked("INSTRUCTION_BUDGET");\n        return false;',
                dispatch,
            )

    def test_deferred_start_disables_boot_autostart(self):
        with tempfile.TemporaryDirectory(prefix="n3d-v3-no-boot-") as dirname:
            path = setup_source(dirname)
            self.assertEqual(git_apply(dirname).returncode, 0)
            patched = path.read_text()
            self.assertIn(
                '// Deferred start takes precedence when both variables were supplied.\n        auto_start = false;',
                patched,
            )


if __name__ == "__main__":
    unittest.main()
