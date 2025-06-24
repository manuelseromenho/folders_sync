import hashlib
import logging


def hash_file_sha1(file_path):
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
