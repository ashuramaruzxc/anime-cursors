#!/usr/bin/env python
# -*- coding: utf-8 -*-
import argparse
import json
import os
import shutil
import subprocess
import sys
import zipfile
import tempfile
from pathlib import Path

repo_root = Path(__file__).resolve().parent
cursor_converter_dir = repo_root / "CursorConverter"


def process_touhou_cursors() -> None:
    """
    Process Touhou cursor sets from the cursor_data.json file and create separate zip files
    with the correct directory structure.
    """
    dist_dir = repo_root / "dist"
    os.makedirs(dist_dir, exist_ok=True)

    # Path to cursor_data.json file
    json_file_path = cursor_converter_dir / "config" / "cursor_data.json"

    with open(json_file_path, "r", encoding="utf-8") as f:
        cursor_data = json.load(f)

    touhou_sets = {
        "東方マウスカーソル　1～10": cursor_data.get("東方マウスカーソル　1～10", {}),
        "東方マウスカーソル　11～20": cursor_data.get("東方マウスカーソル　11～20", {}),
    }

    for set_name, characters in touhou_sets.items():
        print(f"Processing {set_name}...")
        for character_jp, char_data in characters.items():
            try:
                character_en = char_data["en_name"]
                character_name = char_data["short_character_name"]
                print(f"  Converting {character_jp} ({character_en})...")

                # Create a temporary directory for processing
                with tempfile.TemporaryDirectory() as temp_dir:
                    temp_dir_path = Path(temp_dir)
                    input_dir = repo_root / char_data["path"] / character_jp
                    cmd = [
                        sys.executable,
                        "-m",
                        "CursorConverter",
                        "--prefix",
                        str(input_dir),
                        "--output",
                        str(temp_dir_path),
                        "--name",
                        character_name,
                        "--comment",
                        f"{character_en}",
                        "-j",
                        "4",
                    ]
                    print(f"  Running command: {' '.join(cmd)}")
                    subprocess.run(cmd, check=True)

                    zip_path = dist_dir / f"{character_name}.zip"
                    print(f"  Creating zip file: {zip_path}")

                    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
                        for root, _, files in os.walk(temp_dir_path):
                            for file in files:
                                if file.lower() in ["thumbs.db", ".ds_store"]:
                                    continue
                                file_path = Path(root) / file
                                if file.lower() in ["thumb.png", "index.theme"]:
                                    # These go in the root
                                    arcname = file
                                else:
                                    arcname = f"Cursors/{file}"

                                zipf.write(file_path, arcname)

                print(f"  Created zip file: {zip_path}")

            except Exception as e:
                print(f"  Error processing {character_jp}: {e}")
                import traceback

                traceback.print_exc()

    print("All Touhou cursor sets processed successfully!")


if __name__ == "__main__":
    process_touhou_cursors()
