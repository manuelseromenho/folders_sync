import math
from shutil import copy2


def copy_file(source_path, target_path, file_name):
    copy2(f"{source_path}/{file_name}", f"{target_path}/{file_name}")


def convert_size(size_bytes):
    """
    Converts size in bytes to human readable string.

    :param size_bytes: bytes
    :return: string
    """
    if size_bytes == 0:
        return "0B"
    size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
    i = int(math.floor(math.log(size_bytes, 1024)))
    p = math.pow(1024, i)
    s = round(size_bytes / p, 2)
    return f"{s} {size_name[i]}"
