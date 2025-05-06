#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json
import subprocess
import sys
import tempfile
import multiprocessing
import zipfile
from pathlib import Path
from typing import Dict, Any, List
from tqdm import tqdm

repo_root: Path = Path(__file__).resolve().parent
cursor_converter_dir: Path = repo_root / "CursorConverter"


def create_cursor_archive(source_dir: Path, archive_name: Path) -> bool:
    try:
        all_files = [file_path for file_path in source_dir.rglob("*") if file_path.is_file()]

        with zipfile.ZipFile(archive_name.with_suffix(".zip"), "w", zipfile.ZIP_DEFLATED) as zipf:
            for file_path in tqdm(all_files, desc="Zipping files"):
                arcname = file_path.relative_to(source_dir)
                zipf.write(file_path, arcname)
        return True
    except Exception as e:
        print(f"Error creating archive: {e}")
        return False


def process_touhou_cursors() -> None:
    dist_dir: Path = repo_root / "dist"
    dist_dir.mkdir(exist_ok=True)
    json_file_path: Path = cursor_converter_dir / "config" / "cursor_data.json"

    with json_file_path.open("r", encoding="utf-8") as f:
        cursor_data: Dict[str, Any] = json.load(f)

    # Get Touhou cursor sets
    touhou_sets = {
        "東方マウスカーソル　1～10": cursor_data.get("東方マウスカーソル　1～10", {}),
        "東方マウスカーソル　11～20": cursor_data.get("東方マウスカーソル　11～20", {}),
        "東方マウスカーソル　20～31": cursor_data.get("東方マウスカーソル　20～31", {}),
    }
    # Determine optimal number of jobs
    num_jobs: int = multiprocessing.cpu_count()

    # Track successful and failed cursors
    total_success: int = 0
    total_failed: int = 0

    # Process each set
    for set_name, characters in touhou_sets.items():
        print(f"\n{'=' * 40}")
        print(f"Processing {set_name}...")
        print(f"{'=' * 40}")

        set_success: int = 0
        set_failed: int = 0

        for character_jp, char_data in characters.items():
            try:
                # Extract character information
                character_en = char_data["en_name"]
                character_name = char_data["short_character_name"]
                print(f"\n{'=' * 40}")
                print(f"Processing cursor: {character_jp} ({character_en})")
                print(f"{'=' * 40}")

                with tempfile.TemporaryDirectory() as process_temp_dir:
                    process_temp_path = Path(process_temp_dir)
                    input_dir = repo_root / char_data["path"] / character_jp

                    cmd: List[str] = [
                        sys.executable,
                        "-m",
                        "CursorConverter",
                        "--prefix",
                        str(input_dir),
                        "--output",
                        str(process_temp_path),
                        "--name",
                        character_name,
                        "--comment",
                        f"{character_en}",
                        "-j",
                        str(num_jobs),
                    ]

                    print("Running cursor converter...")
                    subprocess.run(cmd, check=True)

                    with tempfile.TemporaryDirectory() as theme_temp_dir:
                        theme_temp_path = Path(theme_temp_dir)
                        cursors_dir = theme_temp_path / "cursors"
                        cursors_dir.mkdir(exist_ok=True)

                        processed_dir = process_temp_path / character_name
                        if not processed_dir.exists():
                            raise FileNotFoundError(f"Expected processed directory {processed_dir} not found")

                        # Copy files to appropriate locations
                        for file_path in processed_dir.iterdir():
                            if file_path.is_file():
                                if file_path.name in ["thumb.png", "index.theme"]:
                                    dest_path = theme_temp_path / file_path.name
                                    dest_path.write_bytes(file_path.read_bytes())
                                else:
                                    dest_path = cursors_dir / file_path.name
                                    dest_path.write_bytes(file_path.read_bytes())
                            elif file_path.is_dir() and file_path.name.lower() == "cursors":
                                # If there's a "cursors" subdirectory, copy its contents
                                for cursor_file in file_path.iterdir():
                                    if cursor_file.is_file():
                                        dest_path = cursors_dir / cursor_file.name
                                        dest_path.write_bytes(cursor_file.read_bytes())

                        # Step 3: Create zip file in dist directory
                        zip_path = dist_dir / f"{character_name}"
                        print(f"Creating zip file: {zip_path}.zip")
                        success = create_cursor_archive(source_dir=theme_temp_path, archive_name=zip_path)

                        if success:
                            print(f"Created zip file: {zip_path}.zip")
                            set_success += 1
                            total_success += 1
                        else:
                            print(f"Failed to create zip file for {character_name}")
                            set_failed += 1
                            total_failed += 1

                print(f"{'=' * 40}")

            except Exception as e:
                print(f"Error processing {character_jp}: {e}")
                print(f"{'=' * 40}")
                import traceback

                traceback.print_exc()
                set_failed += 1
                total_failed += 1

        # Print set summary
        print(f"\n{'=' * 40}")
        print(f"Set '{set_name}' summary:")
        print(f"  Successful: {set_success}")
        print(f"  Failed: {set_failed}")
        print(f"{'=' * 40}")

    # Print final summary
    print(f"\n{'=' * 40}")
    print("Processing complete!")
    print(f"Total successful: {total_success}")
    print(f"Total failed: {total_failed}")
    print(f"Total processed: {total_success + total_failed}")
    print(f"Success rate: {total_success / (total_success + total_failed) * 100:.2f}%")
    print(f"Zipped cursor packages are available in: {dist_dir.resolve()}")
    print(f"{'=' * 40}")


if __name__ == "__main__":
    print("=" * 80)
    print("⭐ Touhou Cursor Processor ⭐")
    print("=" * 80)
    print("This script creates cursor theme packages using zipfile library.")
    print(f"Output directory for zipped files: {repo_root / 'dist'}")
    print(f"Using {multiprocessing.cpu_count()} CPU cores for processing.")
    print("=" * 80)

    process_touhou_cursors()
