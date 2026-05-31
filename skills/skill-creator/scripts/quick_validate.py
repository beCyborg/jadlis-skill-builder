#!/usr/bin/env python3
"""
Quick validation script for skills - minimal version
"""

import sys
import os
import re
import yaml
from pathlib import Path

def validate_skill(skill_path):
    """Basic validation of a skill"""
    skill_path = Path(skill_path)

    # Check SKILL.md exists
    skill_md = skill_path / 'SKILL.md'
    if not skill_md.exists():
        return False, "SKILL.md not found"

    # Read and validate frontmatter
    content = skill_md.read_text()
    if not content.startswith('---'):
        return False, "No YAML frontmatter found"

    # Extract frontmatter
    match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
    if not match:
        return False, "Invalid frontmatter format"

    frontmatter_text = match.group(1)

    # Parse YAML frontmatter
    try:
        frontmatter = yaml.safe_load(frontmatter_text)
        if not isinstance(frontmatter, dict):
            return False, "Frontmatter must be a YAML dictionary"
    except yaml.YAMLError as e:
        return False, f"Invalid YAML in frontmatter: {e}"

    # Define allowed properties
    ALLOWED_PROPERTIES = {
        'name', 'description', 'when_to_use', 'license', 'allowed-tools', 'disallowed-tools',
        'metadata', 'argument-hint', 'arguments', 'effort', 'context', 'agent', 'hooks',
        'model', 'disable-model-invocation', 'user-invocable',
        'paths', 'shell', 'compatibility',
    }

    # Check for unexpected properties (excluding nested keys under metadata)
    unexpected_keys = set(frontmatter.keys()) - ALLOWED_PROPERTIES
    if unexpected_keys:
        return False, (
            f"Unexpected key(s) in SKILL.md frontmatter: {', '.join(sorted(unexpected_keys))}. "
            f"Allowed properties are: {', '.join(sorted(ALLOWED_PROPERTIES))}"
        )

    # Check required fields
    if 'name' not in frontmatter:
        return False, "Missing 'name' in frontmatter"
    if 'description' not in frontmatter:
        return False, "Missing 'description' in frontmatter"

    # Extract name for validation
    name = frontmatter.get('name', '')
    if not isinstance(name, str):
        return False, f"Name must be a string, got {type(name).__name__}"
    name = name.strip()
    if name:
        # Check naming convention (kebab-case: lowercase with hyphens)
        if not re.match(r'^[a-z0-9-]+$', name):
            return False, f"Name '{name}' should be kebab-case (lowercase letters, digits, and hyphens only)"
        if name.startswith('-') or name.endswith('-') or '--' in name:
            return False, f"Name '{name}' cannot start/end with hyphen or contain consecutive hyphens"
        # Check name length (max 64 characters per spec)
        if len(name) > 64:
            return False, f"Name is too long ({len(name)} characters). Maximum is 64 characters."

    # Extract and validate description
    description = frontmatter.get('description', '')
    if not isinstance(description, str):
        return False, f"Description must be a string, got {type(description).__name__}"
    description = description.strip()
    if description:
        # Check for angle brackets
        if '<' in description or '>' in description:
            return False, "Description cannot contain angle brackets (< or >)"

    # Validate combined description + when_to_use length (max 1536 characters per spec)
    when_to_use = frontmatter.get('when_to_use', '')
    if not isinstance(when_to_use, str):
        when_to_use = str(when_to_use) if when_to_use is not None else ''
    when_to_use = when_to_use.strip()
    if description and when_to_use:
        combined = description + " " + when_to_use
    else:
        combined = description + when_to_use
    if len(combined) > 1536:
        return False, f"Combined description + when_to_use is too long ({len(combined)} characters). Maximum is 1,536 characters."

    # Deprecation warning for compatibility field
    compatibility = frontmatter.get('compatibility')
    if compatibility is not None:
        print("WARNING: 'compatibility' field is deprecated and may not be recognized by current Claude Code versions.")

    # Validate argument-hint if present
    argument_hint = frontmatter.get('argument-hint')
    if argument_hint is not None:
        if not isinstance(argument_hint, str):
            return False, f"argument-hint must be a string, got {type(argument_hint).__name__}"
        # The spec defines no hard length limit; a very long hint just won't render well.
        if len(argument_hint) > 128:
            print(f"WARNING: argument-hint is {len(argument_hint)} characters; long hints may be clipped in the autocomplete box. Consider shortening it.")

    # Validate arguments if present
    arguments = frontmatter.get('arguments')
    if arguments is not None:
        if isinstance(arguments, list):
            for item in arguments:
                if not isinstance(item, str):
                    return False, f"arguments list items must be strings, got {type(item).__name__}"
        elif not isinstance(arguments, str):
            return False, f"arguments must be a string or list, got {type(arguments).__name__}"

    # Validate disallowed-tools if present (string or list, like allowed-tools)
    disallowed_tools = frontmatter.get('disallowed-tools')
    if disallowed_tools is not None:
        if isinstance(disallowed_tools, list):
            for item in disallowed_tools:
                if not isinstance(item, str):
                    return False, f"disallowed-tools list items must be strings, got {type(item).__name__}"
        elif not isinstance(disallowed_tools, str):
            return False, f"disallowed-tools must be a string or list, got {type(disallowed_tools).__name__}"

    # Validate effort if present
    effort = frontmatter.get('effort')
    if effort is not None:
        valid_efforts = {'low', 'medium', 'high', 'xhigh', 'max'}
        if effort not in valid_efforts:
            return False, f"effort must be one of {', '.join(sorted(valid_efforts))}, got '{effort}'"

    # Validate context if present
    context_val = frontmatter.get('context')
    if context_val is not None:
        if context_val != 'fork':
            return False, f"context must be 'fork' if present, got '{context_val}'"

    # Validate agent if present
    agent = frontmatter.get('agent')
    if agent is not None:
        if not isinstance(agent, str):
            return False, f"agent must be a string, got {type(agent).__name__}"
        if context_val != 'fork':
            print("WARNING: 'agent' is set but 'context' is not 'fork'. The agent field typically requires context: fork.")

    # Validate paths if present
    paths = frontmatter.get('paths')
    if paths is not None:
        if not isinstance(paths, (str, list)):
            return False, f"paths must be a string or list, got {type(paths).__name__}"
        if isinstance(paths, list):
            for item in paths:
                if not isinstance(item, str):
                    return False, f"paths list items must be strings, got {type(item).__name__}"

    # Validate shell if present
    shell = frontmatter.get('shell')
    if shell is not None:
        valid_shells = {'bash', 'powershell'}
        if shell not in valid_shells:
            return False, f"shell must be one of {', '.join(sorted(valid_shells))}, got '{shell}'"

    # Validate hooks if present
    hooks = frontmatter.get('hooks')
    if hooks is not None:
        if not isinstance(hooks, dict):
            return False, f"hooks must be a dictionary, got {type(hooks).__name__}"

    # Validate model if present
    model = frontmatter.get('model')
    if model is not None:
        if not isinstance(model, str):
            return False, f"model must be a string, got {type(model).__name__}"

    # Validate disable-model-invocation if present
    disable_model = frontmatter.get('disable-model-invocation')
    if disable_model is not None:
        if not isinstance(disable_model, bool):
            return False, f"disable-model-invocation must be a boolean, got {type(disable_model).__name__}"

    # Validate user-invocable if present
    user_invocable = frontmatter.get('user-invocable')
    if user_invocable is not None:
        if not isinstance(user_invocable, bool):
            return False, f"user-invocable must be a boolean, got {type(user_invocable).__name__}"

    return True, "Skill is valid!"

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python quick_validate.py <skill_directory>")
        sys.exit(1)
    
    valid, message = validate_skill(sys.argv[1])
    print(message)
    sys.exit(0 if valid else 1)