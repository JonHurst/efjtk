import tkinter as tk
from tkinter import ttk
# from tkinter import messagebox
from tkinter import filedialog
import os.path
import ctypes
import json

import efjtk.modify

SETTINGS_FILE = os.path.expanduser("~/.efjtkguirc")


class TextWithSyntaxHighlighting(tk.Text):

    def __init__(self, parent, highlight_mode, **kwargs):
        tk.Text.__init__(self, parent, background='white',
                         wrap="none", undo=True, autoseparators=False,
                         **kwargs)
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
        self.edit_modified(False)

    def highlight_efj(self):
        count = tk.IntVar()
        start_idx = "1.0"
        while True:
            new_idx = self.search(
                r"\d{4}-\d{2}-\d{2}",
                start_idx, count=count, regexp=True,
                stopindex="end")
            if not new_idx:
                break
            start_idx = f"{new_idx} + {count.get()} chars"
            self.tag_add("datetime", new_idx, start_idx)
        start_idx = "1.0"
        while True:
            new_idx = self.search(
                r"\d{4}/\d{4}",
                start_idx, count=count, regexp=True,
                stopindex="end")
            if not new_idx:
                break
            start_idx = f"{new_idx} + {count.get()} chars"
            self.tag_add("datetime", new_idx, start_idx)
        start_idx = "1.0"
        while True:
            new_idx = self.search(
                "CP:|FO:|PU:|FA:",
                start_idx, count=count, regexp=True,
                stopindex="end")
            if not new_idx:
                break
            start_idx = f"{new_idx} + {count.get()} chars"
            self.tag_add("keyword", new_idx, start_idx)
        start_idx = "1.0"
        while True:
            new_idx = self.search(
                r"#.*",
                start_idx, count=count, regexp=True,
                stopindex="end")
            if not new_idx:
                break
            start_idx = f"{new_idx} + {count.get()} chars"
            self.tag_add("grayed", new_idx, start_idx)


class MainWindow(tk.Tk):

    def __init__(self):
        try:
            with open(SETTINGS_FILE) as f:
                self.settings = json.load(f)
        except Exception:
            self.settings = {}
        tk.Tk.__init__(self)
        self.title("efjtk")
        self.menus = {}
        self.__make_menu()
        self.menus["edit"].entryconfigure("Undo", state="disabled")
        self.menus["edit"].entryconfigure("Redo", state="disabled")
        self.__make_widgets()
        self.txt.bind("<<UndoStack>>", self.__manage_undo)

    def destroy(self):
        with open(SETTINGS_FILE, "w") as f:
            json.dump(self.settings, f, indent=4)
        tk.Tk.destroy(self)

    def __make_widgets(self):
        sbx = ttk.Scrollbar(self, orient='horizontal')
        sby = ttk.Scrollbar(self, orient='vertical')
        sbx.grid(row=1, column=0, sticky=tk.EW)
        sby.grid(row=0, column=1, sticky=tk.NS)
        self.txt = TextWithSyntaxHighlighting(self, "efj")
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
            ('Open', self.__open),
            ('Save', self.__not_implemented),
            ("", None),
            ('Quit', self.quit),
        ))
        self.__make_menu_section(top, "Edit", (
            ('Undo', self.__undo),
            ('Redo', self.__redo),
            ("", None),
            ('Clear', self.__not_implemented),
        ))
        self.__make_menu_section(top, "Modify", (
            ('Expand', self.__expand),
            ('Night', self.__night),
            ('FO', self.__fo),
            ('VFR', self.__vfr),
            ('Instructor', self.__instructor),
        ))
        self.__make_menu_section(top, "Export", (
            ('FCL.050 Logook', self.__not_implemented),
            ('Summary', self.__not_implemented),
        ), 1)

    def __make_menu_section(self, top, label, entries, underline=0):
        menu = tk.Menu(top, tearoff=0)
        self.menus[label.lower()] = menu
        for entry_label, callback in entries:
            if entry_label:
                menu.add_command(label=entry_label,
                                 command=callback,
                                 underline=0)
            else:
                menu.add_separator()
        top.add_cascade(label=label, menu=menu, underline=underline)

    def __not_implemented(self):
        pass

    def __open(self):
        path = self.settings.get('openPath')
        fn = filedialog.askopenfilename(
            filetypes=(("All", "*"),),
            initialdir=path)
        if not fn:
            return
        self.settings['openPath'] = os.path.dirname(fn)
        with open(fn) as f:
            efj = f.read()
            self.txt.delete("1.0", tk.END)
            self.txt.insert("1.0", efj)
            self.txt.see(tk.END)

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
        if range_:
            start_line = int(self.txt.index(range_[0]).split(".")[0]) - 1
            end_line = int(self.txt.index(range_[1]).split(".")[0]) - 1
            text_lines = text.splitlines()
            result_lines = result.splitlines()
            result = "\n".join(text_lines[:start_line] +
                               result_lines[start_line:end_line]
                               + text_lines[end_line:])
        self.txt.edit_separator()
        pos = self.txt.index(tk.INSERT)
        self.txt.delete('1.0', tk.END)
        self.txt.insert('1.0', result)
        self.txt.mark_set(tk.INSERT, pos)

    def __undo(self):
        if self.txt.edit("canundo"):
            self.txt.edit_undo()
            self.txt.highlight_syntax()

    def __redo(self):
        if self.txt.edit("canredo"):
            self.txt.edit_redo()
            self.txt.highlight_syntax()

    def __manage_undo(self, event):
        if self.txt.edit("canundo"):
            self.menus["edit"].entryconfigure("Undo", state="normal")
        else:
            self.menus["edit"].entryconfigure("Undo", state="disabled")
        if self.txt.edit("canredo"):
            self.menus["edit"].entryconfigure("Redo", state="normal")
        else:
            self.menus["edit"].entryconfigure("Redo", state="disabled")


def main():
    if "windll" in dir(ctypes):
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
    MainWindow().mainloop()


if __name__ == "__main__":
    main()
