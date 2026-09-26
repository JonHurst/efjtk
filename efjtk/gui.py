import tkinter as tk
import tkinter.font as tkfont
from tkinter import ttk
from tkinter import messagebox
from tkinter import filedialog
import os.path
import ctypes
import json
import webbrowser
import datetime as dt
import re
import efjtk.modify
import efjtk.convert
import efjtk.version
from efj_parser import ValidationError as VE
from functools import partial
from dataclasses import dataclass
from typing import NamedTuple, Any
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
    status_caretpos: tk.StringVar
    status_daterange: tk.StringVar
    menus: Menus
    goto_bar: tk.Frame
    goto_button_go: ttk.Button
    goto_button_cancel: ttk.Button
    goto_value: tk.StringVar
    daterange_bar: tk.Frame
    daterange_button_ok: ttk.Button
    daterange_button_cancel: ttk.Button
    date_from: tk.StringVar
    date_to: tk.StringVar
    fr_bar: tk.Frame
    fr_from: tk.StringVar
    fr_to: tk.StringVar
    fr_button_next: ttk.Button
    fr_button_replace: ttk.Button
    fr_button_cancel: ttk.Button


@dataclass
class Model():
    settings: dict[str, str]
    bar_stack: list[tk.Frame | None]
    date_from: dt.date | None = None
    date_to: dt.date | None = None
    filename: str = ""
    dirty: bool = False


class DrawData(NamedTuple):
    dirty: bool
    cansave: bool
    canreplace: bool
    canreplaceall: bool
    dates: tuple[dt.date | None, dt.date | None]
    bar: tk.Frame | None


UpdateFunc = Callable[[str], None]


def update(
        model: Model, ui: UI, draw: Callable[[DrawData], None], msg: str
) -> None:
    if msg in {"open", "save", "saveas", "insert", "quit"}:
        file_operation(model, ui, msg)
    elif msg.startswith("modify_"):
        modify(model, ui, msg)
    elif msg.startswith("export_"):
        export(model, ui, msg)
    elif msg in {"cut", "copy", "paste"}:
        ui.text.event_generate(
            {"cut": "<<Cut>>", "copy": "<<Copy>>", "paste": "<<Paste>>"}[msg])
    elif msg == "undo":
        ui.text.edit_undo()
    elif msg == "redo":
        ui.text.edit_redo()
    elif msg == "modified":
        if ui.text.edit_modified():
            if ui.text.index("sh-end") == "1.0":
                ui.text.event_generate("<<HighlightSyntax>>", when="tail")
            ui.text.mark_set("sh-end", "end")
            ui.text.edit_modified(False)
            model.dirty = True
    elif msg == "clear":
        ui.text.delete("1.0", tk.END)
    elif msg == "selectall":
        ui.text.tag_add("sel", "1.0", tk.END)
    elif msg in {"goto_bar", "daterange_bar", "far_bar"}:
        push_bar(model.bar_stack, {"goto_bar": ui.goto_bar,
                                   "daterange_bar": ui.daterange_bar,
                                   "far_bar": ui.fr_bar}[msg])
    elif msg == "popbar":
        pop_bar(model.bar_stack)
    elif msg == "goto":
        if (line := ui.goto_value.get()):
            ui.text.mark_set("insert", f"{line}.0")
            ui.text.see(ui.text.index("insert"))
            pop_bar(model.bar_stack)
    elif msg == "capture_daterange":
        capture_daterange(model, ui)
    elif msg == "findnext":
        if find_next(ui):
            ui.text.see(ui.text.index("insert"))
            ui.text.focus()
    elif msg == "replace":
        replace(ui)
    if msg in {"open", "insert", "initialise"} or msg.startswith("modify_"):
        ui.text.mark_set("sh-end", "end")
        ui.text.event_generate("<<HighlightSyntax>>")
    if (msg in {"quit", "clear", "selectall"} or msg.startswith("export_")):
        return
    draw(DrawData(dirty=model.dirty,
                  canreplace=canreplace(ui),
                  canreplaceall=bool(ui.fr_from.get()),
                  cansave=bool(model.filename),
                  dates=(model.date_from, model.date_to),
                  bar=model.bar_stack[-1] if len(model.bar_stack) else None))


def draw(state: dict[str, Any], ui: UI, data: DrawData) -> None:
    ui.menus.file_.entryconfigure(
        "Save",
        state="normal" if data.dirty and data.cansave else "disabled")
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
    modified = " *" if data.dirty else ""
    ui.root.title(f"efjtk (v{efjtk.version.VERSION}){modified}")
    ui.status_caretpos.set(ui.text.index('insert'))
    if any(data.dates):
        ui.status_daterange.set(
            f"{data.dates[0] or 'Start'} to {data.dates[1] or 'End'}")
    else:
        ui.status_daterange.set("All")
    current_bar = state.get("current_bar")
    if data.bar != current_bar:
        if current_bar:
            current_bar.grid_remove()
        if data.bar:
            data.bar.grid(row=1, column=0, columnspan=2, sticky=tk.EW)
            data.bar.event_generate("<<FocusChild>>")
        else:
            ui.text.focus()
        state["current_bar"] = data.bar
    if data.canreplace:
        ui.fr_button_replace.config(text="Replace", state="normal")
    elif data.canreplaceall:
        ui.fr_button_replace.config(text="Replace All", state="normal")
    else:
        ui.fr_button_replace.config(text="Replace", state="disabled")


def find_next(ui: UI) -> bool:
    target = ui.fr_from.get()
    start = ui.text.index("insert")
    next_ = ui.text.search(target, start + " +1 chars", nocase=True)
    if not next_:
        next_ = ui.text.search(target, "1.0", stopindex=start, nocase=True, )
    if next_:
        ui.text.mark_set("insert", next_)
        ui.text.tag_remove("sel", "1.0", tk.END)
        ui.text.tag_add("sel", next_, f"{next_} + {len(target)} chars")
        return True
    return False


def replace(ui: UI) -> None:
    if canreplace(ui):
        ui.text.edit_separator()
        start, end = ui.text.tag_ranges("sel")[:2]
        ui.text.replace(start, end, ui.fr_to.get())
    elif target := ui.fr_from.get():  # can do replace all
        ui.text.edit_separator()
        ui.text.mark_set("insert", "1.0")
        while next_ := ui.text.search(
                target, ui.text.index("insert"),
                nocase=True, stopindex=tk.END):
            ui.text.replace(
                next_, f"{next_} + {len(target)} chars", ui.fr_to.get())
            ui.text.mark_set("insert",
                             f"{next_} + {len(ui.fr_to.get())} chars")
        ui.text.see(ui.text.index("insert"))
        ui.text.focus()


def canreplace(ui: UI) -> bool:
    retval = False
    if (selection := ui.text.tag_ranges("sel")) and len(selection) == 2:
        retval = (ui.fr_from.get().lower() ==
                  ui.text.get(*selection).lower())
    return retval


def push_bar(stack: list[tk.Frame | None], bar: tk.Frame) -> None:
    if bar in stack:
        stack[stack.index(bar)] = None
    stack.append(bar)


def pop_bar(stack: list[tk.Frame | None]) -> None:
    if len(stack):
        stack.pop()
    while len(stack) and not stack[-1]:
        stack.pop()


def highlight_syntax(t: tk.Text) -> None:
    end = t.index("sh-end")
    start = t.index(end + " - 100 lines linestart")
    for tag in ("keyword", "datetime", "grayed"):
        t.tag_remove(tag, start, end)
    start_line, end_line = (int(X.split(".")[0]) for X in (start, end))
    for line in range(start_line, end_line):
        line_text = t.get(f"{line}.0", f"{line + 1}.0")
        split = line_text.split("#")
        if len(split) == 2:
            comment_start = f"{line}.{len(split[0])}"
            comment_end = f"{line}.{len(line_text) - 1}"
            t.tag_add("grayed", comment_start, comment_end)
            line_text = split[0]
        if mo := re.search(r"(\d{4}-\d{2}-\d{2})|(\d{4}/\d{4})", line_text):
            datetime_start = f"{line}.{mo.start()}"
            datetime_end = f"{line}.{mo.end()}"
            t.tag_add("datetime", datetime_start, datetime_end)
        else:
            for mo in re.finditer(r"CP:|FO:|PU:|FA:", line_text):
                keyword_start = f"{line}.{mo.start()}"
                keyword_end = f"{line}.{mo.end()}"
                t.tag_add("keyword", keyword_start, keyword_end)
    t.mark_set("sh-end", start)
    if start != "1.0":
        t.after_idle(lambda: t.event_generate("<<HighlightSyntax>>"))


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
                initialdir=model.settings.get("savePath"))
            if not fn:  # dialog was cancelled
                return
            model.filename = fn
            model.settings['savePath'] = os.path.dirname(fn)
        with open(model.filename, "w", encoding="utf-8") as f:
            f.write(ui.text.get("1.0", tk.END).strip())
            model.dirty = False
    if msg in {"open", "insert"}:
        path = model.settings.get(
            "openPath" if msg == "open" else "insertPath")
        if fn := filedialog.askopenfilename(
                initialdir=path,
                filetypes=(("All", "*"), ("Text", "*.txt"), ("eFJ", "*.efj"))):
            with open(fn) as f:
                newtext = f.read()
                if msg == "open":
                    model.settings['openPath'] = os.path.dirname(fn)
                    ui.text.delete("1.0", tk.END)
                    ui.text.insert("1.0", newtext)
                    ui.text.edit_reset()
                    ui.text.edit_modified(False)
                    model.dirty = False
                    model.filename = fn
                    ui.text.see("insert")
                else:
                    model.settings['insertPath'] = os.path.dirname(fn)
                    ui.text.edit_separator()
                    insert_index = ui.text.index("insert")
                    ui.text.insert(ui.text.index("insert"), newtext)
                    ui.text.mark_set("insert", insert_index)
                    ui.text.edit_modified(False)
                    model.dirty = True
    if msg == "quit":
        model.settings["last-search"] = ui.fr_from.get()
        with open(SETTINGS_FILE, "w") as f:
            json.dump(model.settings, f, indent=4)
        ui.root.destroy()


def modify(model: Model, ui: UI, msg: str) -> None:
    fn = {"modify_expand": efjtk.modify.expand_efj,
          "modify_night": efjtk.modify.add_night_data,
          "modify_fo": efjtk.modify.add_fo_role_flag,
          "modify_vfr": efjtk.modify.add_vfr_flag,
          "modify_ins": efjtk.modify.add_ins_flag}
    text = ui.text.get('1.0', 'end')
    try:
        insert = ui.text.index("insert")
        result = fn[msg](text)
        range_ = ui.text.tag_ranges("sel")
        ui.text.edit_separator()
        if range_:
            start = f"{ui.text.index(range_[0])} linestart"
            end = f"{ui.text.index(range_[1])} - 1 chars lineend"
            start_line = int(ui.text.index(start).split(".")[0])
            end_line = int(ui.text.index(end).split(".")[0])
            result_lines = result.splitlines()
            result = "\n".join(result_lines[start_line - 1:end_line])
            ui.text.delete(start, end)
            ui.text.insert(start, result)
            ui.text.tag_add("sel", start, end)
        else:
            ui.text.delete('1.0', tk.END)
            ui.text.insert('1.0', result)
        ui.text.edit_modified(False)
        model.dirty = True
        ui.text.mark_set("insert", insert)
        ui.text.see("insert")
    except VE as e:
        messagebox.showerror("Parse Error", str(e))


def export(model: Model, ui: UI, msg: str) -> None:
    text = ui.text.get("1.0", tk.END)
    fn = {"export_logbook": efjtk.convert.build_logbook,
          "export_cumulative": efjtk.convert.build_cumulative,
          "export_summary": efjtk.convert.build_summary}
    try:
        to = model.date_to + dt.timedelta(days=1) if model.date_to else None
        result = fn[msg](text, (model.date_from, to))
        if fname := filedialog.asksaveasfilename(
                filetypes=(("HTML", "*.html"), ("All", "*")),
                defaultextension=".html",
                initialdir=model.settings.get("exportPath")):
            with open(fname, "w", encoding="utf-8") as f:
                f.write(result)
            model.settings["exportPath"] = os.path.dirname(fname)
    except VE as e:
        messagebox.showerror("Parse Error", str(e))


def capture_daterange(model: Model, ui: UI) -> None:
    try:
        r = [dt.date.fromisoformat(X) if X else None for X in (
            ui.date_from.get().strip(), ui.date_to.get().strip())]
        model.date_from, model.date_to = r
        pop_bar(model.bar_stack)
    except ValueError as e:
        messagebox.showerror(
            "Invalid Date",
            f"{str(e)}\n\nDates must by in ISO 8601 format\n"
            f"e.g. 2026-09-25")


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
    root.minsize(em(75), em(40))

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
    status_caretpos = tk.StringVar()
    status_daterange = tk.StringVar()
    ttk.Label(statusbar, text="Cursor Position:").grid(row=0, column=1)
    ttk.Label(statusbar, textvariable=status_caretpos, relief="sunken",
              padding=(em(1), em(0.25))).grid(row=0, column=2, padx=em(1))
    ttk.Label(statusbar, text="Date Range for Export:").grid(row=0, column=3)
    ttk.Label(statusbar, textvariable=status_daterange, relief="sunken",
              padding=(em(1), em(0.25))).grid(row=0, column=4, padx=em(1))
    statusbar.grid_columnconfigure(5, weight=1)
    ttk.Frame(statusbar).grid(row=0, column=5)
    ttk.Sizegrip(statusbar).grid(row=0, column=6, sticky=tk.SE)

    top = tk.Menu()
    menus = Menus(*(tk.Menu(top, tearoff=0) for _ in range(5)))
    top.add_cascade(label="File", underline=0, menu=menus.file_)
    top.add_cascade(label="Edit", underline=0, menu=menus.edit)
    top.add_cascade(label="Modify", underline=0, menu=menus.modify)
    top.add_cascade(label="Export", underline=1, menu=menus.export)
    top.add_cascade(label="Help", underline=0, menu=menus.help_)
    root.config(menu=top)

    goto_bar = tk.Frame(root, padx=em(1), pady=em(0.5))
    tk_validate_integer = root.register(validate_integer)
    goto_val = tk.StringVar()
    goto_entry = ttk.Entry(
        goto_bar, textvariable=goto_val, validate="key",
        validatecommand=(tk_validate_integer, "%P"), justify="center")
    goto_bar.bind("<<FocusChild>>", lambda _: goto_entry.focus())
    goto_go = ttk.Button(goto_bar, text="Go")
    goto_entry.bind("<Return>", lambda _: goto_go.invoke())
    goto_cancel = ttk.Button(goto_bar, text="Cancel")
    goto_entry.bind("<Escape>", lambda _: goto_cancel.invoke())
    goto_bar.grid_columnconfigure(2, weight=1)
    ttk.Label(goto_bar, text="Goto line:").grid(row=0, column=1)
    goto_entry.grid(row=0, column=2, sticky=tk.EW, padx=em(2))
    goto_go.grid(row=0, column=3)
    goto_cancel.grid(row=0, column=5, padx=(em(0.5), 0))

    dr_bar = tk.Frame(root, padx=em(1), pady=em(0.5))
    dr_validate = (root.register(validate_date), "%P")
    from_ = tk.StringVar()
    to = tk.StringVar()
    dr_from = ttk.Entry(dr_bar, textvariable=from_, justify="center",
                        validate="key", validatecommand=dr_validate)
    dr_bar.bind("<<FocusChild>>", lambda _: dr_from.focus())
    dr_to = ttk.Entry(dr_bar, textvariable=to, justify="center",
                      validate="key", validatecommand=dr_validate)
    dr_ok = ttk.Button(dr_bar, text="OK")
    dr_from.bind("<Return>", lambda _: dr_ok.invoke())
    dr_to.bind("<Return>", lambda _: dr_ok.invoke())
    dr_cancel = ttk.Button(dr_bar, text="Cancel")
    dr_from.bind("<Escape>", lambda _: dr_cancel.invoke())
    dr_to.bind("<Escape>", lambda _: dr_cancel.invoke())
    dr_bar.grid_columnconfigure(1, weight=1)
    dr_bar.grid_columnconfigure(3, weight=1)
    ttk.Label(dr_bar, text="From:").grid(row=0, column=0)
    dr_from.grid(row=0, column=1, sticky=tk.EW, padx=(em(1), em(2)))
    ttk.Label(dr_bar, text="To:").grid(row=0, column=2)
    dr_to.grid(row=0, column=3, sticky=tk.EW, padx=(em(1), em(2)))
    dr_ok.grid(row=0, column=4, padx=(em(1), 0))
    dr_cancel.grid(row=0, column=5, padx=(em(1), 0))

    fr_bar = tk.Frame(root, padx=em(0.5), pady=em(0.5))
    fr_from_val = tk.StringVar()
    fr_to_val = tk.StringVar()
    fr_from = ttk.Entry(fr_bar, textvariable=fr_from_val, width=15)
    fr_bar.bind("<<FocusChild>>", lambda _: fr_from.focus())
    fr_to = ttk.Entry(fr_bar, textvariable=fr_to_val, width=15)
    fr_next = ttk.Button(fr_bar, text="Next")
    fr_replace = ttk.Button(fr_bar, text="Replace")
    fr_cancel = ttk.Button(fr_bar, text="Close")
    fr_from.bind("<Return>", lambda _: fr_next.invoke())
    fr_from.bind("<Escape>", lambda _: fr_cancel.invoke())
    fr_to.bind("<Escape>", lambda _: fr_cancel.invoke())
    fr_bar.grid_columnconfigure(1, weight=1)
    fr_bar.grid_columnconfigure(3, weight=1)
    ttk.Label(fr_bar, text="Find:").grid(row=0, column=0)
    fr_from.grid(row=0, column=1, sticky=tk.EW, padx=(em(1), em(1)))
    ttk.Label(fr_bar, text="Replace with:").grid(row=0, column=2)
    fr_to.grid(row=0, column=3, sticky=tk.EW, padx=(em(1), em(1)))
    fr_next.grid(row=0, column=5, padx=(em(1), 0))
    fr_replace.grid(row=0, column=6, padx=(em(1), 0))
    fr_cancel.grid(row=0, column=7, padx=(em(1), 0))

    text.grid(row=2, column=0, sticky=tk.NSEW)
    sbx.grid(row=3, column=0, sticky=tk.EW)
    sby.grid(row=2, column=1, rowspan=2, sticky=tk.NS)
    statusbar.grid(row=4, column=0, columnspan=2, sticky=tk.EW,
                   padx=em(0.25), pady=em(0.5))

    return UI(
        root=root, menus=menus, text=text,
        status_caretpos=status_caretpos, status_daterange=status_daterange,
        goto_bar=goto_bar, goto_value=goto_val,
        goto_button_go=goto_go, goto_button_cancel=goto_cancel,
        daterange_bar=dr_bar, date_from=from_, date_to=to,
        daterange_button_ok=dr_ok, daterange_button_cancel=dr_cancel,
        fr_bar=fr_bar, fr_from=fr_from_val, fr_to=fr_to_val,
        fr_button_next=fr_next, fr_button_replace=fr_replace,
        fr_button_cancel=fr_cancel)


def grid_remove_bar(bar: tk.Frame, text: tk.Text) -> None:
    bar.grid_remove()
    text.focus()


def recenter(t: tk.Text) -> None:
    index_line = int(t.index("insert").split(".")[0])
    end_line = int(t.index(tk.END).split(".")[0])
    index_frac = index_line / end_line
    page = t.yview()
    page_height = page[1] - page[0]
    target = max(0, index_frac - page_height / 2)
    if math.isclose(target, t.yview()[0], abs_tol=page_height / 10):
        t.yview_moveto(index_frac)
    else:
        t.yview_moveto(target)


def validate_integer(s: str) -> bool:
    return False if re.search(r"[^\d]", s) else True


def validate_date(s: str) -> bool:
    return False if re.search(r"[^\d-]", s) else True


def initialise_menus(ui: UI, update: UpdateFunc) -> None:
    ui.menus.file_.add_command(label="Open", accelerator="Ctrl-O",
                               underline=0, command=lambda: update("open"))

    def open_only(_):  # needed to prevent default text "open line" behavior
        update("open")
        return "break"
    ui.text.bind("<Control-Key-o>", open_only)
    ui.root.bind("<Control-Key-o>", open_only)
    ui.menus.file_.add_command(label="Insert",
                               underline=0, command=lambda: update("insert"))
    ui.menus.file_.add_separator()
    ui.menus.file_.add_command(label="Save", accelerator="Ctrl-S",
                               underline=0, command=lambda: update("save"))
    ui.root.bind("<Control-Key-s>", lambda _: update("save"))
    ui.menus.file_.add_command(label="Save As", underline=5,
                               command=lambda: update("saveas"))
    ui.menus.file_.add_separator()
    ui.menus.file_.add_command(label="Quit", accelerator="Ctrl-Q",
                               underline=0, command=lambda: update("quit"))
    ui.root.bind("<Control-Key-q>", lambda _: update("quit"))

    ui.menus.edit.add_command(label="Undo", accelerator="Ctrl-Z",
                              underline=0, command=lambda: update("undo"))
    ui.menus.edit.add_command(label="Redo", underline=0,
                              command=lambda: update("redo"))
    ui.menus.edit.add_separator()
    ui.menus.edit.add_command(label="Cut", accelerator="Ctrl-X",
                              underline=1, command=lambda: update("cut"))
    ui.menus.edit.add_command(label="Copy", accelerator="Ctrl-C",
                              underline=1, command=lambda: update("copy"))
    ui.menus.edit.add_command(label="Paste", accelerator="Ctrl-V",
                              underline=0, command=lambda: update("paste"))
    ui.menus.edit.add_separator()
    ui.menus.edit.add_command(label="Recenter", accelerator="Ctrl-L",
                              underline=0, command=lambda: recenter(ui.text))
    ui.menus.edit.add_separator()
    ui.menus.edit.add_command(label="Select All", underline=7,
                              command=lambda: update("selectall"))
    ui.menus.edit.add_command(label="Clear", underline=0,
                              command=lambda: update("clear"))
    ui.menus.edit.add_separator()
    ui.menus.edit.add_command(label="Find & Replace", accelerator="Ctrl-F",
                              underline=0, command=lambda: update("far_bar"))
    ui.root.bind("<Control-Key-f>", lambda _: update("far_bar"))
    ui.menus.edit.add_command(label="Find Next", accelerator="F3", underline=5,
                              command=lambda: ui.fr_button_next.invoke())
    ui.root.bind("<F3>", lambda _: ui.fr_button_next.invoke())
    ui.menus.edit.add_separator()
    ui.menus.edit.add_command(label="Goto", accelerator="Ctrl-G",
                              underline=0, command=lambda: update("goto_bar"))
    ui.root.bind("<Control-Key-g>", lambda _: update("goto_bar"))

    ui.menus.modify.add_command(label="Expand", accelerator="F2", underline=0,
                                command=lambda: update("modify_expand"))
    ui.text.bind("<F2>", lambda _: update("modify_expand"))
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
                               accelerator="F1",
                               command=lambda: webbrowser.open(HELP_URL))
    ui.root.bind("<F1>", lambda _: webbrowser.open(HELP_URL))
    ui.menus.help_.add_command(label="eFJ Format", underline=0,
                               command=lambda: webbrowser.open(HELP_EFJ))
    ui.menus.export.add_separator()
    ui.menus.export.add_command(label="Restrict Dates", underline=0,
                                command=lambda: update("daterange_bar"))


def initialise_bindings(ui: UI, update: UpdateFunc) -> None:
    ui.root.protocol("WM_DELETE_WINDOW", lambda: update("quit"))
    ui.root.bind("<Control-Key-l>", lambda _: recenter(ui.text))
    ui.root.bind("<Control-Key-L>", lambda _: recenter(ui.text))

    ui.text.bind("<<Modified>>", lambda _: update("modified"))
    ui.text.bind("<<Selection>>", lambda _: update("selection"))
    ui.text.bind("<<HighlightSyntax>>", lambda _: highlight_syntax(ui.text))
    ui.text.bind("<KeyRelease>", lambda _: update("status"))
    ui.text.bind("<ButtonRelease>", lambda _: update("status"))
    ui.text.bind("<Return>", lambda _: ui.text.edit_separator())

    ui.goto_button_go.config(command=lambda: update("goto"))
    ui.goto_button_cancel.config(command=lambda: update("popbar"))

    ui.daterange_button_ok.config(command=lambda: update("capture_daterange"))
    ui.daterange_button_cancel.config(command=lambda: update("popbar"))

    ui.fr_button_cancel.config(command=lambda: update("popbar"))
    ui.fr_button_next.config(command=lambda: update("findnext"))
    ui.fr_button_replace.config(command=lambda: update("replace"))
    ui.fr_from.trace_add("write", lambda *_: update("find_changed"))


def main():
    if "windll" in dir(ctypes):
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
    try:
        with open(SETTINGS_FILE) as f:
            settings = json.load(f)
    except Exception:
        settings = {}
    root = tk.Tk()
    ui = initialise_ui(root)
    ui.fr_from.set(settings.get("last-search", ""))
    _update = partial(update, Model(settings, []), ui, partial(draw, {}, ui))
    initialise_menus(ui, _update)
    initialise_bindings(ui, _update)
    _update("initialise")
    ui.text.focus()
    root.mainloop()


if __name__ == "__main__":
    main()
