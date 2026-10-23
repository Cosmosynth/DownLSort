<p align="center">
  <img src="src/downlsort/assets/downlsort-logo.png" alt="DownLSort icon" width="96">
</p>

<h1 align="center">DownLSort</h1>

<p align="center">Organize a cluttered Downloads folder — preview, sort by type, and undo with one click.</p>

![DownLSort screenshot](assets/Design/image.png)

## Quick start

### Windows (no Python needed)

Download `DownLSort.exe` from the [Releases page](https://github.com/Cosmosynth/DownLSort/releases) and double-click it. If no release is available yet, [build the EXE](#build-a-windows-exe).

> The build is unsigned, so SmartScreen may appear: choose **More info → Run anyway**.

### From source (Python 3.10+)

```bash
git clone https://github.com/Cosmosynth/DownLSort.git
cd DownLSort
python -m venv .venv
```

Activate the environment:

- **Windows:** `.\.venv\Scripts\Activate.ps1`
- **macOS / Linux:** `source .venv/bin/activate`

Then install and run:

```bash
pip install -e .
downlsort
```

On Linux, Tk may need to be installed separately (`sudo apt install python3-tk`, or the equivalent for your distro). If `downlsort` is not recognized, use `python -m downlsort`.

## Usage

The app opens your Downloads folder by default. Click the `Path:` label to choose another folder, review the preview, then press **Sort** and confirm.

| Button | Action |
|---|---|
| **Refresh** | Re-scan the current folder |
| **Sort** | Move files into category subfolders |
| **Unsort** | Move the last sorted files back |
| `Path:` label | Choose a different folder |

Command line:

```bash
downlsort --path "D:\Temp"          # organize another folder
python -m downlsort --path "D:\Temp" # same, without the installed script
downlsort --version
```

## Features

- **Live preview** — nothing moves until you confirm the sort plan.
- **Category filters** — browse the grid without moving files.
- **Safe by design** — never overwrites; conflicts become `file (1).pdf`.
- **Robust** — locked files are skipped and reported while the rest continue.
- **Exact undo** — every sort is logged and can be reversed, newest first.

**Good to know:** only top-level files move; existing subfolders are untouched. Unsort history lives at `%APPDATA%\DownLSort\history.json` on Windows and `~/.config/downlsort/history.json` elsewhere.

## Categories

| Category | Examples |
|---|---|
| Applications | `.exe` `.msi` `.bat` `.dmg` `.deb` `.apk` |
| Documents | `.pdf` `.docx` `.txt` `.md` `.xlsx` `.pptx` `.epub` |
| Images | `.jpg` `.png` `.gif` `.webp` `.svg` `.heic` |
| Videos | `.mp4` `.mkv` `.avi` `.mov` `.webm` |
| Audio | `.mp3` `.wav` `.flac` `.m4a` `.opus` |
| Archives | `.zip` `.rar` `.7z` `.tar.gz` `.iso` |
| Other | everything else, including extensionless files |

Extend the mapping in [`src/downlsort/categories.py`](src/downlsort/categories.py).

## Development

```bash
pip install -e ".[dev]"
python -m pytest        # 18 tests
```

Build the Windows EXE (creates `dist\DownLSort.exe`, which is git-ignored):

```powershell
powershell -ExecutionPolicy Bypass -File build_exe.ps1
```

To regenerate the icons after editing `assets/downlsort-logo.svg`:

```bash
pip install pillow
python tools/make_icon.py
```

## Troubleshooting

- `'downlsort' is not recognized` — activate `.venv`, or run `python -m downlsort`.
- `ModuleNotFoundError: customtkinter` — install into the active environment: `pip install -e .`.
- `No module named '_tkinter'` — install Tk for your OS (see above).
- Files fail to sort — close programs using them, then **Refresh** and retry.
- EXE build can't delete the old file — close the running app first.

## License

MIT — see [`pyproject.toml`](pyproject.toml).
