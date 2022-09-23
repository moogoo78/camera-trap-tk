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

        # self.toggle_button = ttk.Button(
        #     self,
        #     text='顯示',
        #     command=self.app.toggle_panel
        # )
        # self.toggle_button.grid(row=0, column=0, padx=10)
        self.hamburger = ImageTk.PhotoImage(file='./assets/icon-hamburger.png')

        btn_menu = tk.Button(
            self,
            image=self.hamburger,
            bg=self.app.app_primary_color,
            command=self.app.toggle_panel,
            borderwidth=0)
        btn_menu.image = self.hamburger
        btn_menu.grid(row=0, column=0, sticky='w', pady=(8, 8), padx=(12, 8))

        banner = ImageTk.PhotoImage(file='./assets/banner.png')
        img_label = tk.Label(self,image=banner, bg=self.app.app_primary_color)
        img_label.image = banner
        img_label.grid(row=0, column=1, sticky='w', pady=(14, 4))

