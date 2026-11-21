"""Check that local Markdown links in reader-facing docs resolve.

Skips http(s), mailto, and pure-anchor links. Removes fenced code blocks so
example commands are not interpreted as links.

Run from the repository root:
    python -I tests/check_links.py
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCS = [
    "README.md",
    "README.zh.md",
    "MODEL_CARD.md",
    "MODEL_CARD.en.md",
    "CHANGELOG.md",
    "REPORT.md",
    "docs/quickstart.md",
    "docs/reproduction.md",
    "docs/evaluation.md",
    "docs/architecture.md",
    "docs/faq.md",
]

FENCE_RE = re.compile(r"```.*?```", re.DOTALL)
INLINE_CODE_RE = re.compile(r"`[^`]*`")
LINK_RE = re.compile(r"\[[^\]]*\]\(([^)\s]+)(?:\s+\"[^\"]*\")?\)")


def main() -> int:
    broken: list[tuple[str, str, str]] = []
    for rel in DOCS:
        path = ROOT / rel
        assert path.exists(), f"missing doc: {rel}"
        text = path.read_text(encoding="utf-8")
        text = FENCE_RE.sub("", text)
        text = INLINE_CODE_RE.sub("", text)
        for target in LINK_RE.findall(text):
            if target.startswith(("http://", "https://", "mailto:", "#")):
                continue
            if target.startswith("<") and target.endswith(">"):
                target = target[1:-1]
            target = target.split("#", 1)[0].split("?", 1)[0]
            if not target:
                continue
            resolved = (path.parent / target).resolve()
            if not resolved.exists():
                broken.append((rel, target, str(resolved)))
        print(f"OK {rel}")

    if broken:
        print("\nBroken links:")
        for rel, target, resolved in broken:
            print(f"  {rel}: {target} -> {resolved}")
        return 1
    print(f"\nOK {len(DOCS)} documents, 0 broken local links")
    return 0


if __name__ == "__main__":
    sys.exit(main())