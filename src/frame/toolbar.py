import tkinter as tk
from tkinter import (
    ttk,
)


class Toolbar(tk.Frame):

    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent
        self.layout()

        self.source_list = []

    def layout(self):
        self.toggle_button = ttk.Button(
            self,
            text='顯示目錄',
            command=self.toggle_sidebar)
        self.toggle_button.grid(row=0, column=0, padx=10)
        self.big_image_button = ttk.Button(
            self,
            text='全視窗照片',
            command=self.toggle_big_image)
        self.big_image_button.grid(row=0, column=1, padx=10)

    def toggle_sidebar(self):
        sidebar = self.parent.sidebar
        if sidebar.winfo_viewable():
            sidebar.grid_remove()
        else:
            sidebar.grid()

    def toggle_big_image(self):
        image_viewer = self.parent.image_viewer
        if image_viewer.winfo_viewable():
            image_viewer.grid_remove()
            # unbind key event
            self.parent.unbind('<Left>')
            self.parent.unbind('<Up>')
            self.parent.unbind('<Right>')
            self.parent.unbind('<Down>')
        else:
            image_viewer.grid(row=2, column=1, sticky='nsew')
            image_viewer.refresh()
