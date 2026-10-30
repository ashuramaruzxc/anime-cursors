from importlib.resources import files
from importlib.resources.abc import Traversable
from pathlib import Path

import msgspec

from CursorConverter.models import Manifest, RoleMapping, Theme

CONFIG_ROOT = files("CursorConverter").joinpath("config")
MAPPING_PATH = CONFIG_ROOT.joinpath("definitions.json")
JAPANESE_MAPPING_PATH = CONFIG_ROOT.joinpath("definitions_jp.json")
CATALOG_PATH = CONFIG_ROOT.joinpath("cursor_data.json")
MANIFEST_PATH = CONFIG_ROOT.joinpath("asset_sources.json")
MENU_PATH = CONFIG_ROOT.joinpath("menu.json")

TEXT_ENCODING = "utf-8"
UNICODE_NORMALIZATION = "NFKC"
ANIMATED_FORMAT = "ani"
DEFAULT_OUTPUT = Path("dist")
DEFAULT_JOBS = 1
CURSOR_DIRECTORY = "cursors"
CURSOR_SIZES = (12, 18, 24, 30, 32, 36, 42, 48, 64)
EXPECTED_ALIAS_COUNT = 76

MAPPING_DECODER = msgspec.json.Decoder(RoleMapping)
CATALOG_DECODER = msgspec.json.Decoder(dict[str, Theme])
MANIFEST_DECODER = msgspec.json.Decoder(Manifest)
ARCHIVE_MAP_DECODER = msgspec.json.Decoder(dict[str, str])


def read_json[T](path: Traversable, decoder: msgspec.json.Decoder[T], kind: str) -> T:
    """Decode configuration data and include its filename in validation errors"""
    try:
        data = path.read_bytes()
        return decoder.decode(data)
    except msgspec.DecodeError as error:
        raise ValueError(f"Invalid {kind} {path.name}: {error}") from error


def load_mapping(path: Traversable) -> dict[str, list[str]]:
    return read_json(path, MAPPING_DECODER, "mapping")
