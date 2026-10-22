#!/usr/bin/env python3
"""Validate the evidence PROVENANCE registry, not the original game's parity.

Only committed documentation metadata is read. No private EXE, game data,
RAM snapshots, or emulator are required. A PASS does not mean a listed
archived original experiment was independently re-executed.
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

SCHEMA = "n3d.re-evidence-registry.v1"
GRADES = frozenset({
    "original_runtime_report",
    "archived_runtime_report",
    "original_static_report",
    "archived_static_report",
    "bounded_original_replay",
    "synthetic_contract",
    "planning",
})
SHA256 = re.compile(r"[0-9a-f]{64}\Z")
SHA1 = re.compile(r"[0-9a-f]{40}\Z")
IDENTIFIER = re.compile(r"[A-Z0-9_]+\Z")


def _source(root: Path, value: object) -> str:
    if not isinstance(value, str) or not value.startswith("docs/"):
        raise ValueError(f"source must be under docs/: {value!r}")
    if "\\" in value or ".." in Path(value).parts:
        raise ValueError(f"unsafe source path: {value!r}")
    parent = root.resolve()
    resolved = (parent / value).resolve()
    if not resolved.is_relative_to(parent) or not resolved.is_file():
        raise ValueError(f"missing or escaping source: {value!r}")
    return value


def validate_registry(doc: dict, root: Path) -> dict:
    if not isinstance(doc, dict) or doc.get("schema") != SCHEMA:
        raise ValueError("unknown or absent schema")
    if doc.get("snapshot_date") != "2026-10-22":
        raise ValueError("unexpected snapshot date")
    if not SHA1.fullmatch(str(doc.get("source_commit_sha", ""))):
        raise ValueError("invalid source commit SHA")
    if doc.get("full_original_vs_remake_parity_proven") is not False:
        raise ValueError("registry must not claim global parity")
    if doc.get("original_files_committed") is not False:
        raise ValueError("original binaries must not be committed")
    exe = doc.get("original_reference_exe")
    if not isinstance(exe, dict) or not SHA256.fullmatch(
        str(exe.get("sha256", ""))
    ):
        raise ValueError("missing pinned original reference SHA256")
    inventory = doc.get("source_document_inventory")
    if not isinstance(inventory, list) or len(inventory) < 100:
        raise ValueError("historical source inventory incomplete")
    if len(inventory) != len(set(inventory)) or inventory != sorted(inventory):
        raise ValueError("historical source inventory not sorted and unique")
    documents = set(_source(root, name) for name in inventory)
    observations = doc.get("observations")
    if not isinstance(observations, list) or len(observations) < 20:
        raise ValueError("observations missing or incomplete")
    ids = set()
    grades = set()
    for i, row in enumerate(observations):
        if not isinstance(row, dict):
            raise ValueError(f"observation {i} not a JSON object")
        tag = row.get("id")
        if not isinstance(tag, str) or not IDENTIFIER.fullmatch(tag) or tag in ids:
            raise ValueError(f"invalid/duplicated observation ID {tag!r}")
        ids.add(tag)
        grade = row.get("grade")
        if grade not in GRADES:
            raise ValueError(f"{tag}: unknown grade {grade!r}")
        grades.add(grade)
        if not isinstance(row.get("domain"), str) or not row["domain"]:
            raise ValueError(f"{tag}: empty domain")
        if not isinstance(row.get("statement"), str) or len(row["statement"]) < 25:
            raise ValueError(f"{tag}: missing substantial statement")
        if row.get("original_vs_remake_parity_proven") is not False:
            raise ValueError(f"{tag}: unacceptable parity promotion")
        if row.get("verified_against_original_in_this_update") is not False:
            raise ValueError(f"{tag}: original rerun must not be fabricated")
        sources = row.get("sources")
        if not isinstance(sources, list) or not sources:
            raise ValueError(f"{tag}: missing sources")
        for path in sources:
            valid = _source(root, path)
            if valid not in documents:
                raise ValueError(f"{tag}: source not in inventory: {valid}")
    if len(grades) < 5:
        raise ValueError("evidence classes unexpectedly collapsed")
    return {
        "status": "PASS_metadata_and_links_only",
        "observations": len(observations),
        "source_documents": len(inventory),
        "evidence_grades": sorted(grades),
        "original_vs_remake_parity_proven": False,
        "original_reexecution_during_validation": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--root", type=Path,
        default=Path(__file__).resolve().parents[1]
    )
    parser.add_argument(
        "--registry", type=Path,
        default=Path("docs/RE_EVIDENCE_REGISTRY_20261022.json")
    )
    args = parser.parse_args()
    path = args.registry
    if not path.is_absolute():
        path = args.root / path
    try:
        report = validate_registry(
            json.loads(path.read_text(encoding="utf-8")), args.root
        )
    except (ValueError, OSError, json.JSONDecodeError) as exc:
        parser.error(str(exc))
    print(json.dumps(report, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
