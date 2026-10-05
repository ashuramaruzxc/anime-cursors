"""Fetch checksum-pinned cursor archives from the artist's distribution links"""

import argparse
import hashlib
import os
import tempfile
import zipfile
from collections import defaultdict
from pathlib import Path

from platformdirs import user_cache_path

from CursorConverter.configuration import (
    ARCHIVE_MAP_DECODER,
    CATALOG_DECODER,
    CATALOG_PATH,
    MANIFEST_DECODER,
    MANIFEST_PATH,
    read_json,
)
from CursorConverter.downloads import digest, download_archive
from CursorConverter.models import Asset, Manifest

ASSET_ROOT_ENV = "ANIME_CURSOR_ASSET_ROOT"
DEFAULT_ASSET_ROOT = user_cache_path("anime-cursors") / "animated"
ASSET_ROOT = Path(os.environ.get(ASSET_ROOT_ENV, DEFAULT_ASSET_ROOT))
NOTICE_ROOT = ASSET_ROOT.parent / "notices"
ARCHIVE_ROOT = ASSET_ROOT.parent / "archives"
ARCHIVE_FILENAME_ENCODING = "cp932"


def load_manifest() -> Manifest:
    return read_json(MANIFEST_PATH, MANIFEST_DECODER, "manifest")


def ensure_assets(themes: list[str] | None = None, archive_paths: dict[str, str] | None = None) -> None:
    manifest = load_manifest()
    needed: dict[str, list[tuple[Path, Asset]]] = defaultdict(list)
    catalog = read_json(CATALOG_PATH, CATALOG_DECODER, "catalog")
    if themes is None:
        selected = list(manifest.themes)
    else:
        selected = themes
    unknown = set(selected) - manifest.themes.keys()
    if unknown:
        unknown_names = ", ".join(sorted(unknown))
        raise ValueError(f"Unknown themes: {unknown_names}")
    groups: set[str] = set()
    collections: list[tuple[Path, str, dict[str, Asset]]] = []
    for theme in selected:
        groups.add(catalog[theme].group)
        members = manifest.themes[theme]
        collections.append((ASSET_ROOT, theme, members))
    for group in sorted(groups):
        members = manifest.notices.get(group, {})
        collections.append((NOTICE_ROOT, group, members))
    for root, name, members in collections:
        for filename, asset in members.items():
            member_path = Path(filename)
            if Path(name).name != name or member_path.is_absolute() or ".." in member_path.parts:
                raise ValueError(f"Invalid asset destination: {name}/{filename}")
            destination = root / name / filename
            expected_checksum = asset.sha256
            if not destination.is_file() or digest(destination) != expected_checksum:
                needed[asset.archive].append((destination, asset))
    for key, assets in needed.items():
        archive = manifest.archives[key]
        archive_checksum = archive["sha256"]
        if archive_paths is not None:
            path = Path(archive_paths[key])
            if digest(path) != archive_checksum:
                raise ValueError(f"Archive checksum mismatch: {path}")
        else:
            path = ARCHIVE_ROOT / f"{archive_checksum}.zip"
            if not path.is_file() or digest(path) != archive_checksum:
                print(f"Downloading {key}", flush=True)
                download_archive(archive, path)
        with zipfile.ZipFile(path, metadata_encoding=ARCHIVE_FILENAME_ENCODING) as bundle:
            for destination, asset in assets:
                data = bundle.read(asset.member)
                checksum = hashlib.sha256(data).hexdigest()
                if checksum != asset.sha256:
                    raise ValueError(f"Cursor checksum mismatch: {destination.name}")
                destination.parent.mkdir(parents=True, exist_ok=True)
                with tempfile.TemporaryDirectory(dir=destination.parent) as directory:
                    temporary = Path(directory) / destination.name
                    temporary.write_bytes(data)
                    temporary.replace(destination)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--theme", action="append", help="Download only this theme; repeat to select more")
    parser.add_argument(
        "--archive-map", type=Path, help="JSON mapping of archive IDs to local files, for offline builds"
    )
    parser.add_argument("--download", help="Download one archive ID instead of extracting cursors")
    parser.add_argument("--output", type=Path, help="Destination for --download")
    args = parser.parse_args()
    if args.download:
        if args.output is None:
            parser.error("--download requires --output")
        manifest = load_manifest()
        archive = manifest.archives[args.download]
        download_archive(archive, args.output)
    else:
        archive_paths = None
        if args.archive_map:
            archive_paths = read_json(args.archive_map, ARCHIVE_MAP_DECODER, "archive map")
        ensure_assets(args.theme, archive_paths)


if __name__ == "__main__":
    main()
