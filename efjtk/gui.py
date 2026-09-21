import tkinter as tk
import tkinter.font as font
from tkinter import ttk
from tkinter import messagebox
from tkinter import filedialog
import os.path
import ctypes
import json
import webbrowser
import datetime as dt
import re
import configparser as cp

import efjtk.modify
import efjtk.convert
import efjtk.config
import efjtk.version
from efj_parser import ValidationError as VE


SETTINGS_FILE = os.path.expanduser("~/.efjtkguirc")
CONFIG_FILE = os.path.expanduser("~/.efjtkrc")
HELP_URL = "https://hursts.org.uk/efjtkdocs/gui.html"
HELP_EFJ = "https://hursts.org.uk/efjdocs/format.html"


class TextWithSyntaxHighlighting(tk.Text):

    def __init__(self, parent, highlight_mode, **kwargs):
        family = "Courier"
        if "IBM Plex Mono" in font.families():
            family = "IBM Plex Mono"
        elif "Consolas" in font.families():
            family = "Consolas"
        tk.Text.__init__(self, parent, background='white',
                         wrap="none", undo=True,
                         font=(family, 10, 'normal'), **kwargs)
        self.highlight_mode = highlight_mode
        self.tag_configure("grayed", foreground="#707070")
        self.tag_configure("keyword", foreground="green")
        self.tag_configure("datetime", foreground="blue")
        self.bind(
            '<KeyRelease>',
            lambda *args: self.edit_modified() and self.schedule_highlight())
        self.highlight_timer = None

    def insert(self, idx, text, *args):
        tk.Text.insert(self, idx, text, *args)
        self.highlight_syntax()

    def schedule_highlight(self):
        if self.highlight_timer:
            self.winfo_toplevel().after_cancel(self.highlight_timer)
        self.highlight_timer = self.winfo_toplevel().after(
            1000, lambda *args: self.highlight_syntax())

    def highlight_syntax(self):
        if not self.highlight_mode:
            return
        for tag in ("keyword", "datetime", "grayed"):
            self.tag_remove(tag, "1.0", "end")
        if self.highlight_mode == 'efj':
            self.highlight_efj()
        elif self.highlight_mode == 'config':
            self.highlight_config()
        self.highlight_timer = None

    def __highlight(self, re, tag):
        count = tk.IntVar()
        start_idx = "1.0"
        while True:
            if not (new_idx := self.search(
                    re, start_idx, count=count, regexp=True, stopindex="end")):
                break
            start_idx = f"{new_idx} + {count.get()} chars"
            self.tag_add(tag, new_idx, start_idx)

    def highlight_efj(self):
        for r, tag in ((r"\d{4}-\d{2}-\d{2}", "datetime"),
                       (r"\d{4}/\d{4}", "datetime"),
                       ("CP:|FO:|PU:|FA:", "keyword"),
                       (r"#.*", "grayed")):
            self.__highlight(r, tag)

    def highlight_config(self):
        for r, tag in ((r"(spse|spme|mc)\s", "keyword"),
                       (r"\[[\w.]+\]\n", "grayed")):
            self.__highlight(r, tag)

    def search_next(self, s):
        next_ = self.search(s, self.index("insert+1chars"),
                            forwards=True, nocase=True)
        if next_:
            self.mark_set("insert", next_)
            self.see(self.index("insert"))
            self.focus()

    def search_prev(self, s):
        prev = self.search(s, self.index("insert"),
                           backwards=True, nocase=True)
        if prev:
            self.mark_set("insert", prev)
            self.see(self.index("insert"))
            self.focus()


class ConfigDialog(tk.Toplevel):

    def __init__(self, parent):
        tk.Toplevel.__init__(self)
        self.parent = parent
        self.callback = None
        self.title("Config Editor")
        self.transient(parent)
        self.__make_widgets()

    def __make_widgets(self):
        buttons_frm = tk.Frame(self, padx="2m", pady="1m")
        tk.Button(buttons_frm, text="Save", width="7", command=self.__save
                  ).pack(side=tk.RIGHT)
        tk.Button(buttons_frm, text="Cancel", width="7", command=self.destroy
                  ).pack(side=tk.RIGHT, padx="1m")
        tk.Button(buttons_frm, text="Help", width="7", command=self.__help
                  ).pack(side=tk.LEFT)
        buttons_frm.pack(side=tk.BOTTOM, fill=tk.X)

        tk.Frame(self, height="2m").pack(side=tk.BOTTOM)  # Spacer

        self.msg = TextWithSyntaxHighlighting(
            self, "config", width=35, height=3)
        self.msg.insert("1.0",
                        "spse : single pilot single engine\n"
                        "spme : single pilot multi engine\n"
                        "mc   : multi crew")
        self.msg.config(state="disabled", bg="#E0E0E0")
        self.msg.pack(side=tk.BOTTOM, fill=tk.X)

        tk.Frame(self, height="2m").pack(side=tk.BOTTOM)  # Spacer

        text_frm = tk.Frame(self)
        text_frm.columnconfigure(0, weight=1)
        text_frm.rowconfigure(0, weight=1)
        sbx = ttk.Scrollbar(text_frm, orient='horizontal')
        sby = ttk.Scrollbar(text_frm, orient='vertical')
        sbx.grid(row=1, column=0, sticky=tk.EW)
        sby.grid(row=0, column=1, sticky=tk.NS)
        self.txt = TextWithSyntaxHighlighting(
            text_frm, "config", width=30,  height=20)
        self.txt.grid(row=0, column=0, sticky=tk.NSEW)
        sbx.config(command=self.txt.xview)
        sby.config(command=self.txt.yview)
        self.txt.config(xscrollcommand=sbx.set)
        self.txt.config(yscrollcommand=sby.set)
        self.txt.focus()
        text_frm.pack(fill=tk.BOTH, expand=tk.YES)

    def __save(self):
        parser = cp.ConfigParser()
        try:
            parser.read_string(self.txt.get("1.0", tk.END))
        except cp.Error as e:
            messagebox.showerror(
                "Bad INI format",
                str(e),
                parent=self)
            return
        if "aircraft.classes" not in parser.sections():
            messagebox.showerror(
                "Missing Section",
                "[aircraft.classes] not found",
                parent=self)
            return
        for key in parser["aircraft.classes"]:
            if parser["aircraft.classes"][key] not in {"spse", "spme", "mc"}:
                messagebox.showerror(
                    "Bad aircraft class",
                    f"{parser['aircraft.classes'][key]} is not a class\n"
                    f"Must be one of spse, spme or mc",
                    parent=self)
                return
        with open(CONFIG_FILE, "w") as f:
            parser.write(f)
        self.destroy()
        if self.callback:
            self.callback()

    def __help(self):
        webbrowser.open(HELP_URL)

    def do_modal(self, text, callback=None):
        self.callback = callback
        self.withdraw()
        try:
            with open(CONFIG_FILE) as f:
                config_str = f.read()
        except OSError:
            config_str = ""
        try:
            config_str = efjtk.config.build_config(text, config_str, True)
            self.txt.insert("1.0", config_str)
            self.txt.edit_reset()
            self.update_idletasks()
            c_x = self.parent.winfo_x() + self.parent.winfo_width() // 2
            c_y = self.parent.winfo_y() + self.parent.winfo_height() // 2
            self.geometry(f"+{c_x - self.winfo_reqwidth() // 2}"
                          f"+{c_y - self.winfo_reqheight() // 2}")
            self.deiconify()
            self.focus_set()
            self.grab_set()
        except VE as e:
            messagebox.showerror("Parse Error", str(e))
            self.destroy()


class MainWindow(tk.Tk):

    def __init__(self):
        tk.Tk.__init__(self)
        self.title(f"efjtk (v{efjtk.version.VERSION})")
        try:
            with open(SETTINGS_FILE) as f:
                self.settings = json.load(f)
        except Exception:
            self.settings = {}
        self.ac = self.__load_aircraft_classes()
        self.filename = None
        self.menus = {}
        self.__make_menu()
        self.menus["file"].entryconfigure("Save", state="disabled")
        self.menus["edit"].entryconfigure("Undo", state="disabled")
        self.menus["edit"].entryconfigure("Redo", state="disabled")
        self.__make_widgets()
        self.__update_status()
        self.txt.bind("<<UndoStack>>", self.__manage_undo)
        self.txt.bind("<<Modified>>", self.__manage_modified)

    def destroy(self):
        with open(SETTINGS_FILE, "w") as f:
            json.dump(self.settings, f, indent=4)
        if self.txt.edit_modified():
            if messagebox.askyesno("Save", "Save before quitting?"):
                if self.filename:
                    self.__save()
                else:
                    if not self.__save_as():
                        return  # don't quit if "save as" is cancelled
        self.quit()

    def __load_aircraft_classes(self):
        try:
            with open(CONFIG_FILE) as fc:
                config_str = fc.read()
        except OSError:
            config_str = ""
        return efjtk.config.aircraft_classes(config_str)

    def __make_widgets(self):
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)
        sbx = ttk.Scrollbar(self, orient='horizontal')
        sby = ttk.Scrollbar(self, orient='vertical')
        sbx.grid(row=2, column=0, sticky=tk.EW)
        sby.grid(row=1, column=1, rowspan=2, sticky=tk.NS)
        self.txt = TextWithSyntaxHighlighting(
            self, "efj", autoseparators=False)
        self.txt.bind('<KeyRelease>', self.__update_status, '+')
        self.txt.bind('<ButtonRelease>', self.__update_status, '+')
        self.txt.grid(row=1, column=0, sticky=tk.NSEW)
        sbx.config(command=self.txt.xview)
        sby.config(command=self.txt.yview)
        self.txt.config(xscrollcommand=sbx.set)
        self.txt.config(yscrollcommand=sby.set)
        self.search = SearchBar(self, self.txt)
        statusbar = ttk.Frame(self)
        statusbar.grid(row=3, column=0, columnspan=2, sticky=tk.EW)
        self.status = ttk.Label(statusbar, anchor="e",
                                padding=(16, 0), text=" ")
        ttk.Sizegrip(statusbar).pack(side=tk.RIGHT, anchor=tk.SE)
        self.status.pack(fill=tk.X)
        self.txt.focus()

    def __make_menu(self):
        top = tk.Menu(self)
        self.menus["top"] = top
        self.config(menu=top)
        self.__make_menu_section(top, "File", (
            ('Open', self.__open, "Ctrl+O", "<Control-Key-o>", 0),
            ('Save', self.__save, "Ctrl+S", "<Control-Key-s>", 0),
            ('Save As', self.__save_as, "Ctrl+A", "<Control-Key-a>", 5),
            ("", None),
            ('Update Config', self.__update_config),
            ("", None),
            ('Quit', self.destroy, "Ctrl+Q", "<Control-Key-q>", 0),
        ))
        self.__make_menu_section(top, "Edit", (
            ('Undo', self.__undo, "Ctrl+Z", "<Control-Key-z>", 0),
            ('Redo', self.__redo),
            ("", None),
            ('Cut', self.__cut, "Ctrl+X", None, 1),
            ('Copy', self.__copy, "Ctrl+C", None, 1),
            ('Paste', self.__paste, "Ctrl+V", None, 0),
            ("", None),
            ('Select All', self.__select_all, None, None, 7),
            ('Clear', self.__clear),
            ("", None),
            ('Goto Line', self.__goto_line, "Ctrl+G", "<Control-Key-g>", 1),
            ('Search', self.__search),
        ))
        self.__make_menu_section(top, "Modify", (
            ('Expand', self.__expand),
            ('Night', self.__night),
            ('FO', self.__fo),
            ('VFR', self.__vfr),
            ('Instructor', self.__instructor),
        ))
        self.__make_menu_section(top, "Export", (
            ('FCL.050 Logbook', self.__export_logbook),
            ('Cumulative Totals', self.__export_cumulative),
            ('Summary', self.__export_summary),
        ), 1)
        self.__make_menu_section(top, "Help", (
            ('Online Help', self.__help),
            ('eFJ format', self.__efj_help),
        ))

    def __make_accelerator(self, callback):
        def accelerator(ev):
            callback()
        return accelerator

    def __make_menu_section(self, top, label, entries, underline=0):
        menu = tk.Menu(top, tearoff=0)
        self.menus[label.lower()] = menu
        for entry in entries:
            entry_label, callback = entry[:2]
            accelerator, event, e_underline = None, None, 0
            if len(entry) == 5:
                accelerator, event, e_underline = entry[2:]
            if entry_label:
                menu.add_command(label=entry_label,
                                 command=callback,
                                 underline=e_underline,
                                 accelerator=accelerator)
                if event:
                    self.bind(event, self.__make_accelerator(callback))
            else:
                menu.add_separator()
        top.add_cascade(label=label, menu=menu, underline=underline)

    def __open(self):
        path = self.settings.get('openPath')
        fn = filedialog.askopenfilename(
            filetypes=(("Text", "*.txt"), ("Text", "*.efj"), ("All", "*")),
            initialdir=path)
        if not fn:
            return
        self.filename = fn
        self.settings['openPath'] = os.path.dirname(fn)
        with open(fn) as f:
            efj = f.read().strip()
            self.txt.delete("1.0", tk.END)
            self.txt.insert("1.0", efj)
            self.txt.see(tk.END)
            self.txt.edit_modified(False)
            self.txt.edit_reset()
            self.__update_status()

    def __save(self):
        assert self.filename
        with open(self.filename, "w", encoding="utf-8") as f:
            f.write(self.txt.get("1.0", tk.END))
            self.txt.edit_modified(False)

    def __save_as(self):
        path = self.settings.get('savePath')
        fn = filedialog.asksaveasfilename(
            filetypes=(("All", "*"),),
            initialdir=path)
        if fn:
            self.settings['savePath'] = os.path.dirname(fn)
            with open(fn, "w", encoding="utf-8") as f:
                f.write(self.txt.get("1.0", tk.END))
                self.filename = fn
                self.txt.edit_modified(False)
                return True
        return False

    def __update_config(self, callback=None):

        def update_ac_classes():
            self.ac = self.__load_aircraft_classes()
            if callback:
                callback()
        text = self.txt.get("1.0", tk.END)
        ConfigDialog(self).do_modal(text, update_ac_classes)

    def __expand(self):
        self.__modify(efjtk.modify.expand_efj)

    def __night(self):
        self.__modify(efjtk.modify.add_night_data)

    def __fo(self):
        self.__modify(efjtk.modify.add_fo_role_flag)

    def __vfr(self):
        self.__modify(efjtk.modify.add_vfr_flag)

    def __instructor(self):
        self.__modify(efjtk.modify.add_ins_flag)

    def __modify(self, fn):
        self.busy()
        self.update()
        text = self.txt.get('1.0', 'end')
        try:
            result = fn(text)
            range_ = self.txt.tag_ranges("sel")
            self.txt.edit_separator()
            if range_:
                start = f"{self.txt.index(range_[0])} linestart"
                end = f"{self.txt.index(range_[1])} lineend"
                start_line = int(self.txt.index(start).split(".")[0])
                end_line = int(self.txt.index(end).split(".")[0])
                result_lines = result.splitlines()
                result = "\n".join(result_lines[start_line - 1:end_line])
                self.txt.delete(start, end)
                self.txt.insert(start, result)
            else:
                self.txt.delete('1.0', tk.END)
                self.txt.insert('1.0', result)
                self.txt.see(tk.END)
        except VE as e:
            self.busy_forget()
            messagebox.showerror("Parse Error", str(e))
        finally:
            self.busy_forget()

    def __undo(self):
        if self.txt.edit("canundo"):
            self.txt.edit_undo()
            self.txt.highlight_syntax()

    def __redo(self):
        if self.txt.edit("canredo"):
            self.txt.edit_redo()
            self.txt.highlight_syntax()

    def __clear(self):
        self.txt.edit_separator()
        self.txt.delete('1.0', tk.END)
        self.menus["file"].entryconfigure("Save", state="disabled")

    def __cut(self):
        self.txt.edit_separator()
        self.txt.event_generate("<<Cut>>")

    def __copy(self):
        self.txt.event_generate("<<Copy>>")

    def __paste(self):
        self.txt.edit_separator()
        self.txt.event_generate("<<Paste>>")
        self.txt.highlight_syntax()

    def __select_all(self):
        self.txt.tag_add("sel", "1.0", tk.END)

    def __manage_undo(self, event):
        if self.txt.edit("canundo"):
            self.menus["edit"].entryconfigure("Undo", state="normal")
        else:
            self.menus["edit"].entryconfigure("Undo", state="disabled")
        if self.txt.edit("canredo"):
            self.menus["edit"].entryconfigure("Redo", state="normal")
        else:
            self.menus["edit"].entryconfigure("Redo", state="disabled")

    def __manage_modified(self, event):
        if self.filename and self.txt.edit_modified():
            self.menus["file"].entryconfigure("Save", state="normal")
            self.title("efjtk *")
        else:
            self.menus["file"].entryconfigure("Save", state="disabled")
            self.title("efjtk")

    def __export_logbook(self):
        self.__export(efjtk.convert.build_logbook)

    def __export_summary(self):
        self.__export(efjtk.convert.build_summary)

    def __export_cumulative(self):
        self.__export(efjtk.convert.build_cumulative)

    def __export(self, fn):
        text = self.txt.get("1.0", tk.END)

        def callback(daterange):
            try:
                result = fn(text, self.ac, daterange)
                path = self.settings.get('exportPath')
                if fname := filedialog.asksaveasfilename(
                        filetypes=(("HTML", "*.html"), ("All", "*")),
                        defaultextension=".html",
                        initialdir=path):
                    self.settings['exportPath'] = os.path.dirname(fname)
                    with open(fname, "w", encoding="utf-8") as f:
                        f.write(result)
            except efjtk.convert.UnknownAircraftType:
                self.__update_config(lambda: callback(daterange))
            except VE as e:
                messagebox.showerror("Parse Error", str(e))
        DateRangeDialog(self).show_modal(text, callback)

    def __help(self):
        webbrowser.open(HELP_URL)

    def __efj_help(self):
        webbrowser.open(HELP_EFJ)

    def __update_status(self, _=None):
        line, col = self.txt.index("insert").split(".")
        self.status.configure(text=f"Line {line}, Column {col}")

    def __goto_line(self):

        def callback(line):
            index = f"{line}.0"
            self.txt.mark_set("insert", index)
            self.txt.see(index)
        last = int(self.txt.index("end-1 chars").split(".")[0])
        GotoLineDialog(self).do_modal(last, callback)

    def __search(self):
        self.search.grid(row=0, column=0, columnspan=2, sticky=tk.EW)
        self.search.grab_focus()


class SearchBar(ttk.Frame):

    def __init__(self, parent, target):
        ttk.Frame.__init__(self, parent, padding=2)
        self.search_term = tk.StringVar()
        self.target = target
        self.__make_widgets()
        self.entry.bind("<Return>", lambda _: self.__next())

    def __make_widgets(self):
        ttk.Label(self, text="Search for:"
                  ).grid(row=0, column=1)
        self.entry = ttk.Entry(self, textvariable=self.search_term)
        self.entry.grid(row=0, column=2, sticky=tk.EW, padx="10p")
        ttk.Button(self, text="Prev", command=self.__previous
                   ).grid(row=0, column=3, padx="2p")
        ttk.Button(self, text="Next", command=self.__next
                   ).grid(row=0, column=4, padx="2p")
        ttk.Button(self, text="Close", command=self.__remove
                   ).grid(row=0, column=5, padx=["10p", 0])
        self.grid_columnconfigure(2, weight=1)

    def __remove(self):
        self.grid_remove()

    def __next(self):
        self.target.search_next(self.search_term.get())

    def __previous(self):
        self.target.search_prev(self.search_term.get())

    def grab_focus(self):
        self.entry.focus()


class DateRangeDialog(tk.Toplevel):

    def __init__(self, parent):
        tk.Toplevel.__init__(self, padx=5, pady=5)
        self.parent = parent

        self.title("Date Range")
        self.resizable(False, False)
        self.transient(parent)

        self.tk_from = tk.StringVar(parent)
        self.tk_to = tk.StringVar(parent)
        tk_validate = self.register(self.validate)

        PADDING = 5
        f = ttk.Frame(self)
        f.pack(padx=PADDING, pady=PADDING)
        ttk.Label(f, width=15, text="From (inclusive): ").pack(side=tk.LEFT)
        ttk.Entry(f, width=20, justify="center", textvariable=self.tk_from,
                  validate="key", validatecommand=(tk_validate, "%P"),
                  ).pack(side=tk.RIGHT)
        f = ttk.Frame(self)
        f.pack(padx=PADDING, pady=PADDING)
        ttk.Label(f, width=15, text="To (exclusive): ").pack(side=tk.LEFT)
        ttk.Entry(f, width=20, justify="center", textvariable=self.tk_to,
                  validate="key", validatecommand=(tk_validate, "%P"),
                  ).pack(side=tk.RIGHT)
        buttons = ttk.Frame(self)
        buttons.pack(fill=tk.X, padx=PADDING, pady=PADDING)
        ttk.Button(buttons, width=10, text="OK", command=self.ok
                   ).pack(side=tk.RIGHT, padx=PADDING)
        ttk.Button(buttons, width=10, text="Cancel", command=self.destroy
                   ).pack(side=tk.RIGHT, padx=PADDING)

    def efj_full_range(self, efj):
        dates: list[dt.date] = []
        for line in efj.splitlines():
            if mo := re.match(r"\s*(\d{4}-\d{2}-\d{2})|([+]+)", line):
                if mo.group(1):
                    try:
                        dates.append(dt.date.fromisoformat(mo.group(1)))
                    except ValueError:
                        continue
                elif dates and mo.group(2):
                    dates.append(dates[-1] +
                                 dt.timedelta(days=len(mo.group(2))))
        if len(dates) == 0:
            return None
        return (min(dates), max(dates) + dt.timedelta(days=1))

    def show_modal(self, efj, callback):
        if r := self.efj_full_range(efj):
            self.callback = callback
            self.tk_from.set(r[0].isoformat())
            self.tk_to.set(r[1].isoformat())
            self.withdraw()
            self.update_idletasks()
            c_x = self.parent.winfo_x() + self.parent.winfo_width() // 2
            c_y = self.parent.winfo_y() + self.parent.winfo_height() // 2
            self.geometry(f"+{c_x - self.winfo_reqwidth() // 2}"
                          f"+{c_y - self.winfo_reqheight() // 2}")
            self.deiconify()
            self.grab_set()
            self.focus_set()
        else:
            self.destroy()
            messagebox.showerror("Invalid Data", "No dates found")

    def ok(self):
        try:
            daterange = (dt.date.fromisoformat(self.tk_from.get()),
                         dt.date.fromisoformat(self.tk_to.get()))
            self.destroy()
            self.callback(daterange)
        except ValueError as e:
            messagebox.showerror("Invalid Data", str(e))

    def validate(self, s):
        return False if re.search(r"[^\d-]", s) else True


class GotoLineDialog(tk.Toplevel):

    def __init__(self, parent):
        tk.Toplevel.__init__(self)
        self.parent = parent
        tk_validate = self.register(self.validate)
        self.tk_line = tk.StringVar(parent, "")

        PADDING = 5
        f = ttk.Frame(self)
        f.pack(padx=PADDING, pady=PADDING)
        ttk.Label(f, width=10, text="Go to line: ").pack(side=tk.LEFT)
        self.entry = ttk.Entry(
            f, width=20, justify="center", textvariable=self.tk_line,
            validate="key", validatecommand=(tk_validate, "%P"))
        self.entry.pack(side=tk.RIGHT)
        self.entry.bind("<Return>", self.ok)
        self.entry.bind("<Escape>", lambda _: self.destroy())
        buttons = ttk.Frame(self)
        buttons.pack(fill=tk.X, padx=PADDING, pady=PADDING)
        ttk.Button(buttons, width=10, text="OK", command=self.ok
                   ).pack(side=tk.RIGHT, padx=PADDING)
        ttk.Button(buttons, width=10, text="Cancel", command=self.destroy
                   ).pack(side=tk.RIGHT, padx=PADDING)

    def validate(self, s):
        return False if re.search(r"[^\d]", s) else True

    def ok(self, _):
        try:
            try:
                line = int(self.tk_line.get())
            except ValueError:
                raise ValueError(f"{self.tk_line.get()} is not valid")
            if line > self.maxvalue:
                raise ValueError(f"Last line is {self.maxvalue}")
            self.callback(line)
            self.destroy()
        except ValueError as e:
            messagebox.showerror("Invalid Data", str(e))

    def do_modal(self, maxvalue, callback):
        self.callback = callback
        self.maxvalue = maxvalue
        self.withdraw()
        self.update_idletasks()
        c_x = self.parent.winfo_x() + self.parent.winfo_width() // 2
        c_y = self.parent.winfo_y() + self.parent.winfo_height() // 2
        self.geometry(f"+{c_x - self.winfo_reqwidth() // 2}"
                      f"+{c_y - self.winfo_reqheight() // 2}")
        self.deiconify()
        self.grab_set()
        self.entry.focus_set()


def main():
    if "windll" in dir(ctypes):
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
    MainWindow().mainloop()


if __name__ == "__main__":
    main()
