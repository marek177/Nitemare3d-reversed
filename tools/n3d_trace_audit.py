#!/usr/bin/env python3
"""Offline DOS v2.0 FAST/RNG trace diagnostics; NOT original game emulation.

CSV values are decimal or 0x-prefixed hex. This tool reads files only and
never claims that synthetic fixtures validate original game runtime parity.
"""

import argparse
import csv
import json
from pathlib import Path

FAST_DIRECT = (0xC51A, 0x0A40, 0x5F26, 0xA19A, 0xA4A2,
               0x0E50, 0xA4AC, 0xA0CC, 0x89A2, 0x9026, 0x89A2)
RNG_DIRECT_CALLERS = frozenset((
    0x2478, 0x525E, 0x5582, 0x5666, 0x56A6, 0x573F, 0x58A7,
    0x85AD, 0x887C, 0x9A68, 0x9A77, 0x9C98, 0x9CC2, 0x9D6E,
    0x9F0C, 0x9F36, 0x9FE3, 0xA047, 0xA12B, 0xB276,
))
FAST_CALLER = 0xC150


def parse_number(value):
    text = value.strip()
    return int(text, 16) if text.lower().startswith('0x') else int(text, 10)


def read_csv(path, required):
    with Path(path).open('r', encoding='utf-8-sig', newline='') as fh:
        reader = csv.DictReader(fh)
        if not reader.fieldnames or not set(required).issubset(reader.fieldnames):
            raise ValueError('CSV columns required: ' + ', '.join(required))
        result = []
        for line, row in enumerate(reader, start=2):
            try:
                parsed = {k: parse_number(row[k]) for k in required}
            except (ValueError, KeyError, AttributeError) as exc:
                raise ValueError(f'line {line}: invalid number or missing cell') from exc
            if any(v < 0 for v in parsed.values()):
                raise ValueError(f'line {line}: negative number')
            result.append(parsed)
        return result


def audit_fast(rows, invocation, tick_at_gate):
    """Compare only direct children of ONE identified C150 invocation."""
    expected = FAST_DIRECT if (tick_at_gate & 7) == 0 else FAST_DIRECT[:-1]
    actual = [r['target'] for r in rows
              if r['invocation'] == invocation and r['caller'] == FAST_CALLER]
    for pos, observed in enumerate(actual):
        wanted = expected[pos] if pos < len(expected) else None
        if wanted != observed:
            return dict(ok=False, verdict='divergent', index=pos,
                        expected=wanted, observed=observed,
                        expected_count=len(expected), observed_count=len(actual))
    if len(actual) < len(expected):
        return dict(ok=False, verdict='missing' if not actual else 'incomplete',
                    index=len(actual), expected=expected[len(actual)], observed=None,
                    expected_count=len(expected), observed_count=len(actual))
    return dict(ok=True, verdict='match', index=None, expected=None, observed=None,
                expected_count=len(expected), observed_count=len(actual))


def audit_rng(rows, seed=None, strict_callers=False):
    """Validate local LCG rows and adjacency; no subsystem labeling guessed."""
    if not rows:
        return dict(ok=False, rows=0, error='empty trace', index=0, unknown_callers=[])
    unknown = []
    previous_after = None
    for i, r in enumerate(rows):
        caller, before, after, value = (r[k] for k in ('caller', 'before', 'after', 'result'))
        if caller > 0xFFFF or before > 0xFFFFFFFF or after > 0xFFFFFFFF or value > 0xFFFF:
            return dict(ok=False, rows=len(rows), index=i, error='out-of-range field', unknown_callers=unknown)
        if caller not in RNG_DIRECT_CALLERS:
            unknown.append({'index': i, 'caller': caller})
            if strict_callers:
                return dict(ok=False, rows=len(rows), index=i, error='caller not in direct-call census', unknown_callers=unknown)
        if i == 0 and seed is not None and before != seed:
            return dict(ok=False, rows=len(rows), index=i, error='seed mismatch', unknown_callers=unknown)
        if previous_after is not None and before != previous_after:
            return dict(ok=False, rows=len(rows), index=i, error='RNG state discontinuity', unknown_callers=unknown)
        expected_after = (before * 214013 + 2531011) & 0xFFFFFFFF
        if after != expected_after:
            return dict(ok=False, rows=len(rows), index=i, error='LCG transition mismatch', unknown_callers=unknown)
        if value != ((after >> 16) & 0x7FFF):
            return dict(ok=False, rows=len(rows), index=i, error='RNG result mismatch', unknown_callers=unknown)
        previous_after = after
    return dict(ok=True, rows=len(rows), error=None, index=None,
                final_state=previous_after, unknown_callers=unknown)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='mode', required=True)
    fast = sub.add_parser('fast', help='Check normalized direct calls from one DOS v2.0 FAST invocation')
    fast.add_argument('csv_file')
    fast.add_argument('--invocation', type=lambda x: int(x, 0), required=True)
    fast.add_argument('--tick-at-gate', type=lambda x: int(x, 0), required=True)
    rng = sub.add_parser('rng', help='Check a complete ordered DOS v2.0 RNG draw trace')
    rng.add_argument('csv_file')
    rng.add_argument('--seed', type=lambda x: int(x, 0))
    rng.add_argument('--strict-callers', action='store_true')
    args = parser.parse_args(argv)
    try:
        if args.mode == 'fast':
            rows = read_csv(args.csv_file, ('invocation', 'caller', 'target'))
            report = audit_fast(rows, args.invocation, args.tick_at_gate)
        else:
            rows = read_csv(args.csv_file, ('caller', 'before', 'after', 'result'))
            report = audit_rng(rows, args.seed, args.strict_callers)
    except (ValueError, OSError) as exc:
        parser.error(str(exc))
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report['ok'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
