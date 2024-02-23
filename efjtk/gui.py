import tkinter as tk
import tkinter.font as font
from tkinter import ttk
from tkinter import messagebox
from tkinter import filedialog
import os.path
import ctypes
import json
import webbrowser
import configparser as cp

import efjtk.modify
import efjtk.convert
import efjtk.config


SETTINGS_FILE = os.path.expanduser("~/.efjtkguirc")
CONFIG_FILE = os.path.expanduser("~/.efjtkrc")
HELP_URL = "https://staging.hursts.org.uk/efjtkdocs/gui.html"
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
            lambda *args: self.edit_modified() and self.highlight_syntax())

    def insert(self, idx, text, *args):
        tk.Text.insert(self, idx, text, *args)
        self.highlight_syntax()

    def highlight_syntax(self):
        if not self.highlight_mode:
            return
        for tag in ("keyword", "datetime", "grayed"):
            self.tag_remove(tag, "1.0", "end")
        if self.highlight_mode == 'efj':
            self.highlight_efj()
        elif self.highlight_mode == 'config':
            self.highlight_config()

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
        for re, tag in ((r"\d{4}-\d{2}-\d{2}", "datetime"),
                        (r"\d{4}/\d{4}", "datetime"),
                        ("CP:|FO:|PU:|FA:", "keyword"),
                        (r"#.*", "grayed")):
            self.__highlight(re, tag)

    def highlight_config(self):
        for re, tag in ((r"(spse|spme|mc)\s", "keyword"),
                        (r"\[[\w.]+\]\n", "grayed")):
            self.__highlight(re, tag)


class ConfigDialog(tk.Toplevel):

    def __init__(self):
        tk.Toplevel.__init__(self)
        self.title("Config Editor")
        self.__make_widgets()
        self.retval = False

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
        self.retval = True
        self.destroy()

    def __help(self):
        webbrowser.open(HELP_URL)

    def do_modal(self):
        try:
            with open(CONFIG_FILE) as f:
                self.txt.insert("1.0", f.read())
        except OSError:
            self.txt.insert("1.0", "[aircraft.classes]\n")
        self.txt.edit_reset()
        self.focus_set()
        self.grab_set()
        self.wait_window()
        return self.retval


class MainWindow(tk.Tk):

    def __init__(self):
        try:
            with open(SETTINGS_FILE) as f:
                self.settings = json.load(f)
        except Exception:
            self.settings = {}
        tk.Tk.__init__(self)
        self.title("efjtk")
        self.filename = None
        self.menus = {}
        self.__make_menu()
        self.menus["file"].entryconfigure("Save", state="disabled")
        self.menus["edit"].entryconfigure("Undo", state="disabled")
        self.menus["edit"].entryconfigure("Redo", state="disabled")
        self.__make_widgets()
        self.txt.bind("<<UndoStack>>", self.__manage_undo)
        self.txt.bind("<<Modified>>", self.__manage_modified)

    def destroy(self):
        with open(SETTINGS_FILE, "w") as f:
            json.dump(self.settings, f, indent=4)
        if self.txt.edit_modified():
            if messagebox.askyesno("Save", "Save before quitting?"):
                self.__save()
        self.quit()

    def __make_widgets(self):
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        sbx = ttk.Scrollbar(self, orient='horizontal')
        sby = ttk.Scrollbar(self, orient='vertical')
        grip = ttk.Sizegrip(self)
        sbx.grid(row=1, column=0, sticky=tk.EW)
        sby.grid(row=0, column=1, sticky=tk.NS)
        grip.grid(row=1, column=1, sticky=tk.NSEW)
        self.txt = TextWithSyntaxHighlighting(
            self, "efj", autoseparators=False)
        self.txt.grid(row=0, column=0, sticky=tk.NSEW)
        sbx.config(command=self.txt.xview)
        sby.config(command=self.txt.yview)
        self.txt.config(xscrollcommand=sbx.set)
        self.txt.config(yscrollcommand=sby.set)
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
            ('Edit Config', self.__config, "Ctrl+G", "<Control-Key-g>", 10),
            ("", None),
            ('Quit', self.destroy, "Ctrl+Q", "<Control-Key-q>", 0),
        ))
        self.__make_menu_section(top, "Edit", (
            ('Undo', self.__undo, "Ctrl+Z", "<Control-Key-z>", 0),
            ('Redo', self.__redo, "Ctrl-Shift+Z", "<Control-Shift-Key-z>", 0),
            ("", None),
            ('Cut', self.__cut, "Ctrl+X", None, 0),
            ('Copy', self.__copy, "Ctrl+C", None, 0),
            ('Paste', self.__paste, "Ctrl+V", None, 0),
            ("", None),
            ('Select All', self.__select_all, "Ctrl+L", "<Control-Key-l>", 8),
            ('Clear', self.__clear, "Ctrl+Del", "<Control-Delete>", 0),
        ))
        self.__make_menu_section(top, "Modify", (
            ('Expand', self.__expand, "Ctrl+E", "<Control-Key-e>", 0),
            ('Night', self.__night, "Ctrl+N", "<Control-Key-n>", 0),
            ('FO', self.__fo, "Ctrl+F", "<Control-Key-f>", 0),
            ('VFR', self.__vfr, "Ctrl+R", "<Control-Key-r>", 0),
            ('Instructor', self.__instructor, "Ctrl+I", "<Control-Key-i>", 0),
        ))
        self.__make_menu_section(top, "Export", (
            ('FCL.050 Logbook', self.__export_logbook,
             "Ctrl-L", "<Control-Key-l>", 8),
            ('Summary', self.__export_summary, "Ctrl-M", "<Control-Key-m>", 2),
        ), 1)
        self.__make_menu_section(top, "Help", (
            ('Online Help', self.__help, "Ctrl-H", "<Control-Key-h>", 7),
            ('eFJ format', self.__efj_help, "Ctrl-J", "<Control-Key-j>", 2),
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
            filetypes=(("All", "*"),),
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

    def __save(self):
        if not self.filename:
            return
        with open(self.filename, "w", encoding="utf-8") as f:
            f.write(self.txt.get("1.0", tk.END))
            self.txt.edit_modified(False)

    def __save_as(self):
        path = self.settings.get('savePath')
        fn = filedialog.asksaveasfilename(
            filetypes=(("All", "*"),),
            initialdir=path)
        if not fn:
            return
        self.settings['savePath'] = os.path.dirname(fn)
        with open(fn, "w", encoding="utf-8") as f:
            f.write(self.txt.get("1.0", tk.END))
            self.filename = fn
            self.txt.edit_modified(False)

    def __config(self):
        return ConfigDialog().do_modal()

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
        text = self.txt.get('1.0', 'end')
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
        if not (text := self.txt.get("1.0", tk.END)):
            return
        try:
            with open(CONFIG_FILE) as fc:
                config_str = fc.read()
        except OSError:
            config_str = ""
        ac = efjtk.config.aircraft_classes(config_str)
        try:
            result = efjtk.convert.build_logbook(text, ac)
            path = self.settings.get('exportPath')
            if not (fn := filedialog.asksaveasfilename(
                    filetypes=(("HTML", "*.html"),
                               ("All", "*")),
                    defaultextension=".html",
                    initialdir=path)):
                return
            self.settings['exportPath'] = os.path.dirname(fn)
            with open(fn, "w", encoding="utf-8") as f:
                f.write(result)
                messagebox.showinfo("Saved", "Logbook saved")
        except efjtk.convert.UnknownAircraftType:
            self.__add_unknown_aircraft_to_config(text, config_str)
            if self.__config():
                self.__export_logbook()

    def __add_unknown_aircraft_to_config(self, text, config_str):
        try:
            config_str = efjtk.config.build_config(text, config_str, True)
            with open(CONFIG_FILE, "w") as fc:
                fc.write(config_str)
        except cp.Error:
            messagebox.showerror(
                "Config Error",
                "Bad config file. Please correct it!")

    def __export_summary(self):
        if not (text := self.txt.get("1.0", tk.END)):
            return
        result = efjtk.convert.build_summary(text)
        path = self.settings.get('exportPath')
        if not (fn := filedialog.asksaveasfilename(
                filetypes=(("HTML", "*.html"),
                           ("All", "*")),
                defaultextension=".html",
                initialdir=path)):
            return
        self.settings['exportPath'] = os.path.dirname(fn)
        with open(fn, "w", encoding="utf-8") as f:
            f.write(result)
            messagebox.showinfo("Saved", "Summary saved")

    def __help(self):
        webbrowser.open(HELP_URL)

    def __efj_help(self):
        webbrowser.open(HELP_EFJ)


def main():
    if "windll" in dir(ctypes):
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
    MainWindow().mainloop()


if __name__ == "__main__":
    main()
