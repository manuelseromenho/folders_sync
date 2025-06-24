from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from shutil import copy2
from typing import Optional, Union

from .utils import hash_file_sha1


@dataclass
class FileToSync:
    file_name: str = ""
    file_path: Path = Path()
    file_update_datetime: str = ""
    file_size: int = 0
    hash_value: str = ""


class SyncManager:
    def __init__(self, source_path, target_path, logger):
        self.source_path = Path(source_path)
        self.target_path = Path(target_path)
        self.logger = logger
        self.source_files = None
        self.target_files = None

    def sync(self) -> None:
        self.logger.info("Starting synchronization")
        self.source_files = self._create_files_set(self.source_path)
        self.target_files = self._create_files_set(self.target_path)
        self._sync_folders()
        self.logger.info("Synchronization completed")

    def _sync_folders(self) -> None:
        self._sync_remove()

        for file_name in self.source_files:
            target_file = self.target_path / file_name
            source_file = self.source_path / file_name

            if not target_file.exists():
                self._sync_copy(source_file, target_file, file_name)
            elif target_file != source_file:
                self._sync_update(source_file, target_file, file_name)

    def _sync_remove(self) -> None:
        for file_name in self.target_files:
            try:
                if file_name not in self.source_files:
                    target_file = self.target_path / file_name
                    (self.target_path / file_name).unlink()
                    self.logger.info(f"file {self.target_path / file_name} deleted")
            except FileNotFoundError:
                self.logger.error(f"File not found: {target_file}")
            except PermissionError:
                self.logger.error(f"Permission denied while copying: {target_file}")
            except Exception as e:
                self.logger.error(f"Failed to copy {file_name}: {e}")

    def _sync_copy(
        self,
        source_file,
        target_file,
        file_name: Union[Path, str],
        msg_log: Optional[str] = None,
    ):
        try:
            copy2(source_file, target_file)
            if msg_log is None:
                msg_log = f"file {source_file} was copied to {target_file}"
            self.logger.info(msg_log)
        except FileNotFoundError:
            self.logger.error(f"File not found: {source_file}")
        except PermissionError:
            self.logger.error(f"Permission denied while copying: {source_file}")
        except Exception as e:
            self.logger.error(f"Failed to copy {file_name}: {e}")

    def _sync_update(
        self,
        source_file: Path,
        target_file: Path,
        file_name: Union[Path, str],
    ):
        msg_log = f"file {source_file} was updated to {target_file}"
        target_hash = hash_file_sha1(f"{self.target_path}/{file_name}")
        source_hash = hash_file_sha1(f"{self.source_path}/{file_name}")

        if target_file.stat().st_size != source_file.stat().st_size:
            self._sync_copy(source_file, target_file, file_name, msg_log)
        elif target_hash != source_hash:
            self._sync_copy(source_file, target_file, file_name, msg_log)

    @staticmethod
    def _create_files_set(path: Path) -> dict:
        files = {}
        for file in path.iterdir():
            if file.is_file():
                stats = file.stat()
                files[file.name] = FileToSync(
                    file_name=file.name,
                    file_path=file,
                    file_update_datetime=datetime.fromtimestamp(
                        stats.st_mtime
                    ).strftime("%Y-%m-%d %H:%M:%S"),
                    file_size=stats.st_size,
                )
        return files
