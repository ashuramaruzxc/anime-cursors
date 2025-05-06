#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json
import subprocess
import sys
import tempfile
import multiprocessing
import zipfile
import logging
import argparse
from pathlib import Path
from typing import Dict, Any, List, NamedTuple, Optional, Set
from dataclasses import dataclass
from tqdm import tqdm

class CharacterData(NamedTuple):
    en_name: str
    short_character_name: str
    path: str

class CursorSet(NamedTuple):
    name: str
    characters: Dict[str, CharacterData]

class ProcessResult(NamedTuple):
    character_jp: str
    character_en: str
    success: bool
    error_msg: Optional[str] = None

class ProcessStats(NamedTuple):
    successful: int
    failed: int

    @property
    def total(self) -> int:
        return self.successful + self.failed

    @property
    def success_rate(self) -> float:
        return self.successful / self.total * 100 if self.total > 0 else 0.0

@dataclass
class AppConfig:
    repo_root: Path
    cursor_converter_dir: Path
    dist_dir: Path
    num_jobs: int
    verbose: bool = False

# Initialize logger
logger = logging.getLogger(__name__)

def setup_logger(verbose: bool = False) -> None:
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[logging.StreamHandler()]
    )

def create_cursor_archive(source_dir: Path, archive_name: Path) -> bool:
    try:
        all_files: List[Path] = [
            file_path for file_path in source_dir.rglob("*")
            if file_path.is_file()
        ]

        with zipfile.ZipFile(archive_name.with_suffix(".zip"), "w", zipfile.ZIP_DEFLATED) as zipf:
            for file_path in tqdm(all_files, desc="Zipping files"):
                arcname = file_path.relative_to(source_dir)
                zipf.write(file_path, arcname)
        return True
    except Exception as e:
        logger.error(f"Error creating archive: {e}")
        return False

def load_cursor_data(json_path: Path) -> Dict[str, Dict[str, Dict[str, Any]]]:
    try:
        with json_path.open("r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        logger.error(f"Cursor data file not found: {json_path}")
        raise
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in cursor data file: {e}")
        raise

def extract_touhou_sets(cursor_data: Dict[str, Any]) -> List[CursorSet]:
    touhou_set_names = [
        "東方マウスカーソル　1～10",
        "東方マウスカーソル　11～20",
        "東方マウスカーソル　20～31"
    ]

    result: List[CursorSet] = []

    for set_name in touhou_set_names:
        if set_name in cursor_data:
            # Convert dictionary to CharacterData named tuples
            characters: Dict[str, CharacterData] = {}
            for char_jp, char_dict in cursor_data[set_name].items():
                characters[char_jp] = CharacterData(
                    en_name=char_dict["en_name"],
                    short_character_name=char_dict["short_character_name"],
                    path=char_dict["path"]
                )
            result.append(CursorSet(name=set_name, characters=characters))

    return result

def process_character(
        config: AppConfig,
        character_jp: str,
        character_data: CharacterData
) -> ProcessResult:
    try:
        character_en = character_data.en_name
        character_name = character_data.short_character_name

        logger.info(f"\n{'=' * 40}")
        logger.info(f"Processing cursor: {character_jp} ({character_en})")
        logger.info(f"{'=' * 40}")

        with tempfile.TemporaryDirectory() as process_temp_dir:
            process_temp_path = Path(process_temp_dir)
            input_dir = config.repo_root / character_data.path / character_jp

            # Prepare command for cursor converter
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
                str(config.num_jobs),
            ]

            if config.verbose:
                cmd.append("-v")

            logger.info("Running cursor converter...")
            subprocess.run(cmd, check=True)

            with tempfile.TemporaryDirectory() as theme_temp_dir:
                theme_temp_path = Path(theme_temp_dir)
                cursors_dir = theme_temp_path / "cursors"
                cursors_dir.mkdir(exist_ok=True)

                processed_dir = process_temp_path / character_name
                if not processed_dir.exists():
                    raise FileNotFoundError(f"Expected processed directory {processed_dir} not found")

                _copy_theme_files(processed_dir, theme_temp_path, cursors_dir)

                zip_path = config.dist_dir / f"{character_name}"
                logger.info(f"Creating zip file: {zip_path}.zip")
                success = create_cursor_archive(source_dir=theme_temp_path, archive_name=zip_path)

                if success:
                    logger.info(f"Created zip file: {zip_path}.zip")
                    return ProcessResult(character_jp, character_en, True)
                else:
                    error_msg = f"Failed to create zip file for {character_name}"
                    logger.error(error_msg)
                    return ProcessResult(character_jp, character_en, False, error_msg)

    except Exception as e:
        logger.error(f"Error processing {character_jp}: {e}")
        import traceback
        logger.debug(traceback.format_exc())
        return ProcessResult(character_jp, character_en, False, str(e))

def _copy_theme_files(processed_dir: Path, theme_temp_path: Path, cursors_dir: Path) -> None:
    theme_files: Set[str] = {"thumb.png", "index.theme"}

    for file_path in processed_dir.iterdir():
        if file_path.is_file():
            file_content = file_path.read_bytes()
            if file_path.name in theme_files:
                dest_path = theme_temp_path / file_path.name
                dest_path.write_bytes(file_content)
            else:
                dest_path = cursors_dir / file_path.name
                dest_path.write_bytes(file_content)
        elif file_path.is_dir() and file_path.name.lower() == "cursors":
            for cursor_file in file_path.iterdir():
                if cursor_file.is_file():
                    file_content = cursor_file.read_bytes()
                    dest_path = cursors_dir / cursor_file.name
                    dest_path.write_bytes(file_content)

def process_cursor_set(config: AppConfig, cursor_set: CursorSet) -> ProcessStats:
    logger.info(f"\n{'=' * 40}")
    logger.info(f"Processing {cursor_set.name}...")
    logger.info(f"{'=' * 40}")

    successful: int = 0
    failed: int = 0

    for character_jp, character_data in cursor_set.characters.items():
        result = process_character(config, character_jp, character_data)

        if result.success:
            successful += 1
        else:
            failed += 1

    return ProcessStats(successful=successful, failed=failed)

def process_touhou_cursors(config: AppConfig) -> None:
    json_file_path: Path = config.cursor_converter_dir / "config" / "cursor_data.json"

    try:
        cursor_data = load_cursor_data(json_file_path)
        touhou_sets = extract_touhou_sets(cursor_data)

        total_stats = ProcessStats(successful=0, failed=0)

        for cursor_set in touhou_sets:
            set_stats = process_cursor_set(config, cursor_set)

            # Print set summary
            logger.info(f"\n{'=' * 40}")
            logger.info(f"Set '{cursor_set.name}' summary:")
            logger.info(f"  Successful: {set_stats.successful}")
            logger.info(f"  Failed: {set_stats.failed}")
            logger.info(f"{'=' * 40}")

            # Update total stats
            total_stats = ProcessStats(
                successful=total_stats.successful + set_stats.successful,
                failed=total_stats.failed + set_stats.failed
            )

        # Print final summary
        logger.info(f"\n{'=' * 40}")
        logger.info("Processing complete!")
        logger.info(f"Total successful: {total_stats.successful}")
        logger.info(f"Total failed: {total_stats.failed}")
        logger.info(f"Total processed: {total_stats.total}")
        logger.info(f"Success rate: {total_stats.success_rate:.2f}%")
        logger.info(f"Zipped cursor packages are available in: {config.dist_dir.resolve()}")
        logger.info(f"{'=' * 40}")

    except Exception as e:
        logger.error(f"Error processing Touhou cursors: {e}")
        import traceback
        logger.debug(traceback.format_exc())

def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Touhou Cursor Processor")
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable verbose logging"
    )

    parser.add_argument(
        "-j", "--jobs",
        type=int,
        default=multiprocessing.cpu_count(),
        help="Number of CPU cores to use for processing"
    )

    parser.add_argument(
        "-o", "--output",
        type=Path,
        default=None,
        help="Custom output directory for cursor packages"
    )

    return parser.parse_args()

def main() -> None:
    args = parse_arguments()

    setup_logger(args.verbose)

    repo_root: Path = Path(__file__).resolve().parent
    cursor_converter_dir: Path = repo_root / "CursorConverter"

    dist_dir: Path = args.output if args.output else repo_root / "dist"
    dist_dir.mkdir(exist_ok=True)

    config = AppConfig(
        repo_root=repo_root,
        cursor_converter_dir=cursor_converter_dir,
        dist_dir=dist_dir,
        num_jobs=args.jobs,
    )

    logger.info("=" * 80)
    logger.info("⭐ Touhou Cursor Processor ⭐")
    logger.info("=" * 80)
    logger.info("This script creates cursor theme packages using zipfile library.")
    logger.info(f"Output directory for zipped files: {dist_dir}")
    logger.info(f"Using {config.num_jobs} CPU cores for processing.")
    logger.info("=" * 80)

    # Process cursor sets
    process_touhou_cursors(config)

if __name__ == "__main__":
    main()