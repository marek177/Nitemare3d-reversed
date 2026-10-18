#!/usr/bin/env python3
"""Bounded data-free models for Nitemare3D RE-MAX v0.41.

These helpers encode selected statically verified local contracts and derived
conditional examples. They do not execute original binaries or establish live
IRQ, gameplay, framebuffer or audio parity.
"""

from __future__ import annotations

import argparse
import json


def clear_radio_wall_only(wall_id: int, object_id: int) -> tuple[int, int]:
    return 0, object_id & 0xFF


def split_clock(low_word: int, high_word: int) -> int:
    return (low_word & 0xFFFF) | ((high_word & 0xFFFF) << 16)


def projectile_rearm_deadline(low_word: int, high_word: int, interval: int) -> int:
    return (split_clock(low_word, high_word) + (interval & 0xFFFF)) & 0xFFFFFFFF


def outer_tail_after_nested(global_frame_scratch: int, outer_local_epoch: int) -> dict:
    return {
        "next_frame": (global_frame_scratch + 1) & 0xFFFFFFFF,
        "legacy_epoch": outer_local_epoch & 0xFFFFFFFF,
    }


def preclass_damage(object18: int, projection_base: int, rng_mod25: int) -> int:
    delta = (object18 - projection_base) & 0xFFFF
    return ((delta * 8) + (rng_mod25 % 25)) & 0xFFFF


def projectile_proximity(dx: int, dy: int) -> bool:
    return abs(dx) < 10 and abs(dy) < 10


POOL_FACTS = {
    "world_object": {"capacity": 350, "source_max": 323, "reserve": 27},
    "guard": {"capacity": 100, "source_max": 99, "reserve": 1},
    "door": {"capacity": 64, "source_max": 62, "reserve": 2},
    "secret": {"capacity": 32, "source_max": 32, "reserve": 0},
    "push": {"capacity": 12, "source_max": 11, "reserve": 1},
}

E1M9_GROUPS = {"frankenstein": 17, "skeleton": 9, "mrs_h": 5, "dancers": 12}


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--torn-clock-demo", action="store_true")
    args = p.parse_args()

    out = {
        "pool_facts": POOL_FACTS,
        "e1m9_initial_groups": E1M9_GROUPS,
        "e1m1_object_byte_differences_dos_vs_win": 20,
        "e1m1_guard_count_dos": 33,
        "e1m1_guard_count_win": 39,
        "e2m10_door_controller_candidates": 60,
        "e3m8_secret_panels": 32,
        "secret_64unit_cleanup_call": 33,
    }
    if args.torn_clock_demo:
        torn = projectile_rearm_deadline(0xFFFF, 0x0002, 50)
        coherent = (0x00020000 + 50) & 0xFFFFFFFF
        out["torn_clock_demo"] = {
            "torn_deadline": torn,
            "coherent_deadline": coherent,
            "difference": (torn - coherent) & 0xFFFFFFFF,
        }

    print(json.dumps(out, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
