import tkinter as tk
from tkinter import (
    ttk,
)


class Toolbar(tk.Frame):

    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        self.parent = parent
        self.layout()

        self.source_list = []

    def layout(self):
        self.toggle_button = ttk.Button(
            self,
            text='顯示目錄',
            command=self.parent.toggle_sidebar)
        self.toggle_button.grid()
