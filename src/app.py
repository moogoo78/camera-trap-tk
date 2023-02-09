import os
import argparse
import tkinter as tk
from tkinter import (
    Label,
    ttk,
    font,
 )
#from memory_profiler import profile

# log
import logging
import sys
import socket

from version import __version__
from frame import (
    #Toolbar,
    AppBar,
    FolderList,
    #Statusbar,
    #ImageViewer,
    UploadProgress,
    Panel,
    Main,
    Landing,
    Footer,
    HelpPage,
)


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
        self.app_width = 1200
        self.app_height = int(config.get('Layout', 'app_height'))
        self.app_width_resize_to = 0
        self.app_height_resize_to = 0
        self.app_primary_color = '#2A7F60'
        self.app_secondary_color = '#8AC731'
        self.app_comp_color = '#FF8C23'  # Complementary color
        self.app_font = 'Microsoft JhengHei UI' #'Yu Gothic'  #'Arial'

        self.geometry(f'{self.app_width}x{self.app_height}+40+20')
        self.title(f'Camera Trap Desktop - v{self.version}')
        self.maxsize(1200, 2000)

        self.protocol('WM_DELETE_WINDOW', self.quit)
        self.bind('<Configure>', self.resize)

        style = ttk.Style()
        style.theme_use('clam') # clam, classic

        # == logging ===
        log_level = logging.INFO
        if ll := config.get('Mode', 'log_level'):
            ll = ll.upper()
            log_level = getattr(logging, ll)

        file_handler = logging.FileHandler(
            filename='ct-log.txt',
            encoding='utf-8', mode='a+')
        stdout_handler = logging.StreamHandler(sys.stdout)
        #text_handler = TextHandler(text)
        logging.basicConfig(
            handlers=[
                file_handler,
                stdout_handler,
            ],
            format="%(asctime)s|%(levelname)s|%(filename)s:%(lineno)d|%(funcName)s 👉 %(message)s",
            datefmt="%Y-%m-%d:%H:%M:%S",
            level=log_level)

        # %(name)s:%(levelname)s:%(message)s | p%(process)s {%(pathname)s:%(lineno)d} %(filename)s %(module)s %(funcName)s
        self.logger = logging.getLogger('ct-tk')


        # == helpers ==
        self.db = Database(config.get('SQLite', 'dbfile'))
        self.db.init()

        self.config = config
        self.source = Source(self)
        self.server = Server(dict(config['Server']))

        self.cached_project_map = self.server.get_project_map()
        # print(self.cached_project_map)
        # don't show alert, 2022-11-09
        #if err := self.cached_project_map.get('error'):
        #    tk.messagebox.showerror('server error', f'{err}\n (無法上傳檔案，但是其他功能可以運作)')


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

        self.layout()

    def layout(self):
        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=1)
        self.grid_rowconfigure(2, weight=0)
        self.grid_columnconfigure(0, weight=1)

        self.appbar = AppBar(
            self,
            background=self.app_primary_color,
            width=self.app_width,
            height='50')
        self.appbar.grid(row=0, column=0, sticky='ew')

        self.contents = {}
        self.contents['landing'] = Landing(self)
        self.contents['landing'].grid(row=1, column=0, sticky='nw')

        self.footer = Footer(
            self,
            background=self.app_primary_color,
            width=self.app_width,
            height='25'
        )
        self.footer.grid(row=2, column=0, sticky='ew')

        self.contents['folder_list'] = FolderList(
            self,
            background='#4f5d75',
            width=300)

        self.contents['main'] = Main(
            self,
            background='#F2F2F2')

        self.contents['upload_progress'] = UploadProgress(self)
        self.contents['help_page'] = HelpPage(self)

        self.panel = Panel(
            self,
            width=240)
        # self.panel.place(x=0, y=50, anchor='nw')


        #self.toolbar = Toolbar(
        #    self,
        #    background='#ef8354'
        #)

        #self.statusbar = Statusbar(
        #    self,
        #    background='#bfc0c0')

        # self.on_upload_progress() # for quick test

    def show_content(self, name):
        self.clear_contents(exclude=name)
        if not self.contents[name].winfo_viewable():
            self.contents[name].grid(row=1, column=0, sticky='nw')

        self.update_idletasks()

    def clear_contents(self, exclude=''):
        for k, v in self.contents.items():
            v.update_idletasks()
            if v.winfo_viewable():
                if exclude == '' or exclude != k:
                    # print('clear ', k)
                    self.contents[k].grid_remove()

    def toggle_panel(self):
        # if this method in panel, then panel should declare before AppBar, and may by cover by other widget
        if self.panel.is_viewable is True:
            self.panel.hide()
        else:
            self.panel.show()

    def on_folder_list(self, event=None):
        logging.debug(f'event: {event}')

        self.contents['folder_list'].refresh_source_list()
        self.show_content('folder_list')

        if self.panel.is_viewable is True:
            self.panel.hide()

    def on_folder_detail(self, event, tag):
        logging.debug(f'click on tag: {tag}')
        if event:
            logging.debug(f'evoked by {event}')
        source_id = tag.replace('source_', '')

        self.contents['main'].change_source(int(source_id))
        self.show_content('main')

    def on_add_folder(self, event=None):
        logging.debug(f'{event}')
        self.contents['folder_list'].add_folder()

        if self.panel.is_viewable is True:
            self.panel.hide()

    def on_upload_progress(self, event=None):
        logging.debug(f'event: {event}')
        self.show_content('upload_progress')
        #if not self.contents['upload_progress'].check_running():
        self.contents['upload_progress'].refresh()

        if self.panel.is_viewable is True:
            self.panel.hide()

    def on_help_page(self, event=None):
        logging.debug(f'{event}')
        self.show_content('help_page')

        if self.panel.is_viewable is True:
            self.panel.hide()

    def get_font(self, size_code='default'):
        SIZE_MAP = {
            'display-1': 32,
            'display-2': 24,
            'display-3': 18,
            'display-4': 12,
            'default': 10,
        }
        if size_code in SIZE_MAP:
            size = SIZE_MAP[size_code] if isinstance(size_code, str) else size_code
            return (self.app_font, size)
        elif int(size_code) > 0:
            return (self.app_font, int(size_code))
        else:
            return (self.app_font, 10)

    def toggle_image_viewer_DEPRICATED(self, is_image_viewer=True):
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
        self.contents['upload_progress'].terminate_upload_task()

        # don't save
        # if h:= self.app_height_resize_to:
        #     try:
        #         if int(h) >= 150:
        #             self.config.set('Layout', 'app_height', str(h))
        #             logging.info(f'save config - Layout.app_height: {h}')
        #             self.config.overwrite()
        #     except:
        #         print('write error')
        #         pass

        self.destroy()

    def resize(self, event):
        self.app_height_resize_to = event.height


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
