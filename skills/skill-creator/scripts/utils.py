"""Shared utilities for skill-creator scripts."""

from pathlib import Path



def parse_skill_md(skill_path: Path) -> tuple[str, str, str, str]:
    """Parse a SKILL.md file, returning (name, description, when_to_use, full_content)."""
    # utf-8-sig: a BOM-prefixed SKILL.md loads fine in Claude Code (v2.1.239+) and
    # quick_validate accepts it, so this parser must not choke on the BOM either —
    # otherwise the validator says OK and run_eval/run_loop/improve_description die.
    content = (skill_path / "SKILL.md").read_text(encoding="utf-8-sig")
    lines = content.split("\n")

    if lines[0].strip() != "---":
        raise ValueError("SKILL.md missing frontmatter (no opening ---)")

    end_idx = None
    for i, line in enumerate(lines[1:], start=1):
        if line.strip() == "---":
            end_idx = i
            break

    if end_idx is None:
        raise ValueError("SKILL.md missing frontmatter (no closing ---)")

    name = ""
    description = ""
    when_to_use = ""
    frontmatter_lines = lines[1:end_idx]
    i = 0
    while i < len(frontmatter_lines):
        line = frontmatter_lines[i]
        if line.startswith("name:"):
            name = line[len("name:"):].strip().strip('"').strip("'")
        elif line.startswith("description:"):
            value = line[len("description:"):].strip()
            # Handle YAML multiline indicators (>, |, >-, |-)
            if value in (">", "|", ">-", "|-"):
                continuation_lines: list[str] = []
                i += 1
                while i < len(frontmatter_lines) and (frontmatter_lines[i].startswith("  ") or frontmatter_lines[i].startswith("\t")):
                    continuation_lines.append(frontmatter_lines[i].strip())
                    i += 1
                description = " ".join(continuation_lines)
                continue
            else:
                description = value.strip('"').strip("'")
        elif line.startswith("when_to_use:"):
            value = line[len("when_to_use:"):].strip()
            # Handle YAML multiline indicators (>, |, >-, |-)
            if value in (">", "|", ">-", "|-"):
                continuation_lines_wtu: list[str] = []
                i += 1
                while i < len(frontmatter_lines) and (frontmatter_lines[i].startswith("  ") or frontmatter_lines[i].startswith("\t")):
                    continuation_lines_wtu.append(frontmatter_lines[i].strip())
                    i += 1
                when_to_use = " ".join(continuation_lines_wtu)
                continue
            else:
                when_to_use = value.strip('"').strip("'")
        i += 1

    return name, description, when_to_use, content
