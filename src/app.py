import tkinter as tk
from tkinter import (
    Label,
    ttk,
    font
)

from frame import (
    Toolbar,
    Sidebar,
    Main,
    Statusbar,
    ImageList,
    Landing,
)

from page import (
    SourceListPage,
    ImageListPage,
    ImageViewer,
)
from db import Database
from source import Source

DB_FILE = 'ct.db'

MAIN_FRAMES = {
    'landing': Landing,
    'image-list': ImageList,
}

class Application(tk.Tk):

    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)

        self.geometry("800x600+400+50")
        self.title('Camera Trap Desktop')
        #self.maxsize(1000, 400)

        self.db = Database(DB_FILE)
        self.db.init()

        # helpers
        self.source = Source(self.db)

        #self.state = {}

        '''
        container = tk.Frame(self)
        #container.pack(side='top', fill='both', expand=True)
        container.grid(row=0, column=0)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.db = Database(DB_FILE)
        self.db.init()

        self.state = {}

        self.frames = {}
        for F in ALL_FRAMES:
            frame_name = F.__name__
            frame = F(parent=container, controller=self)
            self.frames[frame_name] = frame

            frame.grid(row=0, column=0, sticky='nsew')
        self.show_frame('SourceListPage')'''

        self.grid_rowconfigure(2, weight=1)
        self.grid_columnconfigure(1, weight=1)

        #self.title_font = font.Font(family='Helvetica', size=18, weight="bold", slant="italic")
        self.toolbar = Toolbar(self)
        self.sidebar = Sidebar(self, background='bisque', width=150, height=200)
        self.main = Main(self, frames=MAIN_FRAMES, background='white', width=300, height=200, bd=1, relief='sunken')
        self.statusbar = Statusbar(self, background='gray')

        #self.message = tk.Label(self, text="Hello, world!")
        #self.message.grid(row=1, column=0, columnspan=2)

        self.toolbar.grid(row=0, column=0, columnspan=2)
        self.sidebar.grid(row=2, column=0, sticky='nsew')
        self.main.grid(row=2, column=1, sticky='nsew')
        self.statusbar.grid(row=3, column=0, columnspan=2)

    def toggle_sidebar(self):
        if self.sidebar.winfo_viewable():
            self.sidebar.grid_remove()
        else:
            self.sidebar.grid()


if __name__ == '__main__':
    app = Application()
    app.mainloop()

