#!/usr/bin/env python3
"""Recover ORIGINAL DOS2 CEDC -> 22CA -> 25DC wall texture-U results.

The input is the user-owned unpacked DOS2 EXE (pinned SHA-256) and original
DOSBox-X N3DTRC01 trace ZIP. This does NOT run a remake or prove pixel parity.
No copyrighted game binaries or texels are distributed by this script.
"""
from __future__ import annotations
import argparse
import csv
import hashlib
import json
from pathlib import Path
import zipfile

from n3d_v071_dos20_opcode_gap_audit import verify_original_exe
from n3d_v073_dos2_gap_trace_witness import iterate_cpu

SOURCE_ZIP_SHA = "26995d0ebf2e5e0bde8561b85d85ad6174278a2237b3c202c63444eec49f2207"
BASE_LINEAR = 0x8240
SITES = {
    0x26A6: "orientation", 0x26AB: "cedc_return", 0x26B0: "cedc_stable",
    0x26C9: "edge_call", 0x22D6: "vec_near",
    0x26CC: "u_first", 0x26CF: "u_final"
}
SIZE = {0x26A6: 5, 0x26AB: 3, 0x26B0: 3, 0x26C9: 3,
        0x22D6: 2, 0x26CC: 3, 0x26CF: 2}


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def verify_instruction(row: dict, image: bytes, offset: int) -> None:
    size = SIZE[offset]
    expected = image[offset:offset+size]
    if offset == 0x26A6:
        # DOS2 FAR CALL 0x0C7D:070C becomes 0x14A1:070C when loaded at 0824h.
        relocated = (int.from_bytes(expected[3:5], "little") +
                     (BASE_LINEAR >> 4)) & 0xffff
        expected = expected[:3] + relocated.to_bytes(2, "little")
    if len(row["code"]) < size or row["code"][:size] != expected:
        raise ValueError(f"Original trace opcode mismatch at 0x{offset:05X}")


def extract_session(trace_zip: zipfile.ZipFile, session: str,
                    image: bytes) -> tuple[list[list[dict]], dict]:
    files = sorted(n for n in trace_zip.namelist()
                   if n.endswith(".n3dt") and
                   f"/{session}/" in f"/{n}")
    if not files:
        raise ValueError("Trace session not present in ZIP")
    rows: list[dict] = []
    current: dict = {}
    counts = {name: 0 for name in SITES.values()}
    for name in files:
        with trace_zip.open(name) as file:
            for rec in iterate_cpu(file):
                if rec["code32"] or rec["protected_mode"] or rec["ip"] > 65535:
                    continue
                off = 16*rec["cs"] + rec["ip"] - BASE_LINEAR
                if off not in SITES:
                    continue
                verify_instruction(rec, image, off)
                counts[SITES[off]] += 1
                ax, x = rec["ax"], rec["di"]
                if off == 0x26A6:
                    if current:
                        raise ValueError("Incomplete wall U operation")
                    current = {"x": x, "orientation": ax,
                               "event_first": rec["event"],
                               "source_trace": name}
                elif off == 0x26AB:
                    current["cedc_u"] = ax
                elif off == 0x26B0:
                    if rec["si"] != ax or current.get("cedc_u") != ax:
                        raise ValueError("CEDC AX -> SI propagation mismatch")
                elif off == 0x26C9:
                    current["unadjusted_u"] = rec["si"]
                    current["frame_width"] = ax
                elif off == 0x22D6:
                    current["vec_near"] = rec["si"]
                    if rec["cx"] != current.get("x"):
                        raise ValueError("22CA screen X differs from caller")
                elif off == 0x26CC:
                    current["post_edge_u"] = ax
                else:
                    if x != current.get("x") or ax != current.get("post_edge_u"):
                        raise ValueError("22CA return U mismatch at original callsite")
                    width = current.get("frame_width")
                    if width not in (64, 128) or ax >= width:
                        raise ValueError("Unsupported original U/IMG width")
                    current["u"] = ax
                    current["edge_corrected"] = (
                        ax != (current["unadjusted_u"] & (width-1)))
                    current["event_final"] = rec["event"]
                    rows.append(current)
                    current = {}
    if current:
        raise ValueError("Original trace ends inside an unfinished U call")
    if not rows:
        raise ValueError("No original U calls recovered")

    groups: list[list[dict]] = []
    cur: list[dict] = []
    for row in rows:
        if cur and row["x"] <= cur[-1]["x"]:
            groups.append(cur)
            cur = []
        cur.append(row)
    if cur:
        groups.append(cur)
    full = [group for group in groups if len(group) == 304 and
            [row["x"] for row in group] == list(range(8, 312))]
    return full, {
        "input_trace_files": len(files),
        "original_u_calls": len(rows),
        "partial_frame_lengths": [len(g) for g in groups if len(g) != 304],
        "callsite_counts": counts,
    }


def write_u_report(trace_path: Path, exe_path: Path, session: str,
                   target: Path) -> dict:
    raw = exe_path.read_bytes()
    verify_original_exe(raw)
    if digest(trace_path.read_bytes()) != SOURCE_ZIP_SHA:
        raise ValueError("Original trace ZIP SHA mismatch: different capture set")
    target.mkdir(parents=True, exist_ok=True)
    image = raw[0x200:]
    with zipfile.ZipFile(trace_path) as z:
        frames, stats = extract_session(z, session, image)
    if not frames:
        raise ValueError("No complete original 304-column viewport found")
    reported = []
    for n, frame in enumerate(frames):
        u = bytes(r["u"] for r in frame)
        uid = f"{session}_frame{n:03d}"
        (target / f"{uid}.u8").write_bytes(u)
        columns = ["x","orientation","vec_near","cedc_u","unadjusted_u",
                   "frame_width","post_edge_u","u","edge_corrected",
                   "event_first","event_final"]
        with (target/f"{uid}.csv").open("w",newline="") as output:
            w = csv.DictWriter(output,columns)
            w.writeheader()
            w.writerows({key:r.get(key) for key in columns} for r in frame)
        reported.append({
            "frame": n,
            "original_u_sha256": digest(u),
            "columns": len(frame),
            "unique_wall_vecs": len({r["vec_near"] for r in frame}),
            "edge_correction_columns": [r["x"] for r in frame
                                       if r["edge_corrected"]],
            "orientation_histogram": {str(k): sum(r["orientation"] == k for r in frame)
                                      for k in range(4)},
            "source_widths": sorted({r["frame_width"] for r in frame}),
            "witness_file": f"{uid}.csv", "u_file": f"{uid}.u8",
        })
    report = {
        "schema": "N3D-DOS20-ORIGINAL-U-V077",
        "evidence": "ORIGINAL_ARCHIVED_CPU_PRESTATE_NOT_A_NEW_RUNTIME_SESSION",
        "original_vs_candidate_u": "NOT_TESTED",
        "original_vs_candidate_indexed_framebuffer": "NOT_TESTED",
        "original_exe_sha256": digest(raw),
        "trace_zip_sha256": SOURCE_ZIP_SHA,
        "session": session,
        "complete_original_frames": len(frames),
        "complete_original_U_samples": 304*len(frames),
        "stats": stats, "frames": reported,
        "warning": "These are original-game outputs only. A same-tick remake U capture is still required.",
    }
    (target/f"{session}_manifest.json").write_text(
        json.dumps(report,indent=2)+"\n",encoding="utf-8")
    return report


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--exe", type=Path, required=True)
    p.add_argument("--trace-zip", type=Path, required=True)
    p.add_argument("--session", required=True)
    p.add_argument("--out", type=Path, required=True)
    a = p.parse_args()
    try:
        proof = write_u_report(a.trace_zip,a.exe,a.session,a.out)
    except (OSError,ValueError,zipfile.BadZipFile) as exc:
        p.exit(2,f"UNVERIFIED: {exc}\n")
    print(json.dumps(proof,indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
