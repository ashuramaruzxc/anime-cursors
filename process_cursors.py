#!/usr/bin/env python3
import argparse
import shutil
import tempfile
from pathlib import Path

import msgspec

from CursorConverter.__main__ import build_theme
from CursorConverter.assets import NOTICE_ROOT, load_manifest
from CursorConverter.catalog import load_catalog, theme_sources
from CursorConverter.configuration import DEFAULT_JOBS, DEFAULT_OUTPUT, TEXT_ENCODING
from CursorConverter.models import Manifest, Theme

REPO_ROOT = Path(__file__).resolve().parent
LICENSE_FILENAME = "LICENSE"
ATTRIBUTION_FILENAME = "ATTRIBUTION.txt"
NOTICES_DIRECTORY = "notices"
THEME_DIRECTORY_PREFIX = "anime-"
ZIP_FORMAT = "zip"
DIRECTORY_FORMAT = "directory"
CATALOG_JSON_INDENT = 2
ATTRIBUTION_TEMPLATE = (
    "Theme: {theme_name}\n"
    "Cursor artwork and thumbnail: 夜夢（よるむ）\n"
    "Artist: https://www.pixiv.net/en/users/345405\n"
    "Artwork license: CC BY-NC-SA 4.0\n"
    "https://creativecommons.org/licenses/by-nc-sa/4.0/\n"
    "\nOriginal artwork sources:\n{source_links}\n"
    "\nChanges: converted Windows .ani cursors to Xcursor format, resized\n"
    "cursor images for multiple sizes, and generated a resized PNG thumbnail.\n"
    "Converted artwork remains under CC BY-NC-SA 4.0.\n"
    "See LICENSE and any files in notices/ for license terms and author notices.\n"
)


def select_themes(catalog: dict[str, Theme], requested: list[str] | None) -> list[str]:
    if requested:
        selected = requested
    else:
        selected = []
        for name, theme in catalog.items():
            if not theme.missing_roles:
                selected.append(name)

    for name in selected:
        if name not in catalog:
            raise ValueError(f"Unknown theme: {name}")
        missing_roles = catalog[name].missing_roles
        if missing_roles:
            missing_names = ", ".join(missing_roles)
            raise ValueError(f"Incomplete theme {name}: {missing_names}")
    return selected


def write_theme_notices(name: str, theme: Theme, manifest: Manifest, output: Path) -> None:
    license_path = REPO_ROOT / LICENSE_FILENAME
    license_path.copy(output / LICENSE_FILENAME, preserve_metadata=True)
    archive_ids: set[str] = set()
    for asset in manifest.themes[name].values():
        archive_ids.add(asset.archive)
    source_pages: set[str] = set()
    for archive_id in archive_ids:
        source_pages.add(manifest.archives[archive_id]["page"])
    source_links = "\n".join(sorted(source_pages))
    attribution = ATTRIBUTION_TEMPLATE.format(theme_name=theme.name, source_links=source_links)
    attribution_path = output / ATTRIBUTION_FILENAME
    attribution_path.write_text(attribution, encoding=TEXT_ENCODING)

    notices = NOTICE_ROOT / theme.group
    if notices.is_dir():
        notices.copy(output / NOTICES_DIRECTORY, preserve_metadata=True)


def package_theme(name: str, source: Path, output_root: Path, output_format: str) -> None:
    if output_format == ZIP_FORMAT:
        archive_path = output_root / name
        shutil.make_archive(str(archive_path), ZIP_FORMAT, root_dir=source)
    else:
        destination = output_root / f"{THEME_DIRECTORY_PREFIX}{name}"
        if destination.exists():
            raise ValueError(f"Output already exists: {destination}")
        source.copy(destination, follow_symlinks=False, preserve_metadata=True)


def main() -> None:
    parser = argparse.ArgumentParser(description="Build complete animated cursor themes")
    parser.add_argument("--theme", action="append", help="Theme ID to build; repeat to select multiple themes")
    parser.add_argument("--list", action="store_true", help="List all themes and their missing roles as JSON")
    parser.add_argument("-j", "--jobs", type=int, default=DEFAULT_JOBS)
    parser.add_argument("-o", "--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--format", choices=[ZIP_FORMAT, DIRECTORY_FORMAT], default=ZIP_FORMAT)
    args = parser.parse_args()
    if args.jobs < 1:
        parser.error("--jobs must be at least 1")
    try:
        catalog = load_catalog()
        manifest = load_manifest()
    except (OSError, ValueError) as error:
        parser.error(str(error))
    if args.list:
        catalog_json = msgspec.json.encode(catalog)
        formatted_catalog = msgspec.json.format(catalog_json, indent=CATALOG_JSON_INDENT)
        print(formatted_catalog.decode(TEXT_ENCODING))
        return
    try:
        selected = select_themes(catalog, args.theme)
    except ValueError as error:
        parser.error(str(error))

    args.output.mkdir(parents=True, exist_ok=True)
    for name in selected:
        theme = catalog[name]
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / name
            sources = theme_sources(name, theme)
            build_theme(sources, output, theme.name, theme.group, args.jobs)
            write_theme_notices(name, theme, manifest, output)
            try:
                package_theme(name, output, args.output, args.format)
            except ValueError as error:
                parser.error(str(error))
        print(f"Built {name}", flush=True)


if __name__ == "__main__":
    main()
