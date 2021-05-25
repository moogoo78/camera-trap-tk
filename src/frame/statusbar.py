import tkinter as tk
from tkinter import (
    ttk,
)


class Statusbar(tk.Frame):

    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent

        self.progress_bar = ttk.Progressbar(self, orient=tk.HORIZONTAL, length=800, mode='determinate', value=0)
        self.progress_bar.grid()
