import hashlib
from shutil import copy2


def copy_file(source_path, target_path, file_name):
    copy2(f"{source_path}/{file_name}", f"{target_path}/{file_name}")


def get_files(path):
    files = [entry for entry in path.iterdir() if entry.is_file()]
    return files


def hash_file_sha1(file_path):
    hash_sha1 = hashlib.sha1()
    with open(file_path, "rb") as file:
        while chunk := file.read(4096):
            hash_sha1.update(chunk)
    return hash_sha1.hexdigest()
