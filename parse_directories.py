#!/usr/bin/env python3
"""Audit the catalog against every animated source file"""

from pathlib import Path
from unicodedata import normalize

from CursorConverter.__main__ import match_files
from CursorConverter.assets import ASSET_ROOT, ensure_assets
from CursorConverter.catalog import load_catalog
from CursorConverter.configuration import (
    ANIMATED_FORMAT,
    JAPANESE_MAPPING_PATH,
    MAPPING_PATH,
    UNICODE_NORMALIZATION,
    load_mapping,
)
from CursorConverter.models import Theme

EXTRA_CATALOG_ROLES = frozenset({"human", "place", "base"})
BASE_ROLE = "base"
BASE_FILENAME_SUFFIX = " 基"
LELIEL_ROLE = "idle"
LELIEL_FILENAME_STEM = "EVA マウスカーソル レリエル"
STATIC_CURSOR_PATTERN = "*.cur"


def validate_source_role(path: Path, role: str, japanese_mapping: dict[str, list[str]]) -> None:
    matched, unmatched = match_files([path], japanese_mapping)
    if matched:
        matched_role = matched[0][1]
        if matched_role != role:
            raise ValueError(f"Incorrect role {role} for {path}: expected {matched_role}")
    if unmatched:
        # These source name patterns have no alias in the Japanese role mapping
        stem = normalize(UNICODE_NORMALIZATION, path.stem)
        is_base = role == BASE_ROLE and stem.endswith(BASE_FILENAME_SUFFIX)
        is_leliel = role == LELIEL_ROLE and stem == LELIEL_FILENAME_STEM
        if not (is_base or is_leliel):
            raise ValueError(f"Unrecognized role for {path}")


def audit_theme(
    name: str,
    theme: Theme,
    required_roles: set[str],
    japanese_mapping: dict[str, list[str]],
    expected_sources: set[Path],
) -> bool:
    """Validate one theme and record its sources, returning whether it is complete"""
    allowed_roles = required_roles | EXTRA_CATALOG_ROLES
    unknown_roles = set(theme.roles) - allowed_roles
    if unknown_roles:
        raise ValueError(f"Unknown roles in {name}")
    missing_roles = sorted(required_roles - theme.roles.keys())
    if missing_roles != theme.missing_roles:
        raise ValueError(f"Incorrect missing roles for {name}: {missing_roles}")

    theme_root = ASSET_ROOT / name
    for role, filenames in theme.roles.items():
        if not filenames:
            raise ValueError(f"Empty role {role} in {name}")
        for filename in filenames:
            path = theme_root / filename
            if path in expected_sources or path.name != filename or not path.is_file():
                raise ValueError(f"Missing, duplicate, or invalid source: {path}")
            validate_source_role(path, role, japanese_mapping)
            expected_sources.add(path)
    return not missing_roles


def main() -> None:
    catalog = load_catalog()
    ensure_assets()
    mapping = load_mapping(MAPPING_PATH)
    japanese_mapping = load_mapping(JAPANESE_MAPPING_PATH)
    required_roles = set(mapping)
    expected_sources: set[Path] = set()
    complete_themes = 0
    for name, theme in catalog.items():
        is_complete = audit_theme(name, theme, required_roles, japanese_mapping, expected_sources)
        if is_complete:
            complete_themes += 1

    actual_sources = set(ASSET_ROOT.rglob(f"*.{ANIMATED_FORMAT}"))
    if actual_sources != expected_sources:
        uncataloged_sources = actual_sources - expected_sources
        missing_sources = expected_sources - actual_sources
        raise ValueError(f"Uncataloged assets: {uncataloged_sources}; missing assets: {missing_sources}")
    static_sources = list(ASSET_ROOT.rglob(STATIC_CURSOR_PATTERN))
    if static_sources:
        raise ValueError("Static cursor assets are not supported")
    print(
        f"Catalog covers {len(expected_sources)} animated files in {len(catalog)} sets; "
        f"{complete_themes} complete themes"
    )


if __name__ == "__main__":
    main()
