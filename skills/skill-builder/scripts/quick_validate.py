#!/usr/bin/env python3
"""
Quick validation script for skills — an authoring guardrail, not the canon.

The canonical validator is `claude plugin validate`. What counts as a hard error
depends on the mode, because the two target platforms disagree:

Claude Code mode (default) — lenient, matching what Claude Code actually loads.
    Fails only on things Claude Code itself rejects or silently mangles (missing
    description, malformed YAML, over-limit combined description, bad types,
    invalid enum values). Everything portability-related — unknown keys,
    non-portable fields, an over-long name or compatibility, a non-string
    license, a non-map metadata — is a warning, and the exit code stays 0.

Portable mode (--portable, and what package_skill.py's default gate uses) —
    strict, matching claude.ai uploads / the Skills API / `.skill` packaging.
    Only the six Agent Skills spec fields (name, description, license,
    compatibility, metadata, allowed-tools) are legal; anything else is an
    error, as are a name that breaks the spec, compatibility over 500 chars, a
    non-string license and a non-map metadata. Checks that only exist for
    Claude Code-only fields are skipped here — those keys already failed the
    allowlist, and re-reporting them would double up (and, for `context: fork`,
    advise a fix that is itself a portable error).

Usage:
    python -m scripts.quick_validate <skill_directory> [--portable]
    python -m scripts.quick_validate --self-test [--portable]

`--self-test` ignores `--portable`: each fixture carries its own mode, so the
combination runs the same suite rather than erroring out.
"""

import argparse
import os
import re
import sys
import tempfile
from pathlib import Path

import yaml

# Fields documented in the Claude Code docs, plus the Claude Code-only keys
# display-name/default-enabled/fallback (changelog v2.1.186).
ALLOWED_PROPERTIES = {
    'name', 'description', 'when_to_use', 'license', 'allowed-tools', 'disallowed-tools',
    'metadata', 'argument-hint', 'arguments', 'effort', 'context', 'agent', 'background',
    'hooks', 'model', 'disable-model-invocation', 'user-invocable',
    'paths', 'shell', 'compatibility',
    'display-name', 'default-enabled', 'fallback',
}

# The only fields the Agent Skills spec allows. Outside Claude Code — claude.ai
# uploads, the Skills API, `.skill` packaging, and enabling a skill for Cowork
# or cloud sessions — anything else is a hard "Unexpected key(s)" error.
PORTABLE_PROPERTIES = {
    'name', 'description', 'license', 'compatibility', 'metadata', 'allowed-tools',
}

# Agent Skills spec caps. Not in skills.md — the spec (agentskills.io) is the
# source, and they bind on the portable path.
NAME_MAX = 64
COMPATIBILITY_MAX = 500

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


def validate_frontmatter(frontmatter, dir_name=None, portable=False):
    """Validate a parsed frontmatter dict. Returns (errors, warnings).

    Normalizes the KEY_ALIASES spellings in place before checking.

    portable=False — Claude Code mode: every documented field is legal, and
    non-portable fields only earn a warning.
    portable=True  — the upload/packaging path: only the six Agent Skills spec
    fields are legal and anything else is an error, matching the hard error
    claude.ai and the Skills API raise.
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

    # Portability: the Agent Skills spec allows only six fields.
    non_portable = sorted(set(frontmatter.keys()) - PORTABLE_PROPERTIES)
    if non_portable:
        allowed = ', '.join(sorted(PORTABLE_PROPERTIES))
        if portable:
            errors.append(
                f"Unexpected key(s) in SKILL.md frontmatter: {', '.join(non_portable)}. "
                f"Allowed properties are: {allowed}"
            )
        else:
            warnings.append(
                f"Non-portable field(s): {', '.join(non_portable)}. Legal in Claude Code, but this "
                f"skill won't upload to claude.ai / the Skills API and won't package portably "
                f"(package_skill.py --cc-only packages it for Claude Code only) — those paths "
                f"reject anything outside {allowed} with a hard error. Enabling a personal skill for "
                f"Cowork or cloud sessions counts as an upload."
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
        # Angle brackets are NOT rejected by Claude Code — it escapes `<>` in the
        # text that reaches Claude. Keep them out for readability, not validity.

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
        name_is_str = isinstance(name, str)
        if not name_is_str:
            errors.append(f"Name must be a string, got {type(name).__name__}")
            name = ''
        name = name.strip()
        if not name:
            # A present-but-blank `name` is not the "fall back to the directory
            # name" case — it's a broken value, and skipping every name check for
            # it would let an empty name through both modes.
            if name_is_str:
                errors.append(
                    "'name' is present but empty. Remove the key to fall back to the "
                    "directory name, or set it to the skill's kebab-case folder name."
                )
        else:
            # Portable mode follows the Agent Skills spec (agentskills.io): plain
            # kebab-case, <= 64 chars, equal to the folder name. Claude Code mode
            # additionally accepts a plugin-namespaced name such as
            # `my-plugin:fancy`, which the docs show as a working plugin skill.
            segments = name.split(':')
            kebab_ok = all(re.match(r'^[a-z0-9-]+$', seg) for seg in segments) and bool(segments[-1])
            hyphen_ok = all(
                not (seg.startswith('-') or seg.endswith('-') or '--' in seg) for seg in segments
            )
            if portable:
                if not re.match(r'^[a-z0-9-]+$', name):
                    errors.append(
                        f"Name '{name}' must be kebab-case (lowercase letters, digits, and hyphens "
                        f"only) on the portable path — the Agent Skills spec forbids other characters, "
                        f"including the plugin ':' namespace."
                    )
                elif not hyphen_ok:
                    errors.append(f"Name '{name}' cannot start/end with hyphen or contain consecutive hyphens")
                if len(name) > NAME_MAX:
                    errors.append(
                        f"Name is too long ({len(name)} characters). The Agent Skills spec caps it at "
                        f"{NAME_MAX} characters."
                    )
                if dir_name and name != dir_name:
                    errors.append(
                        f"Name '{name}' != directory basename '{dir_name}'. The Agent Skills spec "
                        f"requires the name to match the skill's folder name."
                    )
            else:
                if not kebab_ok:
                    errors.append(
                        f"Name '{name}' should be kebab-case (lowercase letters, digits, and hyphens; "
                        f"':' allowed only as the plugin namespace separator, e.g. 'my-plugin:fancy')"
                    )
                elif not hyphen_ok:
                    errors.append(f"Name '{name}' cannot start/end with hyphen or contain consecutive hyphens")
                if len(name) > NAME_MAX:
                    warnings.append(
                        f"Name is {len(name)} characters. Claude Code imposes no cap, but the Agent "
                        f"Skills spec caps it at {NAME_MAX} — over that the skill won't upload or package."
                    )
                # No name != dir_name warning here: in a personal or project skill
                # `name` is only a display label, and in a plugin skill replacing the
                # command's last segment is the documented pattern.

    # In portable mode the three shared fields below bind as hard errors: the
    # upload path rejects them outright, so a warning would green-light an archive
    # claude.ai will refuse.
    portable_bucket = errors if portable else warnings

    compatibility = frontmatter.get('compatibility')
    if compatibility is not None:
        if not isinstance(compatibility, str):
            errors.append(f"compatibility must be a string, got {type(compatibility).__name__}")
        elif len(compatibility) > COMPATIBILITY_MAX:
            portable_bucket.append(
                f"compatibility is {len(compatibility)} characters; the documented cap is "
                f"{COMPATIBILITY_MAX}."
            )

    license_val = frontmatter.get('license')
    if license_val is not None and not isinstance(license_val, str):
        portable_bucket.append(
            f"license should be a string identifier (e.g. 'MIT'), got {type(license_val).__name__}."
        )

    metadata = frontmatter.get('metadata')
    if metadata is not None:
        if not isinstance(metadata, dict):
            portable_bucket.append(
                f"metadata must be a YAML map; Claude Code silently drops a value that isn't one "
                f"(got {type(metadata).__name__})."
            )
        else:
            shadowed = sorted(str(k) for k in metadata if str(k) in ALLOWED_PROPERTIES)
            if shadowed:
                warnings.append(
                    f"metadata reuses frontmatter field name(s) as keys: {', '.join(shadowed)}. "
                    f"The docs advise against it."
                )

    def _check_str_or_list(field):
        value = frontmatter.get(field)
        if value is None:
            return
        if isinstance(value, list):
            for item in value:
                if not isinstance(item, str):
                    errors.append(f"{field} list items must be strings, got {type(item).__name__}")
        elif not isinstance(value, str):
            errors.append(f"{field} must be a string or list, got {type(value).__name__}")

    # allowed-tools is one of the six portable fields — checked in both modes.
    _check_str_or_list('allowed-tools')

    # Everything below is a Claude Code-only field. In portable mode those keys were
    # already rejected wholesale by the allowlist above, so re-checking their values
    # would double-report — and the `agent`/`background` hints would recommend
    # `context: fork`, which is itself a portable error.
    if not portable:
        argument_hint = frontmatter.get('argument-hint')
        if argument_hint is not None:
            if not isinstance(argument_hint, str):
                errors.append(f"argument-hint must be a string, got {type(argument_hint).__name__}")
            elif len(argument_hint) > 128:
                warnings.append(
                    f"argument-hint is {len(argument_hint)} characters; long hints may be clipped "
                    f"in the autocomplete box. Consider shortening it."
                )

        for field in ('arguments', 'disallowed-tools', 'paths'):
            _check_str_or_list(field)

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


def validate_skill(skill_path, portable=False):
    """Basic validation of a skill. Returns (bool, str) — kept stable for callers.

    Set portable=True to validate against the Agent Skills spec's six fields,
    which is what claude.ai uploads, the Skills API and `.skill` packaging enforce.
    """
    skill_path = Path(skill_path)

    skill_md = skill_path / 'SKILL.md'
    if not skill_md.exists():
        return False, "SKILL.md not found"

    # utf-8-sig: Claude Code loads a BOM-prefixed SKILL.md fine (v2.1.239+), so a
    # BOM must not make this script think the frontmatter is missing.
    content = skill_md.read_text(encoding='utf-8-sig')
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

    # abspath, not resolve(): resolve() dereferences symlinks, so a skill reached
    # through a symlinked directory would be compared against the link *target*'s
    # name and fail the portable name == folder-name rule for no real reason.
    dir_name = Path(os.path.abspath(skill_path)).name
    errors, warnings = validate_frontmatter(frontmatter, dir_name=dir_name, portable=portable)

    warning_text = "".join(f"\nWARNING: {w}" for w in warnings)
    if errors:
        return False, "; ".join(errors) + warning_text
    return True, "Skill is valid!" + warning_text


def _self_test():
    """Fixture suite for the validation contract. Returns the number of failures."""
    def load(doc):
        return yaml.safe_load(doc)

    fixtures = [
        # (label, frontmatter-doc, dir_name, want_error_substr, want_warning_substr, extra_check, portable)
        ("happy path", "name: my-skill\ndescription: Does X when asked.", "my-skill", None, None, None, False),
        ("missing name -> warn", "description: Does X.", "my-skill", None, "name", None, False),
        ("missing description -> FAIL", "name: my-skill", "my-skill", "description", None, None, False),
        ("displayName normalized", "description: X.\nname: my-skill\ndisplayName: My Skill", "my-skill",
         None, None, lambda fm: 'display-name' in fm and 'displayName' not in fm, False),
        ("default_enabled yes", "description: X.\nname: my-skill\ndefault_enabled: yes", "my-skill", None, None,
         lambda fm: _as_bool(fm.get('default-enabled')) is True, False),
        ("disable-model-invocation as int", "description: X.\nname: my-skill\ndisable-model-invocation: 1", "my-skill",
         None, None, None, False),
        ("user-invocable off literal", "description: X.\nname: my-skill\nuser-invocable: 'off'", "my-skill",
         None, None, lambda fm: _as_bool(fm.get('user-invocable')) is False, False),
        ("fork + background false", "description: X.\nname: my-skill\ncontext: fork\nbackground: false", "my-skill",
         None, None, None, False),
        ("background without fork -> warn", "description: X.\nname: my-skill\nbackground: true", "my-skill",
         None, "background", None, False),
        ("unknown key -> warn not fail", "description: X.\nname: my-skill\nfrobnicate: 1", "my-skill",
         None, "frobnicate", None, False),
        ("description 1600 -> FAIL", "name: my-skill\ndescription: " + "x" * 1600, "my-skill",
         "1,536", None, None, False),
        ("Bad_Name -> FAIL", "description: X.\nname: Bad_Name", "my-skill", "kebab-case", None, None, False),
        ("when_to_use NOT renamed", "description: X.\nname: my-skill\nwhen_to_use: when asked", "my-skill",
         None, None, lambda fm: 'when_to_use' in fm, False),
        # --- name semantics (P0 #6/#15) ---
        ("plugin name with colon OK in CC mode", "description: X.\nname: my-plugin:fancy", "review",
         None, None, None, False),
        ("name != dirname -> no warning in CC mode", "description: X.\nname: fancy", "review",
         None, "!directory basename", None, False),
        ("plugin colon name -> FAIL in portable mode", "description: X.\nname: my-plugin:fancy", "my-plugin:fancy",
         "kebab-case", None, None, True),
        ("name != dirname -> FAIL in portable mode", "description: X.\nname: fancy", "review",
         "folder name", None, None, True),
        ("name 70 chars -> warn in CC mode", "description: X.\nname: " + "a" * 70, "a" * 70,
         None, "64", None, False),
        ("name 70 chars -> FAIL in portable mode", "description: X.\nname: " + "a" * 70, "a" * 70,
         "64 characters", None, None, True),
        # --- angle brackets are escaped by Claude Code, not rejected (P0 #16) ---
        ("angle brackets in description -> no error", "name: my-skill\ndescription: Convert CSV -> JSON when asked.",
         "my-skill", None, None, None, False),
        # --- portability allowlist (P0 #1) ---
        ("non-portable field -> warn in CC mode", "description: X.\nname: my-skill\nargument-hint: '[file]'",
         "my-skill", None, "won't upload", None, False),
        ("non-portable field -> FAIL in portable mode", "description: X.\nname: my-skill\nargument-hint: '[file]'",
         "my-skill", "Unexpected key(s)", None, None, True),
        ("six portable fields pass portable mode",
         "name: my-skill\ndescription: X.\nlicense: MIT\ncompatibility: claude-code\nmetadata:\n  team: core\n"
         "allowed-tools: Read Grep", "my-skill", None, None, None, True),
        # --- compatibility is current, capped at 500 (P0 #3) ---
        ("compatibility -> no deprecation warning", "description: X.\nname: my-skill\ncompatibility: claude>=2",
         "my-skill", None, "!deprecated", None, False),
        ("compatibility 600 -> warn", "description: X.\nname: my-skill\ncompatibility: " + "x" * 600, "my-skill",
         None, "500", None, False),
        # --- metadata must be a map (P1) ---
        ("metadata non-map -> warn", "description: X.\nname: my-skill\nmetadata: not-a-map", "my-skill",
         None, "YAML map", None, False),
        ("metadata reusing a field name -> warn", "description: X.\nname: my-skill\nmetadata:\n  paths: x",
         "my-skill", None, "reuses frontmatter field name", None, False),
        # --- a present-but-blank name is broken, not "fall back to dirname" (review #4) ---
        ("empty name -> FAIL in CC mode", "description: X.\nname: ''", "my-skill",
         "present but empty", None, None, False),
        ("whitespace name -> FAIL in portable mode", "description: X.\nname: '   '", "my-skill",
         "present but empty", None, None, True),
        # --- portable mode hardens the shared-field value checks (review #5) ---
        ("compatibility 600 -> FAIL in portable mode", "description: X.\nname: my-skill\ncompatibility: " + "x" * 600,
         "my-skill", "500", None, None, True),
        ("license non-string -> warn in CC mode", "description: X.\nname: my-skill\nlicense: 42", "my-skill",
         None, "license should be a string", None, False),
        ("license non-string -> FAIL in portable mode", "description: X.\nname: my-skill\nlicense: 42", "my-skill",
         "license should be a string", None, None, True),
        ("metadata non-map -> FAIL in portable mode", "description: X.\nname: my-skill\nmetadata: not-a-map",
         "my-skill", "YAML map", None, None, True),
        # --- portable mode doesn't re-report keys the allowlist already killed (review #9) ---
        ("bad context value -> only the allowlist error in portable mode",
         "description: X.\nname: my-skill\ncontext: forked", "my-skill",
         ["Unexpected key(s)", "!must be 'fork'"], None, None, True),
        ("agent without fork -> no 'context: fork' advice in portable mode",
         "description: X.\nname: my-skill\nagent: Explore", "my-skill",
         "Unexpected key(s)", "!context: fork", None, True),
        ("background without fork -> no warning in portable mode",
         "description: X.\nname: my-skill\nbackground: true", "my-skill",
         "Unexpected key(s)", "!only applies with", None, True),
        ("allowed-tools is portable -> type still checked in portable mode",
         "description: X.\nname: my-skill\nallowed-tools: 5", "my-skill",
         "allowed-tools must be a string or list", None, None, True),
    ]

    def _expectations(want):
        """Normalize a want_* cell into a list of substrings ('!' = must be absent)."""
        if want is None:
            return []
        return [want] if isinstance(want, str) else list(want)

    failures = 0
    for label, doc, dir_name, want_err, want_warn, extra, portable in fixtures:
        fm = load(doc)
        errors, warnings = validate_frontmatter(fm, dir_name=dir_name, portable=portable)
        problems = []
        for kind, wants, actual in (
            ("error", _expectations(want_err), errors),
            ("warning", _expectations(want_warn), warnings),
        ):
            # A leading '!' asserts the message must NOT be present.
            if kind == "error" and not any(not w.startswith('!') for w in wants) and actual:
                problems.append(f"unexpected errors: {actual}")
            for want in wants:
                if want.startswith('!'):
                    if any(want[1:] in a for a in actual):
                        problems.append(f"{kind} {want[1:]!r} should be gone, got: {actual}")
                elif not any(want in a for a in actual):
                    problems.append(f"expected {kind} containing {want!r}, got: {actual}")
        if want_warn is None and want_err is None and warnings and label == "happy path":
            problems.append(f"unexpected warnings: {warnings}")
        if extra is not None and not extra(fm):
            problems.append("extra check failed")
        status = "PASS" if not problems else "FAIL"
        print(f"{status}: {label}" + ("".join(f"\n      {p}" for p in problems)))
        failures += bool(problems)

    # Filesystem-level fixtures: things validate_frontmatter alone can't cover.
    file_cases = 0
    with tempfile.TemporaryDirectory() as tmp:
        # BOM-prefixed SKILL.md must still parse (Claude Code loads it fine, v2.1.239+).
        bom_dir = Path(tmp) / 'bom-skill'
        bom_dir.mkdir()
        (bom_dir / 'SKILL.md').write_text(
            "---\nname: bom-skill\ndescription: Does X when asked.\n---\n\nBody.\n",
            encoding='utf-8-sig',
        )
        for label, kwargs, want_valid in [
            ("BOM-prefixed SKILL.md parses", {}, True),
            ("BOM-prefixed SKILL.md passes portable mode", {"portable": True}, True),
        ]:
            file_cases += 1
            valid, message = validate_skill(bom_dir, **kwargs)
            ok = valid is want_valid
            print(f"{'PASS' if ok else 'FAIL'}: {label}" + ("" if ok else f"\n      got: {message}"))
            failures += not ok

        # The same BOM must not break scripts/utils.parse_skill_md, which run_eval,
        # run_loop and improve_description all go through (review #3): a validator
        # that says OK while the parser raises ValueError is the worst combination.
        file_cases += 1
        try:
            from scripts.utils import parse_skill_md
        except ImportError:
            print("SKIP: parse_skill_md handles a BOM (run with `python -m scripts.quick_validate`)")
            file_cases -= 1
        else:
            try:
                parsed_name, _, _, _ = parse_skill_md(bom_dir)
                ok = parsed_name == 'bom-skill'
                detail = f"name parsed as {parsed_name!r}"
            except Exception as exc:  # noqa: BLE001 — the point is that nothing raises
                ok, detail = False, f"raised {type(exc).__name__}: {exc}"
            print(f"{'PASS' if ok else 'FAIL'}: parse_skill_md handles a BOM"
                  + ("" if ok else f"\n      {detail}"))
            failures += not ok

        # A skill reached through a symlinked directory must be judged by the link's
        # own name, not the target's (review #8) — otherwise it can't be packaged.
        target_dir = Path(tmp) / 'real-target'
        target_dir.mkdir()
        (target_dir / 'SKILL.md').write_text(
            "---\nname: linked-skill\ndescription: Does X when asked.\n---\n\nBody.\n",
            encoding='utf-8',
        )
        link_dir = Path(tmp) / 'linked-skill'
        try:
            link_dir.symlink_to(target_dir, target_is_directory=True)
        except OSError:
            print("SKIP: symlinked skill dir keeps its own name (symlinks unavailable)")
        else:
            file_cases += 1
            valid, message = validate_skill(link_dir, portable=True)
            print(f"{'PASS' if valid else 'FAIL'}: symlinked skill dir keeps its own name"
                  + ("" if valid else f"\n      got: {message}"))
            failures += not valid

        # A non-portable field must block packaging (package_skill.py's gate).
        np_dir = Path(tmp) / 'np-skill'
        np_dir.mkdir()
        (np_dir / 'SKILL.md').write_text(
            "---\nname: np-skill\ndescription: Does X.\nargument-hint: '[file]'\n---\n\nBody.\n",
            encoding='utf-8',
        )
        for label, kwargs, want_valid in [
            ("non-portable skill is valid in CC mode", {}, True),
            ("non-portable skill fails portable mode", {"portable": True}, False),
        ]:
            file_cases += 1
            valid, message = validate_skill(np_dir, **kwargs)
            ok = valid is want_valid
            print(f"{'PASS' if ok else 'FAIL'}: {label}" + ("" if ok else f"\n      got: {message}"))
            failures += not ok

    # improve_description must refuse a when_to_use that leaves no room for a
    # description, instead of chasing a negative budget through claude calls (review #6).
    try:
        from scripts.improve_description import improve_description
    except (ImportError, TypeError):
        # ImportError: run as a plain script, no package context.
        # TypeError: interpreter older than 3.10 — improve_description's `str | None`
        # annotations are evaluated at import, so the module can't load at all there.
        print("SKIP: improve_description floors the description budget "
              "(needs `python -m scripts.quick_validate` on Python 3.10+)")
    else:
        file_cases += 1
        try:
            improve_description(
                skill_name="x", skill_content="", current_description="d",
                eval_results={"results": [], "summary": {"passed": 0, "total": 0}},
                history=[], model="haiku", when_to_use="w" * 1500,
            )
            ok, detail = False, "no exception raised — it would have called claude"
        except ValueError as exc:
            ok = "shorten when_to_use" in str(exc).lower()
            detail = f"ValueError text lacks the 'shorten when_to_use' hint: {exc}"
        except Exception as exc:  # noqa: BLE001
            ok, detail = False, f"raised {type(exc).__name__} instead of ValueError: {exc}"
        print("PASS: improve_description floors the description budget" if ok else
              f"FAIL: improve_description floors the description budget\n      {detail}")
        failures += not ok

    total = len(fixtures) + file_cases
    print(f"\n{total - failures}/{total} fixtures passed")
    return failures


def main():
    parser = argparse.ArgumentParser(
        prog="python -m scripts.quick_validate",
        description="Validate a skill's SKILL.md frontmatter (authoring guardrail; "
                    "`claude plugin validate` is the canon).",
        epilog="--self-test ignores --portable: every fixture carries its own mode.",
    )
    parser.add_argument("skill_directory", nargs="?", help="Path to the skill directory")
    parser.add_argument("--portable", action="store_true",
                        help="Validate against the Agent Skills spec's six fields "
                             "(what claude.ai uploads / the Skills API / packaging enforce)")
    parser.add_argument("--self-test", action="store_true",
                        help="Run the built-in fixture suite instead of validating a directory")
    args = parser.parse_args()

    if args.self_test:
        if args.skill_directory:
            parser.error("--self-test takes no skill directory")
        sys.exit(1 if _self_test() else 0)

    if not args.skill_directory:
        parser.error("a skill directory is required (or use --self-test)")

    valid, message = validate_skill(args.skill_directory, portable=args.portable)
    print(message)
    sys.exit(0 if valid else 1)


if __name__ == "__main__":
    main()
