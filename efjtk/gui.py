import tkinter as tk
import tkinter.font as tkfont
from tkinter import ttk
from tkinter import messagebox
from tkinter import filedialog
import os.path
import ctypes
# import json
import webbrowser
# import datetime as dt
# import re
import efjtk.modify
import efjtk.convert
import efjtk.version
from efj_parser import ValidationError as VE
from functools import partial
from dataclasses import dataclass
from typing import NamedTuple
from collections.abc import Callable
import math

SETTINGS_FILE = os.path.expanduser("~/.efjtkguirc")
HELP_URL = "https://hursts.org.uk/efjtkdocs/gui.html"
HELP_EFJ = "https://hursts.org.uk/efjdocs/format.html"


class Menus(NamedTuple):
    file_: tk.Menu
    edit: tk.Menu
    modify: tk.Menu
    export: tk.Menu
    help_: tk.Menu


class UI(NamedTuple):
    root: tk.Tk
    text: tk.Text
    status: Callable[[str], None]
    em: Callable[[int], int]
    menus: Menus


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
    elif msg.startswith("modify_"):
        modify(model, ui, msg)
    elif msg.startswith("export_"):
        export(model, ui, msg)
    elif msg.startswith("help_"):
        webbrowser.open(
            {"help_online": HELP_URL,
             "help_format": HELP_EFJ}[msg])
    elif msg in {"cut", "copy", "paste"}:
        ui.text.event_generate({
            "cut": "<<Cut>>",
            "copy": "<<Copy>>",
            "paste": "<<Paste>>"}[msg])
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
    elif msg == "clear":
        ui.text.delete("1.0", tk.END)
    elif msg == "selectall":
        ui.text.tag_add("sel", "1.0", tk.END)
    if msg in {"open", "initialise"}:
        ui.text.mark_set("sh-end", "end")
        ui.text.event_generate("<<HighlightSyntax>>", when="tail")

    if msg not in {"quit", "clear", "selectall", "export_logbook",
                   "export_summary", "export_cumulative",
                   "help_online", "help_format"}:
        draw(model, ui)


def draw(model: Model, ui: UI) -> None:
    ui.menus.file_.entryconfigure(
        "Save",
        state="normal" if model.dirty and model.filename else "disabled")
    ui.menus.edit.entryconfigure(
        "Undo",
        state="normal" if ui.text.edit("canundo") else "disabled")
    ui.menus.edit.entryconfigure(
        "Redo",
        state="normal" if ui.text.edit("canredo") else "disabled")
    ui.menus.edit.entryconfigure(
        "Cut",
        state="normal" if ui.text.tag_ranges("sel") else "disabled")
    ui.menus.edit.entryconfigure(
        "Copy",
        state="normal" if ui.text.tag_ranges("sel") else "disabled")
    modified = " *" if model.dirty else ""
    ui.root.title(f"efjtk (v{efjtk.version.VERSION}){modified}")
    ui.status(ui.text.index("insert"))


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
            initialdir="/home/jon/proj/efj/toolkit/tests")
        if not fn:  # dialog was cancelled
            return
        else:
            with open(fn) as f:
                newtext = f.read().strip()
                ui.text.delete("1.0", tk.END)
                ui.text.insert("1.0", newtext)
                ui.text.edit_reset()
                ui.text.see("insert")
                ui.text.edit_reset()
                ui.text.edit_modified(False)
                model.dirty = False
                model.filename = fn
    if msg == "quit":
        ui.root.destroy()


def modify(model: Model, ui: UI, msg: str) -> None:
    fn = {"modify_expand": efjtk.modify.expand_efj,
          "modify_night": efjtk.modify.add_night_data,
          "modify_fo": efjtk.modify.add_fo_role_flag,
          "modify_vfr": efjtk.modify.add_vfr_flag,
          "modify_ins": efjtk.modify.add_ins_flag}
    ui.root.busy(cursor="watch")
    ui.root.update()
    text = ui.text.get('1.0', 'end')
    try:
        result = fn[msg](text)
        range_ = ui.text.tag_ranges("sel")
        ui.text.edit_separator()
        if range_:
            start = f"{ui.text.index(range_[0])} linestart"
            end = f"{ui.text.index(range_[1])} lineend"
            start_line = int(ui.text.index(start).split(".")[0])
            end_line = int(ui.text.index(end).split(".")[0])
            result_lines = result.splitlines()
            result = "\n".join(result_lines[start_line - 1:end_line])
            ui.text.delete(start, end)
            ui.text.insert(start, result)
        else:
            ui.text.delete('1.0', tk.END)
            ui.text.insert('1.0', result)
            ui.text.see(tk.END)
    except VE as e:
        ui.root.busy_forget()
        messagebox.showerror("Parse Error", str(e))
    finally:
        if ui.root.busy_status():
            ui.root.busy_forget()


def export(model: Model, ui: UI, msg: str) -> None:
    text = ui.text.get("1.0", tk.END)
    fn = {"export_logbook": efjtk.convert.build_logbook,
          "export_cumulative": efjtk.convert.build_cumulative,
          "export_summary": efjtk.convert.build_summary}
    try:
        result = fn[msg](text)
        path = "/home/jon/downloads"
        if fname := filedialog.asksaveasfilename(
                filetypes=(("HTML", "*.html"), ("All", "*")),
                defaultextension=".html",
                initialdir=path):
            with open(fname, "w", encoding="utf-8") as f:
                f.write(result)
    except VE as e:
        messagebox.showerror("Parse Error", str(e))


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

    text = tk.Text(root, background='white', font=font, wrap="none",
                   undo=True, autoseparators=False, exportselection=True)
    text.mark_set("sh-end", "end")
    text.tag_configure("grayed", foreground="#707070")
    text.tag_configure("keyword", foreground="green")
    text.tag_configure("datetime", foreground="blue")

    sbx = ttk.Scrollbar(root, orient='horizontal')
    sby = ttk.Scrollbar(root, orient='vertical')
    sbx.config(command=text.xview)
    sby.config(command=text.yview)
    text.config(xscrollcommand=sbx.set)
    text.config(yscrollcommand=sby.set)

    statusbar = ttk.Frame(root)
    status = ttk.Label(statusbar, anchor="e", padding=(em(2), 0), text=" ")
    ttk.Sizegrip(statusbar).pack(side=tk.RIGHT, anchor=tk.SE)
    status.pack(fill=tk.X)

    def status_func(index: str) -> None:
        row, col = index.split(".")
        status.config(text=f"Row: {row} Column: {col}")

    top = tk.Menu()
    menus = Menus(*(tk.Menu(top, tearoff=0) for _ in range(5)))
    top.add_cascade(label="File", underline=0, menu=menus.file_)
    top.add_cascade(label="Edit", underline=0, menu=menus.edit)
    top.add_cascade(label="Modify", underline=0, menu=menus.modify)
    top.add_cascade(label="Export", underline=0, menu=menus.export)
    top.add_cascade(label="Help", underline=0, menu=menus.help_)
    root.config(menu=top)

    text.grid(row=2, column=0, stick=tk.NSEW)
    sbx.grid(row=3, column=0, sticky=tk.EW)
    sby.grid(row=2, column=1, rowspan=2, sticky=tk.NS)
    statusbar.grid(row=4, column=0, columnspan=2, sticky=tk.EW)

    return UI(root, text, status_func, em, menus)


def initialise_menus(ui: UI, update: UpdateFunc) -> None:
    ui.menus.file_.add_command(label="Open", accelerator="Ctrl-O",
                               underline=0, command=lambda: update("open"))
    ui.root.bind("<Control-Key-o>", lambda _: update("open"))
    ui.menus.file_.add_command(label="Save", underline=0,
                               command=lambda: update("save"))
    ui.menus.file_.add_command(label="Save As", underline=5,
                               command=lambda: update("saveas"))
    ui.menus.file_.add_separator()
    ui.menus.file_.add_command(label="Quit", underline=0,
                               command=lambda: update("quit"))

    ui.menus.edit.add_command(label="Undo", underline=0,
                              command=lambda: update("undo"))
    ui.menus.edit.add_command(label="Redo", underline=0,
                              command=lambda: update("redo"))
    ui.menus.edit.add_separator()
    ui.menus.edit.add_command(label="Cut", underline=1,
                              command=lambda: update("cut"))
    ui.menus.edit.add_command(label="Copy", underline=1,
                              command=lambda: update("copy"))
    ui.menus.edit.add_command(label="Paste", underline=0,
                              command=lambda: update("paste"))
    ui.menus.edit.add_separator()
    ui.menus.edit.add_command(label="Select All", underline=7,
                              command=lambda: update("selectall"))
    ui.menus.edit.add_command(label="Clear", underline=0,
                              command=lambda: update("clear"))

    ui.menus.modify.add_command(label="Expand", underline=0,
                                command=lambda: update("modify_expand"))
    ui.menus.modify.add_command(label="Night", underline=0,
                                command=lambda: update("modify_night"))
    ui.menus.modify.add_command(label="First Officer", underline=0,
                                command=lambda: update("modify_fo"))
    ui.menus.modify.add_command(label="VFR", underline=0,
                                command=lambda: update("modify_vfr"))
    ui.menus.modify.add_command(label="Instructor", underline=0,
                                command=lambda: update("modify_ins"))

    ui.menus.export.add_command(label="FCL.050 Logbook", underline=0,
                                command=lambda: update("export_logbook"))
    ui.menus.export.add_command(label="Cumulative Totals", underline=0,
                                command=lambda: update("export_cumulative"))
    ui.menus.export.add_command(label="Summary", underline=0,
                                command=lambda: update("export_summary"))

    ui.menus.help_.add_command(label="Online Help", underline=0,
                               command=lambda: update("help_online"))
    ui.menus.help_.add_command(label="eFJ Format", underline=0,
                               command=lambda: update("help_format"))


def main():
    if "windll" in dir(ctypes):
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
    root = tk.Tk()
    ui = initialise_ui(root)
    _update = partial(update, Model({}), ui)
    initialise_menus(ui, _update)
    _update("initialise")
    # bindings
    root.protocol("WM_DELETE_WINDOW", lambda: _update("quit"))
    ui.text.bind("<<Modified>>", lambda _: _update("modified"))
    ui.text.bind("<<Selection>>", lambda _: _update("selection"))
    ui.text.bind("<<HighlightSyntax>>", lambda _: highlight_syntax(ui.text))
    ui.text.bind("<KeyRelease>", lambda _: ui.status(ui.text.index("insert")))
    ui.text.bind("<ButtonPress>", lambda _: ui.status(ui.text.index("insert")))
    ui.text.bind("<Return>", lambda _: ui.text.edit_separator())

    ui.text.focus()
    root.mainloop()


if __name__ == "__main__":
    main()
