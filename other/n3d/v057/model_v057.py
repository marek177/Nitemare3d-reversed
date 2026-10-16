#!/usr/bin/env python3
"""Clean-room, bounded local Nitemare 3-D v0.57 semantics, NOT game execution.

The callbacks stand for unresolved FAR callees. Inputs are symbolic in-game
values or synthetic values, not inferred from an actual runtime frame.
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Callable, Mapping, Tuple


def u16(v: int) -> int:
    return v & 0xFFFF


def s16(v: int) -> int:
    v &= 0xFFFF
    return v - 65536 if v & 0x8000 else v


def sar16(v: int, bits: int) -> int:
    return u16(s16(v) >> bits)


@dataclass(frozen=True)
class Tile:
    wall_flags: int = 0
    object_flags: int = 0


@dataclass(frozen=True)
class GeometryResult:
    reached: bool
    reason: str
    traversed: Tuple[Tuple[int, int], ...]
    examined: Tuple[Tuple[int, int], ...]
    wall_callbacks: int
    last_error: int


def geometry_line(start_x: int, start_y: int, dx: int, dy: int,
                  max_steps: int, check_object: bool,
                  tile_at: Callable[[int, int], Tile] | None = None,
                  special_wall: Callable[[int, int], bool] | None = None
                  ) -> GeometryResult:
    """Exact local conditions of IMG:BB60/NE3:D50A for nominal map positions.

    No emulation of the original FAR 'dynamic wall' callbacks is asserted.
    They are injected as `special_wall`, which represents their final AL result.
    Map indexing outside 0..63 is intentionally not claimed: raw routine wraps
    16-bit addresses, so caller must resolve an exact emulated map to handle it.
    """
    tile_at = tile_at or (lambda x, y: Tile())
    special_wall = special_wall or (lambda x, y: True)
    dx, dy = s16(dx), s16(dy)
    sx = 1 if dx > 0 else -1
    sy = 1 if dy > 0 else -1
    end_x, end_y = u16(start_x + dx), u16(start_y + dy)
    abx, aby = u16(abs(dx)), u16(abs(dy))
    x_major = s16(aby) < s16(abx)  # original JGE is signed16, including -32768
    major, minor = (abx, aby) if x_major else (aby, abx)
    err = u16(2 * minor - major)
    correction_no_second_step = u16(2 * minor)
    correction_two_steps = u16(2 * (minor - major))
    max_steps = s16(max_steps)
    visited: list[tuple[int, int]] = []
    examined: list[tuple[int, int]] = []
    callbacks = 0
    if max_steps <= 0:
        return GeometryResult(False, 'limit_nonpositive', (), (), 0, s16(err))
    x, y = u16(start_x), u16(start_y)
    for _ in range(max_steps):
        if x_major:
            x = u16(x + sx)
        else:
            y = u16(y + sy)
        if s16(err) < 0:
            err = u16(err + correction_no_second_step)
        else:
            err = u16(err + correction_two_steps)
            if x_major:
                y = u16(y + sy)
            else:
                x = u16(x + sx)
        visited.append((x, y))
        # Crucial: goal check precedes both map property tests and callbacks.
        if x == end_x and y == end_y:
            return GeometryResult(True, 'endpoint_before_collision',
                                  tuple(visited), tuple(examined), callbacks, s16(err))
        tile = tile_at(x, y)
        examined.append((x, y))
        wf = tile.wall_flags & 0xFF
        if wf & 0x02:
            if wf & 0x04:
                return GeometryResult(False, 'wall_flags_02_and_04',
                                      tuple(visited), tuple(examined), callbacks, s16(err))
            if wf & 0x08:
                callbacks += 1
                if not special_wall(x, y):
                    return GeometryResult(False, 'special_wall_callback_false',
                                          tuple(visited), tuple(examined), callbacks, s16(err))
        if check_object:
            of = tile.object_flags & 0xFF
            if of & 0x02 and not (of & 0x20):
                return GeometryResult(False, 'object_flags_02_without_20',
                                      tuple(visited), tuple(examined), callbacks, s16(err))
    return GeometryResult(False, 'step_limit_reached',
                          tuple(visited), tuple(examined), callbacks, s16(err))


# Table indexes OBJECT+06 class 0C..1F. These symbolic labels correspond
# to verified raw case targets across DOS 2.0 and both Win16 executables.
CLASS_PATH = {
    0x0C: 'shr3', 0x0D: 'sel1_shr1_else3', 0x0E: 'sel2_shr1_else3',
    0x0F: 'sel1_shr8_else1', 0x10: 'sel1_shr8_else1',
    0x11: 'sel2_shr1_else3', 0x12: 'shr2', 0x13: 'shr2',
    0x14: 'sel2_shr1_else3', 0x15: 'callback_zero',
    0x16: 'global3_const3_else_zero',
    0x17: 'sel1_shr8_else2', 0x18: 'sel1_shr8_sel2_shr4_else3',
    0x19: 'zero', 0x1A: 'sel1_shr1_else_zero',
    0x1B: 'shr1', 0x1C: 'shr1', 0x1D: 'shr3',
    0x1E: 'sel1_zero_else3', 0x1F: 'sel1_zero_else2',
}


@dataclass(frozen=True)
class DamageScalar:
    class_path: str
    rng_draws_direct: int
    special_callback: bool
    value_after_rng: int
    value_after_class: int
    value_after_difficulty: int
    returned_ax: int
    consumed_damage_byte: int


def damage_scalar(object_class: int, selector_418f: int, difficulty_4180: int,
                  object_slotdepth_18: int, reference_4552: int, rng_result: int,
                  special_626a: int = 0) -> DamageScalar:
    """IMG:8590 local scalar algorithm, before guard damage wrapper IMG:5F74.

    The draw was made unconditionally by the original function. `rng_result`
    supplies that draw; this standalone model doesn't advance global RNG.
    No meaning is assumed for selector_418f or special_626a beyond comparisons.
    """
    if not 0 <= rng_result <= 0x7FFF:
        raise ValueError('caller must provide 15-bit result from original RNG')
    cls = object_class & 0xFF
    mode = selector_418f & 0xFF
    v = u16(u16(object_slotdepth_18 - reference_4552) << 3)
    v = u16(v + rng_result % 25)  # signed IDIV remainder is 0..24 here
    after_rng = s16(v)
    path = CLASS_PATH.get(cls, 'default_unshifted')
    callback = (cls == 0x15)
    if path == 'callback_zero' or path == 'zero':
        v = 0
    elif path == 'global3_const3_else_zero':
        v = 3 if s16(special_626a) == 3 else 0
    elif path == 'shr1':
        v = sar16(v, 1)
    elif path == 'shr2':
        v = sar16(v, 2)
    elif path == 'shr3':
        v = sar16(v, 3)
    elif path == 'sel1_shr1_else3':
        v = sar16(v, 1 if mode == 1 else 3)
    elif path == 'sel2_shr1_else3':
        v = sar16(v, 1 if mode == 2 else 3)
    elif path == 'sel1_shr8_else1':
        v = sar16(v, 8 if mode == 1 else 1)
    elif path == 'sel1_shr8_else2':
        v = sar16(v, 8 if mode == 1 else 2)
    elif path == 'sel1_shr8_sel2_shr4_else3':
        v = sar16(v, 8 if mode == 1 else 4 if mode == 2 else 3)
    elif path == 'sel1_shr1_else_zero':
        v = sar16(v, 1) if mode == 1 else 0
    elif path == 'sel1_zero_else3':
        v = 0 if mode == 1 else sar16(v, 3)
    elif path == 'sel1_zero_else2':
        v = 0 if mode == 1 else sar16(v, 2)
    elif path != 'default_unshifted':
        raise AssertionError('missing class branch '+path)
    after_class = s16(v)
    if difficulty_4180 == 2:
        v = sar16(v, 1)
    elif difficulty_4180 == 0:
        v = u16(v + v)
    after_difficulty = s16(v)
    ax = 0xFF if s16(v) > 0xFF else v  # only upper signed clamp
    return DamageScalar(path, 1, callback, after_rng, after_class,
                        after_difficulty, ax, ax & 0xFF)


STATE_MAP_3_TO_21 = ('return', 'return', 'transition_21', 'transition_21',
                     'special_animation', 'special_animation',
                     'transition_21', 'transition_21', 'return',
                     'transition_21', 'transition_21', 'transition_21',
                     'transition_21', 'transition_21', 'transition_21',
                     'transition_21', 'transition_21', 'transition_21',
                     'special_animation')


def guard_hit_local_branch(guard_hp: int, scalar_damage_byte: int,
                           strategy_0a: int, state_0b: int) -> dict:
    """Only *local* branches of 5F74 wrapper. FAR effects remain unmodeled.

    The original wrapper treats damage as zero-extended unsigned byte.
    """
    hp, dmg = guard_hp & 0xFF, scalar_damage_byte & 0xFF
    if hp <= dmg:
        return dict(terminal=True, hp_after=0, pain_timer_written=False,
                    transition='death_helpers', pre_state7_callback=False)
    if dmg == 0:
        return dict(terminal=False, hp_after=hp, pain_timer_written=False,
                    transition='return_zero_damage', pre_state7_callback=False)
    special7 = (state_0b & 0xFF) == 7
    hp_after = hp - dmg
    strategy = strategy_0a & 0xFF
    if strategy == 2:
        route='strategy_2_effect'
    elif strategy == 4:
        route='return_strategy_4'
    else:
        state = state_0b & 0xFF
        route=STATE_MAP_3_TO_21[state-3] if 3 <= state <= 21 else 'transition_21'
    return dict(terminal=False, hp_after=hp_after, pain_timer_written=True,
                timer_value=8, transition=route, pre_state7_callback=special7)

@dataclass(frozen=True)
class MovingWallRecord:
    """Only the fields used by the DOS 0:0000 lookup and DOS 0:01E0 gate."""
    cell_offset: int
    cell_segment: int
    state_word_08: int


class MissingMovingWallRecord(RuntimeError):
    """Symbolizes original error/exit call; does not execute DOS INT 21h."""


def moving_wall_gate_dos20(records: tuple[MovingWallRecord, ...] | list[MovingWallRecord],
                           cell_offset: int, cell_segment: int) -> bool:
    """First matching 18B moving-wall record: state word +08 must be 0 or 4.

    Records must be supplied in original array order. Original lookup compares
    *both* far-pointer words, walks 18B records and signals an error if missing.
    """
    for entry in records:
        if u16(entry.cell_offset)==u16(cell_offset) and u16(entry.cell_segment)==u16(cell_segment):
            return u16(entry.state_word_08) in (0,4)
    raise MissingMovingWallRecord('Original DOS IMG:0000 calls IMG:FBAC error path')
