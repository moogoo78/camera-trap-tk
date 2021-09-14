import tkinter as tk
from tkinter import (
    ttk,
)

class Landing(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.app = parent.app

        self.title = ttk.Label(
            self,
            text='Camera Trap Images',
            font=self.app.nice_font['h2'])
        self.title.grid(row=0, column=0, sticky='w', padx=10, pady=10)

        #self.render_progress_bar(length=300, folder_name='oeue')

    def show(self, is_show=True):
        #and self.winfo_viewable():
        if is_show == False:
            self.grid_remove()
        else:
            self.grid(row=0, column=0, sticky='nsew')

    def render_progress_bar(self, length=100, title='', sub_title1='', sub_title2=''):

        self.pg_box = tk.Frame(self, width=length, background='#DDDDDD')
        self.pg_box.grid(row=1, column=0, padx=10, pady=10)
        self.pg_title = ttk.Label(self.pg_box, text=title) # 'Loading images. Please wait ...'
        self.pg_title.grid(row=0, column=0, sticky='nsew', padx=10, pady=10)
        self.progress_bar = ttk.Progressbar(self.pg_box, orient=tk.HORIZONTAL, length=length, mode='determinate', value=0)
        self.progress_bar.grid(row=1, column=0, sticky='nsew', padx=10, pady=0)

        self.folder_label = ttk.Label(self.pg_box, text=sub_title1)
        self.folder_label.grid(row=2, column=0, sticky='nw', padx=10, pady=(10, 0))
        self.thumb_label = ttk.Label(self.pg_box, text=sub_title2)
        self.thumb_label.grid(row=3, column=0, sticky='nw', padx=10, pady=(0, 6))

        return self.pg_box
