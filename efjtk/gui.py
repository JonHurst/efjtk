import tkinter as tk
from tkinter import ttk
# from tkinter import messagebox
# from tkinter import filedialog
import os.path
import ctypes


SETTINGS_FILE = os.path.expanduser("~/.efjtkguirc")


class MainWindow(tk.Tk):

    def __init__(self):
        tk.Tk.__init__(self)
        self.title("efjtk")
        self.__make_menu()
        self.__make_widgets()

    def __make_widgets(self):
        sbx = ttk.Scrollbar(self, orient='horizontal')
        sby = ttk.Scrollbar(self, orient='vertical')
        sbx.grid(row=1, column=0, sticky=tk.EW)
        sby.grid(row=0, column=1, sticky=tk.NS)
        self.txt = tk.Text(self)
        self.txt.grid(row=0, column=0, sticky=tk.NSEW)
        sbx.config(command=self.txt.xview)
        sby.config(command=self.txt.yview)
        self.txt.config(xscrollcommand=sbx.set)
        self.txt.config(yscrollcommand=sby.set)

    def __make_menu(self):
        top = tk.Menu(self)
        self.config(menu=top)
        self.__make_menu_section(top, "File", (
            ('Open', self.__not_implemented),
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
        ))

    def __make_menu_section(self, top, label, entries):
        menu = tk.Menu(top, tearoff=0)
        for entry_label, callback in entries:
            if entry_label:
                menu.add_command(label=entry_label, command=callback)
            else:
                menu.add_separator()
        top.add_cascade(label=label, menu=menu)

    def __not_implemented(self):
        pass


def main():
    if "windll" in dir(ctypes):
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
    MainWindow().mainloop()


if __name__ == "__main__":
    main()
