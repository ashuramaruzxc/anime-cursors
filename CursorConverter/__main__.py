#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import json
import logging
import os
from io import BytesIO
from multiprocessing.pool import Pool
from pathlib import Path
from string import Template
from typing import Any, Dict, List, Tuple

from cursorgen.parser import open_blob
from cursorgen.writer import to_x11
from PIL import Image

vcs_path = Path(__file__).parents[1]
root_path = os.path.dirname(__file__)


def rename_files(
    files_to_rename: List[Path], destination: Path, rename_map: Dict[str, List[str]]
) -> Tuple[List[Tuple[str, str]], List[Tuple[str, str]], List[str]]:
    old_path = []
    new_path = []
    unmatched_files = []

    dist_dir = destination / "src"

    for file_path in files_to_rename:
        name, extension = os.path.splitext(file_path.name)
        matched = False

        for en, value in rename_map.items():
            for jp in value:
                if jp in name:
                    matched = True
                    old_name = f"{jp}{extension}"
                    old_file_path = str(file_path.parent / file_path.name)
                    old_path.append((old_name, old_file_path))

                    new_name = f"{en}{extension}"
                    new_file_path = str(dist_dir / new_name)
                    new_path.append((new_name, new_file_path))

                    break

            if matched:
                break

        if not matched:
            unmatched_files.append(file_path.name)

    return old_path, new_path, unmatched_files


def generate_standard_xcursors(output: Path, rename_map: dict[str, list[str]]) -> dict[str, list[str]]:
    """Copy non standardized files to xcursors files with standardized names."""
    mapping = {}
    for key, value in rename_map.items():
        new_path = [os.path.join(output, "cursors", os.path.basename(new_name)) for new_name in value]
        mapping[key] = new_path
    return mapping


def list_files(directory: Path, file_format: str, recursive: bool = False) -> list:  # type: ignore
    matched_files = []
    file_format = f".{file_format}" if not file_format.startswith(".") else file_format

    if recursive:
        for root, _, filenames in os.walk(directory):
            for filename in filenames:
                if filename.endswith(file_format):
                    matched_files.append(Path(root) / filename)
    else:
        for file in directory.iterdir():
            if file.is_file() and file.name.endswith(file_format):
                matched_files.append(file)

    return matched_files


def load_rename_map(json_file: Path) -> Any:
    try:
        with open(json_file, "r", encoding="utf-8") as file:
            rename_map = json.load(file)
        return rename_map
    except FileNotFoundError:
        print(f"'{json_file}' not found.")
        exit(1)
    except json.JSONDecodeError:
        print(f"'{json_file}' contains invalid JSON.")
        exit(1)


def load_help_menu(json_file: str = f"{root_path}/config/menu.json") -> Any:
    with open(json_file, "r", encoding="utf-8") as file:
        help_menu = json.load(file)
    return help_menu


def process(arg: Tuple[BytesIO, str, Path, Dict[str, List[str]], List[int]]) -> None:
    stream, name, output, mapping, sizes = arg
    blob = stream.getvalue()

    cursors = open_blob(blob)
    result = to_x11(frames=cursors.frames, sizes=sizes)

    if name in mapping:
        for xcursor_name in mapping[name]:
            final = os.path.join(output, "cursors", xcursor_name)
            with open(final, "wb") as fs:
                fs.write(result)

    if name == "idle":
        frame = cursors.frames[0]
        cursor = frame[0]
        png = cursor.image
        png = png.resize((320, 320), Image.Resampling.NEAREST)
        png.save(f"{output}/thumb.png", "PNG")


def main() -> None:
    help_menu = load_help_menu()

    parser = argparse.ArgumentParser(description=help_menu["description"])
    parser.add_argument(
        "-V",
        "--version",
        action="version",
        version='"{}" version {}'.format(help_menu["name"], help_menu["version"]),
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
        default=f"{vcs_path}/dist",
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
        default=f"{root_path}/config/definitions_jp.json",
        help="Redefine default json file with mapping definitions of [ani, cur] to xcursors",
    )
    parser.add_argument(
        "--format",
        type=str,
        choices=["ani", "cur"],
        default="ani",
        help="File format to filter by (ani or cur) default is ani",
    )
    parser.add_argument(
        "--name",
        type=str,
        required=False,
        metavar="name",
        default="Custom",
        help="specifies the cursor theme name",
    )
    parser.add_argument(
        "--comment",
        type=str,
        required=False,
        metavar="comment",
        default="Custom",
        help="specifies the cursor theme description",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_const",
        dest="loglevel",
        const=logging.DEBUG,
        help="Increase verbosity level (add more -v for more detailed logs)",
    )
    parser.add_argument(
        "-j",
        "--jobs",
        type=int,
        default=1,
        help="amount of jobs",
    )

    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO)
    rename_map = load_rename_map(args.json)
    rename_xmc = load_rename_map(Path(f"{root_path}/config/definitions.json"))
    files_to_rename = list_files(args.prefix, args.format, args.recursive)

    japanese_name, english_name, unmatched_files = rename_files(files_to_rename, args.output, rename_map)
    new = [x[0] for x in english_name]

    if args.name and args.output == args.output:
        args.output = Path(args.output / args.name)
        os.makedirs(args.output, exist_ok=True)
        os.makedirs(f"{args.output}/cursors", exist_ok=True)

    if args.comment and args.name:
        template: Dict[str, Template] = {
            "index.theme": Template('[Icon Theme]\nName="$theme_name Cursors"\nComment="$comment"\n'),
        }
        for file_name, string_template in template.items():
            data = string_template.safe_substitute(theme_name=args.name, comment=args.comment)
            fp: Path = args.output / file_name
            fp.write_text(data)

    if not files_to_rename:
        print("No files matched the criteria for processing.")
        return

    if unmatched_files:
        print("Unmatched files: " + ", ".join(unmatched_files))
        with open("unmatched.json", "w", encoding="utf-8") as file:
            json.dump(sorted(unmatched_files), file, ensure_ascii=False, indent=1)
        return
    if len(new) < 15:
        print("Error: check definitions_jp if files match renaming scheme")

    else:
        files_to_process = []
        for old_name, new_name in zip(japanese_name, english_name):
            with open(old_name[1], "rb") as file:
                stream = BytesIO(file.read())

                name: str = os.path.splitext(os.path.basename(new_name[1]))[0]
                mapping = generate_standard_xcursors(args.output, rename_xmc)
                files_to_process.append((stream, name))

        arg = [
            (
                stream,
                name,
                args.output,
                mapping,
                [22, 24, 28, 32, 36, 40, 48, 56, 64, 72, 96],
            )
            for stream, name in files_to_process
        ]
        with Pool(args.jobs) as pool:
            pool.map(process, arg)


if __name__ == "__main__":
    main()
