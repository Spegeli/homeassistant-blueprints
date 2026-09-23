#!/usr/bin/env python3
"""Validate the Home Assistant blueprints in this repository.

Mirrors the checks Home Assistant runs when it imports a blueprint
(homeassistant/components/blueprint/schemas.py) and adds the repository
conventions from CONTRIBUTING.md. Errors fail the run, warnings do not.

Usage (from any directory):
    python .github/scripts/validate_blueprints.py
"""

import os
import re
import sys
from pathlib import Path

import yaml

VALID_DOMAINS = {"automation", "script", "template"}
BLUEPRINT_KEYS = {"name", "description", "domain", "source_url", "author", "homeassistant", "input"}
INPUT_KEYS = {"name", "description", "default", "selector"}
SECTION_KEYS = {"name", "icon", "description", "collapsed", "input"}
SECTIONS_MIN_VERSION = (2024, 6, 0)

VERSION_LINE = re.compile(r"\*\*Version\*\*: \d+\.\d+")
ISSUES_FOOTER = [
    "Found a bug or have a suggestion? Open an issue on GitHub:",
    "https://github.com/Spegeli/homeassistant-blueprints/issues",
]

IN_CI = os.environ.get("GITHUB_ACTIONS") == "true"


class BlueprintLoader(yaml.SafeLoader):
    """SafeLoader that understands the Home Assistant !input tag."""


class InputRef(str):
    """Input name referenced with !input."""


BlueprintLoader.add_constructor(
    "!input", lambda loader, node: InputRef(loader.construct_scalar(node))
)


def names(items) -> str:
    return ", ".join(sorted(map(str, items)))


def find_input_refs(data) -> set:
    """Recursively collect all !input references."""
    if isinstance(data, InputRef):
        return {str(data)}
    if isinstance(data, dict):
        return set().union(*(find_input_refs(value) for value in data.values()))
    if isinstance(data, list):
        return set().union(*(find_input_refs(item) for item in data))
    return set()


def find_duplicate_keys(node) -> list:
    """Report keys that appear twice in one mapping (YAML silently keeps the last one)."""
    errors = []
    if isinstance(node, yaml.MappingNode):
        seen = set()
        for key_node, value_node in node.value:
            if isinstance(key_node, yaml.ScalarNode):
                if key_node.value in seen:
                    errors.append(f"Duplicate key '{key_node.value}' (line {key_node.start_mark.line + 1})")
                seen.add(key_node.value)
            errors += find_duplicate_keys(value_node)
    elif isinstance(node, yaml.SequenceNode):
        for item in node.value:
            errors += find_duplicate_keys(item)
    return errors


def parse_version(value):
    """Return (major, minor, patch) for a Home Assistant version string, else None."""
    if not isinstance(value, str):
        return None
    parts = value.split(".")
    if len(parts) != 3 or not all(part.isdigit() for part in parts):
        return None
    return tuple(int(part) for part in parts)


def check_metadata(bp: dict, errors: list):
    """Check blueprint metadata; return the parsed min_version or None."""
    unknown = set(bp) - BLUEPRINT_KEYS
    if unknown:
        errors.append(f"Unknown key(s) under blueprint: {names(unknown)}")

    if not isinstance(bp.get("name"), str):
        errors.append("blueprint.name is missing or not a string")

    if bp.get("domain") not in VALID_DOMAINS:
        errors.append(f"blueprint.domain must be one of {names(VALID_DOMAINS)}, got {bp.get('domain')!r}")

    if "author" in bp and not isinstance(bp["author"], str):
        errors.append("blueprint.author must be a string")

    source_url = bp.get("source_url")
    if source_url is not None and not (isinstance(source_url, str) and source_url.startswith(("http://", "https://"))):
        errors.append("blueprint.source_url must be an http(s) URL")

    description = bp.get("description")
    if not isinstance(description, str) or not description.strip():
        errors.append("blueprint.description is missing or not a string")
    else:
        lines = [line.strip() for line in description.strip().splitlines()]
        if not VERSION_LINE.fullmatch(lines[0]):
            errors.append("blueprint.description must start with '**Version**: X.Y'")
        if lines[-2:] != ISSUES_FOOTER:
            errors.append("blueprint.description must end with the GitHub issues footer (see CONTRIBUTING.md)")

    min_version = None
    ha = bp.get("homeassistant")
    if ha is not None:
        if not isinstance(ha, dict) or set(ha) - {"min_version"}:
            errors.append("blueprint.homeassistant only supports 'min_version'")
        elif "min_version" in ha:
            min_version = parse_version(ha["min_version"])
            if min_version is None:
                errors.append("blueprint.homeassistant.min_version must be a quoted string like '2024.6.0'")
    return min_version


def add_input(name, config, where: str, declared: dict, errors: list) -> None:
    """Register one input and check its keys."""
    if name in declared:
        errors.append(f"Duplicate input '{name}' (input names must be unique across sections)")
    declared[name] = config
    if config is None:
        return
    if not isinstance(config, dict):
        errors.append(f"{where} must be a mapping")
        return
    unknown = set(config) - INPUT_KEYS
    if unknown:
        errors.append(f"{where}: unknown key(s) {names(unknown)} (allowed: {names(INPUT_KEYS)})")
    for key in ("name", "description"):
        if key in config and not isinstance(config[key], str):
            errors.append(f"{where}: '{key}' must be a string")


def check_section(key, section: dict, declared: dict, errors: list, warnings: list) -> None:
    """Check an input section and register its inputs."""
    where = f"section '{key}'"
    unknown = set(section) - SECTION_KEYS
    if unknown:
        errors.append(f"{where}: unknown key(s) {names(unknown)} (allowed: {names(SECTION_KEYS)})")
    for field in ("name", "icon", "description"):
        if field in section and not isinstance(section[field], str):
            errors.append(f"{where}: '{field}' must be a string")
    if "collapsed" in section and not isinstance(section["collapsed"], bool):
        errors.append(f"{where}: 'collapsed' must be true or false")

    inner = section["input"]
    if not isinstance(inner, dict):
        errors.append(f"{where}: 'input' must be a mapping of inputs")
        return

    without_default = []
    for name, config in inner.items():
        if isinstance(config, dict) and "input" in config:
            errors.append(f"{where}: nested section '{name}' is not supported")
            continue
        add_input(name, config, f"input '{name}' in {where}", declared, errors)
        if not (isinstance(config, dict) and "default" in config):
            without_default.append(name)

    if section.get("collapsed") is True and without_default:
        warnings.append(
            f"{where} has collapsed: true, but input(s) without default ({names(without_default)}) "
            "keep it expanded in Home Assistant"
        )


def check_inputs(bp: dict, errors: list, warnings: list):
    """Check blueprint.input; return (declared inputs, whether sections are used)."""
    raw = bp.get("input", {})
    if not isinstance(raw, dict):
        errors.append("blueprint.input must be a mapping")
        return {}, False

    declared = {}
    uses_sections = False
    for key, value in raw.items():
        if isinstance(value, dict) and "input" in value:
            uses_sections = True
            check_section(key, value, declared, errors, warnings)
        elif isinstance(value, dict) and value and set(value) <= SECTION_KEYS and not set(value) <= INPUT_KEYS:
            warnings.append(f"'{key}' looks like a section without an 'input' key, Home Assistant shows it empty")
        else:
            add_input(key, value, f"input '{key}'", declared, errors)
    return declared, uses_sections


def validate_blueprint(path: Path):
    """Validate one blueprint file; return (errors, warnings)."""
    errors, warnings = [], []
    text = path.read_text(encoding="utf-8")
    try:
        errors += find_duplicate_keys(yaml.compose(text, Loader=BlueprintLoader))
        data = yaml.load(text, Loader=BlueprintLoader)
    except yaml.YAMLError as err:
        return [f"YAML parse error: {err}"], []

    if not isinstance(data, dict) or not isinstance(data.get("blueprint"), dict):
        errors.append("Missing 'blueprint' mapping at the top level")
        return errors, warnings

    bp = data["blueprint"]
    min_version = check_metadata(bp, errors)
    declared, uses_sections = check_inputs(bp, errors, warnings)

    domain = bp.get("domain")
    if domain == "automation":
        if not {"trigger", "triggers"} & data.keys():
            errors.append("Automation blueprint needs 'triggers' (or legacy 'trigger')")
        if not {"action", "actions"} & data.keys():
            errors.append("Automation blueprint needs 'actions' (or legacy 'action')")
    elif domain == "script" and "sequence" not in data:
        errors.append("Script blueprint needs 'sequence'")

    used = find_input_refs({key: value for key, value in data.items() if key != "blueprint"})
    undeclared = used - set(declared)
    if undeclared:
        errors.append(f"!input used but not declared: {names(undeclared)}")
    unused = set(declared) - used
    if unused:
        warnings.append(f"Input(s) declared but never used: {names(unused)}")

    if uses_sections and (min_version is None or min_version < SECTIONS_MIN_VERSION):
        warnings.append(
            "Input sections need Home Assistant 2024.6.0 or newer, "
            "set min_version: 2024.6.0 under blueprint.homeassistant"
        )

    return errors, warnings


def emit(level: str, rel: str, message: str) -> None:
    if IN_CI:
        print(f"::{level} file={rel}::{message}")
    else:
        print(f"      {level}: {message}")


def is_blueprint_path(path: Path, root: Path) -> bool:
    """Skip hidden folders such as .github, .git and .claude."""
    return not any(part.startswith(".") for part in path.relative_to(root).parts)


def main() -> int:
    root = Path(__file__).resolve().parents[2]
    files = sorted(p for p in root.rglob("*.yaml") if is_blueprint_path(p, root))
    wrong_suffix = sorted(p for p in root.rglob("*.yml") if is_blueprint_path(p, root))

    failed = False
    warning_count = 0

    for path in wrong_suffix:
        rel = path.relative_to(root).as_posix()
        print(f"FAIL  {rel}")
        emit("error", rel, "Blueprint files must end in .yaml, Home Assistant does not load .yml")
        failed = True

    for path in files:
        rel = path.relative_to(root).as_posix()
        errors, warnings = validate_blueprint(path)
        print(f"{'FAIL' if errors else 'WARN' if warnings else 'OK':5} {rel}")
        for message in errors:
            emit("error", rel, message)
        for message in warnings:
            emit("warning", rel, message)
        failed = failed or bool(errors)
        warning_count += len(warnings)

    if not files and not wrong_suffix:
        print("No blueprint files found.")
        return 0

    print()
    if failed:
        print("Validation failed.")
        return 1
    print(f"All {len(files)} blueprint(s) valid, {warning_count} warning(s).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
