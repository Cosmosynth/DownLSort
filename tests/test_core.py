"""Tests for category mapping, scanning, organizing, and history."""

from pathlib import Path

from downlsort import categories
from downlsort.categories import (
    APPLICATIONS,
    ARCHIVES,
    AUDIO,
    DOCUMENTS,
    IMAGES,
    OTHER,
    VIDEOS,
)
from downlsort.history import HistoryLog
from downlsort.organizer import (
    execute_moves,
    plan_moves,
    remove_empty_dirs,
    restore_moves,
    unique_destination,
)
from downlsort.scanner import FileItem, format_size, scan_folder


def test_categorize_common_extensions():
    assert categories.categorize("photo.JPG") == IMAGES
    assert categories.categorize("report.pdf") == DOCUMENTS
    assert categories.categorize("movie.mkv") == VIDEOS
    assert categories.categorize("song.flac") == AUDIO
    assert categories.categorize("backup.tar.gz") == ARCHIVES
    assert categories.categorize("setup.exe") == APPLICATIONS


def test_categorize_is_case_insensitive_and_compound():
    assert categories.categorize("ARCHIVE.TGZ") == ARCHIVES
    assert categories.categorize("notes.TXT") == DOCUMENTS


def test_categorize_unknown_goes_to_other():
    assert categories.categorize("script.py") == OTHER
    assert categories.categorize("noextension") == OTHER
    assert categories.categorize(".gitignore") == OTHER


def test_display_extension_prefers_compound():
    assert categories.display_extension("backup.tar.gz") == ".tar.gz"
    assert categories.display_extension("PHOTO.JPG") == ".jpg"
    assert categories.display_extension("README") == ""


def test_format_size():
    assert format_size(0) == "0 B"
    assert format_size(512) == "512 B"
    assert format_size(2048) == "2.0 KB"
    assert format_size(int(2.4 * 1024 * 1024)) == "2.4 MB"


def test_scan_folder_lists_only_top_level_files(tmp_path: Path):
    (tmp_path / "b.pdf").write_text("x")
    (tmp_path / "a.jpg").write_text("xx")
    (tmp_path / "Images").mkdir()  # subdir must be ignored
    (tmp_path / "Images" / "nested.jpg").write_text("nested")

    items = scan_folder(tmp_path)

    assert [i.name for i in items] == ["a.jpg", "b.pdf"]
    assert items[0].category == IMAGES
    assert items[0].size == 2
    assert items[1].category == DOCUMENTS


def test_scan_missing_folder_returns_empty(tmp_path: Path):
    assert scan_folder(tmp_path / "does-not-exist") == []


def test_plan_moves_targets_category_subfolders(tmp_path: Path):
    items = [
        FileItem(path=tmp_path / "a.jpg", size=1, category=IMAGES),
        FileItem(path=tmp_path / "b.pdf", size=1, category=DOCUMENTS),
    ]
    moves = plan_moves(tmp_path, items)
    assert moves[0].dst == tmp_path / "Images" / "a.jpg"
    assert moves[1].dst == tmp_path / "Documents" / "b.pdf"


def test_unique_destination_never_overwrites(tmp_path: Path):
    target = tmp_path / "photo.jpg"
    target.write_text("original")
    assert unique_destination(target) == tmp_path / "photo (1).jpg"
    (tmp_path / "photo (1).jpg").write_text("second")
    assert unique_destination(target) == tmp_path / "photo (2).jpg"
    assert unique_destination(tmp_path / "fresh.jpg") == tmp_path / "fresh.jpg"


def test_execute_moves_moves_files_and_creates_folders(tmp_path: Path):
    src = tmp_path / "song.mp3"
    src.write_text("audio")
    moves = plan_moves(tmp_path, [FileItem(path=src, size=5, category=AUDIO)])

    result = execute_moves(moves)

    assert result.ok
    assert (tmp_path / "Audio" / "song.mp3").exists()
    assert not src.exists()


def test_execute_moves_continues_past_failures(tmp_path: Path):
    good = tmp_path / "ok.txt"
    good.write_text("ok")
    missing = tmp_path / "gone.txt"  # never created
    items = [
        FileItem(path=good, size=2, category=DOCUMENTS),
        FileItem(path=missing, size=0, category=DOCUMENTS),
    ]

    result = execute_moves(plan_moves(tmp_path, items))

    assert not result.ok
    assert len(result.moved) == 1
    assert len(result.errors) == 1
    assert (tmp_path / "Documents" / "ok.txt").exists()


def test_restore_moves_undoes_a_sort(tmp_path: Path):
    src = tmp_path / "clip.mp4"
    src.write_text("video")
    executed = execute_moves(
        plan_moves(tmp_path, [FileItem(path=src, size=5, category=VIDEOS)])
    )

    result = restore_moves(executed.moved)

    assert result.ok
    assert src.exists()
    assert not (tmp_path / "Videos" / "clip.mp4").exists()


def test_remove_empty_dirs(tmp_path: Path):
    empty = tmp_path / "Images"
    empty.mkdir()
    full = tmp_path / "Audio"
    full.mkdir()
    (full / "x.mp3").write_text("x")

    remove_empty_dirs(tmp_path, ["Images", "Audio", "Missing"])

    assert not empty.exists()
    assert full.exists()


def test_history_record_and_reload(tmp_path: Path):
    log = HistoryLog(tmp_path / "history.json")
    assert log.latest_pending() is None

    from downlsort.organizer import PlannedMove

    log.record([PlannedMove(src=tmp_path / "a", dst=tmp_path / "b")])

    reloaded = HistoryLog(tmp_path / "history.json")
    pending = reloaded.latest_pending()
    assert pending is not None
    assert len(pending.moves) == 1
    assert not pending.undone


def test_history_mark_undone_hides_session(tmp_path: Path):
    from downlsort.organizer import PlannedMove

    log = HistoryLog(tmp_path / "history.json")
    session = log.record([PlannedMove(src=tmp_path / "a", dst=tmp_path / "b")])
    log.mark_undone(session)

    assert HistoryLog(tmp_path / "history.json").latest_pending() is None


def test_history_corrupt_file_starts_empty(tmp_path: Path):
    hist = tmp_path / "history.json"
    hist.write_text("not valid json {{{")
    assert HistoryLog(hist).latest_pending() is None


def test_full_sort_unsort_roundtrip(tmp_path: Path):
    (tmp_path / "pic.png").write_text("img")
    (tmp_path / "doc.pdf").write_text("doc")
    # History lives outside the managed folder (as in production).
    log = HistoryLog(tmp_path / "meta" / "history.json")

    items = scan_folder(tmp_path)
    executed = execute_moves(plan_moves(tmp_path, items))
    assert executed.ok and len(executed.moved) == 2
    log.record(executed.moved)
    assert scan_folder(tmp_path) == []

    session = log.latest_pending()
    assert session is not None
    restored = restore_moves(session.moves)
    assert restored.ok
    log.mark_undone(session)
    remove_empty_dirs(tmp_path, list(categories.CATEGORIES))

    assert sorted(p.name for p in tmp_path.iterdir() if p.is_file()) == [
        "doc.pdf",
        "pic.png",
    ]
