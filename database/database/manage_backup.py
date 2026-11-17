#!/usr/bin/env python3
"""Create and restore complete PostgreSQL database backups.

Usage:
    python database/manage_backup.py backup
    python database/manage_backup.py list
    python database/manage_backup.py restore database/backups/tourist_safety_db_....dump

Backups use PostgreSQL's custom archive format so they can be restored with
pg_restore. Restore replaces objects and rows represented by the selected
backup in the configured database; it should only be run deliberately.
"""

import argparse
import os
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Sequence

ROOT_DIR = Path(__file__).resolve().parent.parent
BACKUP_DIR = Path(__file__).resolve().parent / "backups"
sys.path.insert(0, str(ROOT_DIR))

from backend.config import Config  # noqa: E402


def postgres_env() -> dict[str, str]:
    env = os.environ.copy()
    env["PGPASSWORD"] = Config.DATABASE_PASSWORD
    return env


def postgres_args() -> list[str]:
    return [
        "--host", Config.DATABASE_HOST,
        "--port", str(Config.DATABASE_PORT),
        "--username", Config.DATABASE_USER,
    ]


def require_tool(name: str) -> str:
    path = shutil.which(name)
    if path is None:
        raise RuntimeError(f"{name} was not found. Install PostgreSQL client tools first.")
    return path


def run(command: Sequence[str]) -> None:
    subprocess.run(command, env=postgres_env(), check=True, stdout=subprocess.DEVNULL)


def create_backup() -> Path:
    pg_dump = require_tool("pg_dump")
    require_tool("pg_restore")
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    backup_path = BACKUP_DIR / f"{Config.DATABASE_NAME}_{timestamp}.dump"
    partial_path = backup_path.with_suffix(".dump.partial")

    command = [
        pg_dump,
        *postgres_args(),
        "--dbname", Config.DATABASE_NAME,
        "--format=custom",
        "--no-owner",
        "--no-privileges",
        "--file", str(partial_path),
    ]
    try:
        run(command)
        # Verify that PostgreSQL can read the archive before exposing it as a backup.
        run([require_tool("pg_restore"), "--list", str(partial_path)])
        partial_path.replace(backup_path)
    except Exception:
        partial_path.unlink(missing_ok=True)
        raise

    return backup_path


def list_backups() -> list[Path]:
    if not BACKUP_DIR.exists():
        return []
    return sorted(BACKUP_DIR.glob("*.dump"), key=lambda path: path.stat().st_mtime, reverse=True)


def restore_backup(backup_file: Path, confirm: bool) -> None:
    pg_restore = require_tool("pg_restore")
    backup_file = backup_file.expanduser().resolve()
    if not backup_file.is_file():
        raise FileNotFoundError(f"Backup file does not exist: {backup_file}")

    # Validate the archive before asking to overwrite data.
    run([pg_restore, "--list", str(backup_file)])

    if not confirm:
        print(f"This will replace backed-up objects/data in database '{Config.DATABASE_NAME}'.")
        answer = input("Type RESTORE to continue: ").strip()
        if answer != "RESTORE":
            print("Restore cancelled; the database was not changed.")
            return

    command = [
        pg_restore,
        *postgres_args(),
        "--dbname", Config.DATABASE_NAME,
        "--clean",
        "--if-exists",
        "--no-owner",
        "--no-privileges",
        "--exit-on-error",
        "--single-transaction",
        str(backup_file),
    ]
    run(command)
    print(f"Restored {backup_file.name} into database '{Config.DATABASE_NAME}'.")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="action", required=True)
    subparsers.add_parser("backup", help="Create a timestamped full database dump")
    subparsers.add_parser("list", help="List available database dump files")
    restore_parser = subparsers.add_parser("restore", help="Restore a dump into the configured database")
    restore_parser.add_argument("backup_file", type=Path, help="Path to a .dump backup file")
    restore_parser.add_argument(
        "--yes",
        action="store_true",
        help="Skip the confirmation prompt (use only when intentionally replacing database data)",
    )
    args = parser.parse_args()

    try:
        if args.action == "backup":
            backup_path = create_backup()
            print(f"Database backup created: {backup_path}")
        elif args.action == "list":
            backups = list_backups()
            if not backups:
                print(f"No backups found in {BACKUP_DIR}")
            else:
                for path in backups:
                    size_mb = path.stat().st_size / (1024 * 1024)
                    print(f"{path} ({size_mb:.2f} MB)")
        else:
            restore_backup(args.backup_file, confirm=args.yes)
        return 0
    except (OSError, RuntimeError, subprocess.CalledProcessError) as exc:
        print(f"Backup operation failed: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
