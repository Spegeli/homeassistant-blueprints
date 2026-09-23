# Contributing

Thanks for wanting to help! This repository is small, so these guidelines are too.

## Scope first

This repository contains **Home Assistant blueprints**: YAML templates that you import into Home Assistant and turn into automations.

Problems with Home Assistant itself or with a device integration (for example a dehumidifier that does not react to `humidifier.turn_on`) belong in the respective project. For general questions about automations and blueprints, the [Home Assistant Community](https://community.home-assistant.io/) is the better place.

## Issues

- Use the issue forms (**Bug report** / **Feature request**).
- For bugs, include the blueprint and its version, your Home Assistant version, the automation configuration (automation editor → **⋮ → Edit in YAML**) and, if possible, the **trace** of a run that went wrong (automation editor → **⋮ → Traces → ⋮ → Download trace**).

## Pull requests

**One blueprint per file.** Put it in the matching category folder (`climate/`, `lighting/`, `presence/`, `security/`, `energy/`, `notifications/`). File names are `snake_case` with the `.yaml` extension; Home Assistant only loads blueprints ending in `.yaml`.

**English only.** Name, description, input names and descriptions, and comments are written in English.

**Description format.** Every blueprint description has the same structure:

```yaml
description: |
  **Version**: 1.0

  One or two sentences on what the blueprint does.

  - Feature 1
  - Feature 2

  Found a bug or have a suggestion? Open an issue on GitHub:
  https://github.com/Spegeli/homeassistant-blueprints/issues
```

**Versioning.** Bump the version with every change to a blueprint:
- minor (`2.6` → `2.7`) for fixes, behaviour changes and new optional inputs,
- major (`2.6` → `3.0`) when existing automations have to be reconfigured, for example because an input was renamed or removed.

**Input keys are public.** Existing automations reference inputs by their key. Rename or remove an input only if there is no other way, and point it out in the PR description.

**Input sections** need Home Assistant 2024.6 or newer, so set `min_version: 2024.6.0` under `homeassistant:` in the blueprint metadata when you use them. A section with `collapsed: true` only collapses if every input in it has a `default`.

**New blueprints** also need:
- a section in `README.md` under the matching category, with a short description, the feature list and an import badge,
- an entry in the blueprint dropdown of both issue forms (`.github/ISSUE_TEMPLATE/bug_report.yml` and `feature_request.yml`).

**PR description:** what changed, why, and how you tested it in Home Assistant.

## Validating locally

You need Python 3 with PyYAML:

```bash
pip install pyyaml
python .github/scripts/validate_blueprints.py
```

The script runs the checks Home Assistant applies when it imports a blueprint, plus the conventions above. Errors fail the check, warnings do not. The GitHub workflow also runs `yamllint`:

```bash
pip install yamllint
yamllint -d "{extends: relaxed, ignore: '.github/', rules: {line-length: {max: 200}}}" .
```

## After merging

Changes on `main` are live right away, because the import badges point to `main`. Users who already imported a blueprint get the update via **Settings → Automations & scenes → Blueprints → ⋮ → Re-import blueprint**.

## Code of Conduct and license

Please follow the [Code of Conduct](CODE_OF_CONDUCT.md). Contributions are licensed under the repository's [MIT License](LICENSE).
