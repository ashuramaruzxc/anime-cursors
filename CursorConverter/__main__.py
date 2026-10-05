#!/usr/bin/env python3

import argparse
import json
import logging
import unicodedata
from concurrent.futures import ProcessPoolExecutor
from configparser import ConfigParser
from functools import partial
from itertools import chain
from pathlib import Path

from rich.console import Console
from rich.progress import track

from CursorConverter.configuration import (
    ANIMATED_FORMAT,
    CURSOR_DIRECTORY,
    CURSOR_SIZES,
    DEFAULT_JOBS,
    DEFAULT_OUTPUT,
    EXPECTED_ALIAS_COUNT,
    JAPANESE_MAPPING_PATH,
    MAPPING_PATH,
    MENU_PATH,
    TEXT_ENCODING,
    UNICODE_NORMALIZATION,
    load_mapping,
)
from CursorConverter.worker import process

DEFAULT_THEME_NAME = "Custom"
DEFAULT_THEME_COMMENT = "Custom"
THEME_INDEX_FILENAME = "index.theme"
THEME_INDEX_SECTION = "Icon Theme"
UNMATCHED_REPORT_PATH = Path("unmatched.json")
UNMATCHED_REPORT_INDENT = 1


class ThemeConfig(ConfigParser):
    def optionxform(self, optionstr: str) -> str:
        return optionstr


def build_theme(sources: dict[str, Path], output: Path, name: str, comment: str, jobs: int) -> None:
    mapping = load_mapping(MAPPING_PATH)
    required_roles = set(mapping)
    missing = required_roles - sources.keys()
    if missing:
        missing_names = ", ".join(sorted(missing))
        raise ValueError(f"Missing cursor roles: {missing_names}")
    aliases = list(chain.from_iterable(mapping.values()))
    expected_names = set(aliases)
    if len(aliases) != EXPECTED_ALIAS_COUNT or len(expected_names) != EXPECTED_ALIAS_COUNT:
        raise ValueError(f"The Xcursor mapping must contain exactly {EXPECTED_ALIAS_COUNT} unique names")
    if output.exists() and any(output.iterdir()):
        raise ValueError(f"Output already contains files: {output}; use a clean output directory")
    cursor_directory = output / CURSOR_DIRECTORY
    cursor_directory.mkdir(parents=True, exist_ok=True)
    theme = ThemeConfig(interpolation=None)
    theme[THEME_INDEX_SECTION] = {"Name": name, "Comment": comment}
    index_path = output / THEME_INDEX_FILENAME
    with index_path.open("w", encoding=TEXT_ENCODING) as stream:
        theme.write(stream, space_around_delimiters=False)
    convert = partial(process, output=output, mapping=mapping, sizes=CURSOR_SIZES)
    source_paths = []
    for role in mapping:
        source_paths.append(sources[role])
    console = Console(stderr=True)
    with ProcessPoolExecutor(max_workers=jobs) as pool:
        results = pool.map(convert, source_paths, mapping, buffersize=jobs)
        for _ in track(
            results,
            total=len(mapping),
            description="Converting cursor roles",
            console=console,
            disable=not console.is_terminal,
        ):
            pass
    actual_names = set()
    for path in cursor_directory.iterdir():
        actual_names.add(path.name)
    if actual_names != expected_names:
        raise ValueError("Output contains unexpected or missing cursor names; use a clean output directory")


def match_files(paths: list[Path], rename_map: dict[str, list[str]]) -> tuple[list[tuple[Path, str]], list[str]]:
    normalized_mapping: dict[str, list[str]] = {}
    for name, aliases in rename_map.items():
        normalized_mapping[name] = []
        for alias in aliases:
            normalized_alias = unicodedata.normalize(UNICODE_NORMALIZATION, alias)
            normalized_mapping[name].append(normalized_alias)

    matched: list[tuple[Path, str]] = []
    unmatched: list[str] = []
    for path in paths:
        stem = unicodedata.normalize(UNICODE_NORMALIZATION, path.stem)
        roles: list[str] = []
        for name, aliases in normalized_mapping.items():
            if any(alias in stem for alias in aliases):
                roles.append(name)
        if len(roles) > 1:
            role_names = ", ".join(sorted(roles))
            raise ValueError(f"Ambiguous cursor role for {path}: {role_names}")
        if not roles:
            unmatched.append(path.name)
        else:
            matched.append((path, roles[0]))
    return matched, unmatched


def main() -> None:
    menu_data = MENU_PATH.read_text(encoding=TEXT_ENCODING)
    help_menu = json.loads(menu_data)

    parser = argparse.ArgumentParser(description=help_menu["description"])
    parser.add_argument(
        "-V",
        "--version",
        action="version",
        version=f'"{help_menu["name"]}" version {help_menu["version"]}',
    )
    parser.add_argument(
        "-p",
        "--prefix",
        type=Path,
        required=True,
        metavar="dir",
        help="Cursor directory",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        required=False,
        metavar="output",
        default=DEFAULT_OUTPUT,
        help="Output directory",
    )
    parser.add_argument(
        "-r",
        "--recursive",
        action="store_true",
        help="Set to list directories recursively",
    )
    parser.add_argument(
        "--json",
        type=Path,
        required=False,
        metavar="json",
        default=None,
        help="Redefine default json file with mapping definitions of animated cursor roles",
    )
    parser.add_argument(
        "--format",
        type=str,
        choices=[ANIMATED_FORMAT],
        default=ANIMATED_FORMAT,
        help="Animated cursor format",
    )
    parser.add_argument(
        "--name",
        type=str,
        required=False,
        metavar="name",
        default=DEFAULT_THEME_NAME,
        help="specifies the cursor theme name",
    )
    parser.add_argument(
        "--comment",
        type=str,
        required=False,
        metavar="comment",
        default=DEFAULT_THEME_COMMENT,
        help="specifies the cursor theme description",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_const",
        dest="loglevel",
        const=logging.DEBUG,
        default=logging.INFO,
        help="Enable verbose logging",
    )
    parser.add_argument(
        "-j",
        "--jobs",
        type=int,
        default=DEFAULT_JOBS,
        help="amount of jobs",
    )

    args = parser.parse_args()
    logging.basicConfig(level=args.loglevel)
    if args.jobs < 1:
        parser.error("--jobs must be at least 1")
    if not args.prefix.is_dir():
        parser.error(f"Cursor directory does not exist: {args.prefix}")
    mapping_path = args.json
    if not mapping_path:
        mapping_path = JAPANESE_MAPPING_PATH
    try:
        rename_map = load_mapping(mapping_path)
    except (OSError, ValueError) as error:
        parser.error(str(error))

    pattern = f"*.{args.format}"
    if args.recursive:
        candidates = args.prefix.rglob(pattern, case_sensitive=True)
    else:
        candidates = args.prefix.glob(pattern, case_sensitive=True)
    paths = []
    for path in candidates:
        if path.is_file():
            paths.append(path)
    paths.sort()
    try:
        matched, unmatched = match_files(paths, rename_map)
    except ValueError as error:
        parser.error(str(error))
    if not paths:
        parser.error("No files matched the criteria for processing")
    if unmatched:
        report = json.dumps(sorted(unmatched), ensure_ascii=False, indent=UNMATCHED_REPORT_INDENT)
        UNMATCHED_REPORT_PATH.write_text(report, encoding=TEXT_ENCODING)
        unmatched_names = ", ".join(unmatched)
        parser.error(f"Unmatched files: {unmatched_names}")
    sources_by_role: dict[str, Path] = {}
    for path, role in matched:
        if role in sources_by_role:
            logging.warning("Using %s for %s; alternative: %s", sources_by_role[role], role, path)
        else:
            sources_by_role[role] = path
    try:
        theme_output = args.output / args.name
        build_theme(sources_by_role, theme_output, args.name, args.comment, args.jobs)
    except ValueError as error:
        parser.error(str(error))


if __name__ == "__main__":
    main()
