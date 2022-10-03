import tkinter as tk
from tkinter import (
    ttk,
)

class HelpPage(tk.Frame):

    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.app = parent

        self.layout()


    def layout(self):
        self.grid_rowconfigure(0, weight=0)
        self.grid_columnconfigure(0, weight=0)

        self.canvas = tk.Canvas(
            self,
            width=self.app.app_width,
            height=self.app.app_height-50-25,
            bg='#CFCFCF',
            bd=0,
            highlightthickness=0,
            relief='ridge',
        )
        self.canvas.grid(row=0, column=0, sticky='ewns')

        self.canvas.create_text(
            250,
            80,
            text='~ 教學內容 ~',
            font=('Arial', 40),
            fill=self.app.app_primary_color,
        )

