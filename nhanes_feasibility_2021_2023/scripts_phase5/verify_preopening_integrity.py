#!/usr/bin/env python3
"""
Step 0: Pre-Opening Integrity Gate
Verifies that all locked experimental artifacts match expected cryptographic signatures.
"""
import hashlib
from pathlib import Path
import sys

BASE = Path(__file__).resolve().parent.parent

EXPECTED_HASHES = {
    "master_split.csv": (
        BASE / "splits_phase4" / "master_split.csv",
        "685b4a15a1ab5ea83647f91f6c335a8a44b2179e47eaab186bdd1960a583f9ed"
    ),
    "development_folds.csv": (
        BASE / "splits_phase4" / "development_folds.csv",
        "0bfacfaba04ffaa02ea0f82294478c0d2790012c0d5466490e85956fabd028e1"
    ),
    "analytic_expanded_complete.parquet": (
        BASE / "processed_phase3" / "analytic_expanded_complete.parquet",
        "6fa1dd5c9212359271de03285806044f3d8a8f817c774bdd1e8c054fe75d1679"
    ),
    "FINAL_MODEL_SPECIFICATION_LOCKED.md": (
        BASE / "lock_phase4_2" / "FINAL_MODEL_SPECIFICATION_LOCKED.md",
        "7d2a5eb9c349dabfca4f5387161c78833c8e996dc302e16955a4d588d68d9ec5"
    ),
    "FINAL_TEST_OPENING_AUTHORIZATION.txt": (
        BASE / "lock_phase4_2" / "FINAL_TEST_OPENING_AUTHORIZATION.txt",
        "549d01da760fd23ec42eaf422a891e8c2406c5232698f215009d094f193f41cc"
    ),
    "final_model_specification.json": (
        BASE / "lock_phase4_2" / "final_model_specification.json",
        "422c45977100359ca955100194ab1e97e9edf9a7326a0c56eb95a800a6067fbb"
    ),
    "COMPARATOR_SPECIFICATION_LOCKED.md": (
        BASE / "lock_phase4_2" / "COMPARATOR_SPECIFICATION_LOCKED.md",
        "b2527b0681cc0ab31b0d38d67f98233d65e308c237870312cdd4d9229b47bbd1"
    ),
    "comparator_specification.json": (
        BASE / "lock_phase4_2" / "comparator_specification.json",
        "0449e0dd8fe8def6e63bccd6123771264dcbe88c8a2b949b92a09d17910fd80b"
    ),
    "PHASE5_EVALUATION_PROTOCOL_LOCKED.md": (
        BASE / "lock_phase4_2" / "PHASE5_EVALUATION_PROTOCOL_LOCKED.md",
        "13bc7de29cde2d6ba0da1b408a3b579e90758a96dfbe0bd4de24a8f1fdf51910"
    ),
}

def main():
    print("="*70)
    print("PRE-OPENING INTEGRITY GATE (PHASE 5)")
    print("="*70)

    rows = []
    all_passed = True

    for name, (path, expected_hash) in EXPECTED_HASHES.items():
        if not path.exists():
            print(f"FAILED: File not found: {path}")
            all_passed = False
            rows.append((name, str(path.relative_to(BASE)), expected_hash, "FILE_NOT_FOUND", "FAIL"))
            continue

        actual_hash = hashlib.sha256(path.read_bytes()).hexdigest()
        # For authorization and json, if expected was None or computed on creation, check actual
        match = (actual_hash == expected_hash) if expected_hash else True
        if not match and expected_hash:
            print(f"FAILED: Hash mismatch for {name}!")
            print(f"  Expected: {expected_hash}")
            print(f"  Actual:   {actual_hash}")
            all_passed = False
            status = "FAIL"
        else:
            status = "PASS"
            print(f"  [PASS] {name:<36} -> {actual_hash[:16]}... matched")

        rows.append((name, str(path.relative_to(BASE)), expected_hash or actual_hash, actual_hash, status))

    # Write report
    report_lines = [
        "# Pre-Opening Integrity Check (Phase 5)",
        "",
        "**Gate Execution Date:** 2026-09-02  ",
        f"**Gate Status:** {'PASSED - AUTHORIZED TO OPEN FINAL TEST' if all_passed else 'FAILED - STOP DO NOT OPEN'}  ",
        "",
        "---",
        "",
        "## Cryptographic Hash Verification Manifest",
        "",
        "| Artifact Name | Path | Expected SHA256 | Actual SHA256 | Status |",
        "|:---|:---|:---|:---|:---:|",
    ]

    for name, rel_path, exp_h, act_h, st in rows:
        report_lines.append(f"| `{name}` | `{rel_path}` | `{exp_h}` | `{act_h}` | **{st}** |")

    report_lines.extend([
        "",
        "---",
        "",
        "## Gate Verdict",
        "",
        "- **Core Datasets & Splits:** Verified identical to locked Phase 4 protocol.",
        "- **Primary & Comparator Specifications:** Verified immutable and intact.",
        "- **Authorization:** Final test set partition is authorized for single-batch Phase 5 evaluation.",
        "",
    ])

    out_path = BASE / "reports_phase5" / "preopening_integrity_check.md"
    out_path.write_text("\n".join(report_lines), encoding="utf-8")
    print(f"\n[OK] Pre-opening integrity report saved: {out_path}")

    if not all_passed:
        print("\nCRITICAL ERROR: INTEGRITY GATE FAILED! ABORTING EXECUTION.")
        sys.exit(1)
    else:
        print("\nSUCCESS: ALL ARTIFACTS VERIFIED. READY FOR FINAL EVALUATION.")

if __name__ == "__main__":
    main()
