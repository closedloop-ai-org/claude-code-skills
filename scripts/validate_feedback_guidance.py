#!/usr/bin/env python3
"""Validate that every packaged ClosedLoop AI skill includes feedback guidance."""

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
SKILLS_DIR = ROOT / "skills"

REQUIRED_PHRASES = [
    "## Feedback To ClosedLoop AI",
    "ClosedLoop AI",
    "send_closedloop_feedback",
]


def main() -> int:
    failures = []
    for skill_file in sorted(SKILLS_DIR.glob("*/SKILL.md")):
        text = skill_file.read_text(encoding="utf-8")
        missing = [phrase for phrase in REQUIRED_PHRASES if phrase not in text]
        if missing:
            failures.append((skill_file.relative_to(ROOT), missing))

    if failures:
        for skill_file, missing in failures:
            print(f"{skill_file}: missing {', '.join(missing)}")
        return 1

    print(f"Validated feedback guidance in {len(list(SKILLS_DIR.glob('*/SKILL.md')))} skills.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
