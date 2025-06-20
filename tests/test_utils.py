from src.utils import copy_file, hash_file_sha1


def test_copy_file(tmp_path):
    source = tmp_path / "source"
    target = tmp_path / "target"
    source.mkdir()
    target.mkdir()

    file_name = "testfile.txt"
    source_file = source / file_name
    source_file.write_text("content")

    source_hash = hash_file_sha1(source_file)

    copy_file(source, target, file_name)

    target_file_path = target / file_name
    assert target_file_path.exists()

    target_hash = hash_file_sha1(target_file_path)
    assert source_hash == target_hash

    assert (target / file_name).read_text() == "content"
