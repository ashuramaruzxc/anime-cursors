#!/usr/bin/env python
# -*- coding: utf-8 -*-
import argparse
import json
import os
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path

# Get the repository root path
repo_root = Path(__file__).resolve().parents[2]
cursor_converter_dir = repo_root / "CursorConverter"


def process_touhou_cursors() -> None:
    """
    Process Touhou cursor sets from the cursor_data.json file and create separate zip files
    with a single directory inside named with the short_character_name
    """
    dist_dir = repo_root / "dist"
    os.makedirs(dist_dir, exist_ok=True)

    temp_base = repo_root / "temp"
    os.makedirs(temp_base, exist_ok=True)

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
                
                temp_dir = temp_base / character_name
                
                os.makedirs(temp_dir, exist_ok=True)
                
                input_dir = repo_root / char_data["path"] / character_jp
                cmd = [
                    sys.executable,
                    "-m",
                    "CursorConverter",
                    "--prefix",
                    str(input_dir),
                    "--output",
                    str(temp_dir),
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
                    for root, _, files in os.walk(temp_dir):
                        for file in files:
                            file_path = Path(root) / file
                            arcname = file_path.relative_to(temp_dir)
                            arcname = Path(character_name) / arcname
                            zipf.write(file_path, arcname)

                print(f"  Created zip file: {zip_path}")

                shutil.rmtree(temp_dir, ignore_errors=True)

            except Exception as e:
                print(f"  Error processing {character_jp}: {e}")
                import traceback

                traceback.print_exc()
                
    shutil.rmtree(temp_base, ignore_errors=True)

    print("All Touhou cursor sets processed successfully!")


if __name__ == "__main__":
    process_touhou_cursors()
