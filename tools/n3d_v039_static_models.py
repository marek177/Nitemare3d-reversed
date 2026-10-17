#!/usr/bin/env python3
"""Data-free bounded models for selected Nitemare 3D v0.39 static closures.

This does not execute any original EXE. It mirrors only the local arithmetic
and state transitions explicitly documented by the audited reports.
"""

from __future__ import annotations

import argparse
import json


THRESHOLDS = (2, 1, 3, 1)


def class19_weapon_damage() -> dict:
    return {"damage": 0, "rng_draws": 1}


def e2m10_property40_collision() -> dict:
    return {
        "script_return": 1,
        "collision_accepted": True,
        "dda_budget_reread": False,
        "impact": True,
    }


def radio_state14_tick(timer: int) -> dict:
    timer &= 0xFFFF
    if timer == 0:
        return {"timer": 0, "action": "global_stop"}
    after = (timer - 1) & 0xFFFF
    return {"timer": after, "action": "move" if after < 0x60 else "none"}


def fire_cadence_input(timer: int, weapon: int, press_edge: bool) -> dict:
    timer &= 0xFF
    weapon &= 0xFF
    if weapon >= len(THRESHOLDS):
        return {"valid_weapon_index": False, "accepted": False, "next_timer": timer}
    if timer < THRESHOLDS[weapon]:
        return {"valid_weapon_index": True, "accepted": False, "next_timer": timer}
    accepted = True if weapon == 3 else bool(press_edge)
    return {
        "valid_weapon_index": True,
        "accepted": accepted,
        "next_timer": 0 if accepted else timer,
    }


def fire_cadence_fast_tick(timer: int) -> int:
    timer &= 0xFF
    return 0xFF if timer == 0xFF else timer + 1


def cached_clock_source(rtc_timing_enabled: bool) -> str:
    return "rtc_cache" if rtc_timing_enabled else "backend"


def backend_clock_source(flag_3cc7: bool, flag_3ccf: bool) -> str:
    return "bios_bda_x55" if (not flag_3cc7 and flag_3ccf) else "system_datetime"


def bios_clock55(bda_tick: int, origin: int) -> dict:
    bda_tick &= 0xFFFFFFFF
    origin &= 0xFFFFFFFF
    if origin == 0:
        origin = bda_tick
    value = ((bda_tick - origin) & 0xFFFFFFFF) * 55
    return {"value": value & 0xFFFFFFFF, "origin": origin}


def normalize_angle_one_turn(value: int) -> int:
    if not -32768 <= value <= 32767:
        raise ValueError("input must fit signed 16-bit")
    a = value
    if a < 0:
        a += 360
    if a >= 360:
        a -= 360
    return a


def angle_input_statically_safe(value: int) -> bool:
    return -360 <= value <= 719


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--angle", type=int)
    p.add_argument("--radio-timer", type=lambda s: int(s, 0))
    p.add_argument("--weapon", type=lambda s: int(s, 0))
    p.add_argument("--timer", type=lambda s: int(s, 0))
    p.add_argument("--press-edge", action="store_true")
    args = p.parse_args()

    out = {}
    if args.angle is not None:
        out["angle"] = {
            "input": args.angle,
            "normalized": normalize_angle_one_turn(args.angle),
            "statically_safe": angle_input_statically_safe(args.angle),
        }
    if args.radio_timer is not None:
        out["radio"] = radio_state14_tick(args.radio_timer)
    if args.weapon is not None or args.timer is not None:
        if args.weapon is None or args.timer is None:
            p.error("--weapon and --timer must be supplied together")
        out["cadence"] = fire_cadence_input(args.timer, args.weapon, args.press_edge)

    out["class19"] = class19_weapon_damage()
    out["e2m10_property40"] = e2m10_property40_collision()
    print(json.dumps(out, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
