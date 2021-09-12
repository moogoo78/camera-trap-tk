import tkinter as tk
from tkinter import (
    ttk,
)
from PIL import Image, ImageTk

class Panel(tk.Frame):

    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        #self.parent = parent
        self.app = parent
        self.layout()


    def layout(self):
        #miFrame=tk.Frame(self,bg='red',width=800,height=700)
        #miFrame.grid()
        photo_folder = ImageTk.PhotoImage(file="./src/img/folder.png")
        photo_cloud = ImageTk.PhotoImage(file="./src/img/cloud.png")

        self.button_folder = ttk.Button(
            self,
            image=photo_folder,
            command=self.app.toggle_folder_list,
            takefocus=0,
        )
        self.button_folder.image = photo_folder
        self.button_folder.grid(row=0, column=0, sticky='news')
        self.button_upload = ttk.Button(
            self,
            image=photo_cloud,
            command=self.app.toggle_upload_progress,
            takefocus=0,
        )
        self.button_upload.image = photo_cloud
        self.button_upload.grid(row=1, column=0, sticky='news')


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
