import tkinter as tk
from tkinter import (
    Label,
    ttk,
    font
)


from page import (
    SourceListPage,
    ImageListPage
)
from db import Database

DB_FILE = 'ct.db'

class Application(tk.Tk):

    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)

        self.geometry("800x600+400+50")
        self.title('Camera Trap Desktop')
        #self.maxsize(1000, 400)

        self.title_font = font.Font(family='Helvetica', size=18, weight="bold", slant="italic")

        container = tk.Frame(self)
        #container.pack(side='top', fill='both', expand=True)
        container.grid(row=0, column=0)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.db = Database(DB_FILE)
        self.db.init()

        self.state = {}

        self.frames = {}
        for F in (SourceListPage, ImageListPage):
            frame_name = F.__name__
            frame = F(parent=container, controller=self)
            self.frames[frame_name] = frame

            frame.grid(row=0, column=0, sticky='nsew')
        self.show_frame('SourceListPage')


    def show_frame(self, page_name, **kwargs):
        frame = self.frames[page_name]

        if page_name == 'ImageListPage':
            self.get_source(kwargs['source_id'])
            frame.refresh();

        frame.tkraise()

    def get_source(self, source_id):
        source = self.db.fetch_sql('SELECT * FROM source WHERE source_id={}'.format(source_id))
        images = self.db.fetch_sql_all('SELECT * FROM image WHERE source_id={}'.format(source_id))
        #print (images, 'xxx')
        self.state = {
            'image_list': images,
            'source': source,
            'current_row_index': 0,
        }


if __name__ == '__main__':
    app = Application()
    app.mainloop()

