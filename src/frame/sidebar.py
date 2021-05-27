import tkinter as tk
from tkinter import (
    ttk,
)

from tkinter import filedialog as fd


class Sidebar(tk.Frame):

    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent

        self.source_list = []

        add_button = ttk.Button(
            self,
            text='新增目錄',
            command=self.add_folder)
        add_button.grid(pady=4)

        separator = ttk.Separator(self, orient='horizontal')
        separator.grid(sticky='ew', pady=2)

        self.refresh_source_list()

    def refresh_source_list(self):
        db = self.parent.db

        # reset source_list
        if a := self.source_list:
            for i in a:
                i.destroy()
            self.source_list = []

        # get all source from db
        res = db.fetch_sql_all('SELECT * FROM source')
        for i in res:
            source_button = ttk.Button(
                self,
                text=i[3],
                command=lambda x=i[0]: self.parent.main.show_frame('datatable', source_id=x))
            source_button.grid(pady=2)
            self.source_list.append(source_button)


    def add_folder(self):
        directory = fd.askdirectory()

        if not directory:
            return False

        src = self.parent.source
        progress_bar = self.parent.statusbar.progress_bar

        folder_path = src.get_folder_path(directory)
        if not folder_path:
            tk.messagebox.showinfo('info', '已經加過此目錄')
            return False

        image_list = src.get_image_list(folder_path)

        progress_bar['maximum'] = len(image_list)
        self.update_idletasks()

        for i, v in enumerate(src.gen_import_image(image_list, folder_path)):
            progress_bar['value'] = i+1
            self.update_idletasks()

        progress_bar['value'] = 0
        self.update_idletasks()

        self.refresh_source_list()
