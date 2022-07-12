import tkinter as tk
from tkinter import (
    ttk,
)
import queue
import logging
import json
import time
from datetime import datetime
import random
import sys

import threading
import asyncio
#import concurrent.futures
from queue import Queue

from PIL import (
    Image,
    ImageTk
)

from worker import UploadTask
from image import get_thumb
from utils import create_round_polygon

class Uploader(threading.Thread):

    def __init__(self, caller):
        # non-daemon thread
        threading.Thread.__init__(self)

        # upload source_list, image left
        self.upload_queue = Queue()

        # sql for image updated by event_generate
        self.image_sql_queue = Queue()

        # sql for source updated by event_generate
        self.source_sql_queue = Queue()

        self.caller = caller

        self.is_pause = False
        self.is_done = False

    def run(self):
        fin = False

        while not self.is_pause and not self.is_done:
            for _ in range(self.upload_queue.qsize()):
                counter = 0
                data = self.upload_queue.get()
                source_id = data[0][0]
                left = len(data[1])
                logging.debug(f'🧵 start upload source: {source_id}, num_images: {left}')
                for image in data[1]:
                    counter += 1
                    time.sleep(1)
                    sql = f"UPDATE image SET status='33' WHERE image_id={image[0]}"
                    self.image_sql_queue.put(sql)
                    self.caller.after_image_upload(source_id, image[0], counter)
                    self.caller.event_generate('<<uploaded>>', when='tail', data=f'${source_id}-{image[0]}')

                # wait last <<uploaded>> event fired
                time.sleep(2)
                if counter == left:
                    sql = f"UPDATE source SET status='b4' WHERE source_id={source_id}"
                    self.source_sql_queue.put(sql)
                    self.caller.after_source_complete(source_id)
            self.is_done = True
            self.caller.complete_all()
        self.caller.event_generate('<<complete>>', when='tail')


class UploadProgress(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.app = parent
        self.layout()

        # self.async_loop = asyncio.get_event_loop()
        self.is_uploading = False
        self.progress_bars = {} # don't how to get canvas window widget to configure
        self.source_list = []
        self.uploader = Uploader(self)
        self.to_update = []
        self.bind('<<complete>>', self.event_complete)
        self.bind('<<uploaded>>', self.event_uploaded)


        self.refresh()

    def layout(self):
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=0)

        self.canvas = tk.Canvas(
            self,
            width=self.app.app_width,
            height=self.app.app_height-50-25,
            bg='#F2F2F2',
            bd=0,
            highlightthickness=0,
            relief='ridge',
        )
        self.canvas.grid(row=0, column=0, sticky='ewns')

        self.bg = ImageTk.PhotoImage(file='./assets/upload_progress_vector.png')
        self.canvas.create_image(
            690,
            350,
            image=self.bg,
            anchor='nw',
        )
        self.canvas.create_text(
            50,
            20,
            anchor='nw',
            text='上傳進度',
            font=(self.app.app_font, 32),
            fill=self.app.app_primary_color,
        )
        self.upload_folder_image = ImageTk.PhotoImage(file='./assets/upload_folder.png')

    def refresh(self):
        db = self.app.db
        rows = db.fetch_sql_all("SELECT * FROM source WHERE status LIKE 'b%' ORDER BY upload_created")

        start_x = 124 # begin
        start_y = 124
        shift_x = 0 # shift
        shift_y = 0

        # clear
        self.canvas.delete('item')
        self.source_list = []

        for i, r in enumerate(rows):
            # print(r)
            source_id = r[0]
            total = r[4]
            left = 0
            sql_images = f"SELECT * FROM image WHERE source_id={r[0]} AND upload_status != '200' ORDER BY image_id"
            res_images = self.app.db.fetch_sql_all(sql_images)
            data = (r, res_images)
            self.source_list.append(data)
            self._render_box(data, start_x, start_y, shift_x, shift_y)

            shift_x += 316  # 300 + 16
            if i > 0 and (i+1) % 3 == 0:
                shift_y += 162  # 150 + 12
                shift_x = 0

    def _render_box(self, data, start_x, start_y, shift_x, shift_y):
        r = data[0]
        source_id = r[0]
        total = r[4]
        left = len(data[1])

        timestamp = datetime.fromtimestamp(r[5]).strftime('%Y-%m-%d %H:%M')
        x = start_x + shift_x
        y = start_y + shift_y
        xlist = [x, x + 300, x + 300, x]
        ylist = [y, y, y + 150, y + 150]

        create_round_polygon(
            self.canvas,
            xlist,
            ylist,
            10,
            #width=1,
            #outline="#82B366",
            fill='#FFFFFF',
            tags=('item'),
        )
        gap = y + 16
        # change font size
        title_font_size = 20
        # if len(r[3]) > 32:
        #    title_font_size = 14
        # elif len(r[3]) > 27:
        #    title_font_size = 17
        # change line
        limiter = 23
        if len(r[3]) > limiter:
            title1 = r[3][:limiter]
            title2 = r[3][limiter:]
            self.canvas.create_text(
                x+50,
                gap-10,
                anchor='nw',
                text=title1,
                font=(self.app.app_font, title_font_size),
                fill=self.app.app_primary_color,
                tags=('item'))
            self.canvas.create_text(
                x+50,
                gap+10,
                anchor='nw',
                text=title2,
                font=(self.app.app_font, title_font_size),
                fill=self.app.app_primary_color,
                tags=('item'))
        else:
            self.canvas.create_text(
                x+50,
                gap,
                anchor='nw',
                text=r[3],
                font=(self.app.app_font, title_font_size),
                fill=self.app.app_primary_color,
                tags=('item'))

        self.canvas.create_image(
            x+20,
            gap,
            image=self.upload_folder_image,
            anchor='nw',
            tags=('item'))

        gap += 40
        status_text = ''
        button_text = ''
        button_cmd = None
        if r[6] == self.app.source.STATUS_DONE_UPLOAD:
            status_text = '資料夾上傳完畢'
            button_text = '確認並歸檔'
            button_cmd = lambda source_id=source_id: self.handle_archive(source_id)
        else:
            status_text = '資料夾上傳中...'
            button_text = '重啟上傳'
            button_cmd = lambda source_id=source_id: self.handle_upload(source_id)


        self.canvas.create_text(
            x+24,
            gap,
            anchor='nw',
            text=status_text,
            font=(self.app.app_font, 16),
            fill='#464646',
            tags=('item'))

        self.canvas.create_text(
            x+286,
            gap,
            anchor='ne',
            text='{:.2f}%'.format(((total-left) / total) * 100.0),
            font=(self.app.app_font, 16),
            fill=self.app.app_primary_color,
            tags=('item', f'{source_id}-text'))

        gap += 22
        self.canvas.create_text(
            x+24,
            gap,
            anchor='nw',
            text=f'({total-left}/{total})',
            font=(self.app.app_font, 16),
            fill='#464646',
            tags=('item', f'{source_id}-step'))

        #if r[6] == '0':
        # importing progress bar
        pb = ttk.Progressbar(self.canvas, orient=tk.HORIZONTAL, length=122, value=0, mode='determinate', maximum=total)
        pb.grid(row=0, column=0)
        self.progress_bars[r[0]] = pb
        self.canvas.create_window(
            x+160,
            gap,
            width=122,
            window=pb,
            anchor='nw',
            tags=('item', f'{source_id}-pb_frame'),
        )

        gap += 22
        btn = ttk.Button(
            self,
            text=button_text,
            command=button_cmd)

        self.canvas.create_window(
            x+20,
            gap+4,
            width=261,
            height=36,
            window=btn,
            anchor='nw',
            tags=('item')
        )

    def event_complete(self, event):
        for _ in range(self.uploader.source_sql_queue.qsize()):
            sql = self.uploader.source_sql_queue.get()
            logging.debug(f'update source sql: {sql}')
            res = self.app.db.exec_sql(sql, True)

        self.refresh()

    def event_uploaded(self, event):
        for _ in range(self.uploader.image_sql_queue.qsize()):
            sql = self.uploader.image_sql_queue.get()
            logging.debug(f'update image sql: {sql}')
            res = self.app.db.exec_sql(sql, True)

    def after_source_complete(self, source_id):
        logging.debug(f'complete source_id: {source_id}')


    def complete_all(self):
        print('complete all')
        self.is_uploading = False

    def after_image_upload(self, source_id, image_id, counter):
        if found := self._find_source(source_id):
            total = found['data'][0][4]
            left = len(found['data'][1])
            value = total - left + counter
            # update layout
            self.progress_bars[source_id]['value'] = value
            self.canvas.itemconfigure(f'{source_id}-text', text='{:.2f}%'.format((value / total) * 100.0))
            self.canvas.itemconfigure(f'{source_id}-step', text=f'({value}/{total})')

    def _find_source(self, source_id):
        for i, v in enumerate(self.source_list):
            if v[0][0] == source_id:
                return {
                    'index': i,
                    'data': v,
                }
        return False

    def handle_upload(self, source_id):
        logging.debug(f'source_id: {source_id}')
        upload_queue = Queue()
        index = -1
        if found := self._find_source(source_id):
            index = found['index']

        if index >= 0:
            upload_queue.put(self.source_list[index])
            for i, v in enumerate(self.source_list):
                if i != index:
                    upload_queue.put(v)
        else:
            for v in self.source_list:
                upload_queue.put(v)

        self.uploader.upload_queue = upload_queue
        self.is_uploading = True
        self.uploader.start()

    def handle_archive(self, source_id):
        print('on archive', source_id)
