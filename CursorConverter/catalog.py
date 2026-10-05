from pathlib import Path

from CursorConverter.assets import ASSET_ROOT, ensure_assets
from CursorConverter.configuration import CATALOG_DECODER, CATALOG_PATH, read_json
from CursorConverter.models import Theme


def load_catalog() -> dict[str, Theme]:
    return read_json(CATALOG_PATH, CATALOG_DECODER, "catalog")


def theme_sources(name: str, theme: Theme) -> dict[str, Path]:
    ensure_assets([name])
    # Catalog order selects the default artwork while retaining every alternative
    sources: dict[str, Path] = {}
    theme_root = ASSET_ROOT / name
    for role, names in theme.roles.items():
        sources[role] = theme_root / names[0]
    return sources
