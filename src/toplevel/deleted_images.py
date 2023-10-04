import tkinter as tk
from tkinter import (
    ttk,
)

class DeletedImages(tk.Toplevel):

    def __init__(self, parent, *args, **kwargs):
        #tk.Frame.__init__(self, parent, *args, **kwargs)
        super().__init__(parent, bg='#eeeeee')
        self.app = parent.app

        self.protocol('WM_DELETE_WINDOW', self.quit)
        self.geometry('400x300')
        self.title('網頁已刪除檔案列表')

        self.layout()

        self.render_item(kwargs.get('images'))

    def layout(self):
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # container
        container = ttk.Frame(self, padding=10)
        container.grid(row=0, column=0, sticky='nwes')
        container.grid_rowconfigure(0, weight=0)
        container.grid_rowconfigure(1, weight=0)
        container.grid_rowconfigure(2, weight=1)
        container.grid_columnconfigure(0, weight=0)

        title = ttk.Label(
            container,
            text='網頁已刪除檔案列表',
            font=self.app.get_font('display-3'),
        )
        verbose = ttk.Label(
            container,
            text='已刪除的檔案將不會更新',
        )

        self.treeview = ttk.Treeview(container, columns=('id', 'filename'), show='headings')
        self.treeview.heading('id', text='local id')
        self.treeview.heading('filename', text='檔名')
        #self.treeview.heading('species', text='物種')
        self.treeview.column('id', width=60,stretch=False)

        title.grid(row=0, column=0, sticky='we', padx=8, pady=(8, 4))
        verbose.grid(row=1, column=0, sticky='we', padx=8, pady=(0, 4))
        self.treeview.grid(row=2, column=0, sticky='nsew')


    def render_item(self, items):
        self.treeview.delete(*self.treeview.get_children())

        for i in items:
            self.treeview.insert('', tk.END, values=i)
