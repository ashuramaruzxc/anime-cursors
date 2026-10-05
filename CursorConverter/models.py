"""Schemas for the packaged cursor catalog and asset manifest"""

from typing import Annotated

import msgspec

from CursorConverter.downloads import Archive

NonemptyString = Annotated[str, msgspec.Meta(min_length=1)]
Aliases = Annotated[list[NonemptyString], msgspec.Meta(min_length=1)]
RoleMapping = Annotated[dict[NonemptyString, Aliases], msgspec.Meta(min_length=1)]


class Theme(msgspec.Struct, frozen=True):
    name: NonemptyString
    original_path: str
    group: str
    roles: RoleMapping
    missing_roles: list[NonemptyString]


class Asset(msgspec.Struct, frozen=True):
    archive: str
    member: str
    sha256: str


class Manifest(msgspec.Struct, frozen=True):
    archives: dict[str, Archive]
    themes: dict[str, dict[str, Asset]]
    notices: dict[str, dict[str, Asset]]
