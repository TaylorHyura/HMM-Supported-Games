#!/usr/bin/env python3
"""Validate the HMM supported-games catalog.

The script checks both catalog lists for JSON errors, schema mistakes, duplicate
IDs, unsafe paths, and links that would not work in the app. It never downloads
anything, so it is safe to run on pull requests from forks.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_LISTS = [
    ROOT / "lists" / "main_list.json",
    ROOT / "lists" / "community_list.json",
]

ENGINES = {"UnrealEngine", "REEngine", "MTFramework", "RenderWare"}
SOURCES = {"Nexus"}
MOD_DIRECTORY_TYPES = {"pak", "logicpak", "lua", "hook"}

GAME_KEYS = {"ID", "Name", "Engine", "CoverURL", "ModDirectories", "Dependencies", "Source"}
MOD_DIRECTORY_KEYS = {"Type", "Directory"}
DEPENDENCY_KEYS = {
    "Id",
    "ID",
    "Name",
    "Variant",
    "Description",
    "Author",
    "CoverURL",
    "WebPage",
    "Link",
    "Files",
    "Folders",
    "Config",
}
FILE_KEYS = {"Source", "Destination"}
CONFIG_KEYS = {"Name", "Type", "Content"}

ID_RE = re.compile(r"^[a-z0-9][a-z0-9_-]{0,99}$")
INVALID_PATH_CHARS = set('<>:"|?*')


class Report:
    def __init__(self) -> None:
        self.errors: list[str] = []
        self.warnings: list[str] = []

    def error(self, message: str) -> None:
        self.errors.append(message)

    def warning(self, message: str) -> None:
        self.warnings.append(message)


def display_path(path: Path) -> str:
    try:
        return path.resolve().relative_to(ROOT).as_posix()
    except ValueError:
        return str(path)


def load_list(path: Path, report: Report) -> list[Any] | None:
    label = display_path(path)

    if not path.is_file():
        report.error(f"{label}: file not found")
        return None

    try:
        text = path.read_text(encoding="utf-8-sig")
    except OSError as exc:
        report.error(f"{label}: cannot read file: {exc}")
        return None

    try:
        data = json.loads(text)
    except json.JSONDecodeError as exc:
        report.error(f"{label}: invalid JSON at line {exc.lineno}, column {exc.colno}: {exc.msg}")
        return None

    if not isinstance(data, list):
        report.error(f"{label}: the top level must be a JSON array")
        return None

    return data


def check_keys(
    value: dict[str, Any],
    allowed: set[str],
    label: str,
    report: Report,
    *,
    ignore: set[str] | None = None,
) -> None:
    ignored = ignore or set()
    unknown = sorted(set(value) - allowed - ignored)
    if unknown:
        report.error(f"{label}: unknown key(s): {', '.join(unknown)}")


def require_string(
    value: dict[str, Any],
    key: str,
    label: str,
    report: Report,
    *,
    required: bool = True,
    allow_empty: bool = False,
) -> str | None:
    if key not in value:
        if required:
            report.error(f"{label}: missing required key '{key}'")
        return None

    item = value[key]

    if not isinstance(item, str):
        report.error(f"{label}: '{key}' must be a string")
        return None

    if not allow_empty and not item.strip():
        report.error(f"{label}: '{key}' must not be empty")
        return None

    if not allow_empty and item != item.strip():
        report.error(f"{label}: '{key}' must not have leading or trailing whitespace")
        return None

    return item


def check_url(value: str, label: str, key: str, report: Report) -> None:
    parsed = urlparse(value)

    if parsed.scheme != "https":
        report.error(f"{label}: '{key}' must use https")
        return

    if not parsed.netloc:
        report.error(f"{label}: '{key}' must be an absolute URL")
        return

    if any(char.isspace() for char in value):
        report.error(f"{label}: '{key}' must not contain whitespace")


def check_relative_path(value: str, label: str, key: str, report: Report) -> None:
    if value.startswith(("\\", "/")):
        report.error(f"{label}: '{key}' must be relative to the game root, without a leading slash")
        return

    if re.match(r"^[A-Za-z]:", value):
        report.error(f"{label}: '{key}' must not include a drive letter")
        return

    if "/" in value:
        report.error(f"{label}: '{key}' must use backslashes, not forward slashes")
        return

    if value.endswith("\\"):
        report.error(f"{label}: '{key}' must not end with a backslash")
        return

    parts = value.split("\\")

    if any(part in {"", ".", ".."} for part in parts):
        report.error(f"{label}: '{key}' must not contain empty, '.' or '..' path segments")
        return

    if any(part != part.strip() or part.endswith(".") for part in parts):
        report.error(f"{label}: '{key}' has a path segment with a trailing space or dot")
        return

    invalid = sorted(INVALID_PATH_CHARS.intersection(value))
    if invalid:
        report.error(f"{label}: '{key}' contains invalid path character(s): {', '.join(invalid)}")
        return

    if any(ord(char) < 32 for char in value):
        report.error(f"{label}: '{key}' contains control characters")


def validate_mod_directories(
    game: dict[str, Any],
    label: str,
    report: Report,
) -> set[str]:
    directories = game.get("ModDirectories")
    found_types: set[str] = set()

    if directories is None:
        directories = []
    elif not isinstance(directories, list):
        report.error(f"{label}: 'ModDirectories' must be an array")
        return found_types

    for index, directory in enumerate(directories):
        item_label = f"{label}.ModDirectories[{index}]"

        if not isinstance(directory, dict):
            report.error(f"{item_label}: must be an object")
            continue

        check_keys(directory, MOD_DIRECTORY_KEYS, item_label, report)

        directory_type = require_string(directory, "Type", item_label, report)
        path = require_string(directory, "Directory", item_label, report)

        if directory_type is not None:
            if directory_type not in MOD_DIRECTORY_TYPES:
                report.error(
                    f"{item_label}: 'Type' must be one of {', '.join(sorted(MOD_DIRECTORY_TYPES))}"
                )
            elif directory_type in found_types:
                report.error(f"{item_label}: duplicate ModDirectories type '{directory_type}'")
            else:
                found_types.add(directory_type)

        if path is not None:
            check_relative_path(path, item_label, "Directory", report)

    if game.get("Engine") == "UnrealEngine" and "pak" not in found_types:
        report.error(f"{label}: UnrealEngine entries must include a 'pak' ModDirectory")

    return found_types


def validate_file_paths(
    value: Any,
    key: str,
    label: str,
    report: Report,
) -> int:
    if not isinstance(value, list):
        report.error(f"{label}: '{key}' must be an array")
        return 0

    for index, item in enumerate(value):
        item_label = f"{label}.{key}[{index}]"

        if not isinstance(item, dict):
            report.error(f"{item_label}: must be an object")
            continue

        check_keys(item, FILE_KEYS, item_label, report)

        source = require_string(item, "Source", item_label, report)
        destination = require_string(item, "Destination", item_label, report)

        if source is not None:
            check_relative_path(source, item_label, "Source", report)
        if destination is not None:
            check_relative_path(destination, item_label, "Destination", report)

    return len(value)


def validate_dependencies(
    game: dict[str, Any],
    label: str,
    report: Report,
    warnings: Report,
) -> None:
    dependencies = game.get("Dependencies")

    if dependencies is None:
        return

    if not isinstance(dependencies, list):
        report.error(f"{label}: 'Dependencies' must be an array")
        return

    seen_ids: dict[str, int] = {}

    for index, dependency in enumerate(dependencies):
        item_label = f"{label}.Dependencies[{index}]"

        if not isinstance(dependency, dict):
            report.error(f"{item_label}: must be an object")
            continue

        check_keys(dependency, DEPENDENCY_KEYS, item_label, report)

        if "Id" in dependency and "ID" in dependency:
            report.error(f"{item_label}: use either 'Id' or 'ID', not both")

        if "Id" in dependency or "ID" in dependency:
            dependency_id = require_string(
                dependency,
                "Id" if "Id" in dependency else "ID",
                item_label,
                report,
            )
        else:
            dependency_id = None
            report.error(f"{item_label}: missing required key 'Id'")

        if dependency_id is not None:
            key = dependency_id.casefold()
            if key in seen_ids:
                report.error(
                    f"{item_label}: duplicate dependency Id '{dependency_id}' "
                    f"(also used at index {seen_ids[key]})"
                )
            else:
                seen_ids[key] = index

        require_string(dependency, "Name", item_label, report)
        require_string(dependency, "Variant", item_label, report)

        if "Description" not in dependency:
            warnings.warning(f"{item_label}: 'Description' is recommended")
        else:
            require_string(dependency, "Description", item_label, report)

        if "Author" not in dependency:
            warnings.warning(f"{item_label}: 'Author' is recommended")
        else:
            require_string(dependency, "Author", item_label, report)

        if "WebPage" not in dependency:
            warnings.warning(f"{item_label}: 'WebPage' is recommended")
        else:
            web_page = require_string(dependency, "WebPage", item_label, report)
            if web_page is not None:
                check_url(web_page, item_label, "WebPage", report)

        if "CoverURL" in dependency:
            cover_url = require_string(dependency, "CoverURL", item_label, report)
            if cover_url is not None:
                check_url(cover_url, item_label, "CoverURL", report)

        link = require_string(dependency, "Link", item_label, report)
        if link is not None:
            check_url(link, item_label, "Link", report)

        file_count = 0
        folder_count = 0

        if "Files" in dependency:
            file_count = validate_file_paths(dependency["Files"], "Files", item_label, report)

        if "Folders" in dependency:
            folder_count = validate_file_paths(dependency["Folders"], "Folders", item_label, report)

        has_config = "Config" in dependency

        if "Config" in dependency:
            config = dependency["Config"]
            config_label = f"{item_label}.Config"

            if not isinstance(config, dict):
                report.error(f"{config_label}: must be an object")
            else:
                check_keys(config, CONFIG_KEYS, config_label, report)

                for config_key in ("Name", "Type"):
                    config_value = require_string(config, config_key, config_label, report)
                    if config_value is not None and any(
                        char in config_value for char in '\\/:<>"|?*'
                    ):
                        report.error(
                            f"{config_label}: '{config_key}' must be a plain file name, "
                            "without path separators"
                        )

                config_type = config.get("Type")
                if isinstance(config_type, str) and config_type.startswith("."):
                    report.error(f"{config_label}: 'Type' must not start with a dot")

                require_string(config, "Content", config_label, report, allow_empty=True)

        if file_count == 0 and folder_count == 0 and not has_config:
            report.error(
                f"{item_label}: provide at least one non-empty 'Files', 'Folders' or 'Config' entry"
            )


def validate_game(
    game: Any,
    label: str,
    report: Report,
    warnings: Report,
) -> str | None:
    if not isinstance(game, dict):
        report.error(f"{label}: each game entry must be an object")
        return None

    check_keys(game, GAME_KEYS, label, report, ignore={"CoverPath"})

    if "CoverPath" in game:
        report.error(f"{label}: 'CoverPath' is written by the app and must not be in the catalog")

    game_id = require_string(game, "ID", label, report)

    if game_id is not None:
        if not ID_RE.fullmatch(game_id):
            report.error(
                f"{label}: 'ID' must be 1-100 characters of lowercase letters, digits, '-' or '_'"
            )

    require_string(game, "Name", label, report)

    engine = require_string(game, "Engine", label, report)
    if engine is not None and engine not in ENGINES:
        warnings.warning(
            f"{label}: 'Engine' is not a recognized native handler; "
            "only Hyura packages will install for this entry"
        )

    source = require_string(game, "Source", label, report)
    if source is not None and source not in SOURCES:
        report.error(f"{label}: 'Source' must be one of {', '.join(sorted(SOURCES))}")

    if "CoverURL" not in game:
        warnings.warning(f"{label}: 'CoverURL' is strongly recommended")
    else:
        cover_url = require_string(game, "CoverURL", label, report)
        if cover_url is not None:
            check_url(cover_url, label, "CoverURL", report)

    validate_mod_directories(game, label, report)
    validate_dependencies(game, label, report, warnings)

    return game_id


def main(argv: list[str]) -> int:
    paths = [Path(arg) for arg in argv[1:]] or DEFAULT_LISTS
    report = Report()
    warnings = Report()
    seen_ids: dict[str, tuple[str, str]] = {}
    entry_count = 0
    list_count = 0

    for path in paths:
        label = display_path(path)
        data = load_list(path, report)

        if data is None:
            continue

        list_count += 1
        print(f"Checking {label} ({len(data)} entries)")

        for index, game in enumerate(data):
            entry_count += 1
            entry_label = f"{label}[{index}]"

            if isinstance(game, dict) and isinstance(game.get("ID"), str):
                entry_label = f"{entry_label} ({game['ID']})"

            game_id = validate_game(game, entry_label, report, warnings)

            if game_id is None:
                continue

            normalized_id = game_id.casefold()

            if normalized_id in seen_ids:
                first_label, first_id = seen_ids[normalized_id]
                report.error(
                    f"{entry_label}: duplicate game ID '{game_id}' "
                    f"(already used by {first_label} as '{first_id}')"
                )
            else:
                seen_ids[normalized_id] = (entry_label, game_id)

    print(f"Checked {entry_count} entries in {list_count} list(s).")

    for warning in warnings.warnings:
        print(f"WARNING {warning}")

    for error in report.errors:
        print(f"ERROR {error}")

    print(f"{len(report.errors)} error(s), {len(warnings.warnings)} warning(s).")

    return 1 if report.errors else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
