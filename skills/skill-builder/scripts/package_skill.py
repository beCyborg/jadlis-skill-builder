#!/usr/bin/env python3
"""
Skill Packager - Creates a distributable .skill file of a skill folder

Two modes:
    default   — portable gate: the skill must pass the Agent Skills spec's six
                fields, because that is what claude.ai / the Skills API accept.
    --cc-only — Claude Code-only archive: skips the portable gate (still runs the
                Claude Code validation) and warns that the archive will be
                rejected by a claude.ai upload.

Usage:
    python -m scripts.package_skill <path/to/skill-folder> [output-directory] [--cc-only]

Example:
    python -m scripts.package_skill skills/public/my-skill
    python -m scripts.package_skill skills/public/my-skill ./dist
    python -m scripts.package_skill skills/private/my-cc-skill --cc-only
"""

import argparse
import fnmatch
import sys
import zipfile
from pathlib import Path

# Support both invocation forms: `python -m scripts.package_skill` and a direct
# `python3 scripts/package_skill.py` (no package context → absolute import fails).
if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from scripts.quick_validate import validate_skill

# Patterns to exclude when packaging skills.
EXCLUDE_DIRS = {"__pycache__", "node_modules"}
EXCLUDE_GLOBS = {"*.pyc"}
EXCLUDE_FILES = {".DS_Store"}
# Directories excluded only at the skill root (not when nested deeper).
ROOT_EXCLUDE_DIRS = {"evals"}


def should_exclude(rel_path: Path) -> bool:
    """Check if a path should be excluded from packaging."""
    parts = rel_path.parts
    if any(part in EXCLUDE_DIRS for part in parts):
        return True
    # rel_path is relative to skill_path.parent, so parts[0] is the skill
    # folder name and parts[1] (if present) is the first subdir.
    if len(parts) > 1 and parts[1] in ROOT_EXCLUDE_DIRS:
        return True
    name = rel_path.name
    if name in EXCLUDE_FILES:
        return True
    return any(fnmatch.fnmatch(name, pat) for pat in EXCLUDE_GLOBS)


def package_skill(skill_path, output_dir=None, cc_only=False):
    """
    Package a skill folder into a .skill file.

    Args:
        skill_path: Path to the skill folder
        output_dir: Optional output directory for the .skill file (defaults to current directory)
        cc_only: Skip the portable gate and package a Claude Code-only archive
                 (validated in Claude Code mode; won't upload to claude.ai).

    Returns:
        Path to the created .skill file, or None if error
    """
    skill_path = Path(skill_path).resolve()

    # Validate skill folder exists
    if not skill_path.exists():
        print(f"❌ Error: Skill folder not found: {skill_path}")
        return None

    if not skill_path.is_dir():
        print(f"❌ Error: Path is not a directory: {skill_path}")
        return None

    # Validate SKILL.md exists
    skill_md = skill_path / "SKILL.md"
    if not skill_md.exists():
        print(f"❌ Error: SKILL.md not found in {skill_path}")
        return None

    # Run validation before packaging, in PORTABLE mode: a `.skill` archive goes
    # to claude.ai / the Skills API, which accept only the six Agent Skills spec
    # fields (name, description, license, compatibility, metadata, allowed-tools)
    # and reject anything else with a hard "Unexpected key(s)" error. Packaging a
    # skill that can't be uploaded is worse than refusing to package it.
    # --cc-only is the escape hatch: most real Claude Code skills legitimately use
    # non-portable fields and still want a distributable archive.
    if cc_only:
        print("🔍 Validating skill (Claude Code rules; portable gate skipped)...")
    else:
        print("🔍 Validating skill (portable / upload rules)...")
    valid, message = validate_skill(skill_path, portable=not cc_only)
    if not valid:
        print(f"❌ Validation failed: {message}")
        print("   Please fix the validation errors before packaging.")
        if not cc_only:
            print("   Claude Code-only frontmatter fields must be removed for a portable .skill;")
            print("   see references/frontmatter-reference.md section 1.1.")
            print("   Or pass --cc-only to package a Claude Code-only archive anyway.")
        return None
    print(f"✅ {message}\n")
    if cc_only:
        print("⚠️  --cc-only: the portable gate was skipped. This archive will NOT pass a")
        print("   claude.ai upload / the Skills API if the frontmatter uses Claude Code-only")
        print("   fields — it is for Claude Code distribution only.\n")

    # Determine output location
    skill_name = skill_path.name
    if output_dir:
        output_path = Path(output_dir).resolve()
        output_path.mkdir(parents=True, exist_ok=True)
    else:
        output_path = Path.cwd()

    skill_filename = output_path / f"{skill_name}.skill"

    # Create the .skill file (zip format)
    try:
        with zipfile.ZipFile(skill_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
            # Walk through the skill directory, excluding build artifacts
            for file_path in skill_path.rglob('*'):
                if not file_path.is_file():
                    continue
                arcname = file_path.relative_to(skill_path.parent)
                if should_exclude(arcname):
                    print(f"  Skipped: {arcname}")
                    continue
                zipf.write(file_path, arcname)
                print(f"  Added: {arcname}")

        print(f"\n✅ Successfully packaged skill to: {skill_filename}")
        return skill_filename

    except Exception as e:
        print(f"❌ Error creating .skill file: {e}")
        return None


def main():
    parser = argparse.ArgumentParser(
        prog="python -m scripts.package_skill",
        description="Package a skill folder into a distributable .skill archive.",
        epilog=(
            "By default the skill must pass the portable gate (the six Agent Skills "
            "spec fields), because that is what claude.ai and the Skills API accept. "
            "Use --cc-only to package a Claude Code-only skill: the portable gate is "
            "skipped and the resulting archive will not pass a claude.ai upload.\n"
            "\nExamples:\n"
            "  python -m scripts.package_skill skills/public/my-skill\n"
            "  python -m scripts.package_skill skills/public/my-skill ./dist\n"
            "  python -m scripts.package_skill skills/private/my-cc-skill --cc-only"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("skill_path", help="Path to the skill folder")
    parser.add_argument("output_dir", nargs="?", default=None,
                        help="Optional output directory for the .skill file")
    parser.add_argument("--cc-only", action="store_true",
                        help="Skip the portable gate; package a Claude Code-only archive "
                             "(will NOT upload to claude.ai / the Skills API)")
    args = parser.parse_args()

    skill_path = args.skill_path
    output_dir = args.output_dir

    print(f"📦 Packaging skill: {skill_path}")
    if output_dir:
        print(f"   Output directory: {output_dir}")
    print()

    result = package_skill(skill_path, output_dir, cc_only=args.cc_only)

    if result:
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
