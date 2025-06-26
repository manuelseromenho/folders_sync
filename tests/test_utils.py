from pathlib import Path

from src.__main__ import hash_file_sha1


def test_hash_nonexistent_file():
    fake_path = Path("/this/path/does/not/exist.txt")
    result = hash_file_sha1(fake_path)
    assert result == ""
