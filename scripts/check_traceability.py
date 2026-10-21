"""Cổng L0 "Traceability": mỗi commit trong khoảng phải gắn ít nhất một mã US-nnn.

Cách dùng: python scripts/check_traceability.py <revision-range>
Ví dụ:     python scripts/check_traceability.py origin/main..HEAD
"""

import re
import subprocess
import sys

_US_TAG = re.compile(r"\bUS-\d{3}\b")


def commits_in_range(revision_range: str) -> list[tuple[str, str]]:
    """Trả về danh sách (sha, thông điệp đầy đủ) của các commit trong khoảng."""
    log = subprocess.run(
        ["git", "log", "--format=%H%x1f%B%x1e", revision_range],
        capture_output=True,
        encoding="utf-8",
        check=True,
    ).stdout
    commits: list[tuple[str, str]] = []
    for record in log.split("\x1e"):
        if not record.strip():
            continue
        sha, _, message = record.strip("\n").partition("\x1f")
        commits.append((sha.strip(), message))
    return commits


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print(__doc__)
        return 2
    missing = [sha for sha, message in commits_in_range(argv[1]) if not _US_TAG.search(message)]
    for sha in missing:
        print(f"FAIL: commit {sha[:10]} has no US-nnn tag in its message")
    if missing:
        return 1
    print(f"OK: every commit in {argv[1]} has a US-nnn tag")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
