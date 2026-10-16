#!/usr/bin/env python3
"""Run the project's database-independent checks."""

from pathlib import Path
import sys
import unittest


ROOT = Path(__file__).resolve().parent


def check_python_syntax() -> list[str]:
    failures = []
    for source in sorted(ROOT.rglob("*.py")):
        if any(part in {".venv", ".git", "__pycache__"} for part in source.parts):
            continue
        try:
            compile(source.read_bytes(), str(source), "exec")
        except (OSError, SyntaxError) as exc:
            failures.append(f"{source.relative_to(ROOT)}: {exc}")
    return failures


def main() -> int:
    print("Checking Python syntax...")
    syntax_failures = check_python_syntax()
    if syntax_failures:
        for failure in syntax_failures:
            print(f"FAIL {failure}")
        print(f"Syntax check failed ({len(syntax_failures)} issue(s)).")
        return 1
    print("Python syntax OK.")

    print("Running unit tests...")
    suite = unittest.defaultTestLoader.discover(
        start_dir=str(ROOT / "tests"),
        top_level_dir=str(ROOT),
    )
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    sys.exit(main())
