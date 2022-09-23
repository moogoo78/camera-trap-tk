import tkinter as tk
from tkinter import (
    ttk,
)
from PIL import Image, ImageTk

class Panel(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)

        self.app = parent

        self.is_viewable = False  # for decide toggle

        self.layout()

    def layout(self):
        '''
        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=0)
        self.grid_rowconfigure(2, weight=0)
        self.grid_rowconfigure(3, weight=0)
        self.grid_columnconfigure(0, weight=1)
        '''

        self.canvas = tk.Canvas(
            self,
            width=240,
            height=self.app.app_height-50-25,
            bg='#CFCFCF',
            bd=0,
            highlightthickness=0,
            relief='ridge',
        )
        self.canvas.grid(row=0, column=0, sticky='ewns')

        self.canvas.create_rectangle(
            0, 24,
            240, 74,
            fill='#FFFFFF',
            outline='#FFFFFF',
            tags=('import_folder'),
        )
        self.canvas.create_text(
            120,
            50,
            text='加入資料夾',
            font=self.app.get_font('display-3'),
            fill=self.app.app_primary_color,
            tags=('import_folder'),
        )
        self.canvas.tag_bind(
            'import_folder',
            '<Button-1>',
            self.app.on_add_folder
        )

        self.canvas.create_rectangle(
            0, 94,
            240, 144,
            fill='#FFFFFF',
            outline='#FFFFFF',
            tags=('list_folder'),
        )
        self.canvas.create_text(
            120,
            120,
            text='現有資料夾',
            font=self.app.get_font('display-3'),
            fill=self.app.app_primary_color,
            tags=('list_folder'),
        )
        self.canvas.tag_bind(
            'list_folder',
            '<Button-1>',
            self.app.on_folder_list
        )

        self.canvas.create_rectangle(
            0, 164,
            240, 214,
            fill='#FFFFFF',
            outline='#FFFFFF',
            tags=('upload_progress'),
        )
        self.canvas.create_text(
            120,
            190,
            text='上傳進度',
            font=self.app.get_font('display-3'),
            fill=self.app.app_primary_color,
            tags=('upload_progress'),
        )
        self.canvas.tag_bind(
            'upload_progress',
            '<Button-1>',
            self.app.on_upload_progress
        )

        self.canvas.create_rectangle(
            0, 234,
            240, 284,
            fill='#FFFFFF',
            outline='#FFFFFF',
            tags=('help_page'),
        )
        self.canvas.create_text(
            120,
            260,
            text='教學說明',
            font=self.app.get_font('display-3'),
            fill=self.app.app_primary_color,
            tags=('help_page'),
        )
        self.canvas.tag_bind(
            'help_page',
            '<ButtonPress-1>',
            self.app.on_help_page
        )


    def show(self):
        self.place(x=0, y=50, anchor='nw')
        self.is_viewable = True

    def hide(self):
        self.place_forget()
        self.is_viewable = False
        # self.place(x=-240, y=50, anchor='nw')

class Panel_DEPRECATED(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)

        #self.app = parent.app

        #self.layout()
        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=0)
        self.grid_rowconfigure(2, weight=0)
        self.grid_rowconfigure(3, weight=0)
        self.grid_columnconfigure(0, weight=1)

        self.add_folder_btn = ttk.Button(
            self,
            text='加入資料夾',
            #command=self.app.toggle_folder_list,
            takefocus=0,
            #width=30,
        )
        self.add_folder_btn.grid(row=0, column=0)
        self.folder_list_btn = ttk.Button(
            self,
            text='現有資料夾',
            #command=self.app.toggle_folder_list,
            takefocus=0,
        )
        self.folder_list_btn.grid(row=1, column=0)
        self.upload_progress_btn = ttk.Button(
            self,
            text='上傳進度',
            #command=self.app.toggle_folder_list,
            takefocus=0,
        )
        self.upload_progress_btn.grid(row=2, column=0)

    def layout(self):
        miFrame=tk.Frame(self,bg='red',width=800,height=700)
        miFrame.grid()
        photo_folder = ImageTk.PhotoImage(file="./assets/folder.png")
        photo_cloud = ImageTk.PhotoImage(file="./assets/cloud.png")

        self.button_folder = ttk.Button(
            self,
            image=photo_folder,
            #command=self.app.toggle_folder_list,
            takefocus=0,
        )
        self.button_folder.image = photo_folder
        self.button_folder.grid(row=0, column=0, sticky='news')
        self.button_upload = ttk.Button(
            self,
            image=photo_cloud,
            #command=self.app.toggle_upload_progress,
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
