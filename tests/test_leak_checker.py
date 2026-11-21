"""Positive and negative controls for the evaluation-leak checker.

The checker is only trustworthy if it catches a known collision. This test
feeds it a short-prompt collision (the historical false-negative class) and
then checks that the frozen holdout v3 is clean against a tracked clean
fixture. If the real (gitignored) extras are present, it also runs the full
local negative control.

Run from the repository root:
    python -I tests/test_leak_checker.py
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CHECKER = ROOT / "tools" / "check_eval_leak.py"
FIXTURE_EVAL = ROOT / "tests" / "fixtures" / "leak_eval.json"
FIXTURE_EXTRAS = ROOT / "tests" / "fixtures" / "leak_extras"
FIXTURE_CLEAN = ROOT / "tests" / "fixtures" / "clean_extras"


def run(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-I", str(CHECKER), *args],
        capture_output=True,
        text=True,
        cwd=ROOT,
    )


def main() -> int:
    assert CHECKER.exists(), f"missing {CHECKER}"
    assert FIXTURE_EVAL.exists(), f"missing {FIXTURE_EVAL}"
    assert FIXTURE_EXTRAS.exists(), f"missing {FIXTURE_EXTRAS}"
    assert FIXTURE_CLEAN.exists(), f"missing {FIXTURE_CLEAN}"

    # Positive control: a short prompt (6 chars) hidden inside a brevity
    # extra. The old len(prompt)>=8 guard missed exactly this case.
    hit = run("--eval", str(FIXTURE_EVAL), "--extra-dir", str(FIXTURE_EXTRAS), "--skip-sft-source")
    assert hit.returncode == 1, (
        "known collision was NOT caught (checker false negative)\n"
        f"stdout:\n{hit.stdout}\nstderr:\n{hit.stderr}"
    )
    assert "HIT" in hit.stdout, f"expected HIT in output, got:\n{hit.stdout}"
    print("OK positive control: known short-prompt collision caught (EXIT 1)")

    # Negative control (tracked fixture): holdout v3 must be clean against a
    # known non-colliding extras sample. This runs on a fresh clone, where the
    # real SFT extras are not present (only their SHA256SUMS manifest is).
    clean_fixture = run(
        "--eval", str(ROOT / "data/eval/tests-holdout-v3.json"),
        "--extra-dir", str(FIXTURE_CLEAN),
        "--skip-sft-source",
    )
    assert clean_fixture.returncode == 0, (
        "holdout v3 has collisions against the clean fixture\n"
        f"stdout:\n{clean_fixture.stdout}\nstderr:\n{clean_fixture.stderr}"
    )
    assert "total hits = 0" in clean_fixture.stdout, f"unexpected output:\n{clean_fixture.stdout}"
    print("OK negative control: holdout v3 vs clean fixture = 0 hits (EXIT 0)")

    # Full local negative control: the real extras directory is gitignored, so
    # this only runs where the data is present.
    real_extras = ROOT / "data/sft-extra-v2"
    if any(real_extras.glob("*.jsonl")):
        clean = run(
            "--eval", str(ROOT / "data/eval/tests-holdout-v3.json"),
            "--extra-dir", str(real_extras),
            "--skip-sft-source",
        )
        assert clean.returncode == 0, (
            "holdout v3 has collisions against the real extras\n"
            f"stdout:\n{clean.stdout}\nstderr:\n{clean.stderr}"
        )
        assert "total hits = 0" in clean.stdout, f"unexpected output:\n{clean.stdout}"
        print("OK negative control: holdout v3 vs real extras = 0 hits (EXIT 0)")
    else:
        print("SKIP real extras negative control (data/sft-extra-v2/*.jsonl not present)")
    return 0


if __name__ == "__main__":
    sys.exit(main())