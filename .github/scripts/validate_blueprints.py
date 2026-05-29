#!/usr/bin/env python3
"""Validate Home Assistant blueprint YAML files for structure and consistency."""

import sys
import yaml
from pathlib import Path

VALID_DOMAINS = {"automation", "script", "button"}


class BlueprintLoader(yaml.SafeLoader):
    """YAML loader that handles HA-specific tags like !input."""


def _handle_input_tag(loader, node):
    """Convert !input foo to a sentinel string so we can track references."""
    return f"__input__{loader.construct_scalar(node)}"


BlueprintLoader.add_constructor("!input", _handle_input_tag)


def find_input_refs(data) -> set:
    """Recursively find all !input references in parsed data."""
    refs = set()
    if isinstance(data, str) and data.startswith("__input__"):
        refs.add(data[len("__input__"):])
    elif isinstance(data, dict):
        for v in data.values():
            refs |= find_input_refs(v)
    elif isinstance(data, list):
        for item in data:
            refs |= find_input_refs(item)
    return refs


def validate_blueprint(path: Path) -> list:
    errors = []

    try:
        with open(path, "r", encoding="utf-8") as f:
            data = yaml.load(f, Loader=BlueprintLoader)
    except yaml.YAMLError as e:
        return [f"YAML parse error: {e}"]

    if not isinstance(data, dict):
        errors.append("Root element is not a mapping")
        return errors

    # blueprint key required
    if "blueprint" not in data:
        errors.append("Missing required key: 'blueprint'")
        return errors

    bp = data["blueprint"]

    if not isinstance(bp, dict):
        errors.append("'blueprint' must be a mapping")
        return errors

    # Required metadata fields
    if "name" not in bp:
        errors.append("Missing required field: blueprint.name")

    if "domain" not in bp:
        errors.append("Missing required field: blueprint.domain")
    elif bp["domain"] not in VALID_DOMAINS:
        errors.append(
            f"Invalid domain '{bp['domain']}'. Must be one of: {', '.join(sorted(VALID_DOMAINS))}"
        )

    domain = bp.get("domain")

    # Automation-specific required keys
    if domain == "automation":
        if "trigger" not in data and "triggers" not in data:
            errors.append("Automation blueprint missing 'trigger' / 'triggers'")
        if "action" not in data and "actions" not in data:
            errors.append("Automation blueprint missing 'action' / 'actions'")

    # Check !input reference consistency
    declared = set(bp["input"].keys()) if isinstance(bp.get("input"), dict) else set()
    used = find_input_refs(data)
    undefined = used - declared

    if undefined:
        errors.append(f"Undefined !input references: {', '.join(sorted(undefined))}")

    return errors


def main():
    files = sorted(
        f for f in Path(".").rglob("*.yaml")
        if ".github" not in f.parts
    )

    if not files:
        print("No blueprint YAML files found.")
        sys.exit(0)

    failed = False
    for path in files:
        errs = validate_blueprint(path)
        if errs:
            print(f"FAIL  {path}")
            for e in errs:
                print(f"      - {e}")
            failed = True
        else:
            print(f"OK    {path}")

    if failed:
        print("\nValidation failed.")
        sys.exit(1)

    print(f"\nAll {len(files)} blueprint(s) valid.")


if __name__ == "__main__":
    main()
