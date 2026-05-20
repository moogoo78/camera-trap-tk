import os
import argparse
import tkinter as tk
from tkinter import (
    ttk,
    font,
)
#from memory_profiler import profile

# log
import logging
from logging.handlers import RotatingFileHandler
import sys
import socket

from PIL import ImageTk
import webbrowser
from uuid import getnode

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
    # HelpPage,
)
from toplevel import (
    HelpPage,
    ImportData,
    LoginForm,
    ConfigureKeyboardShortcut,
    ConfigureFont,
)

from database import Database
from source import Source
from server import Server
from config import Config

class Application(tk.Tk):

    def __init__(self, config, is_debug, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)

        self.version = __version__
        if hostname := socket.gethostname():
            self.user_hostname = hostname
        else:
            self.user_hostname = '--'

        app_logo = ImageTk.PhotoImage(file='./assets/logo-leaf.png')
        self.iconphoto(False, app_logo)
        #self.iconbitmap('trees.ico')

        self.screen_ppi = self.winfo_fpixels('1i')
        self.screen_width_px = self.winfo_screenwidth()
        self.screen_height_px = self.winfo_screenheight()

        # Scale design sizes (authored at 96 ppi) to the actual screen ppi,
        # then clamp so the window fits on-screen with a small margin.
        self.ui_scale = self.screen_ppi / 96.0
        base_width = 1200
        base_height = int(config.get('Layout', 'app_height'))
        self.app_width = min(int(base_width * self.ui_scale), self.screen_width_px - 80)
        self.app_height = min(int(base_height * self.ui_scale), self.screen_height_px - 120)
        self.app_width_resize_to = 0
        self.app_height_resize_to = 0
        self.app_primary_color = '#2A7F60'
        self.app_secondary_color = '#8AC731'
        self.app_comp_color = '#FF8C23'  # Complementary color
        self.app_font = 'Microsoft JhengHei UI' #'Yu Gothic'  #'Arial'
        self.secrets = {}
        self.contents = {}
        self.is_debug = is_debug

        self.geometry(f'{self.app_width}x{self.app_height}+40+20')
        self.title(f'Camera Trap Desktop - v{self.version}')
        self.maxsize(self.screen_width_px, self.screen_height_px)

        self.protocol('WM_DELETE_WINDOW', self.quit)
        # self.bind('<Configure>', self.resize)

        self.is_help_open = False
        self.toplevels = {
            'import_data': False,
            'login_form': False,
        }

        self.user_info = {
            'projects': [],
        }

        style = ttk.Style()
        style.theme_use('clam') # clam, classic

        # == logging ===
        log_level = logging.INFO
        if ll := config.get('Mode', 'log_level'):
            ll = ll.upper()
            log_level = getattr(logging, ll)

        file_handler = logging.handlers.RotatingFileHandler(
            filename='ct-app.log',
            encoding='utf-8',
            mode='a',
            backupCount=10,
            maxBytes=10000000)
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

        # hide image debug logger
        logging.getLogger('PIL.PngImagePlugin').propagate = False
        logging.getLogger('PIL.TiffImagePlugin').propagate = False

        #logging.info(f'starting camera-trap app, version: {self.version}')
        logging.info(f'screen: {self.screen_width_px}x{self.screen_height_px} @ {self.screen_ppi:.1f} ppi, ui_scale={self.ui_scale:.2f}, window={self.app_width}x{self.app_height}')

        # == helpers ==
        self.db = Database(config.get('SQLite', 'dbfile'))
        self.db.init()
        self.config = config

        self.source = Source(self)
        #self.server = Server(dict(config['Server']))
        self.server = Server(self)

        self.menubar = tk.Menu(self)
        userbar = tk.Menu(self.menubar, tearoff=False)
        toolbar = tk.Menu(self.menubar, tearoff=False)
        settingbar = tk.Menu(self.menubar, tearoff=False)
        toolbar.add_command(label='匯入', command=self.on_import_data)
        settingbar.add_command(label='設定快捷鍵', command=lambda: ConfigureKeyboardShortcut(self))
        settingbar.add_command(label='設定字體大小', command=lambda: ConfigureFont(self))
        userbar.add_command(label='登入ORCID', command=self.on_login_form)
        userbar.add_command(label='登出', command=self.on_logout)
        self.menubar.add_cascade(label='帳號', menu=userbar)
        self.menubar.add_cascade(label='工具', menu=toolbar)
        self.menubar.add_cascade(label='設定', menu=settingbar)
        self.configure(menu=self.menubar)

        # process user_info
        if user_id := self.db.get_state('user_id'):
            self.on_login({'user_id': user_id})

        # check latest version
        resp = self.server.check_update()
        if err_msg := resp.get('error', ''):
            self.wait_visibility()
            tk.messagebox.showerror('network error', f'{err_msg}\n (無法匯入及上傳檔案，但是其他功能可以運作)')

            # no network still show info
            logging.info('App version: {} ({})'.format(self.version, 'outdated'))
            tk.messagebox.showinfo('注意', "請至官網下載最新版本軟體")
        else:
            is_outdated_value = self.config.get('State', 'is_outdated', fallback='t')
            if resp['json']['is_latest'] is True:
                logging.info('App version: {} ({})'.format(self.version, 'latest'))
                if str(is_outdated_value).lower() not in ['false', '0', '']:
                    self.config.set('State', 'is_outdated', '0')
                    self.config.overwrite()
                else:
                    # still latest, do nothing
                    pass
            else:
                logging.info('App version: {} ({})'.format(self.version, 'outdated !!'))

                # via: https://stackoverflow.com/a/65734843/644070
                self.wait_visibility()
                tk.messagebox.showinfo('注意', f"請至官網下載最新版本軟體 ({resp['json']['version']['latest']})")

                if str(is_outdated_value).lower() in ['false', '0', '']:
                    self.config.set('State', 'is_outdated', '1')
                    self.config.overwrite()
                else:
                    # still outdated, do nothing
                    pass

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

        # append secrets
        try:
            import credentials

            aws_key = credentials.get_aws_key()
            self.secrets.update({
                'aws_access_key_id': aws_key['access_key_id'],
                'aws_secret_access_key': aws_key['secret_access_key']
            })
            logging.debug('credentials loaded: aws s3')
        except ModuleNotFoundError:
                logging.debug('credentials not found')


        self.app_context_size = self.db.get_state('context_size') or 'S' # SML
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
            height=int(50 * self.ui_scale))
        self.appbar.grid(row=0, column=0, sticky='ew')

        self.contents['landing'] = Landing(self)
        self.contents['landing'].grid(row=1, column=0, sticky='nsew')

        self.footer = Footer(
            self,
            background=self.app_primary_color,
            width=self.app_width,
            height=int(25 * self.ui_scale)
        )
        self.footer.grid(row=2, column=0, sticky='ew')

        self.contents['folder_list'] = FolderList(
            self,
            background='#4f5d75',
            width=int(300 * self.ui_scale))

        self.contents['main'] = Main(
            self,
            background='#F2F2F2')

        self.contents['upload_progress'] = UploadProgress(self)
        # self.contents['help_page'] = HelpPage(self) # for performance, changed to TopLevel

        self.panel = Panel(
            self,
            width=int(240 * self.ui_scale))
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
            self.contents[name].grid(row=1, column=0, sticky='nsew')

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

        # check while import, do not enter editing page
        _, source_id = tag.split('_')
        d = self.contents['folder_list'].import_deque
        if len(d) > 0 and d[0] == int(source_id):
            return False

        if event:
            logging.debug(f'evoked by {event}')
        source_id = tag.replace('source_', '')

        # TODO detect can enter main page or not
        #result = self.db.fetch_sql(f'SELECT status FROM source WHERE source_id={source_id}')
        #print(result, '--------------')

        self.contents['main'].change_source(int(source_id))
        self.show_content('main')

    def on_add_folder(self, event=None):
        logging.debug(f'{event}')

        if len(self.contents['folder_list'].import_deque) > 0:
            tk.messagebox.showinfo('info', '其他資料夾正在匯入中')
        else:
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
        # self.show_content('help_page')

        # if self.panel.is_viewable is True:
        #     self.panel.hide()

        if self.is_help_open is False:
           self.is_help_open = True
           HelpPage(self)

    def on_import_data(self):
        if not self.toplevels['import_data']:
            self.toplevels['import_data'] = ImportData(self)


    def on_login_form(self):
        if not self.toplevels['login_form']:
            if self.db.get_state('user_id'):
                tk.messagebox.showinfo('info', '已登入')
            else:
                self.toplevels['login_form'] = LoginForm(self)


    def on_login(self, payload,):
        logging.info(f'login: {payload}')
        user_id = payload.get('user_id')
        email = payload.get('email')
        name = payload.get('name')

        if user_id:
            resp = self.server.get_user_info(user_id)
            if data := resp.get('json'):
                self.user_info = data['results']
                if 'main' in self.contents:
                    self.contents['main'].update_project_options(self.user_info['projects'])
                logging.info('get user_info')
                name = data['results']['user'].get('name', '')
                email = data['results']['user'].get('email', '')

            # update db
            self.db.set_state('user_id', user_id)

            current_device_id = getnode()
            if exist_device_id := self.db.get_state('device_id'):
                if str(exist_device_id) != str(current_device_id):
                    #tk.messagebox.showerror('err', '更換裝置，帳號無法沿用，請先登出')
                    if not self.is_debug:
                        if tk.messagebox.askokcancel('注意', '更換裝置，帳號無法沿用，請先登出'):
                            self.on_logout()
                        else:
                            #self.quit()
                            # force leave app
                            self.destroy()
                            exit()

            else:
                self.db.set_state('device_id', current_device_id)

            if name:
                self.db.set_state('user_name', name)
            if email:
                self.db.set_state('user_email', email)

            self.menubar.entryconfigure(1, label=f"user: {name} ({email})")

    def on_logout(self):
        if uid := self.db.get_state('user_id'):
            tk.messagebox.showinfo('info', '已登出，請再重新啟動上傳程式')

        self.user_info = {'projects': []}
        if 'main' in self.contents:
            self.contents['main'].update_project_options([])
        self.db.set_state('user_id', '')
        self.db.set_state('user_name', '')
        self.db.set_state('user_email', '')
        self.db.set_state('device_id', '')
        self.menubar.entryconfigure(1, label='login')
        self.quit()

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

    def quit(self):
        is_force_quit = self.config.get('Mode', 'force_quit', fallback='0')
        if str(is_force_quit).lower() not in ['false', '0', '']:
            self.destroy()
            # TODO if other thread is running, may wait for the thread (importing, uploading ?)
            logging.info('force quit app')
            return

        if 'folder_list' in self.contents and len(self.contents['folder_list'].import_deque) > 0:
            tk.messagebox.showwarning('注意', f'尚有資料夾正在匯入中，請等候匯入完成再離開')
            return

        if 'upload_progress' in self.contents:
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
parser.add_argument(
    '--debug',
    action='store_true',
    help='debug mode')
args = parser.parse_args()

def main():
    conf = Config(args.ini_file) if args.ini_file else Config()
    app = Application(conf, args.debug)
    #app.async_loop = async_loop
    app.mainloop()


if __name__ == '__main__':
    #async_loop = asyncio.get_event_loop()
    #main(async_loop)
    main()
