import hashlib
import logging
import math
import os
import sys
import time
from datetime import datetime
from pathlib import Path
from shutil import copy2

USAGE = f"Usage: python {sys.argv[0]} [--help] | source_path target_path sync_period]"


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


def list_files(path):
    files = [entry for entry in path.iterdir() if entry.is_file()]
    print(*files, sep="\n")
    return files


def convert_size(size_bytes):
    if size_bytes == 0:
        return "0B"
    size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
    i = int(math.floor(math.log(size_bytes, 1024)))
    p = math.pow(1024, i)
    s = round(size_bytes / p, 2)
    return f"{s} {size_name[i]}"


def creating_files_obj(files_list):
    files = {}
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


def hash_file_sha1(file_path):
    hash_sha1 = hashlib.sha1()
    with open(file_path, "rb") as file:
        while chunk := file.read(4096):
            hash_sha1.update(chunk)
    return hash_sha1.hexdigest()


def copy_file(source_path, target_path, file_name):
    copy2(f"{source_path}/{file_name}", f"{target_path}/{file_name}")
    logging.info(f"file {source_path}/{file_name} was updated/copied to {target_path}/{file_name}")


def sync_folders(source_path, target_path, sync_period, log_path):

    if source_path.exists():
        print("Source path exists")
        source_files = list_files(source_path)
        source_files_obj = creating_files_obj(source_files)
        print("\n")
    if target_path.exists():
        print("Target path exists")
        target_files = list_files(target_path)
        target_files_obj = creating_files_obj(target_files)
        print("\n")

    for file in target_files:
        target_file = target_files_obj.get(file.name)
        source_file = source_files_obj.get(file.name)

        if target_file is not None and source_file is None:
            os.remove(f"{target_path}/{file.name}")
            logging.info(f"file {target_path}/{file.name} deleted")

    for file in source_files:
        target_file = target_files_obj.get(file.name)
        source_file = source_files_obj.get(file.name)

        if target_file is not None and target_file.file_name == source_file.file_name:
            if target_file.file_size != source_file.file_size:
                copy_file(source_path, target_path, file.name)
            else:
                target_hash = hash_file_sha1(f"{target_path}/{file.name}")
                source_hash = hash_file_sha1(f"{source_path}/{file.name}")
                if target_hash != source_hash:
                    copy_file(source_path, target_path, file.name)

        elif source_file is not None and target_file is None:
            copy_file(source_path, target_path, file.name)


def main() -> None:
    args = sys.argv[1:]
    if len(args) < 2:
        raise SystemExit(USAGE)

    source_path = Path(args[0])
    target_path = Path(args[1])
    sync_period = int(args[2])
    log_path = Path(args[3])

    logging.basicConfig(filename=log_path, level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    console.setFormatter(formatter)
    logging.getLogger().addHandler(console)

    while True:
        logging.info("Starting synchronization")
        sync_folders(source_path, target_path, sync_period, log_path)
        logging.info("Synchronization completed")
        print(f"Sleeping for {sync_period} seconds...")
        time.sleep(sync_period)


if __name__ == "__main__":
    main()
