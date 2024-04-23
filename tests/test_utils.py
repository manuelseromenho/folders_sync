import os

from src.utils import copy_file, hash_file_sha1


def test_copy_file(tmpdir):
    source = tmpdir.mkdir("source")
    target = tmpdir.mkdir("targe")
    file_name = "testfile.txt"
    source_file = source.join(file_name)
    source_file.write("content")

    source_hash = hash_file_sha1(source_file)

    copy_file(str(source), str(target), file_name)

    target_file_path = os.path.join(target, file_name)
    assert os.path.exists(target_file_path)

    target_hash = hash_file_sha1(target_file_path)
    assert source_hash == target_hash

    with open(target_file_path, 'r') as file:
        content = file.read()
    assert content == "content"
