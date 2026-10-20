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
# Compact, literal reference from the previously archived D02-D derived CSV.
# A caller swap that preserves call counts is still a parity failure.
SITE_CODES = ("0x525E", "0x5582", "0x56A6", "0x573F", "0x85AD", "0x9C98", "0x9D6E", "0x9F36", "0x9FE3", "0xA047", "0xA12B")
EXPECTED_CALLSITE_ORDER = (
    "2499999911232248886488888888888888823230499999"
    "94999992023488888a2349923049999948888888888888"
    "8204999949488888887549999999999999999999999949"
    "4999999249499999999999999999999999999999999248"
    "86a232323488888230234888492323232348488884888"
)
# Each block is count:scheduler_entries_before:last_demo_ordinal:key:mask.
# These values pertain ONLY to the D02-D 229-draw reference timing/configuration.
EXPECTED_CLOCK_BLOCKS = (
    "1:57:5:0x48E0:0x0000 9:66:6:0x0000:0x0080 2:69:7:0x0000:0x0000 1:73:8:0x48E0:0x0002 "
    "1:77:8:0x48E0:0x0002 4:83:11:0x0000:0x0080 1:91:12:0x0000:0x0000 16:103:15:0x0000:0x0080 "
    "2:119:18:0x4BE0:0x000A 2:123:19:0x0000:0x0002 1:129:19:0x0000:0x0002 7:134:22:0x0000:0x0080 "
    "6:140:25:0x0000:0x0080 1:147:26:0x0000:0x0000 1:155:27:0x4DE0:0x0010 2:163:30:0x0000:0x0000 "
    "6:163:31:0x0000:0x0080 1:169:34:0x0000:0x0000 2:199:48:0x4BE0:0x0008 3:199:49:0x0000:0x0080 "
    "2:237:64:0x4DE0:0x0010 1:245:64:0x4DE0:0x0010 6:270:77:0x0000:0x0080 15:273:80:0x0000:0x0082 "
    "1:461:121:0x48E0:0x0002 1:465:123:0x4BE0:0x0002 5:500:141:0x0000:0x0080 2:502:143:0x0000:0x0080 "
    "8:504:145:0x0000:0x0080 1:725:188:0x48E0:0x0002 1:735:191:0x4BE0:0x0008 24:738:193:0x0000:0x0000 "
    "2:741:195:0x0000:0x0000 7:744:197:0x0000:0x0000 3:747:199:0x0000:0x0000 33:749:201:0x0000:0x0000 "
    "1:753:202:0x0433:0x0000 3:759:205:0x0000:0x0080 1:767:208:0x0000:0x0000 1:823:219:0x0000:0x0000 "
    "4:969:240:0x48E0:0x0002 2:987:242:0x0000:0x0002 6:997:247:0x0000:0x0000 2:1005:248:0x4DE0:0x0010 "
    "1:1021:252:0x4BE0:0x0008 2:1033:256:0x0000:0x0000 4:1038:260:0x0000:0x0080 "
    "2:1049:263:0x48E0:0x0002 6:1051:263:0x48E0:0x0002 2:1055:263:0x48E0:0x0002 "
    "2:1063:267:0x0000:0x0000 9:1071:273:0x0000:0x0088 "
)


def expected_context():
    result = []
    for token in EXPECTED_CLOCK_BLOCKS.split():
        count, sched, ordinal, key, mask = token.split(":")
        result.extend([(int(sched), int(ordinal), int(key, 16), int(mask, 16))]
                      * int(count))
    check(len(result) == 229, "internal clock fixture length differs")
    return result

DEATH_CALLS = ("0x85AD", "0x9FE3", "0x9FE3", "0x9FE3", "0x9D6E")
DEATH_AX = (9961, 491, 2995, 11942, 4827)
DEATH_SCHEDULER = (83, 83, 83, 83, 91)
REQUIRED = (
    "ordinal", "callsite", "state_before", "state_after_lcg", "return_lcg",
    "original_store_observed", "original_return_observed",
    "original_instruction_complete", "scheduler_depth",
    "scheduler_entries_before", "last_demo_record_ordinal", "last_demo_key",
    "last_demo_mask", "call_event",
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
    expected = expected_context()
    check(len(EXPECTED_CALLSITE_ORDER) == 229, "internal callsite fixture length differs")
    counts = Counter()
    groups = []
    previous_site = None
    consecutive = 0

    for ordinal, row in enumerate(rows, 1):
        tag = "draw %d" % ordinal
        check(int(row["ordinal"]) == ordinal, tag + ": ordinal mismatch")
        site = "0x%04X" % int(row["callsite"], 16)
        check(site in EXPECTED_COUNTS, tag + ": unknown caller")
        check(SITE_CODES.index(site) == int(EXPECTED_CALLSITE_ORDER[ordinal - 1], 16),
              tag + ": original caller ordering differs")
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
        key = int(row["last_demo_key"], 16)
        mask = int(row["last_demo_mask"], 16)
        check((scheduler, demo, key, mask) == expected[ordinal - 1],
              tag + ": reference scheduler/DEMO context differs")
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
        "full_callsite_order_matched": True,
        "reference_scheduler_demo_context_matched": True,
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
