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
import socket

from version import __version__
from frame import (
    #Toolbar,
    FolderList,
    #Statusbar,
    #ImageViewer,
    UploadProgress,
    Panel,
    Main,
)
import asyncio

from database import Database
from source import Source
from server import Server
from config import Config


class Application(tk.Tk):

    def __init__(self, config, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)

        self.version = __version__
        if hostname := socket.gethostname():
            self.user_hostname = hostname
        else:
            self.user_hostname = '--'
        #print (config)
        #self.iconbitmap('trees.ico')
        self.WIDTH = 1200
        self.HEIGHT = 760
        self.geometry(f'{self.WIDTH}x{self.HEIGHT}+40+20')
        self.title(f'Camera Trap Desktop - v{self.version}')
        #self.maxsize(1000, 400)

        self.protocol('WM_DELETE_WINDOW', self.quit)
        s = ttk.Style()
        s.theme_use('clam')

        self.config = config

        # logging
        log_level = logging.INFO
        if ll := config.get('Mode', 'log_level'):
            ll = ll.upper()
            log_level = getattr(logging, ll)

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
            level=log_level)

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

        self.grid_rowconfigure(0, weight=0)
        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)

        self.panel = Panel(self, background='#DEDEDE', width=32) # background='#ef8354'
        self.panel.grid(row=0, column=0, sticky='ns')

        self.frames = {}
        #self.toolbar = Toolbar(
        #    self,
        #    background='#ef8354'
        #)

        #self.statusbar = Statusbar(
        #    self,
        #    background='#bfc0c0')

        #self.message = tk.Label(self, text="Hello, world!")
        #self.message.grid(row=1, column=0, columnspan=2)

        #self.toolbar.grid(row=0, column=0, columnspan=2, sticky='nsew')
        #self.sidebar.grid(row=0, column=1, sticky='nsew')

        #self.landing.grid(row=2, column=1, sticky='nsew')
        #self.statusbar.grid(row=2, column=0, columnspan=2)
        self.panedwindow = ttk.PanedWindow(self, orient=tk.HORIZONTAL, height=self.HEIGHT)
        self.panedwindow.app = self

        #self.panedwindow.pack(fill=tk.BOTH, expand=True)
        self.panedwindow.grid(row=0, column=1, sticky='nsew')
        self.panedwindow.grid_rowconfigure(0, weight=1)
        self.panedwindow.grid_columnconfigure(0, weight=1)

        self.frames['folder_list'] = FolderList(
            self.panedwindow,
            background='#4f5d75',
            width=300)

        self.frames['upload_progress'] = UploadProgress(
            self.panedwindow,
            width=100)

        self.frames['main'] = Main(
            self.panedwindow,
            #fbackground='#ffffff',
            background='#2d3142'
        )

        # init layout
        self.panedwindow.add(self.frames['folder_list'])
        #self.panedwindow.add(self.upload_progress)
        self.panedwindow.add(self.frames['main'])


    # def begin_from_source(self):
    #     if self.landing.winfo_viewable():
    #         self.landing.grid_remove()

    #     if self.image_viewer.winfo_viewable():
    #         self.image_viewer.grid_remove()

    def clear_panedwindow(self):
        if self.frames['folder_list'].winfo_viewable():
            self.panedwindow.remove(self.frames['folder_list'])
        if self.frames['upload_progress'].winfo_viewable():
            self.panedwindow.remove(self.frames['upload_progress'])
        if self.frames['main'].winfo_viewable():
            self.panedwindow.remove(self.frames['main'])

    def toggle_folder_list(self):
        if self.frames['folder_list'].winfo_viewable():
            self.clear_panedwindow()
            self.panedwindow.add(self.frames['main'])
        else:
            self.clear_panedwindow()
            self.panedwindow.add(self.frames['folder_list'])
            self.panedwindow.add(self.frames['main'])

    def toggle_upload_progress(self):
        if self.frames['upload_progress'].winfo_viewable():
            self.clear_panedwindow()
            self.panedwindow.add(self.frames['main'])
        else:
            self.clear_panedwindow()
            self.panedwindow.add(self.frames['upload_progress'])
            self.panedwindow.add(self.frames['main'])

    def toggle_image_viewer(self, is_image_viewer=True):
        # 先不 remove main , 蓋掉就好了
        #if not self.frames['main'].winfo_viewable():
        #self.frames['main'].grid(row=0, column=0, sticky='nsew')
        if is_image_viewer:
            #self.frames['main'].data_grid.main_table.toggle_arrow_key_binding(False)
            self.frames['image_viewer'].toggle_arrow_key_binding(True)
            if not self.frames['image_viewer'].winfo_viewable():
                self.frames['image_viewer'].grid(row=0, column=0, sticky='nsew')
                self.frames['image_viewer'].init_data()
                self.frames['image_viewer'].refresh()
        else:
            self.frames['main'].data_grid.main_table.toggle_arrow_key_binding(True)
            #self.frames['image_viewer'].toggle_arrow_key_binding(False)
            if self.frames['image_viewer'].winfo_viewable():
                self.frames['image_viewer'].grid_remove()

    def quit(self):
        self.frames['upload_progress'].handle_stop()
        self.destroy()

parser = argparse.ArgumentParser(description='camera-trap-desktop')
parser.add_argument(
    '-i', '--ini',
    dest='ini_file',
    help='ini file path')
args = parser.parse_args()

def main():
    conf = Config(args.ini_file) if args.ini_file else Config()
    app = Application(conf)
    #app.async_loop = async_loop
    app.mainloop()


if __name__ == '__main__':
    #async_loop = asyncio.get_event_loop()
    #main(async_loop)
    main()
