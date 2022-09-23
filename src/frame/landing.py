import tkinter as tk
from tkinter import (
    ttk,
)

from PIL import (
    Image,
    ImageTk
)

class Landing(tk.Frame):

    def __init__(self, parent, *args, **kwargs):

        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.app = parent

        self.grid_rowconfigure(0, weight=0)
        self.grid_columnconfigure(0, weight=0)

        canvas = tk.Canvas(
            self,
            width=self.app.app_width,
            height=self.app.app_height-50-25,
            bg='#777777',
            bd=0,
            highlightthickness=0,
            relief='ridge',
        )
        canvas.grid(row=0, column=0, sticky='ewns')

        # assign to self, for not clear by python's garbage collection...
        self.bg = ImageTk.PhotoImage(file='./assets/landing_bg.png')

        canvas.create_image(
            0,
            0,
            image=self.bg,
            anchor='nw',
        )

        canvas.create_text(
            920,
            250,
            text='臺灣自動相機上傳系統',
            fill='#FFFFFF',
            font=self.app.get_font('display-1')
        )
        canvas.create_text(
            900,
            300,
            text='Taiwan Camera Trap System',
            fill='#FFFFFF',
            font=self.app.get_font(29)
        )

        canvas.create_rectangle(
            660, 340,
            900, 398,
            fill=self.app.app_primary_color,
            outline=self.app.app_primary_color,
            tags=('button-folder-list'),
        )
        canvas.create_text(
            785,
            369,
            text='現有資料夾',
            fill='#FFFFFF',
            font=self.app.get_font('display-3'),
            tags=('button-folder-list'),
        )
        canvas.create_rectangle(
            920, 340,
            1160, 398,
            fill=self.app.app_primary_color,
            outline=self.app.app_primary_color,
            tags=('button-folder-add'),
        )
        canvas.create_text(
            1040,
            369,
            text='加入資料夾',
            fill='#FFFFFF',
            font=self.app.get_font('display-3'),
            tags=('button-folder-add'),
        )
        canvas.tag_bind(
            'button-folder-list',
            '<ButtonPress>',
            self.app.on_folder_list)

        canvas.tag_bind(
            'button-folder-add',
            '<ButtonPress>',
            self.app.on_add_folder)

        # self.btn1 = ttk.Button(
        #     self,
        #     text='現有資料夾',
        #     command=self.app.on_folder_list
        # )
        # self.btn1.place(x=800, y=360, anchor='nw')
        # self.btn2 = ttk.Button(
        #     self,
        #     text='加入資料夾',
        #     command=self.app.on_add_folder
        # )
        # self.btn2.place(x=950, y=360, anchor='nw')
