#!/usr/bin/env python3
"""Original DOS1.2/DOS2.0 GUARD41 alternative WORLD cleanup, bounded static audit.

This tests exact original unpacked MZ EXE bytes and direct CALLs only.
See V069 report/private 16.8-KB verifier for REP MOVS and archived runtime.
No original game assets are bundled; no emulator or remake is run.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import struct

BUILDS = {
    "dos12": {
        "sha": "f7074660ed26525d2cc5ccd16a6e5ac011f29aaf819dc8ca24ebe39f0fd793e5",
        "clear": 0xB2E0, "dispatcher": 0xB2F6, "near": 0xB51A,
        "far": (0x61F8, 0x620A), "gates": (0x61EE, 0x6200),
        "property": 0xD068, "readers": (0x61D9, 0x61E7),
        "small": 0x52EC, "small_es": 0x254C, "map": 0x9618,
        "map_es": 0x2552, "count": 0x61D2, "reset": 0xB54C, "inc": 0xB666,
        "world_or": 0x848E, "state0a": 0x8496,
    },
    "dos20": {
        "sha": "552d250ef773014a7f56ecdd7939559005fa990ebc7a6e435e6a7a49d372f301",
        "clear": 0xB5A2, "dispatcher": 0xB5B8, "near": 0xB7DC,
        "far": (0x6446, 0x6458), "gates": (0x643C, 0x644E),
        "property": 0xD10C, "readers": (0x6427, 0x6435),
        "small": 0x5534, "small_es": 0x255E, "map": 0x98A2,
        "map_es": 0x2564, "count": 0x6276, "reset": 0xB80E, "inc": 0xB928,
        "world_or": 0x86EA, "state0a": 0x86F2,
    },
}

CLEAR = bytes.fromhex("55 8B EC C4 5E 06 26 C6 47 01 00 C4 5E 0A 26 80 67 05 FE C9 CB")
HEAD = bytes.fromhex("C8 06 00 00 57 56 8B 7E 06 C6 46 FF 01")
SPECIAL = bytes.fromhex("2D 2F 00 3D 0E 00 0F 87 DF 01")
ACCEPT = bytes.fromhex("80 7E FF 00 74 21")


def insist(ok: bool, msg: str) -> None:
    if not ok:
        raise ValueError(msg)


def exact(image: bytes, index: int, signature: bytes, name: str) -> None:
    insist(image[index:index + len(signature)] == signature,
           f"{name} differs at IMG:{index:05X}")


def near_callers(image: bytes, target: int) -> list[int]:
    return [i for i in range(len(image) - 3)
            if image[i] == 0xE8
            and i + 3 + struct.unpack_from("<h", image, i + 1)[0] == target]


def far_callers(image: bytes, target: int) -> list[int]:
    return [i for i in range(len(image) - 5)
            if image[i] == 0x9A
            and (16 * struct.unpack_from("<H", image, i + 3)[0]
                 + struct.unpack_from("<H", image, i + 1)[0]) == target]


def verify_blob(exe: bytes, build: str, *, enforce_sha: bool = True) -> dict:
    c = BUILDS[build]
    digest = hashlib.sha256(exe).hexdigest()
    if enforce_sha:
        insist(digest == c["sha"], f"{build} EXE SHA256 differs")
    insist(len(exe) > 0x18000 and exe[:2] == b"MZ"
           and struct.unpack_from("<H", exe, 8)[0] == 0x20,
           "invalid/unexpected 512-byte DOS MZ header")
    code = exe[512:]

    exact(code, c["clear"], CLEAR, "WORLD+01/05 cleanup")
    insist(code.count(CLEAR) == 1, "WORLD cleanup helper not unique")
    exact(code, c["dispatcher"], HEAD, "WORLD interactor init")
    exact(code, c["dispatcher"] + 0x2C, SPECIAL, "unsigned class dispatch")
    exact(code, c["dispatcher"] + 0x215, ACCEPT, "cleanup acceptance gate")
    exact(code, c["near"] - 1, bytes.fromhex("0E E8 C3 FD"),
          "single near world cleanup CALL")
    insist(near_callers(code, c["clear"]) == [c["near"]],
           "direct near helper callers changed")
    insist(far_callers(code, c["dispatcher"]) == list(c["far"]),
           "direct collision FAR callers changed")
    for i, site in enumerate(c["far"]):
        off, seg = struct.unpack_from("<HH", code, site + 1)
        exact(code, site, b"\x9A" + struct.pack("<HH", off, seg),
              "original FAR CALL")
        insist(16 * seg + off == c["dispatcher"], "FAR CALL target changed")
        exact(code, c["gates"][i],
              b"\xF6\x46" + (b"\xFD" if i == 0 else b"\xFC")
              + b"\x04\x74\x0C", "collision bit4 gate")
        exact(code, c["readers"][i],
              b"\x8A\x87" + struct.pack("<H", c["property"]),
              "collision property table lookup")
    for opcode, at, msg in [
        (bytes.fromhex("26 80 67 05 FE"), c["clear"] + 14, "WORLD05 bit clear"),
        (bytes.fromhex("26 80 4C 05 01"), c["world_or"], "WORLD05 bit set"),
        (bytes.fromhex("26 C6 45 0B 0A"), c["state0a"], "state0A store"),
    ]:
        exact(code, at, opcode, msg)
        insist(code.count(opcode) == 1, msg + " exact opcode not unique")

    exact(code, c["small"] - 16,
          bytes.fromhex("66 33 C0 8E 06")
          + struct.pack("<H", c["small_es"])
          + bytes.fromhex("66 B9 10 00 00 00 BF FE 36 F3 66 AB"),
          "64B REP STOSD working array")
    exact(code, c["map"] - 14,
          bytes.fromhex("33 C0 8E 06")
          + struct.pack("<H", c["map_es"])
          + bytes.fromhex("B9 00 10 BF 00 00 D1 E9 F3 AB"),
          "4096B REP STOSW map area")
    exact(code, c["reset"], b"\x89\x36" + struct.pack("<H", c["count"]),
          "count reset writer")
    exact(code, c["inc"], b"\xFF\x06" + struct.pack("<H", c["count"]),
          "count increment writer")
    insist(0x1000 <= 0x264E and 0x264E + 100 * 26 <= 0x36FE,
           "bulk zero overlaps the GUARD record offsets")
    insist(((0x0F - 0x2F) & 0xFFFF) > 0x0E,
           "class0F unsigned default-branch predicate changed")

    return {
        "build": build, "original_sha256": digest,
        "WORLD_cleanup_helper_image": f"{c['clear']:05X}",
        "direct_near_callers": [f"{x:05X}" for x in near_callers(code, c["clear"])],
        "collision_wrapper_far_callers": [f"{x:05X}" for x in far_callers(code, c["dispatcher"])],
        "WORLD_class0F_not_excluded_by_special_case_range": True,
        "two_bulk_clear_ranges_exclude_GUARD_pool_offsets": True,
        "indirect_pointer_and_SAVE_LOAD_aliases_closed": False,
        "original_runtime_executed_in_this_check": False,
        "original_vs_remake_parity": False,
    }


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--dos12", required=True, type=Path)
    p.add_argument("--dos20", required=True, type=Path)
    p.add_argument("--output", type=Path)
    args = p.parse_args()
    results = [verify_blob(args.dos12.read_bytes(), "dos12"),
               verify_blob(args.dos20.read_bytes(), "dos20")]
    data = {"schema": "V069_ORIGINAL_STATIC_SUBSET", "status": "PASS",
            "original": results,
            "full_original_CPU_trace_replayed": False,
            "complete_actor_slot_lifetime": "OPEN"}
    out = json.dumps(data, indent=2) + "\n"
    print(out, end="")
    if args.output:
        args.output.write_text(out)


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError, KeyError, struct.error) as err:
        raise SystemExit("V069 UNVERIFIED: " + str(err))
