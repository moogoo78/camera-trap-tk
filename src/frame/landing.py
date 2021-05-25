import tkinter as tk
from tkinter import (
    ttk,
)
class Landing(tk.Frame):

    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent

        self.message = ttk.Label(self, text="Hello")
        self.message.grid(row=0, column=0, sticky='nsew', padx=10, pady=10)
