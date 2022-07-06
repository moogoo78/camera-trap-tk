import tkinter as tk
from tkinter import (
    ttk,
)

class Footer(tk.Frame):

    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent

        self.layout()


    def layout(self):
        label = ttk.Label(
            self,
            text='Copyright © 2021 Forestry Bureau 行政院農業委員會林務局 版權所有?',
            background=self.parent.app_primary_color,
            foreground='white',
        )
        # TODO_LAYOUT: font 10px
        label.grid(row=0, column=0, sticky='w', padx=60, pady=3)
