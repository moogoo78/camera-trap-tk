import tkinter as tk
from tkinter import (
    Label,
    ttk,
    font,
 )

from frame import (
    Toolbar,
    Sidebar,
    Main,
    Statusbar,
    Datatable,
    Landing,
)

from db import Database
from source import Source
from server import Server

DB_FILE = 'ct.db'

MAIN_FRAMES = {
    'landing': Landing,
    'datatable': Datatable,
}

class Application(tk.Tk):

    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)

        self.geometry("1200x760+40+20")
        self.title('Camera Trap Desktop')
        #self.maxsize(1000, 400)
        self.db = Database(DB_FILE)
        self.db.init()

        # helpers
        self.source = Source(self)
        self.server = Server()


        #self.state = {}

        self.grid_rowconfigure(2, weight=1)
        self.grid_columnconfigure(1, weight=1)

        #self.title_font = font.Font(family='Helvetica', size=18, weight="bold", slant="italic")
        self.toolbar = Toolbar(self)
        self.sidebar = Sidebar(
            self,
            background='bisque',
            width=300)
        self.main = Main(
            self,
            frames=MAIN_FRAMES,
            background='white',
            width=980,
            bd=1,
            relief='sunken')
        self.statusbar = Statusbar(
            self,
            background='gray')

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

