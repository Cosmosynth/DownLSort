"""CustomTkinter widgets for DownLSort: file cards and category chips."""

from __future__ import annotations

from collections.abc import Callable

import customtkinter as ctk

CARD_BG = "#ADADAD"
ICON_BG = "#D9D9D9"
ICON_FG = "#6E6E6E"
CHIP_BG = "#ADADAD"
CHIP_ACTIVE_BG = "#5A5A5A"


def truncate(text: str, limit: int = 24) -> str:
    """Shorten *text* with an ellipsis when it exceeds *limit* chars."""
    if len(text) <= limit:
        return text
    return text[: limit - 1] + "…"


class FileCard(ctk.CTkFrame):
    """A single file tile: icon + name on top, size + extension below."""

    def __init__(
        self,
        master,
        name: str,
        size_text: str,
        ext_text: str,
        **kwargs,
    ) -> None:
        super().__init__(master, fg_color=CARD_BG, corner_radius=10, **kwargs)
        self.grid_columnconfigure(1, weight=1)

        icon_box = ctk.CTkFrame(self, fg_color=ICON_BG, corner_radius=4,
                                width=44, height=44)
        icon_box.grid(row=0, column=0, padx=(10, 6), pady=(10, 4), sticky="nw")
        icon_box.grid_propagate(False)
        ctk.CTkLabel(
            icon_box, text=(ext_text or "FILE").lstrip(".").upper()[:4] or "FILE",
            text_color=ICON_FG, font=ctk.CTkFont(size=11, weight="bold"),
        ).place(relx=0.5, rely=0.5, anchor="center")

        ctk.CTkLabel(
            self, text=truncate(name), text_color="white",
            font=ctk.CTkFont(size=13, weight="bold"), anchor="w",
        ).grid(row=0, column=1, padx=(0, 10), pady=(10, 4), sticky="ew")

        ctk.CTkLabel(
            self, text=size_text, text_color="white",
            font=ctk.CTkFont(size=12), anchor="w",
        ).grid(row=1, column=0, columnspan=2, padx=10, pady=(4, 10),
               sticky="w")

        ctk.CTkLabel(
            self, text=ext_text or "no extension", text_color="white",
            font=ctk.CTkFont(size=11), anchor="e",
        ).grid(row=1, column=1, padx=(0, 10), pady=(4, 10), sticky="e")


class ChipBar(ctk.CTkFrame):
    """Row of pill buttons filtering the file grid by category."""

    def __init__(
        self,
        master,
        chips: list[str],
        on_select: Callable[[str], None],
        **kwargs,
    ) -> None:
        super().__init__(master, fg_color="transparent", **kwargs)
        self._on_select = on_select
        self._buttons: dict[str, ctk.CTkButton] = {}
        self.selected = chips[0] if chips else ""
        for col, name in enumerate(chips):
            btn = ctk.CTkButton(
                self, text=name, height=28, corner_radius=14,
                fg_color=CHIP_BG, hover_color="#8F8F8F",
                text_color="white", font=ctk.CTkFont(size=13),
                command=lambda n=name: self.select(n),
            )
            btn.grid(row=0, column=col, padx=(0, 8))
            self._buttons[name] = btn
        self._paint()

    def select(self, name: str) -> None:
        self.selected = name
        self._paint()
        self._on_select(name)

    def _paint(self) -> None:
        for name, btn in self._buttons.items():
            btn.configure(fg_color=CHIP_ACTIVE_BG if name == self.selected else CHIP_BG)
