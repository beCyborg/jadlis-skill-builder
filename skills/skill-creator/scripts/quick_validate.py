#!/usr/bin/env python3
"""
Quick validation script for skills — an authoring guardrail, not the canon.

The canonical validator is `claude plugin validate`. This script fails only on
hard errors (missing description, malformed YAML, over-limit lengths, bad
types); everything else — including unknown keys — is a warning and exit 0.

Usage:
    python -m scripts.quick_validate <skill_directory>
    python -m scripts.quick_validate --self-test
"""

import re
import sys
from pathlib import Path

import yaml

# Fields documented in the Claude Code docs or the Agent Skills standard.
ALLOWED_PROPERTIES = {
    'name', 'description', 'when_to_use', 'license', 'allowed-tools', 'disallowed-tools',
    'metadata', 'argument-hint', 'arguments', 'effort', 'context', 'agent', 'background',
    'hooks', 'model', 'disable-model-invocation', 'user-invocable',
    'paths', 'shell', 'compatibility',
    'display-name', 'default-enabled', 'fallback',
}

# Only these exact alternate spellings are normalized (key casing, v2.1.186+).
# A blanket case transform is forbidden here: it would mangle canonical keys
# such as `when_to_use`, which is snake_case by spec.
KEY_ALIASES = {
    'displayName': 'display-name',
    'display_name': 'display-name',
    'defaultEnabled': 'default-enabled',
    'default_enabled': 'default-enabled',
}

# Boolean literals Claude Code accepts in frontmatter (v2.1.218+), any case.
BOOL_LITERALS = {
    'true': True, 'false': False, 'yes': True, 'no': False,
    'on': True, 'off': False, '1': True, '0': False,
}

BOOLEAN_FIELDS = ('disable-model-invocation', 'user-invocable', 'background', 'default-enabled')


def _as_bool(value):
    """Interpret a frontmatter boolean the way Claude Code does (v2.1.218+).

    Accepts real bools, ints 0/1 (PyYAML parses bare `1`/`0` as int), and the
    yes/no/on/off/true/false string literals in any letter case.
    Returns the bool, or None when the value isn't a recognized boolean.
    """
    if isinstance(value, bool):
        return value
    if isinstance(value, int) and value in (0, 1):
        return bool(value)
    if isinstance(value, str):
        return BOOL_LITERALS.get(value.strip().lower())
    return None


def validate_frontmatter(frontmatter, dir_name=None):
    """Validate a parsed frontmatter dict. Returns (errors, warnings).

    Normalizes the KEY_ALIASES spellings in place before checking.
    """
    errors = []
    warnings = []

    for alias, canonical in KEY_ALIASES.items():
        if alias in frontmatter:
            if canonical in frontmatter:
                warnings.append(f"Both '{alias}' and '{canonical}' are set; keeping '{canonical}'.")
                frontmatter.pop(alias)
            else:
                frontmatter[canonical] = frontmatter.pop(alias)

    unexpected_keys = set(frontmatter.keys()) - ALLOWED_PROPERTIES
    if unexpected_keys:
        warnings.append(
            f"Unknown key(s) in frontmatter: {', '.join(sorted(unexpected_keys))}. "
            f"Not a Claude Code or Agent Skills field — check the docs; `claude plugin validate` is the canon."
        )

    # description is the one hard requirement
    if 'description' not in frontmatter:
        errors.append("Missing 'description' in frontmatter")
    else:
        description = frontmatter.get('description')
        if not isinstance(description, str):
            errors.append(f"Description must be a string, got {type(description).__name__}")
            description = ''
        description = description.strip()
        if description and ('<' in description or '>' in description):
            errors.append("Description cannot contain angle brackets (< or >)")

        when_to_use = frontmatter.get('when_to_use', '')
        if not isinstance(when_to_use, str):
            when_to_use = str(when_to_use) if when_to_use is not None else ''
        when_to_use = when_to_use.strip()
        combined = (description + " " + when_to_use) if (description and when_to_use) else (description + when_to_use)
        if len(combined) > 1536:
            # Mirrors references/frontmatter-reference.md §1 (the canon for this number).
            errors.append(
                f"Combined description + when_to_use is too long ({len(combined)} characters). "
                f"Maximum is 1,536 characters (skill-listing truncation cap)."
            )

    # name is optional: the skill falls back to the directory name
    if 'name' not in frontmatter:
        warnings.append(
            "No 'name' in frontmatter — the skill will use the directory name. "
            "Convention: set name == directory basename."
        )
    else:
        name = frontmatter.get('name')
        if not isinstance(name, str):
            errors.append(f"Name must be a string, got {type(name).__name__}")
            name = ''
        name = name.strip()
        if name:
            if not re.match(r'^[a-z0-9-]+$', name):
                errors.append(f"Name '{name}' should be kebab-case (lowercase letters, digits, and hyphens only)")
            elif name.startswith('-') or name.endswith('-') or '--' in name:
                errors.append(f"Name '{name}' cannot start/end with hyphen or contain consecutive hyphens")
            if len(name) > 64:
                errors.append(f"Name is too long ({len(name)} characters). Maximum is 64 characters.")
            if dir_name and name != dir_name:
                warnings.append(
                    f"Name '{name}' != directory basename '{dir_name}'. The command comes from the "
                    f"directory name; a mismatch can suppress argument-hint/autocomplete."
                )

    compatibility = frontmatter.get('compatibility')
    if compatibility is not None:
        warnings.append("'compatibility' field is deprecated and may not be recognized by current Claude Code versions.")

    argument_hint = frontmatter.get('argument-hint')
    if argument_hint is not None:
        if not isinstance(argument_hint, str):
            errors.append(f"argument-hint must be a string, got {type(argument_hint).__name__}")
        elif len(argument_hint) > 128:
            warnings.append(
                f"argument-hint is {len(argument_hint)} characters; long hints may be clipped "
                f"in the autocomplete box. Consider shortening it."
            )

    for field in ('arguments', 'disallowed-tools', 'allowed-tools', 'paths'):
        value = frontmatter.get(field)
        if value is None:
            continue
        if isinstance(value, list):
            for item in value:
                if not isinstance(item, str):
                    errors.append(f"{field} list items must be strings, got {type(item).__name__}")
        elif not isinstance(value, str):
            errors.append(f"{field} must be a string or list, got {type(value).__name__}")

    effort = frontmatter.get('effort')
    if effort is not None:
        valid_efforts = {'low', 'medium', 'high', 'xhigh', 'max'}
        if effort not in valid_efforts:
            errors.append(f"effort must be one of {', '.join(sorted(valid_efforts))}, got '{effort}'")

    context_val = frontmatter.get('context')
    if context_val is not None and context_val != 'fork':
        errors.append(f"context must be 'fork' if present, got '{context_val}'")

    agent = frontmatter.get('agent')
    if agent is not None:
        if not isinstance(agent, str):
            errors.append(f"agent must be a string, got {type(agent).__name__}")
        if context_val != 'fork':
            warnings.append("'agent' is set but 'context' is not 'fork'. The agent field typically requires context: fork.")

    shell = frontmatter.get('shell')
    if shell is not None:
        valid_shells = {'bash', 'powershell'}
        if shell not in valid_shells:
            errors.append(f"shell must be one of {', '.join(sorted(valid_shells))}, got '{shell}'")

    hooks = frontmatter.get('hooks')
    if hooks is not None and not isinstance(hooks, dict):
        errors.append(f"hooks must be a dictionary, got {type(hooks).__name__}")

    model = frontmatter.get('model')
    if model is not None and not isinstance(model, str):
        errors.append(f"model must be a string, got {type(model).__name__}")

    for field in BOOLEAN_FIELDS:
        value = frontmatter.get(field)
        if value is None:
            continue
        if _as_bool(value) is None:
            errors.append(
                f"{field} must be a boolean (true/false, yes/no, on/off, 1/0), "
                f"got {type(value).__name__}: {value!r}"
            )

    if 'background' in frontmatter and context_val != 'fork':
        warnings.append("'background' only applies with 'context: fork' — without it the field has no effect.")

    return errors, warnings


def validate_skill(skill_path):
    """Basic validation of a skill. Returns (bool, str) — kept stable for callers."""
    skill_path = Path(skill_path)

    skill_md = skill_path / 'SKILL.md'
    if not skill_md.exists():
        return False, "SKILL.md not found"

    content = skill_md.read_text()
    if not content.startswith('---'):
        return False, "No YAML frontmatter found"

    match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
    if not match:
        return False, "Invalid frontmatter format"

    try:
        frontmatter = yaml.safe_load(match.group(1))
        if not isinstance(frontmatter, dict):
            return False, "Frontmatter must be a YAML dictionary"
    except yaml.YAMLError as e:
        return False, f"Invalid YAML in frontmatter: {e}"

    dir_name = skill_path.resolve().name
    errors, warnings = validate_frontmatter(frontmatter, dir_name=dir_name)

    warning_text = "".join(f"\nWARNING: {w}" for w in warnings)
    if errors:
        return False, "; ".join(errors) + warning_text
    return True, "Skill is valid!" + warning_text


def _self_test():
    """Fixture suite for the validation contract. Returns the number of failures."""
    def load(doc):
        return yaml.safe_load(doc)

    fixtures = [
        # (label, frontmatter-doc, dir_name, want_error_substr, want_warning_substr, extra_check)
        ("happy path", "name: my-skill\ndescription: Does X when asked.", "my-skill", None, None, None),
        ("missing name -> warn", "description: Does X.", "my-skill", None, "name", None),
        ("missing description -> FAIL", "name: my-skill", "my-skill", "description", None, None),
        ("displayName normalized", "description: X.\nname: my-skill\ndisplayName: My Skill", "my-skill",
         None, None, lambda fm: 'display-name' in fm and 'displayName' not in fm),
        ("default_enabled yes", "description: X.\nname: my-skill\ndefault_enabled: yes", "my-skill", None, None,
         lambda fm: _as_bool(fm.get('default-enabled')) is True),
        ("disable-model-invocation as int", "description: X.\nname: my-skill\ndisable-model-invocation: 1", "my-skill",
         None, None, None),
        ("user-invocable off literal", "description: X.\nname: my-skill\nuser-invocable: 'off'", "my-skill",
         None, None, lambda fm: _as_bool(fm.get('user-invocable')) is False),
        ("fork + background false", "description: X.\nname: my-skill\ncontext: fork\nbackground: false", "my-skill",
         None, None, None),
        ("background without fork -> warn", "description: X.\nname: my-skill\nbackground: true", "my-skill",
         None, "background", None),
        ("unknown key -> warn not fail", "description: X.\nname: my-skill\nfrobnicate: 1", "my-skill",
         None, "frobnicate", None),
        ("description 1600 -> FAIL", "name: my-skill\ndescription: " + "x" * 1600, "my-skill",
         "1,536", None, None),
        ("Bad_Name -> FAIL", "description: X.\nname: Bad_Name", "my-skill", "kebab-case", None, None),
        ("when_to_use NOT renamed", "description: X.\nname: my-skill\nwhen_to_use: when asked", "my-skill",
         None, None, lambda fm: 'when_to_use' in fm),
        ("compatibility -> deprecation warn", "description: X.\nname: my-skill\ncompatibility: claude>=2", "my-skill",
         None, "deprecated", None),
    ]

    failures = 0
    for label, doc, dir_name, want_err, want_warn, extra in fixtures:
        fm = load(doc)
        errors, warnings = validate_frontmatter(fm, dir_name=dir_name)
        problems = []
        if want_err is None and errors:
            problems.append(f"unexpected errors: {errors}")
        if want_err is not None and not any(want_err in e for e in errors):
            problems.append(f"expected error containing {want_err!r}, got: {errors}")
        if want_warn is not None and not any(want_warn in w for w in warnings):
            problems.append(f"expected warning containing {want_warn!r}, got: {warnings}")
        if want_warn is None and want_err is None and warnings and label == "happy path":
            problems.append(f"unexpected warnings: {warnings}")
        if extra is not None and not extra(fm):
            problems.append("extra check failed")
        status = "PASS" if not problems else "FAIL"
        print(f"{status}: {label}" + ("".join(f"\n      {p}" for p in problems)))
        failures += bool(problems)

    print(f"\n{len(fixtures) - failures}/{len(fixtures)} fixtures passed")
    return failures


if __name__ == "__main__":
    if len(sys.argv) == 2 and sys.argv[1] == "--self-test":
        sys.exit(1 if _self_test() else 0)

    if len(sys.argv) != 2:
        print("Usage: python -m scripts.quick_validate <skill_directory> | --self-test")
        sys.exit(1)

    valid, message = validate_skill(sys.argv[1])
    print(message)
    sys.exit(0 if valid else 1)
