import tkinter as tk
import tkinter.font as tkfont
from tkinter import ttk
from tkinter import messagebox
from tkinter import filedialog
import os.path
import ctypes
# import json
# import webbrowser
# import datetime as dt
# import re
# import efjtk.modify
# import efjtk.convert
import efjtk.version
# from efj_parser import ValidationError as VE
from functools import partial
from dataclasses import dataclass
from typing import NamedTuple
from collections.abc import Callable
import math

SETTINGS_FILE = os.path.expanduser("~/.efjtkguirc")
HELP_URL = "https://hursts.org.uk/efjtkdocs/gui.html"
HELP_EFJ = "https://hursts.org.uk/efjdocs/format.html"


class UI(NamedTuple):
    root: tk.Tk
    text: tk.Text
    status: ttk.Label
    em: Callable[[int], int]
    menus: dict["str", tk.Menu]


@dataclass
class Model():
    paths: dict[str, str]
    highlight_timer: str | None = None
    filename: str = ""
    dirty: bool = False


UpdateFunc = Callable[[str], None]


def update(model: Model, ui: UI, msg: str) -> None:
    if msg in {"open", "save", "saveas", "quit"}:
        file_operation(model, ui, msg)
    elif msg == "undo":
        ui.text.edit_undo()
    elif msg == "redo":
        ui.text.edit_redo()
    elif msg == "modified":
        if ui.text.edit_modified():
            ui.text.edit_modified(False)
            ui.text.mark_set("sh-end", "end")
            ui.text.event_generate("<<HighlightSyntax>>", when="tail")
            model.dirty = True
    if msg in {"open", "initialise"}:
        ui.text.mark_set("sh-end", "end")
        ui.text.event_generate("<<HighlightSyntax>>", when="tail")
    if msg not in {"quit"}:
        draw(model, ui)


def draw(model: Model, ui: UI) -> None:
    ui.menus["file"].entryconfigure(
        "Save",
        state="normal" if model.dirty and model.filename else "disabled")
    ui.menus["edit"].entryconfigure(
        "Undo",
        state="normal" if ui.text.edit("canundo") else "disabled")
    ui.menus["edit"].entryconfigure(
        "Redo",
        state="normal" if ui.text.edit("canredo") else "disabled")
    modified = " *" if model.dirty else ""
    ui.root.title(f"efjtk (v{efjtk.version.VERSION}){modified}")


def highlight_syntax(t: tk.Text) -> None:
    if (end := t.index("sh-end")) == "1.0":
        return
    start = f"{end} - 10 lines"
    for tag in ("keyword", "datetime", "grayed"):
        t.tag_remove(tag, start, end)
    count = tk.IntVar()
    for r, tag in ((r"(\d{4}-\d{2}-\d{2})|(\d{4}/\d{4})", "datetime"),
                   (r"CP:|FO:|PU:|FA:", "keyword"),
                   (r"#.*", "grayed")):
        start_idx = start
        while (idx := t.search(r, start_idx, regexp=True,
                               stopindex=end, count=count)):
            start_idx = t.index(f"{idx} + {count.get()} chars")
            t.tag_add(tag, idx, start_idx)
    t.mark_set("sh-end", start)
    t.after(50, lambda: t.event_generate("<<HighlightSyntax>>", when="tail"))


def file_operation(model: Model, ui: UI, msg: str) -> None:
    save_before = False
    if model.dirty and msg in ["open", "quit"]:
        question = {"open": "opening new file",
                    "quit": "quitting"}[msg]
        if messagebox.askyesno("Save", f"Save before {question}?"):
            save_before = True
    if msg in ["save", "saveas"] or save_before:
        if msg == "saveas" or not model.filename:
            fn = filedialog.asksaveasfilename(
                filetypes=(("All", "*"),),
                initialdir="/home/jon/data")
            if not fn:  # dialog was cancelled
                return
            model.filename = fn
        with open(model.filename, "w", encoding="utf-8") as f:
            f.write(ui.text.get("1.0", tk.END))
            model.dirty = False
    if msg == "open":
        fn = filedialog.askopenfilename(
            filetypes=(("Text", "*.txt"), ("Text", "*.efj"), ("All", "*")),
            initialdir="/home/jon/data")
        if not fn:  # dialog was cancelled
            return
        else:
            with open(fn) as f:
                newtext = f.read().strip()
                ui.text.delete("1.0", tk.END)
                ui.text.insert("1.0", newtext)
                ui.text.edit_reset()
                ui.text.see("insert")
                ui.text.edit_modified(False)
                model.dirty = False
                model.filename = fn
    if msg == "quit":
        ui.root.destroy()


def initialise_ui(root: tk.Tk) -> UI:
    family = "Courier"
    if "IBM Plex Mono" in tkfont.families():
        family = "IBM Plex Mono"
    elif "Consolas" in tkfont.families():
        family = "Consolas"
    font = tkfont.Font(family=family, size=11, weight=tkfont.NORMAL)
    wfont = font.measure("M")

    def em(x):
        return math.floor(x * wfont)

    root.columnconfigure(0, weight=1)
    root.rowconfigure(2, weight=1)

    sbx = ttk.Scrollbar(root, orient='horizontal')
    sby = ttk.Scrollbar(root, orient='vertical')
    text = tk.Text(root, background='white', font=font, wrap="none",
                   undo=True, autoseparators=True)
    text.mark_set("sh-end", "end")
    text.tag_configure("grayed", foreground="#707070")
    text.tag_configure("keyword", foreground="green")
    text.tag_configure("datetime", foreground="blue")
    sbx.config(command=text.xview)
    sby.config(command=text.yview)
    text.config(xscrollcommand=sbx.set)
    text.config(yscrollcommand=sby.set)

    statusbar = ttk.Frame(root)
    status = ttk.Label(statusbar, anchor="e", padding=(em(2), 0), text=" ")
    ttk.Sizegrip(statusbar).pack(side=tk.RIGHT, anchor=tk.SE)
    status.pack(fill=tk.X)

    text.grid(row=2, column=0, stick=tk.NSEW)
    sbx.grid(row=3, column=0, sticky=tk.EW)
    sby.grid(row=2, column=1, rowspan=2, sticky=tk.NS)
    statusbar.grid(row=4, column=0, columnspan=2, sticky=tk.EW)

    return UI(root, text, status, em, {})


def initialise_menus(ui: UI, update: UpdateFunc) -> None:
    top = tk.Menu()
    ui.root.config(menu=top)

    file_menu = tk.Menu(top, tearoff=0)
    file_menu.add_command(label="Open", underline=0,
                          command=lambda: update("open"))
    file_menu.add_command(label="Save", underline=0,
                          command=lambda: update("save"))
    file_menu.add_command(label="Save As", underline=5,
                          command=lambda: update("saveas"))
    file_menu.add_separator()
    file_menu.add_command(label="Quit", underline=0,
                          command=lambda: update("quit"))
    top.add_cascade(label="File", underline=0, menu=file_menu)
    ui.menus["file"] = file_menu

    edit_menu = tk.Menu(top, tearoff=0)
    edit_menu.add_command(label="Undo", underline=0,
                          command=lambda: update("undo"))
    edit_menu.add_command(label="Redo", underline=0,
                          command=lambda: update("redo"))
    edit_menu.add_separator()
    edit_menu.add_command(label="Cut", underline=1)
    edit_menu.add_command(label="Copy", underline=1)
    edit_menu.add_command(label="Paste", underline=0)
    edit_menu.add_separator()
    edit_menu.add_command(label="Select All", underline=7)
    edit_menu.add_command(label="Clear", underline=0)
    edit_menu.add_separator()
    edit_menu.add_command(label="Goto", underline=0)
    edit_menu.add_command(label="Search", underline=0)
    top.add_cascade(label="Edit", underline=0, menu=edit_menu)
    ui.menus["edit"] = edit_menu

    modify_menu = tk.Menu(top, tearoff=0)
    modify_menu.add_command(label="Expand", underline=0)
    modify_menu.add_command(label="Night", underline=0)
    modify_menu.add_command(label="First Officer", underline=0)
    modify_menu.add_command(label="VFR", underline=0)
    modify_menu.add_command(label="Instructor", underline=0)
    top.add_cascade(label="Modify", underline=0, menu=modify_menu)

    export_menu = tk.Menu(top, tearoff=0)
    export_menu.add_command(label="FCL.050 Logbook", underline=0)
    export_menu.add_command(label="Cumulative Totals", underline=0)
    export_menu.add_command(label="Summary", underline=0)
    top.add_cascade(label="Export", underline=0, menu=export_menu)

    help_menu = tk.Menu(top, tearoff=0)
    help_menu.add_command(label="Online Help", underline=0)
    help_menu.add_command(label="eFJ Format", underline=0)
    top.add_cascade(label="Help", underline=0, menu=help_menu)


def main():
    if "windll" in dir(ctypes):
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
    root = tk.Tk()
    ui = initialise_ui(root)
    _update = partial(update, Model({}), ui)
    initialise_menus(ui, _update)
    _update("initialise")
    ui.text.focus()
    root.protocol("WM_DELETE_WINDOW", lambda: _update("quit"))
    ui.text.bind("<<Modified>>", lambda _: _update("modified"))
    ui.text.bind("<<HighlightSyntax>>", lambda _: highlight_syntax(ui.text))
    root.mainloop()


if __name__ == "__main__":
    main()
