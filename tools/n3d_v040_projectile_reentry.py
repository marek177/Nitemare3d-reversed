#!/usr/bin/env python3
"""Bounded model for the Nitemare 3D projectile one-level reentry closure.

The model combines already-audited control-flow facts. It does not execute the
original game and does not exclude unrelated indirect writers or a second
nested scheduler caused by another subsystem.
"""

from __future__ import annotations

import argparse
import json

FREE = 0
FLYING = 1
IMPACT = 2


def visit_flying_slot(collision_accepted: bool) -> dict:
    state = IMPACT if collision_accepted else FLYING
    return {
        "state_after_visit": state,
        "falls_through_to_impact_expiry": False,
        "allocator_can_reuse": state == FREE,
    }


def e2m10_counter_step(before: int) -> dict:
    after = (before + 1) & 0xFFFF
    signed = after - 0x10000 if after & 0x8000 else after
    return {"after": after, "enters_nested_wait": (signed % 20) == 0}


def one_level_self_reentry(nested_collision_accepted: bool) -> dict:
    visit = visit_flying_slot(nested_collision_accepted)
    second = e2m10_counter_step(20)
    return {
        "state_after_nested_pool": visit["state_after_visit"],
        "same_nested_invocation_can_free": False,
        "same_nested_invocation_can_reallocate": visit["allocator_can_reuse"],
        "counter_after_same_path_nested_collision": second["after"],
        "same_property40_hit_immediately_nests_again": second["enters_nested_wait"],
        "direct_one_level_aba_possible": False,
    }


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--nested-collision", choices=("yes", "no"), default="yes")
    args = p.parse_args()
    print(json.dumps(
        one_level_self_reentry(args.nested_collision == "yes"),
        indent=2,
        sort_keys=True,
    ))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
