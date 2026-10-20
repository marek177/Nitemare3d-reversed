#!/usr/bin/env python3
"""Strict offline check of the exported DOS v2.0 D02-D RNG ledger.

This verifies a *derived CSV*, not the original N3DTRC01 instruction stream.
Keep the raw-trace provenance and original-vs-port parity separate.
"""
import argparse
from collections import Counter
import csv
import json

EXPECTED_COUNTS = {
    "0x525E": 5, "0x5582": 2, "0x56A6": 22, "0x573F": 15,
    "0x85AD": 24, "0x9C98": 1, "0x9D6E": 2, "0x9F36": 1,
    "0x9FE3": 62, "0xA047": 93, "0xA12B": 2,
}
DEATH_CALLS = ("0x85AD", "0x9FE3", "0x9FE3", "0x9FE3", "0x9D6E")
DEATH_AX = (9961, 491, 2995, 11942, 4827)
DEATH_SCHEDULER = (83, 83, 83, 83, 91)
REQUIRED = (
    "ordinal", "callsite", "state_before", "state_after_lcg", "return_lcg",
    "original_store_observed", "original_return_observed",
    "original_instruction_complete", "scheduler_depth",
    "scheduler_entries_before", "last_demo_record_ordinal", "call_event",
)


def check(condition, message):
    if not condition:
        raise ValueError(message)


def verify(csv_path):
    with open(csv_path, newline="", encoding="utf-8-sig") as stream:
        reader = csv.DictReader(stream)
        check(reader.fieldnames is not None, "missing CSV header")
        check(all(k in reader.fieldnames for k in REQUIRED), "missing CSV columns")
        rows = list(reader)

    check(len(rows) == 229, "expected 229 draws, got %d" % len(rows))
    state = 1
    last_event = -1
    last_scheduler = -1
    last_demo = -1
    counts = Counter()
    groups = []
    previous_site = None
    consecutive = 0

    for ordinal, row in enumerate(rows, 1):
        tag = "draw %d" % ordinal
        check(int(row["ordinal"]) == ordinal, tag + ": ordinal mismatch")
        site = "0x%04X" % int(row["callsite"], 16)
        check(site in EXPECTED_COUNTS, tag + ": unknown caller")
        check(int(row["state_before"], 16) == state, tag + ": broken state chain")
        state = (state * 214013 + 2531011) & 0xFFFFFFFF
        check(int(row["state_after_lcg"], 16) == state, tag + ": wrong LCG state")
        check(int(row["return_lcg"]) == ((state >> 16) & 0x7FFF),
              tag + ": wrong AX")
        check(all(row[k] == "True" for k in
                  ("original_store_observed", "original_return_observed",
                   "original_instruction_complete")), tag + ": incomplete record")
        check(int(row["scheduler_depth"]) == 1, tag + ": wrong observed depth")

        event = int(row["call_event"])
        scheduler = int(row["scheduler_entries_before"])
        demo = int(row["last_demo_record_ordinal"])
        check(event > last_event, tag + ": event ordering changed")
        check(scheduler >= last_scheduler, tag + ": scheduler counter moved back")
        check(demo >= last_demo, tag + ": DEMO record moved back")
        last_event, last_scheduler, last_demo = event, scheduler, demo
        counts[site] += 1

        if site == previous_site:
            consecutive += 1
        else:
            if previous_site is not None:
                groups.append((previous_site, consecutive))
            previous_site, consecutive = site, 1

    groups.append((previous_site, consecutive))
    check(dict(counts) == EXPECTED_COUNTS, "callsite-count mismatch")
    check(state == 0xD0643564, "final RNG state mismatch")
    check(max(n for _, n in groups) == 32, "max consecutive draw burst differs")

    for i, (site, ax, scheduler) in enumerate(
        zip(DEATH_CALLS, DEATH_AX, DEATH_SCHEDULER), 14
    ):
        row = rows[i]
        check(int(row["callsite"], 16) == int(site, 16), "death caller mismatch")
        check(int(row["return_lcg"]) == ax, "death RNG AX mismatch")
        check(int(row["scheduler_entries_before"]) == scheduler,
              "death scheduler context mismatch")

    return {
        "result": "PASS",
        "derived_rows_checked": len(rows),
        "lcg_continuity_checks": len(rows) - 1,
        "executed_callsites": len(counts),
        "largest_same_callsite_run": max(n for _, n in groups),
        "final_rng_state": "0x%08X" % state,
        "fatal_related_draws": "15-19 (caller-pattern context only)",
        "original_raw_trace_replayed": False,
        "original_vs_port_parity": False,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("ledger", help="Private exported D02-D CSV")
    parser.add_argument("--json", help="Optional result JSON output")
    args = parser.parse_args()
    try:
        result = verify(args.ledger)
    except (OSError, ValueError, KeyError, TypeError) as exc:
        parser.exit(1, "FAIL: %s\n" % exc)
    payload = json.dumps(result, indent=2, sort_keys=True)
    print(payload)
    if args.json:
        with open(args.json, "w", encoding="utf-8") as stream:
            stream.write(payload + "\n")


if __name__ == "__main__":
    main()
