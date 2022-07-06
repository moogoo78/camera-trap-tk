import tkinter as tk
from tkinter import (
    ttk,
)
from PIL import Image, ImageTk

class AppBar(tk.Frame):

    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.app = parent

        self.layout()


    def layout(self):
        self.grid_rowconfigure(0, weight=0)
        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)

        self.toggle_button = ttk.Button(
            self,
            text='顯示',
            command=self.app.toggle_panel
        )
        self.toggle_button.grid(row=0, column=0, padx=10)

        banner = ImageTk.PhotoImage(file='./assets/banner.png')
        img_label = tk.Label(self,image=banner, bg=self.app.app_primary_color)
        img_label.image = banner
        img_label.grid(row=0, column=1, sticky='w', pady=(14, 4))

