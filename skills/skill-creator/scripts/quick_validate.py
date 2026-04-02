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
        'name', 'description', 'license', 'allowed-tools', 'metadata',
        'argument-hint', 'effort', 'context', 'agent', 'hooks',
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
        # Check description length (max 1024 characters per spec)
        if len(description) > 1024:
            return False, f"Description is too long ({len(description)} characters). Maximum is 1024 characters."
        # Warn if description exceeds the 250-char display truncation limit
        if len(description) > 250:
            print(f"WARNING: Description is {len(description)} characters. It will be truncated at 250 characters in the skill listing. Front-load key trigger words.")

    # Deprecation warning for compatibility field
    compatibility = frontmatter.get('compatibility')
    if compatibility is not None:
        print("WARNING: 'compatibility' field is deprecated and may not be recognized by current Claude Code versions.")

    # Validate argument-hint if present
    argument_hint = frontmatter.get('argument-hint')
    if argument_hint is not None:
        if not isinstance(argument_hint, str):
            return False, f"argument-hint must be a string, got {type(argument_hint).__name__}"
        if len(argument_hint) > 128:
            return False, f"argument-hint is too long ({len(argument_hint)} characters). Maximum is 128 characters."

    # Validate effort if present
    effort = frontmatter.get('effort')
    if effort is not None:
        valid_efforts = {'low', 'medium', 'high', 'max'}
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