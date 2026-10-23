<p align="center">
  <img src="src/downlsort/assets/downlsort-logo.png" alt="DownLSort icon" width="96">
</p>

<h1 align="center">DownLSort</h1>

A clean, modern desktop app that organizes a cluttered **Downloads** folder.
Files are grouped by type into subfolders, with a live preview, one-click
sorting, and an **Unsort** button that puts every file back exactly where it
came from.

![DownLSort screenshot](assets/Design/image.png)

## Features

- **Sort by category** — moves top-level files into `Applications`,
  `Documents`, `Images`, `Videos`, `Audio`, `Archives`, or `Other`
  (extension-based, case-insensitive, and handles compound extensions
  such as `.tar.gz`).
- **Live preview** — the grid shows exactly what will be moved before
  anything happens, and a confirmation dialog summarizes the plan
  ("Move 42 files into 5 folders?").
- **Unsort** — reverses the last sort exactly, using a persistent JSON
  movement log. Press it again to walk back through older sorts.
- **Category filter chips** — filter the grid without moving anything.
- **Safe by design** — never overwrites a file (conflicts become
  `file (1).pdf`). If one file fails (in use, permission denied), the rest
  still move and the failures are reported. Sorting runs in a background
  thread, so the window never freezes.
- **Any folder** — click the `Path:` label to pick a different folder, or
  pass `--path` on the command line.

---

## Quick start

Pick the option that fits you.

### Option A — Windows, no Python installed

1. Check the [Releases page](https://github.com/Cosmosynth/DownLSort/releases)
   for `DownLSort.exe` and download it. No release listed yet? Build it once
   yourself — see [Build a Windows EXE](#build-a-windows-exe).
2. Put the `.exe` anywhere you like and double-click it. There is nothing to
   install and no terminal window opens.
3. The app scans `C:\Users\<you>\Downloads` on first launch.

> **Windows SmartScreen:** the executable is not code-signed, so Windows may
> show "Windows protected your PC". Click **More info → Run anyway**.

### Option B — Run from source (Windows, macOS, Linux)

Requires **Python 3.10 or newer**.

```bash
# 1. Get the code
git clone https://github.com/Cosmosynth/DownLSort.git
cd DownLSort

# 2. Create and activate a virtual environment
python -m venv .venv
```

Windows (PowerShell):

```powershell
.\.venv\Scripts\Activate.ps1
```

macOS / Linux:

```bash
source .venv/bin/activate
```

Then, with the environment active:

```bash
# 3. Install the app (pulls in customtkinter)
python -m pip install --upgrade pip
pip install -e .

# 4. Run it
downlsort
```

If `downlsort` is not recognized, `python -m downlsort` does the same thing.

> If PowerShell refuses to activate the environment ("running scripts is
> disabled"), run
> `Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned`
> once, or use `.\.venv\Scripts\activate.bat` from `cmd.exe`.

### Requirements

| Requirement | Notes |
|---|---|
| Python 3.10+ | Only for Option B |
| Tkinter | Bundled with the official Windows/macOS installers |
| `customtkinter` | Installed automatically by `pip install -e .` |
| Desktop session | It is a GUI app; WSL/headless servers won't work |

**Linux only:** Tkinter is usually a separate package.

```bash
sudo apt install python3-tk        # Debian / Ubuntu / Mint
sudo dnf install python3-tkinter   # Fedora
sudo pacman -S tk                  # Arch
```

---

## Using the app

1. **Launch it.** The default folder is your Downloads folder.
2. **Check the preview.** Every file in the folder appears as a card, with
   its size and category. Use the chips (`All`, `Documents`, `Images`, …) to
   filter the view — filtering never moves anything.
3. **Sort.** Click **Sort**. A dialog shows how many files go into which
   folders. Confirm, and the files move into category subfolders.
4. **Changed your mind?** Click **Unsort**. Files return to their original
   names and locations, and empty category folders are removed.
5. **Different folder?** Click the `Path: …` text under the title and pick
   a folder, or start with `--path` (see below).

| Button | What it does |
|---|---|
| **Refresh** | Re-scans the current folder and updates the grid |
| **Sort** | Shows the plan, then moves files into category folders |
| **Unsort** | Moves the most recently sorted files back |
| `Path:` label (click) | Choose a different folder to organize |

The status bar at the bottom shows how many files were found. `0 file(s) —
all organized` means there is nothing left at the top level to sort.

### Command line

```bash
downlsort                              # organize ~/Downloads (or %USERPROFILE%\Downloads)
downlsort --path "D:\Temp"             # organize another folder
python -m downlsort --path "D:\Temp"   # same, without the console script
downlsort --version
```

The GUI is required; `--path` only chooses the starting folder.

---

## What gets touched (and what doesn't)

- Only **files directly inside** the chosen folder are moved. Existing
  subfolders and their contents are left alone.
- **Nothing is ever overwritten.** If `Images/photo.jpg` already exists, the
  incoming file is saved as `Images/photo (1).jpg`.
- **Unsort is one level deep:** each press reverses one previous sort, newest
  first. Files you deleted or moved manually since sorting are skipped and
  reported, not treated as fatal.
- If a file is locked by another program, that one file is skipped and the
  rest of the sort continues.

### Where the undo history lives

Every sort appends a session to a JSON file kept **outside** the organized
folder, so cleaning up that folder can't destroy your ability to undo:

- Windows: `%APPDATA%\DownLSort\history.json`
- macOS / Linux: `~/.config/downlsort/history.json`

Deleting this file only forgets the undo history — it never moves or deletes
your files. The app creates it automatically on the first sort.

---

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

The full mapping lives in one place: [`src/downlsort/categories.py`](src/downlsort/categories.py).
Unknown extensions go to `Other`; add new ones there.

---

## Troubleshooting

| Problem | Fix |
|---|---|
| `'downlsort' is not recognized` | Activate the virtual environment first, or run `python -m downlsort` |
| `ModuleNotFoundError: customtkinter` | The install went to a different Python. Activate `.venv` and re-run `pip install -e .` |
| `No module named '_tkinter'` / `tkinter` (Linux) | Install the system Tk package — see [Requirements](#requirements) |
| `ModuleNotFoundError: downlsort` when running `python -m downlsort` | Run the command from the project root after `pip install -e .` |
| App opens with an empty grid | The folder has no top-level files, or the path is wrong. Click `Path:` to change it, then **Refresh** |
| "Could not delete the old EXE" while building | Close any running `DownLSort.exe`, then rebuild |
| Some files failed to sort | They are open in another program or read-only. Close them, click **Refresh**, and sort again |
| EXE flagged by SmartScreen / antivirus | Expected for an unsigned one-file PyInstaller build. Use "More info → Run anyway", or run from source |

If the app crashes before the window appears, run it from a terminal
(`python -m downlsort`) so the traceback stays visible.

---

## Development

Install the dev extras (pytest, PyInstaller, Pillow):

```bash
pip install -e ".[dev]"
```

Run the test suite:

```bash
python -m pytest
```

18 tests cover category mapping, scanning, conflict-safe moves, the
sort/unsort round-trip, and bundled assets. They only use temporary
directories — your real Downloads folder is never touched.

### Project structure

```
src/downlsort/
├── __init__.py     # version
├── __main__.py     # `python -m downlsort`
├── main.py         # CLI entry point (--path, --version)
├── app.py          # main window: header, chips, grid, wiring
├── widgets.py      # FileCard + ChipBar components
├── categories.py   # extension → category table
├── scanner.py      # folder scan → FileItem list
├── organizer.py    # move planning + conflict-safe execution
├── history.py      # persistent JSON log + undo bookkeeping
└── assets/         # generated icons (see tools/make_icon.py)
    ├── downlsort-logo.png   # window + taskbar icon (Tk)
    └── downlsort-logo.ico   # EXE icon (multi-size)
tests/test_core.py  # 18 tests: mapping, scan, moves, undo round-trip, assets
build_exe.ps1       # one-shot Windows EXE build
tools/make_icon.py  # artwork (SVG) → PNG/ICO
assets/
├── downlsort-logo.svg    # source artwork for the icon
└── Design/image.png      # UI screenshot
pyproject.toml      # packaging, dependencies, pytest config
```

Core logic (`categories`, `scanner`, `organizer`, `history`) is
GUI-independent and fully unit-tested.

---

## Build a Windows EXE

Build this on Windows to hand the app to someone who does not have Python.
Requires the dev extras (they include PyInstaller):

```powershell
pip install -e ".[dev]"
powershell -ExecutionPolicy Bypass -File build_exe.ps1
```

This produces `dist\DownLSort.exe` (~30 MB, one file, no console window).
Double-clicking it opens the app directly — no Python needed on the target
machine. `dist\` is git-ignored, so download the EXE from Releases or build
it locally; it is not checked into the repository.

The build script:

- uses `--windowed` so no terminal flashes behind the GUI,
- passes `--collect-all customtkinter` so theme assets are bundled,
- embeds `src\downlsort\assets\downlsort-logo.ico` as the Explorer/taskbar icon,
- ships the window icon with `--add-data "src\downlsort\assets;downlsort\assets"`,
- launches `src\downlsort\main.py` as the entry point so relative imports
  resolve when frozen.

Share the EXE as a zip, or wrap it in an installer (Inno Setup, MSIX) if you
want a Start Menu entry.

### Icon / artwork

The logo source is `assets/downlsort-logo.svg`. The PNG (window icon) and
multi-size ICO (EXE icon) are generated from it:

```bash
pip install pillow            # only needed to regenerate icons
python tools/make_icon.py     # SVG → src/downlsort/assets/*.png/.ico
```

Re-run that after editing the artwork, then rebuild the EXE.

---

## License

MIT — see [`pyproject.toml`](pyproject.toml).
