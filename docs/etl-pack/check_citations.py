"""Check every `path:line` "fragment" citation in pack.md.

A citation passes when the file exists, the line exists, and the quoted fragment (if any)
appears on that line. Paths resolve under plugins/ first, then the repository root.
Run from anywhere: python3 docs/etl-pack/check_citations.py
"""

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACK = ROOT / "docs/etl-pack/pack.md"
CITE = re.compile(r"`([\w./-]+\.(?:md|py|json|toml)):(\d+)`(?:\s+\"((?:[^\"\\]|\\.)+)\")?")


def resolve(rel: str) -> Path | None:
    for candidate in (ROOT / "plugins" / rel, ROOT / rel):
        if candidate.is_file():
            return candidate
    return None


def main() -> int:
    total = bad = 0
    for match in CITE.finditer(PACK.read_text()):
        total += 1
        rel, line_no, fragment = match.group(1), int(match.group(2)), match.group(3)
        path = resolve(rel)
        if path is None:
            print(f"MISSING FILE {rel}")
            bad += 1
            continue
        lines = path.read_text().splitlines()
        if line_no > len(lines):
            print(f"NO LINE {rel}:{line_no}")
            bad += 1
            continue
        if fragment:
            fragment = fragment.replace('\\"', '"')
            if fragment not in lines[line_no - 1]:
                print(f"FRAGMENT MISS {rel}:{line_no}")
                print(f"  want: {fragment}")
                print(f"  have: {lines[line_no - 1].strip()[:120]}")
                bad += 1
    print(f"{total} citations, {bad} bad")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
