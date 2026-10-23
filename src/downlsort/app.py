"""DownLSort main window."""

from __future__ import annotations

import os
import threading
import tkinter as tk
from tkinter import filedialog, messagebox
from pathlib import Path

import customtkinter as ctk

from . import categories
from .categories import CATEGORIES
from .history import HistoryLog
from .organizer import execute_moves, plan_moves, remove_empty_dirs, restore_moves
from .scanner import DEFAULT_FOLDER, FileItem, format_size, scan_folder
from .widgets import ChipBar, FileCard

BUTTON_BG = "#262626"
PANEL_BG = "#D9D9D9"
COLUMNS = 4


class App(ctk.CTk):
    """Clean, modern Downloads organizer."""

    def __init__(self, folder: str | Path | None = None) -> None:
        super().__init__()
        ctk.set_appearance_mode("light")

        self.folder = Path(folder) if folder else DEFAULT_FOLDER
        self.history = HistoryLog()
        self.items: list[FileItem] = []
        self.active_filter = "All"
        self._busy = False

        self.title("DownLSort")
        self.geometry("1000x700")
        self.minsize(640, 480)
        self.configure(fg_color="white")
        self._set_app_icon()
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        self._build_header()
        self._build_chips()
        self._build_grid()
        self._build_statusbar()

        self.refresh()

    # ------------------------------------------------------------------ layout

    def _build_header(self) -> None:
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=20, pady=(16, 4))
        header.grid_columnconfigure(0, weight=1)

        left = ctk.CTkFrame(header, fg_color="transparent")
        left.grid(row=0, column=0, sticky="w")
        ctk.CTkLabel(
            left, text="DownLSort", font=ctk.CTkFont(size=30, weight="bold"),
            anchor="w",
        ).pack(anchor="w")
        self.path_var = tk.StringVar(value=f"Path: {self.folder}")
        path_label = ctk.CTkLabel(
            left, textvariable=self.path_var, text_color="gray55",
            font=ctk.CTkFont(size=12), anchor="w", cursor="hand2",
        )
        path_label.pack(anchor="w")
        path_label.bind("<Button-1>", lambda _e: self.choose_folder())

        buttons = ctk.CTkFrame(header, fg_color="transparent")
        buttons.grid(row=0, column=1, sticky="e")
        self.refresh_btn = self._action_button(
            buttons, "Refresh", self.refresh, col=0)
        self.sort_btn = self._action_button(
            buttons, "Sort", self.sort_files, col=1)
        self.unsort_btn = self._action_button(
            buttons, "Unsort", self.unsort_files, col=2)

    def _action_button(self, master, text, command, col) -> ctk.CTkButton:
        btn = ctk.CTkButton(
            master, text=text, command=command, width=90, height=32,
            corner_radius=9, fg_color=BUTTON_BG, hover_color="#3D3D3D",
            text_color="white", font=ctk.CTkFont(size=14),
        )
        btn.grid(row=0, column=col, padx=(8, 0))
        return btn

    def _build_chips(self) -> None:
        self.chips = ChipBar(
            self, chips=["All", *CATEGORIES], on_select=self.apply_filter)
        self.chips.grid(row=1, column=0, sticky="w", padx=20, pady=(10, 10))

    def _build_grid(self) -> None:
        self.grid_panel = ctk.CTkScrollableFrame(
            self, fg_color=PANEL_BG, corner_radius=12)
        self.grid_panel.grid(
            row=2, column=0, sticky="nsew", padx=20, pady=(0, 8))

    def _build_statusbar(self) -> None:
        self.status_var = tk.StringVar(value="")
        ctk.CTkLabel(
            self, textvariable=self.status_var, text_color="gray55",
            font=ctk.CTkFont(size=12), anchor="w",
        ).grid(row=3, column=0, sticky="w", padx=22, pady=(0, 12))

    # ------------------------------------------------------------------ actions

    def choose_folder(self) -> None:
        if self._busy:
            return
        chosen = filedialog.askdirectory(
            title="Choose folder to organize", initialdir=str(self.folder))
        if chosen:
            self.folder = Path(chosen)
            self.refresh()

    def refresh(self) -> None:
        if self._busy:
            return
        self.items = scan_folder(self.folder)
        self.path_var.set(f"Path: {self.folder}")
        self._render()
        pending = self.history.latest_pending() is not None
        self.unsort_btn.configure(state="normal" if pending else "disabled")
        self.status_var.set(
            f"{len(self.items)} file(s)" + ("" if self.items else " — all organized"))

    def apply_filter(self, name: str) -> None:
        self.active_filter = name
        self._render()

    def sort_files(self) -> None:
        if self._busy or not self.items:
            return
        by_category: dict[str, int] = {}
        for item in self.items:
            by_category[item.category] = by_category.get(item.category, 0) + 1
        summary = ", ".join(f"{cat} ({n})" for cat, n in sorted(by_category.items()))
        if not messagebox.askyesno(
            "Sort files?",
            f"Move {len(self.items)} file(s) into {len(by_category)} folder(s)?\n\n{summary}",
        ):
            return
        self._run_in_background(
            "Sorting…",
            lambda: execute_moves(plan_moves(self.folder, self.items)),
            self._after_sort,
        )

    def unsort_files(self) -> None:
        if self._busy:
            return
        session = self.history.latest_pending()
        if session is None:
            messagebox.showinfo("Unsort", "Nothing to unsort.")
            return
        if not messagebox.askyesno(
            "Unsort files?",
            f"Move {len(session.moves)} file(s) back to their original locations?\n\nSorted at {session.timestamp}",
        ):
            return

        def work():
            result = restore_moves(session.moves)
            if result.moved:
                self.history.mark_undone(session)
                remove_empty_dirs(self.folder, list(CATEGORIES))
            return result

        self._run_in_background("Unsorting…", work, self._after_unsort)

    # ------------------------------------------------------------- background

    def _run_in_background(self, status: str, work, done) -> None:
        self._busy = True
        self._set_buttons_enabled(False)
        self.status_var.set(status)

        def runner() -> None:
            try:
                result = work()
            except Exception as exc:  # never let the worker die silently
                result = exc
            self.after(0, lambda: done(result))

        threading.Thread(target=runner, daemon=True).start()

    def _set_app_icon(self) -> None:
        """Use the bundled logo as the window/taskbar icon."""
        if os.name == "nt":
            # Without an explicit AppUserModelID, Windows groups the window
            # under python.exe and shows Python's icon on the taskbar.
            try:
                import ctypes

                ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(
                    "Cosmosynth.DownLSort"
                )
            except Exception:
                pass

        try:
            from importlib.resources import files

            assets = files("downlsort") / "assets"
            if os.name == "nt":
                # The multi-size ICO gives a crisp title-bar/taskbar icon.
                try:
                    self.iconbitmap(str(assets / "downlsort-logo.ico"))
                    return
                except Exception:
                    pass  # Fall back to the PNG below.

            icon = assets / "downlsort-logo.png"
            # Keep a reference: Tkinter deletes the image when the Python
            # object is garbage collected, which would drop the icon.
            self._window_icon = tk.PhotoImage(file=str(icon))
            self.iconphoto(True, self._window_icon)
        except Exception:
            # A missing/invalid icon must never stop the app from starting.
            pass

    def _set_buttons_enabled(self, enabled: bool) -> None:
        state = "normal" if enabled else "disabled"
        for btn in (self.refresh_btn, self.sort_btn, self.unsort_btn):
            btn.configure(state=state)

    def _after_sort(self, result) -> None:
        self._busy = False
        self._set_buttons_enabled(True)
        if isinstance(result, Exception):
            messagebox.showerror("Sort failed", str(result))
            self.refresh()
            return
        if result.moved:
            self.history.record(result.moved)
        self.refresh()
        self._report("Sorted", result)

    def _after_unsort(self, result) -> None:
        self._busy = False
        self._set_buttons_enabled(True)
        if isinstance(result, Exception):
            messagebox.showerror("Unsort failed", str(result))
            self.refresh()
            return
        self.refresh()
        self._report("Unsorted", result)

    @staticmethod
    def _report(action: str, result) -> None:
        message = f"{action} {len(result.moved)} file(s)."
        if result.errors:
            shown = "\n".join(result.errors[:10])
            extra = f"\n…and {len(result.errors) - 10} more." if len(result.errors) > 10 else ""
            messagebox.showerror(
                f"{action} — some files failed",
                f"{message}\n\n{shown}{extra}")
        else:
            messagebox.showinfo(action, message)

    # ---------------------------------------------------------------- rendering

    def _render(self) -> None:
        for child in self.grid_panel.winfo_children():
            child.destroy()
        visible = [
            item for item in self.items
            if self.active_filter == "All" or item.category == self.active_filter
        ]
        if not visible:
            ctk.CTkLabel(
                self.grid_panel,
                text="Nothing here — all organized" if not self.items
                else f"No {self.active_filter.lower()} files",
                text_color="gray45", font=ctk.CTkFont(size=14),
            ).pack(pady=40)
            return
        for idx, item in enumerate(visible):
            row, col = divmod(idx, COLUMNS)
            self.grid_panel.grid_columnconfigure(col, weight=1, uniform="cards")
            card = FileCard(
                self.grid_panel,
                name=item.name,
                size_text=format_size(item.size),
                ext_text=item.path.suffix.lower(),
            )
            card.grid(row=row, column=col, padx=8, pady=8, sticky="nsew")
