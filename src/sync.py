import hashlib
import logging
import os
from datetime import datetime
from zipfile import Path

from src.utils import convert_size, copy_file


class File:
    file_name = ""
    file_path = ""
    file_update_datetime = ""
    file_size = 0
    hash_value = ""

    def __init__(self, file_name, file_path, file_update_datetime, file_size, hash_value=""):
        self.file_name = file_name
        self.file_path = file_path
        self.file_update_datetime = file_update_datetime
        self.file_size = file_size
        self.hash_value = hash_value

    @staticmethod
    def hash_file_sha1(file_path):
        hash_sha1 = hashlib.sha1()
        with open(file_path, "rb") as file:
            while chunk := file.read(4096):
                hash_sha1.update(chunk)
        return hash_sha1.hexdigest()


class SyncManager:
    def __init__(self, source_path, target_path, logger):
        self.source_path = source_path
        self.target_path = target_path
        self.logger = logger

    def sync(self):
        self.logger.info("Starting synchronization")
        source_files = self._create_files_obj(self.source_path)
        target_files = self._create_files_obj(self.target_path)
        self._sync_folders(source_files, target_files)
        self.logger.info("Synchronization completed")

    def _create_files_obj(self, path):
        files = {}
        files_list = self._get_files(path)
        for file in files_list:
            file_stats = file.parent.stat()
            source_file = File(
                file_name=str(file.name),
                file_path=str(file),
                file_update_datetime=datetime.fromtimestamp(file.parent.stat().st_mtime).strftime("%Y-%m-%d %H:%M:%S"),
                file_size=convert_size(file_stats.st_size),
            )
            files[source_file.file_name] = source_file
        return files

    def _sync_folders(self, source_files, target_files):

        for file_name in target_files:
            source_file = source_files.get(file_name)

            if file_name is not None and source_file is None:
                os.remove(f"{self.target_path}/{file_name}")
                logging.info(f"file {self.target_path}/{file_name} deleted")

        for file_name in source_files:
            target_file = target_files.get(file_name)
            source_file = source_files.get(file_name)

            if source_file is not None and target_file is None:
                copy_file(self.source_path, self.target_path, file_name)
                logging.info(
                    f"file {self.source_path}/{file_name} was updated/copied to {self.target_path}/{file_name}"
                )
            elif target_file.file_size != source_file.file_size:
                copy_file(self.source_path, self.target_path, file_name)
                logging.info(
                    f"file {self.source_path}/{file_name} was updated/copied to {self.target_path}/{file_name}"
                )
            else:
                target_hash = target_file.hash_file_sha1(f"{self.target_path}/{file_name}")
                source_hash = source_file.hash_file_sha1(f"{self.source_path}/{file_name}")
                if target_hash != source_hash:
                    copy_file(self.source_path, self.target_path, file_name)
                    logging.info(
                        f"file {self.source_path}/{file_name} was updated/copied to {self.target_path}/{file_name}"
                    )

    @staticmethod
    def _get_files(path):
        files = [entry for entry in path.iterdir() if entry.is_file()]
        return files
