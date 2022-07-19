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

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

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
            950,
            250,
            text='臺灣自動相機上傳系統',
            fill='#FFFFFF',
            font=self.app.get_font('display-1')
        )
        canvas.create_text(
            950,
            300,
            text='Camera Trap System',
            fill='#FFFFFF',
            font=self.app.get_font('display-1')
        )

        self.btn1 = ttk.Button(
            self,
            text='現有資料夾',
            command=self.app.on_folder_list
        )
        self.btn1.place(x=800, y=360, anchor='nw')
        self.btn2 = ttk.Button(
            self,
            text='加入資料夾',
            command=self.app.on_add_folder
        )
        self.btn2.place(x=950, y=360, anchor='nw')
