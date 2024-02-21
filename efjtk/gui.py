import tkinter as tk
from tkinter import ttk
# from tkinter import messagebox
from tkinter import filedialog
import os.path
import ctypes
import json


SETTINGS_FILE = os.path.expanduser("~/.efjtkguirc")


class TextWithSyntaxHighlighting(tk.Text):

    def __init__(self, parent, highlight_mode, **kwargs):
        tk.Text.__init__(self, parent, background='white',
                         wrap="none", **kwargs)
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
        self.__make_menu()
        self.__make_widgets()

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
        self.config(menu=top)
        self.__make_menu_section(top, "File", (
            ('Open', self.__open),
            ('Save', self.__not_implemented),
            ("", None),
            ('Quit', self.quit),
        ))
        self.__make_menu_section(top, "Edit", (
            ('Undo', self.__not_implemented),
            ("", None),
            ('Clear', self.__not_implemented),
        ))
        self.__make_menu_section(top, "Modify", (
            ('Expand', self.__not_implemented),
            ('Night', self.__not_implemented),
            ('FO', self.__not_implemented),
            ('VFR', self.__not_implemented),
            ('Instructor', self.__not_implemented),
        ))
        self.__make_menu_section(top, "Export", (
            ('FCL.050 Logook', self.__not_implemented),
            ('Summary', self.__not_implemented),
        ), 1)

    def __make_menu_section(self, top, label, entries, underline=0):
        menu = tk.Menu(top, tearoff=0)
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


def main():
    if "windll" in dir(ctypes):
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
    MainWindow().mainloop()


if __name__ == "__main__":
    main()
