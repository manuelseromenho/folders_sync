import argparse
import hashlib
import logging
import sys
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from shutil import copy2
from typing import Optional, Dict

USAGE = f"Usage: python {sys.argv[0]} [--help] | source_path target_path sync_period sync_amount log_path]"


@dataclass
class FileToSync:
    file_name: str = ""
    file_path: Path = Path()
    file_update_datetime: str = ""
    file_size: int = 0
    hash_value: str = ""


class SyncManager:
    def __init__(self, source_path: Path, target_path: Path, logger):
        self.source_path = Path(source_path)
        self.target_path = Path(target_path)
        self.logger = logger
        self.source_files: Dict[Path, FileToSync] = {}
        self.target_files: Dict[Path, FileToSync] = {}

    def sync(self) -> None:
        self.logger.info("Starting synchronization")
        self.source_files = self._create_files_set(self.source_path)
        self.target_files = self._create_files_set(self.target_path)
        self._sync_folders()
        self.logger.info("Synchronization completed")

    def _sync_folders(self) -> None:
        self._sync_remove()

        for relative_path in self.source_files:
            source_file = self.source_path / relative_path
            target_file = self.target_path / relative_path

            if not target_file.exists():
                self._sync_copy(source_file, target_file, relative_path)
            else:
                # Only update if different and source != target
                if target_file != source_file:
                    self._sync_update(source_file, target_file, relative_path)

    def _sync_remove(self) -> None:
        for relative_path in self.target_files:
            if relative_path not in self.source_files:
                target_file = self.target_path / relative_path
                try:
                    target_file.unlink()
                    self.logger.info(f"file {target_file} deleted")
                    # Optionally, try to remove empty parent dirs here
                    self._remove_empty_parents(target_file.parent)
                except FileNotFoundError:
                    self.logger.error(f"File not found: {target_file}")
                except PermissionError:
                    self.logger.error(
                        f"Permission denied while deleting: {target_file}"
                    )
                except Exception as e:
                    self.logger.error(f"Failed to delete {target_file}: {e}")

    def _remove_empty_parents(self, path: Path) -> None:
        """Recursively remove empty directories up to target_path root."""
        try:
            while path != self.target_path and not any(path.iterdir()):
                path.rmdir()
                self.logger.info(f"Removed empty directory: {path}")
                path = path.parent
        except Exception as e:
            self.logger.error(f"Failed to remove directory {path}: {e}")

    def _sync_copy(
        self,
        source_file: Path,
        target_file: Path,
        relative_path: Path,
        msg_log: Optional[str] = None,
    ) -> None:
        try:
            target_file.parent.mkdir(parents=True, exist_ok=True)
            copy2(source_file, target_file)
            if msg_log is None:
                msg_log = f"file {source_file} was copied to {target_file}"
            self.logger.info(msg_log)
        except FileNotFoundError:
            self.logger.error(f"File not found: {source_file}")
        except PermissionError:
            self.logger.error(f"Permission denied while copying: {source_file}")
        except Exception as e:
            self.logger.error(f"Failed to copy {relative_path}: {e}")

    def _sync_update(
        self,
        source_file: Path,
        target_file: Path,
        relative_path: Path,
    ) -> None:
        msg_log = f"file {source_file} was updated to {target_file}"
        target_hash = hash_file_sha1(target_file)
        source_hash = hash_file_sha1(source_file)

        if (
            target_file.stat().st_size != source_file.stat().st_size
            or target_hash != source_hash
        ):
            self._sync_copy(source_file, target_file, relative_path, msg_log)

    @staticmethod
    def _create_files_set(path: Path) -> Dict[Path, FileToSync]:
        files = {}
        for file in path.rglob("*"):  # Recursive walk for all files
            if file.is_file():
                relative_path = file.relative_to(path)
                stats = file.stat()
                files[relative_path] = FileToSync(
                    file_name=str(relative_path),
                    file_path=file,
                    file_update_datetime=datetime.fromtimestamp(
                        stats.st_mtime
                    ).strftime("%Y-%m-%d %H:%M:%S"),
                    file_size=stats.st_size,
                )
        return files


def hash_file_sha1(file_path: str | Path) -> str:
    hash_sha1 = hashlib.sha1()
    try:
        with open(file_path, "rb") as file:
            while chunk := file.read(4096):
                hash_sha1.update(chunk)
        return hash_sha1.hexdigest()
    except FileNotFoundError:
        logging.error(f"File not found for hashing: {file_path}")
    except PermissionError:
        logging.error(f"Permission denied reading file: {file_path}")
    except Exception as e:
        logging.error(f"Error hashing file {file_path}: {e}")
    return ""


def setup_logger(log_path):
    logging.basicConfig(
        filename=log_path,
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
    )
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    console.setFormatter(formatter)
    logger = logging.getLogger()
    logger.addHandler(console)
    return logger


def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Synchronize files from a SOURCE folder to a TARGET folder."
    )
    parser.add_argument("source_path", type=str, help="Path to the source folder")
    parser.add_argument("target_path", type=str, help="Path to the target folder")
    parser.add_argument(
        "sync_period", type=int, help="Interval between synchronization in seconds"
    )
    parser.add_argument(
        "sync_amount", type=int, help="Amount of synchronizations (integer)"
    )
    parser.add_argument("log_path", type=str, help="Path to the log file")
    return parser.parse_args()


def main() -> None:
    args = parse_arguments()

    source_path = Path(args.source_path)
    target_path = Path(args.target_path)
    sync_period = args.sync_period
    sync_amount = args.sync_amount
    log_path = Path(args.log_path)
    logger = setup_logger(log_path)
    try:
        if not all([source_path.exists(), target_path.exists(), log_path.exists()]):
            logger.warning("Ensure all paths exist in the system")
            return

        sync_manager = SyncManager(source_path, target_path, logger)

        while sync_amount > 0:
            try:
                sync_manager.sync()
            except Exception as e:
                logger.error(f"An error occurred during synchronization: {e}")
            logger.info(f"Sleeping for {sync_period} seconds...")
            time.sleep(sync_period)
            sync_amount -= 1

    except KeyboardInterrupt:
        logger.info("Interrupted by user.")
    except Exception as e:
        logger.error(f"Fatal error: {e}")


if __name__ == "__main__":
    main()
