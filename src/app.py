import os
import argparse
import tkinter as tk
from tkinter import (
    Label,
    ttk,
    font,
 )

from frame import (
    Toolbar,
    Sidebar,
    #Main,
    Statusbar,
    Datatable,
    Landing,
    ImageViewer,
)
from main import Main

from database import Database
from source import Source
from server import Server
from config import Config

# colors
# 2d3142
# 4f5d75
# bfc0c0
# ffffff
# ef8354

DB_FILE = 'ct.db'

'''MAIN_FRAMES = {
    'landing': Landing,
    'datatable': Datatable,
    #'image-viewer': ImageViewer,
}'''

class Application(tk.Tk):

    def __init__(self, config, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        #print (config)
        self.geometry("1200x760+40+20")
        self.title('Camera Trap Desktop')
        #self.maxsize(1000, 400)

        self.config = config

        self.db = Database(config.get('SQLite', 'dbfile'))
        self.db.init()

        # helpers
        self.source = Source(self)
        self.server = Server(dict(config['Server']))


        #self.state = {}

        self.grid_rowconfigure(2, weight=1)
        self.grid_columnconfigure(1, weight=1)

        #self.title_font = font.Font(family='Helvetica', size=18, weight="bold", slant="italic")
        self.toolbar = Toolbar(
            self,
            background='#2d3142'
        )
        self.main = Main(
            self,
            background='#ffffff',
        )
        self.sidebar = Sidebar(
            self,
            background='#4f5d75',
            width=300)
        #self.main = Main(
        #    self,
        #    frames=MAIN_FRAMES,
        #    background='#def',
        #    bd=1,
        #    relief='sunken')
        self.statusbar = Statusbar(
            self,
            background='#bfc0c0')

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


parser = argparse.ArgumentParser(description='camera-trap-desktop')
parser.add_argument(
    '-i', '--ini',
    dest='ini_file',
    help='ini file path')
args = parser.parse_args()

if __name__ == '__main__':
    conf = Config(args.ini_file) if args.ini_file else Config()
    app = Application(conf)

    app.mainloop()
