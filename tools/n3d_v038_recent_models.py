#!/usr/bin/env python3
"""Data-free reference models for selected Nitemare 3D RE-MAX v0.38 findings.

These helpers model bounded, source-audited arithmetic/state transitions only.
They do not execute the original game and do not prove runtime reachability.
"""

from __future__ import annotations

import argparse
import json


def s16(value: int) -> int:
    value &= 0xFFFF
    return value - 0x10000 if value & 0x8000 else value


def joystick_calibration(delta: int, sensitivity: int) -> dict:
    delta &= 0xFFFF
    sensitivity &= 0xFF
    if sensitivity == 0:
        return {"divide_error": True, "raw": None, "v18": None, "v110": None}
    raw = (delta // sensitivity) & 0xFFFF
    return {"divide_error": False, "raw": raw, "v18": raw, "v110": raw if s16(raw) > 0 else 1}


def magic_eye_budget(charge: int) -> dict:
    charge &= 0xFF
    if charge == 0:
        return {"divide_error": True, "dots": 0, "direct_rng_calls": 0}
    if charge > 15:
        return {"divide_error": False, "dots": 0, "direct_rng_calls": 0}
    dots = 500 // (charge * charge * charge)
    return {"divide_error": False, "dots": dots, "direct_rng_calls": dots * 2}


def normal_door_step(coord: int, target: int, state: int = 2) -> dict:
    coord &= 0xFFFF
    target &= 0xFFFF
    state &= 0xFF
    if state != 2:
        return {"coord": coord, "state": state, "completed": False, "cleanup": False}
    if coord != target:
        coord = (coord + 2) & 0xFFFF
    if coord == target:
        return {"coord": coord, "state": 0, "completed": True, "cleanup": False}
    return {"coord": coord, "state": 2, "completed": False, "cleanup": False}


def four_vector_panel_step(coord: int, target: int, state: int = 2) -> dict:
    coord &= 0xFFFF
    target &= 0xFFFF
    state &= 0xFF
    if state != 2:
        return {"coord": coord, "state": state, "completed": False, "cleanup": False}
    if s16(coord) < s16(target):
        coord = (coord + 2) & 0xFFFF
        return {"coord": coord, "state": 2, "completed": False, "cleanup": False}
    return {"coord": coord, "state": 0, "completed": True, "cleanup": True}


def class16_player_hit_damage(episode: int, difficulty: int) -> int:
    damage = 3 if episode == 3 else 0
    if difficulty == 2:
        damage = s16(damage) >> 1
    elif difficulty == 0:
        damage = s16(damage + damage)
    return s16(damage)


def class16_to_player_amount(episode: int, story_stage: int, difficulty: int) -> int:
    amount = 100 if episode == 3 or story_stage != 0 else 33
    if difficulty == 2:
        amount = s16(amount * 2)
    elif difficulty == 0:
        amount = s16(amount) >> 1
    return s16(amount)


def signed_every20_after_increment(before: int) -> bool:
    after = (before + 1) & 0xFFFF
    return s16(after) % 20 == 0


def low16_average(elapsed: int, samples: int) -> int:
    if samples == 0:
        return 0
    return (elapsed // samples) & 0xFFFF


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--magic-eye", type=int)
    p.add_argument("--joystick-delta", type=int)
    p.add_argument("--joystick-sensitivity", type=int)
    p.add_argument("--counter-before", type=lambda x: int(x, 0))
    args = p.parse_args()
    out = {}
    if args.magic_eye is not None:
        out["magic_eye"] = magic_eye_budget(args.magic_eye)
    if args.joystick_delta is not None or args.joystick_sensitivity is not None:
        if args.joystick_delta is None or args.joystick_sensitivity is None:
            p.error("both --joystick-delta and --joystick-sensitivity are required")
        out["joystick"] = joystick_calibration(args.joystick_delta, args.joystick_sensitivity)
    if args.counter_before is not None:
        out["signed_every20_after_increment"] = signed_every20_after_increment(args.counter_before)
    print(json.dumps(out, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
