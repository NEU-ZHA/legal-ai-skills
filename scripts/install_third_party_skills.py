#!/usr/bin/env python3
"""Install recommended third-party legal skills from their upstream repos.

This script does not redistribute third-party source code. It reads
third_party_skills.json, clones the upstream repositories locally, then installs
skill folders by symlink or copy into the user's configured skills directory.
"""

from __future__ import annotations

import argparse
import glob
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MANIFEST = ROOT / "third_party_skills.json"


def expand_path(value: str) -> Path:
    return Path(os.path.expandvars(os.path.expanduser(value))).resolve()


def default_skills_dir() -> Path:
    codex_home = os.environ.get("CODEX_HOME")
    if codex_home:
        return expand_path(codex_home) / "skills"
    return expand_path("~/.codex/skills")


def load_manifest(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as fh:
        data = json.load(fh)
    if "skills" not in data or not isinstance(data["skills"], list):
        raise SystemExit(f"Manifest is missing a skills list: {path}")
    return data


def run(cmd: list[str], *, dry_run: bool) -> None:
    print("+ " + " ".join(cmd))
    if dry_run:
        return
    subprocess.run(cmd, check=True)


def require_git() -> None:
    if shutil.which("git") is None:
        raise SystemExit("git is required to clone third-party skill repositories.")


def selected_entries(data: dict[str, Any], args: argparse.Namespace) -> list[dict[str, Any]]:
    entries = data["skills"]
    if args.only:
        wanted = {item.strip() for item in args.only.split(",") if item.strip()}
        found = {entry["id"] for entry in entries}
        missing = sorted(wanted - found)
        if missing:
            raise SystemExit(f"Unknown skill id(s): {', '.join(missing)}")
        return [entry for entry in entries if entry["id"] in wanted]
    if args.all:
        return entries
    return [entry for entry in entries if entry.get("default_install") is True]


def ensure_restricted_ok(entries: list[dict[str, Any]], args: argparse.Namespace) -> None:
    restricted = [
        entry["id"]
        for entry in entries
        if entry.get("install_policy") != "auto_install_allowed"
    ]
    if restricted and not args.accept_restricted_licenses:
        names = ", ".join(restricted)
        raise SystemExit(
            "The selected third-party skill(s) require explicit license "
            f"confirmation: {names}\n"
            "Read the upstream LICENSE first, then rerun with "
            "--accept-restricted-licenses if you accept the limits."
        )


def clone_or_update(entry: dict[str, Any], repos_dir: Path, args: argparse.Namespace) -> Path:
    repo_dir = repos_dir / entry["id"]
    if repo_dir.exists():
        print(f"Repo cache already exists: {repo_dir}")
        if args.update:
            run(["git", "-C", str(repo_dir), "pull", "--ff-only"], dry_run=args.dry_run)
        return repo_dir

    if not args.dry_run:
        repos_dir.mkdir(parents=True, exist_ok=True)
    run(["git", "clone", "--depth", "1", entry["repo_url"], str(repo_dir)], dry_run=args.dry_run)
    return repo_dir


def explicit_skill_roots(entry: dict[str, Any], repo_dir: Path) -> list[tuple[Path, str]]:
    roots: list[tuple[Path, str]] = []
    for item in entry.get("skill_roots", []):
        rel = item["path"]
        src = (repo_dir / rel).resolve()
        install_as = item.get("install_as") or src.name
        roots.append((src, install_as))
    return roots


def glob_skill_roots(entry: dict[str, Any], repo_dir: Path) -> list[tuple[Path, str]]:
    roots: list[tuple[Path, str]] = []
    prefix = entry.get("install_as_prefix", "")
    for pattern in entry.get("skill_root_globs", []):
        full_pattern = str(repo_dir / pattern)
        for raw in sorted(glob.glob(full_pattern)):
            src = Path(raw).resolve()
            if src.is_dir() and (src / "SKILL.md").exists():
                roots.append((src, f"{prefix}{src.name}"))
    return roots


def skill_roots_for(entry: dict[str, Any], repo_dir: Path, *, dry_run: bool) -> list[tuple[Path, str]]:
    roots = explicit_skill_roots(entry, repo_dir)
    roots.extend(glob_skill_roots(entry, repo_dir))
    if not roots and dry_run and entry.get("skill_root_globs"):
        return []
    if not roots:
        raise SystemExit(f"No installable SKILL.md roots found for {entry['id']}")
    return roots


def install_one_skill(src: Path, dest: Path, args: argparse.Namespace) -> None:
    if not args.dry_run and not src.exists():
        raise SystemExit(f"Expected skill path does not exist: {src}")
    if not args.dry_run and not (src / "SKILL.md").exists():
        raise SystemExit(f"Expected SKILL.md does not exist: {src / 'SKILL.md'}")

    if dest.exists() or dest.is_symlink():
        print(f"Skip existing skill path: {dest}")
        print("  Remove it manually first if you really want to replace it.")
        return

    if args.install_mode == "copy":
        print(f"Install copy: {src} -> {dest}")
        if not args.dry_run:
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copytree(src, dest, symlinks=True)
    else:
        print(f"Install symlink: {dest} -> {src}")
        if not args.dry_run:
            dest.parent.mkdir(parents=True, exist_ok=True)
            os.symlink(src, dest, target_is_directory=True)


def install_entry(entry: dict[str, Any], args: argparse.Namespace) -> None:
    print(f"\n== {entry['id']} ==")
    print(f"Upstream: {entry['homepage']}")
    print(f"License: {entry['license']}")
    repo_dir = clone_or_update(entry, args.repos_dir, args)
    roots = skill_roots_for(entry, repo_dir, dry_run=args.dry_run)
    if not roots and args.dry_run:
        prefix = entry.get("install_as_prefix", "")
        for pattern in entry.get("skill_root_globs", []):
            print(f"Would install cloned directories matching {pattern} as {prefix}<directory-name>")
        return
    for src, install_as in roots:
        install_one_skill(src, args.skills_dir / install_as, args)


def print_list(data: dict[str, Any]) -> None:
    print("Recommended third-party legal skills:\n")
    for entry in data["skills"]:
        default = "default" if entry.get("default_install") else "manual"
        print(f"- {entry['id']} [{default}]")
        print(f"  license: {entry['license']}")
        print(f"  repo: {entry['homepage']}")
        print(f"  policy: {entry['install_policy']}")
        print(f"  use: {'; '.join(entry.get('use_cases_zh', []))}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--skills-dir", type=expand_path, default=default_skills_dir())
    parser.add_argument("--repos-dir", type=expand_path, default=expand_path("~/.codex/third_party_skill_repos"))
    parser.add_argument("--only", help="Comma-separated third-party skill ids to install.")
    parser.add_argument("--all", action="store_true", help="Install every entry in the manifest.")
    parser.add_argument("--accept-restricted-licenses", action="store_true", help="Confirm you accept restricted upstream licenses.")
    parser.add_argument("--install-mode", choices=["symlink", "copy"], default="symlink")
    parser.add_argument("--update", action="store_true", help="Run git pull --ff-only for cached upstream repos.")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--list", action="store_true", help="List manifest entries and exit.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    data = load_manifest(args.manifest)
    if args.list:
        print_list(data)
        return 0
    entries = selected_entries(data, args)
    ensure_restricted_ok(entries, args)
    require_git()
    print(f"Skills dir: {args.skills_dir}")
    print(f"Repo cache: {args.repos_dir}")
    print(f"Install mode: {args.install_mode}")
    for entry in entries:
        install_entry(entry, args)
    print("\nDone. Restart or reload your AI runtime if it does not detect new skills automatically.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
