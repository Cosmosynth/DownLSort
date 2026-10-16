"""File category definitions for DownLSort.

This module is the single source of truth mapping file extensions to
categories. Matching is case-insensitive. Anything not listed falls back
to :data:`OTHER`.
"""

APPLICATIONS = "Applications"
DOCUMENTS = "Documents"
IMAGES = "Images"
VIDEOS = "Videos"
AUDIO = "Audio"
ARCHIVES = "Archives"
OTHER = "Other"

#: Categories in the order they appear as filter chips in the GUI.
CATEGORIES = (APPLICATIONS, DOCUMENTS, IMAGES, VIDEOS, AUDIO, ARCHIVES, OTHER)

_IMAGE = {
    ".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp", ".svg",
    ".tiff", ".tif", ".ico", ".heic", ".heif", ".avif",
    ".cr2", ".nef", ".arw", ".dng", ".psd",
}

_DOCUMENT = {
    ".pdf", ".doc", ".docx", ".odt", ".rtf", ".txt", ".md",
    ".epub", ".mobi", ".azw3",
    ".xls", ".xlsx", ".ods", ".csv",
    ".ppt", ".pptx", ".odp", ".key",
    ".pages", ".numbers",
}

_VIDEO = {
    ".mp4", ".mkv", ".avi", ".mov", ".wmv", ".flv",
    ".webm", ".m4v", ".mpg", ".mpeg", ".3gp", ".ts",
}

_AUDIO = {
    ".mp3", ".wav", ".flac", ".aac", ".ogg", ".m4a",
    ".wma", ".opus", ".mid", ".midi", ".aiff",
}

_ARCHIVE = {
    ".zip", ".rar", ".7z", ".tar", ".gz", ".bz2", ".xz",
    ".cab", ".iso", ".dmg",
    ".tar.gz", ".tar.bz2", ".tar.xz", ".tgz",
}

_APPLICATION = {
    ".exe", ".msi", ".bat", ".cmd", ".com", ".scr",
    ".pkg", ".deb", ".rpm", ".apk", ".appimage",
}

_EXTENSION_MAP = {}
for _category, _extensions in (
    (IMAGES, _IMAGE),
    (DOCUMENTS, _DOCUMENT),
    (VIDEOS, _VIDEO),
    (AUDIO, _AUDIO),
    (ARCHIVES, _ARCHIVE),
    (APPLICATIONS, _APPLICATION),
):
    for _ext in _extensions:
        _EXTENSION_MAP[_ext] = _category


def _candidate_suffixes(filename: str) -> list:
    """Return suffix candidates for *filename*, longest first.

    "backup.tar.gz" -> [".tar.gz", ".gz"], so compound archive
    extensions win over their trailing part.
    """
    parts = filename.lower().split(".")
    if len(parts) < 2:
        return []
    return ["." + ".".join(parts[i:]) for i in range(1, len(parts) - 1)] + [
        "." + parts[-1]
    ]


def categorize(filename: str) -> str:
    """Return the category for a file name (case-insensitive)."""
    for suffix in _candidate_suffixes(filename):
        if suffix in _EXTENSION_MAP:
            return _EXTENSION_MAP[suffix]
    return OTHER


def display_extension(filename: str) -> str:
    """Return the extension to show on a file card, e.g. ".pdf"."""
    for suffix in _candidate_suffixes(filename):
        if suffix in _EXTENSION_MAP:
            return suffix
    # Fall back to the plain trailing suffix (or "" when there is none).
    name = filename.lower()
    dot = name.rfind(".")
    if dot > 0:
        return name[dot:]
    return ""
