#!/usr/bin/env python3
"""Install this repository's legal skills, plus safe default third-party skills."""

from __future__ import annotations

import argparse
import fnmatch
import os
import shutil
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILLS_ROOT = ROOT / "skills"
THIRD_PARTY_INSTALLER = ROOT / "scripts" / "install_third_party_skills.py"

IGNORE_PATTERNS = {
    ".DS_Store",
    "__pycache__",
    "*.pyc",
    "*.pyo",
    "*.pyd",
    "node_modules",
    "package-lock.json",
    ".env",
    ".env.*",
    "*.token",
    "*.secret",
    "secrets.*",
    "credentials.*",
    "*.pem",
    "*.key",
}


def expand_path(value: str) -> Path:
    return Path(os.path.expandvars(os.path.expanduser(value))).resolve()


def default_skills_dir() -> Path:
    codex_home = os.environ.get("CODEX_HOME")
    if codex_home:
        return expand_path(codex_home) / "skills"
    return expand_path("~/.codex/skills")


def should_ignore(_dir: str, names: list[str]) -> set[str]:
    ignored: set[str] = set()
    for name in names:
        if any(fnmatch.fnmatch(name, pattern) for pattern in IGNORE_PATTERNS):
            ignored.add(name)
    return ignored


def discover_first_party_skills() -> list[Path]:
    if not SKILLS_ROOT.exists():
        raise SystemExit(f"Missing skills directory: {SKILLS_ROOT}")
    return sorted(path for path in SKILLS_ROOT.iterdir() if path.is_dir() and (path / "SKILL.md").exists())


def install_one_skill(src: Path, dest: Path, *, mode: str, force: bool, dry_run: bool) -> str:
    if dest.exists() or dest.is_symlink():
        if not force:
            print(f"Skip existing skill: {dest.name}")
            return "skipped"
        print(f"Replace existing skill: {dest}")
        if not dry_run:
            if dest.is_symlink() or dest.is_file():
                dest.unlink()
            else:
                shutil.rmtree(dest)

    if mode == "symlink":
        print(f"Install symlink: {dest} -> {src}")
        if not dry_run:
            dest.parent.mkdir(parents=True, exist_ok=True)
            os.symlink(src, dest, target_is_directory=True)
    else:
        print(f"Install copy: {src} -> {dest}")
        if not dry_run:
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copytree(src, dest, ignore=should_ignore, symlinks=True)
    return "installed"


def install_first_party(args: argparse.Namespace) -> tuple[int, int]:
    skills = discover_first_party_skills()
    wanted = None
    if args.only:
        wanted = {item.strip() for item in args.only.split(",") if item.strip()}
        available = {path.name for path in skills}
        missing = sorted(wanted - available)
        if missing:
            raise SystemExit(f"Unknown first-party skill(s): {', '.join(missing)}")

    selected = [path for path in skills if wanted is None or path.name in wanted]
    print(f"First-party skills dir: {SKILLS_ROOT}")
    print(f"Target skills dir: {args.skills_dir}")
    print(f"Install mode: {args.install_mode}")
    print(f"Selected first-party skills: {len(selected)}")

    installed = 0
    skipped = 0
    for src in selected:
        result = install_one_skill(
            src,
            args.skills_dir / src.name,
            mode=args.install_mode,
            force=args.force,
            dry_run=args.dry_run,
        )
        if result == "installed":
            installed += 1
        else:
            skipped += 1
    return installed, skipped


def install_third_party(args: argparse.Namespace) -> None:
    if args.skip_third_party:
        print("\nSkip third-party recommended skills.")
        return
    if not THIRD_PARTY_INSTALLER.exists():
        raise SystemExit(f"Missing third-party installer: {THIRD_PARTY_INSTALLER}")

    cmd = [
        sys.executable,
        str(THIRD_PARTY_INSTALLER),
        "--skills-dir",
        str(args.skills_dir),
        "--install-mode",
        args.install_mode,
    ]
    if args.update_third_party:
        cmd.append("--update")
    if args.dry_run:
        cmd.append("--dry-run")
    if args.include_restricted_third_party:
        cmd.append("--all")
    if args.accept_restricted_licenses:
        cmd.append("--accept-restricted-licenses")

    print("\nInstall recommended third-party skills from upstream repositories.")
    print("+ " + " ".join(cmd))
    sys.stdout.flush()
    if not args.dry_run:
        subprocess.run(cmd, check=True)
    else:
        subprocess.run(cmd, check=True)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--skills-dir", type=expand_path, default=default_skills_dir())
    parser.add_argument("--only", help="Comma-separated first-party skill folder names to install.")
    parser.add_argument("--install-mode", choices=["copy", "symlink"], default="copy")
    parser.add_argument("--force", action="store_true", help="Replace existing installed first-party skill folders.")
    parser.add_argument("--skip-third-party", action="store_true", help="Install only this repository's skills.")
    parser.add_argument("--full", action="store_true", help="Install this repository plus every recommended third-party skill.")
    parser.add_argument("--include-restricted-third-party", action="store_true", help="Also select restricted-license third-party recommendations.")
    parser.add_argument("--accept-restricted-licenses", action="store_true", help="Confirm you accept restricted upstream licenses.")
    parser.add_argument("--update-third-party", action="store_true", help="Update cached third-party repositories before installing.")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    if args.full:
        args.include_restricted_third_party = True
    if args.full and not args.accept_restricted_licenses:
        raise SystemExit("--full includes restricted-license upstream projects. Rerun with --accept-restricted-licenses after reading their LICENSE files.")
    return args


def main() -> int:
    args = parse_args()
    installed, skipped = install_first_party(args)
    install_third_party(args)
    print(f"\nDone. First-party installed: {installed}; skipped: {skipped}.")
    print("Restart or reload your AI runtime if it does not detect new skills automatically.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
