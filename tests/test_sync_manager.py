import logging
from unittest import mock

from src.sync_manager import SyncManager


def test_sync_copies_new_file(tmp_path, caplog):
    source = tmp_path / "source"
    target = tmp_path / "target"
    source.mkdir()
    target.mkdir()

    file_name = "test1.txt"
    content = "test1..."
    (source / file_name).write_text(content)

    logger = logging.getLogger("test")
    caplog.set_level(logging.INFO)

    manager = SyncManager(source, target, logger)
    manager.sync()

    target_file = target / file_name
    assert target_file.exists()
    assert target_file.read_text() == content
    assert f"was copied to {target_file}" in caplog.text


def test_copy_file_overwrites(tmp_path, caplog):
    source = tmp_path / "source"
    target = tmp_path / "target"
    source.mkdir()
    target.mkdir()

    file_name = "test1.txt"

    source_file = source / file_name
    target_file = target / file_name
    source_file.write_text("new content")
    target_file.write_text("old content")

    logger = logging.getLogger("test1")
    caplog.set_level(logging.INFO)

    manager = SyncManager(source, target, logger)
    manager.sync()

    assert target_file.read_text() == "new content"
    assert f"was updated to {target_file}" in caplog.text


def test_sync_removes_extra_file(tmp_path, caplog):
    source = tmp_path / "source"
    target = tmp_path / "target"
    source.mkdir()
    target.mkdir()

    file_name = "obsolete.txt"
    (target / file_name).write_text("old content")

    logger = logging.getLogger("test")
    caplog.set_level(logging.INFO)

    manager = SyncManager(source, target, logger)
    manager.sync()

    assert not (target / file_name).exists()
    assert f"file {target / file_name} deleted" in caplog.text


def test_sync_updates_changed_file(tmp_path, caplog):
    source = tmp_path / "source"
    target = tmp_path / "target"
    source.mkdir()
    target.mkdir()

    file_name = "file.txt"
    (source / file_name).write_text("new content")
    (target / file_name).write_text("old content")

    logger = logging.getLogger("test")
    caplog.set_level(logging.INFO)

    manager = SyncManager(source, target, logger)
    manager.sync()

    assert (target / file_name).read_text() == "new content"
    assert f"was updated to {target / file_name}" in caplog.text


def test_sync_permission_error_logged(tmp_path, caplog):
    source = tmp_path / "source"
    target = tmp_path / "target"
    source.mkdir()
    target.mkdir()

    file_name = "protected.txt"
    (source / file_name).write_text("can't copy this")

    logger = logging.getLogger()
    caplog.set_level(logging.ERROR)

    manager = SyncManager(source, target, logger)

    with mock.patch(
        "src.sync_manager.copy2", side_effect=PermissionError("No permission")
    ):
        manager.sync()

    assert "Permission denied" in caplog.text or "No permission" in caplog.text


def test_sync_handles_file_not_found(tmp_path, caplog):
    source = tmp_path / "source"
    target = tmp_path / "target"
    source.mkdir()
    target.mkdir()

    file_name = "test1.txt"
    file_path = source / file_name
    file_path.write_text("test1")

    logger = logging.getLogger("test")
    caplog.set_level(logging.ERROR)

    manager = SyncManager(source, target, logger)
    with mock.patch(
        "src.sync_manager.copy2",
        side_effect=FileNotFoundError("File removed during copy"),
    ):
        manager.sync()

    assert "File not found" in caplog.text or "No such file" in caplog.text


def test_sync_skips_identical_files(tmp_path, caplog):
    source = tmp_path / "source"
    target = tmp_path / "target"
    source.mkdir()
    target.mkdir()

    file_name = "test1.txt"
    (source / file_name).write_text("identical1")
    (target / file_name).write_text("identical1")

    caplog.set_level(logging.INFO)
    logger = logging.getLogger("test")
    manager = SyncManager(source, target, logger)
    manager.sync()

    logs = caplog.text.lower()
    assert "copied" not in logs and "updated" not in logs


def test_sync_handles_nested_folders_gracefully(tmp_path):
    source = tmp_path / "source"
    target = tmp_path / "target"
    source.mkdir()
    target.mkdir()

    nested_dir = source / "subdir"
    nested_dir.mkdir()
    (nested_dir / "file.txt").write_text("ignore me")

    logger = logging.getLogger("test")
    manager = SyncManager(source, target, logger)
    manager.sync()

    assert not (target / "subdir").exists()
