import os
import argparse
import tkinter as tk
from tkinter import (
    Label,
    ttk,
    font,
 )

# log
import logging
import sys

from frame import (
    Toolbar,
    Sidebar,
    #Main,
    Statusbar,
    #Datatable,
    Landing,
    ImageViewer,
    #UploadProgress,
)
from main import Main

from database import Database
from source import Source
from server import Server
from config import Config

# colors
# 2d3142 # deep blue
# 4f5d75 # blue
# bfc0c0 # gray
# ffffff
# ef8354


'''MAIN_FRAMES = {
    'landing': Landing,
    'datatable': Datatable,
    #'image-viewer': ImageViewer,
}'''

class Application(tk.Tk):

    def __init__(self, config, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        #print (config)
        #self.iconbitmap('trees.ico')
        self.geometry("1200x760+40+20")
        self.title('Camera Trap Desktop')
        #self.maxsize(1000, 400)

        s = ttk.Style()
        s.theme_use('clam')

        self.config = config

        # logging
        file_handler = logging.FileHandler(
            filename='ct-log.txt',
            encoding='utf-8', mode='a+')
        stdout_handler = logging.StreamHandler(sys.stdout)
        logging.basicConfig(
            handlers=[
                file_handler,
                stdout_handler],
            format="%(asctime)s|%(levelname)s|%(filename)s:%(lineno)d|%(funcName)s => %(message)s",
            datefmt="%Y-%m-%d:%H:%M:%S",
            level=logging.DEBUG)

        # %(name)s:%(levelname)s:%(message)s | p%(process)s {%(pathname)s:%(lineno)d} %(filename)s %(module)s %(funcName)s 
        self.logger = logging.getLogger('ct-tk')

        self.db = Database(config.get('SQLite', 'dbfile'))
        self.db.init()

        # helpers
        self.source = Source(self)
        self.server = Server(dict(config['Server']))


        #print(list(tk.font.families()))
        #Yu Gothic
        #helvetica
        #Microsoft JhengHei UI
        self.nice_font = {
            'h1': tk.font.Font(family='Yu Gotic', size=16, weight="bold"),
            'h2': tk.font.Font(family='Yu Gotic', size=14),
            'h3': tk.font.Font(family='Yu Gotic', size=12),
            'h4': tk.font.Font(family='Yu Gotic', size=10),
        }

        self.grid_rowconfigure(2, weight=1)
        self.grid_columnconfigure(1, weight=1)

        self.toolbar = Toolbar(
            self,
            background='#ef8354'
        )
        self.main = Main(
            self,
            background='#ffffff',
        )
        self.landing = Landing(self)
        self.image_viewer = ImageViewer(self)

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

        #self.toolbar.grid(row=0, column=0, columnspan=2, sticky='nsew')
        self.sidebar.grid(row=2, column=0, sticky='nsew')
        self.main.grid(row=2, column=1, sticky='nsew')
        #self.landing.grid(row=2, column=1, sticky='nsew')
        self.statusbar.grid(row=3, column=0, columnspan=2)

    def begin_from_source(self):
        if self.landing.winfo_viewable():
            self.landing.grid_remove()

        if self.image_viewer.winfo_viewable():
            self.image_viewer.grid_remove()

    def show_landing(self):
        self.landing.grid()


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
