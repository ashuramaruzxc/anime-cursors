from collections.abc import Sequence
from pathlib import Path

import numpy as np
from cursorgen.parser import open_blob
from cursorgen.writer import to_x11
from numpy.typing import NDArray
from PIL import Image

from CursorConverter.configuration import CURSOR_DIRECTORY

THUMBNAIL_ROLE = "idle"
THUMBNAIL_SIZE = (320, 320)
THUMBNAIL_FILENAME = "thumb.png"
THUMBNAIL_FORMAT = "PNG"
THUMBNAIL_COLOR_MODE = "RGBA"
CURSOR_PIXEL_ORDER = "BGRA"


def write_thumbnail(image: Image.Image | NDArray[np.uint8], destination: Path) -> None:
    # The published parser returns Pillow images; the newer parser returns BGRA arrays
    if isinstance(image, Image.Image):
        rgba_image = image.convert(THUMBNAIL_COLOR_MODE)
    else:
        height, width = image.shape[:2]
        pixels = image.tobytes()
        rgba_image = Image.frombytes(THUMBNAIL_COLOR_MODE, (width, height), pixels, "raw", CURSOR_PIXEL_ORDER)
    thumbnail = rgba_image.resize(THUMBNAIL_SIZE, resample=Image.Resampling.NEAREST)
    thumbnail.save(destination, format=THUMBNAIL_FORMAT)


def process(path: Path, name: str, *, output: Path, mapping: dict[str, list[str]], sizes: Sequence[int]) -> None:
    data = path.read_bytes()
    cursors = open_blob(data)
    result = to_x11(frames=cursors.frames, sizes=sizes)

    aliases = mapping[name]
    cursor_directory = output / CURSOR_DIRECTORY
    target = cursor_directory / aliases[0]
    target.write_bytes(result)
    for alias in aliases[1:]:
        alias_path = cursor_directory / alias
        alias_path.unlink(missing_ok=True)
        alias_path.symlink_to(target.name)

    if name == THUMBNAIL_ROLE:
        first_frame = cursors.frames[0]
        cursor_image = first_frame.images[0]
        thumbnail_path = output / THUMBNAIL_FILENAME
        write_thumbnail(cursor_image.image, thumbnail_path)
