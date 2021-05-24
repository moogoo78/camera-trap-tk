import time
from datetime import datetime
import json
from pathlib import Path, PureWindowsPath

import tkinter as tk
from tkinter import (
    filedialog,
    ttk,
)

from image import ImageManager

LARGEFONT =("Verdana", 30)

IGNORE_FILES = ['Thumbs.db', '']
IMAGE_EXTENSIONS = ['.JPG', '.JPEG', '.PNG']

def _check_image_filename(dirent):
    p = Path(dirent)
    if p.suffix.upper() in IMAGE_EXTENSIONS:
        return True
    return False


class SourceListPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller

        label = ttk.Label(self, text ='Camera Trap Desktop', font = LARGEFONT)
        label.grid(row = 0, column = 0, padx = 10, pady = 10)

        button1 = ttk.Button(self, text='新增來源',
                             command=self.add_source)

        button1.grid(row = 1, column = 0, padx = 10, pady = 10)

        self.progress_bar = ttk.Progressbar(self, orient=tk.HORIZONTAL, length=500, mode='determinate', value=0)
        self.progress_bar.grid()

        self.source_list = []
        self.render()

    def render(self):
        db = self.controller.db
        res = db.fetch_sql_all('SELECT * FROM source')

        for i in self.source_list:
            i.grid_forget()

        for i in res:
            #label = ttk.Label(self, text =i[3])
            #label.grid(row=i[0]+1, column=2, padx = 10, pady = 10)
            #label = tk.Label(self.controller, text=i[3], bg='red')
            button = ttk.Button(
                self,
                text=i[3],
                command=lambda x=i[0]: self.controller.show_frame('ImageListPage', source_id=x))
            button.grid(row=3+i[0], column=0)
            self.source_list.append(button)

    def add_source(self):
        ans = tk.filedialog.askdirectory()
        folder_path = Path(ans)

        db = self.controller.db
        exist = db.fetch_sql("SELECT * FROM source WHERE path='{}'".format(folder_path))
        if exist:
            ret = db.fetch_sql_all('SELECT * FROM source')
            return ret

        image_list = []
        for entry in folder_path.iterdir():
            if not entry.name.startswith('.') and \
               entry.is_file() and \
               _check_image_filename(entry):
                image_list.append(entry)

        self.progress_bar['maximum'] = len(image_list)
        self.update_idletasks()

        # save to source
        db = self.controller.db
        ts_now = int(time.time())
        dir_name = folder_path.stem # final path component
        sql = "INSERT INTO source (source_type, path, name, count, created, status) VALUES('folder', '{}', '{}', {}, {}, '10')".format(folder_path, dir_name, len(image_list), ts_now)
        source_id = db.exec_sql(sql, True)

        for i in image_list:
            data = {
                'path': i.as_posix(),
                'name': i.name,
                'img': ImageManager(i),
            }
            self._insert_image_db(data, ts_now, source_id)
            print (i)
            self.progress_bar['value'] += 1
            self.update_idletasks()

        #ret = db.fetch_sql_all('SELECT * FROM source')

        self.progress_bar['value'] = 0
        self.update_idletasks()
        self.render()


    def _insert_db(self, path, image_list):
        db = self.controller.db

        ts_now = int(time.time())
        dir_name = path.stem # final path component

        sql = "INSERT INTO source (source_type, path, name, count, created, status) VALUES('folder', '{}', '{}', {}, {}, '10')".format(path, dir_name, len(image_list), ts_now)
        rid = db.exec_sql(sql, True)

        timestamp = None
        for i in image_list:
            img_hash = i['img'].make_hash()
            exif  = i['img'].exif
            dtime = exif.get('DateTimeOriginal', '')
            via = 'exif'
            if dtime:
                dt = datetime.strptime(exif.get('DateTime', ''), '%Y:%m:%d %H:%M:%S')
                timestamp = dt.timestamp()
            else:
                stat = i['img'].get_stat()
                timestamp = int(stat.st_mtime)
                via = 'mtime'

            sql = "INSERT INTO image (path, name, timestamp, timestamp_via, status, hash, annotation, changed, exif, source_id) VALUES ('{}','{}', {}, '{}', '{}', '{}','{}', {}, '{}', {})".format(
                i['path'],
                i['name'],
                timestamp,
                via,
                '10',
                img_hash,
                '[]',
                ts_now,
                json.dumps(exif),
                rid)

            db.exec_sql(sql)
        db.commit()

    def _insert_image_db(self, i, ts_now, source_id):
        db = self.controller.db

        timestamp = None

        img_hash = i['img'].make_hash()
        exif  = i['img'].exif
        dtime = exif.get('DateTimeOriginal', '')
        via = 'exif'
        if dtime:
            dt = datetime.strptime(exif.get('DateTime', ''), '%Y:%m:%d %H:%M:%S')
            timestamp = dt.timestamp()
        else:
            stat = i['img'].get_stat()
            timestamp = int(stat.st_mtime)
            via = 'mtime'

        sql = "INSERT INTO image (path, name, timestamp, timestamp_via, status, hash, annotation, changed, exif, source_id) VALUES ('{}','{}', {}, '{}', '{}', '{}','{}', {}, '{}', {})".format(
            i['path'],
            i['name'],
            timestamp,
            via,
            '10',
            img_hash,
            '[]',
            ts_now,
            json.dumps(exif),
            source_id)

        db.exec_sql(sql, True)
        #db.commit()
