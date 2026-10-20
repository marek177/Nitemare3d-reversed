#!/usr/bin/env python3
"""Compare 304 DOS2 wall-U values at x=8..311. NUMERIC PAIR ONLY.

Matching bytes here do not prove that original/candidate gameplay states,
IMG frames, wall geometry, shade or 64000-byte framebuffers are identical.
Use an independent synchronized-state manifest/Stage Parity Gate first.
"""
import argparse,hashlib,json
from pathlib import Path

def compare(original: bytes, candidate: bytes) -> dict:
    if len(original)!=304 or len(candidate)!=304:
        raise ValueError("U records must each be exactly 304 bytes (x=8..311)")
    wrong=[x for x in range(8,312) if original[x-8]!=candidate[x-8]]
    return {
        "evidence_level":"SUPPLIED_U_BYTE_PAIR_ONLY",
        "original_sha256":hashlib.sha256(original).hexdigest(),
        "candidate_sha256":hashlib.sha256(candidate).hexdigest(),
        "different_U_columns":len(wrong),
        "first_wrong_screen_x":wrong[0] if wrong else None,
        "all_wrong_screen_x":wrong,
        "numeric_U_equal":not wrong,
        "original_vs_remake_framebuffer":"NOT_TESTED",
        "warning":"A passing U pair is NOT same-tick, same-IMG, or full pixel parity proof.",
    }

def main() -> int:
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--original-u",required=True,type=Path)
    p.add_argument("--candidate-u",required=True,type=Path)
    p.add_argument("--out",type=Path)
    a=p.parse_args()
    try:result=compare(a.original_u.read_bytes(),a.candidate_u.read_bytes())
    except (ValueError,OSError) as exc:p.exit(2,f"INCOMPARABLE: {exc}\n")
    output=json.dumps(result,indent=2)+"\n"
    if a.out:a.out.write_text(output)
    print(output,end="")
    return 0 if result["numeric_U_equal"] else 1

if __name__=="__main__":
    raise SystemExit(main())
