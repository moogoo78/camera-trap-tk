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

from image import get_thumb
from utils import create_round_polygon

class UploadProgress(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.app = parent
        self._layout()

        # self.async_loop = asyncio.get_event_loop()
        self.is_uploading = False
        self.progress_bars = {} # don't how to get canvas window widget to configure
        self.source_list = []

        self.queue_upload = Queue()  # add for uploading
        self.queue_action = Queue()  # state to update
        self.queue_image = Queue()
        self.async_loop = asyncio.get_event_loop()

        self.uploader_thread = None
        # self.uploader_thread.start()

        # self.polling()
        # self.bind('<<event_complete>>', self.event_complete)
        self.bind('<<event_image_uploaded>>', self.event_image_uploaded)
        # self.bind('<<event_source_uploaded>>', self.event_source_uploaded)

        self.refresh()

    def event_image_uploaded(self, event):
        print('-event-', '==============', self.queue_image.qsize())
        for _ in range(self.queue_image.qsize()):
            image_id = self.queue_image.get()
            sql = f"UPDATE image SET upload_status='200' WHERE image_id={image_id}"
            #res = self.app.db.exec_sql(sql, True)

    def uploader2(self, async_loop):
        async_loop.run_until_complete(self.uploader())

    async def uploader(self):
        logging.debug(f'🧵 uploader xxx start!!!')
        for _ in range(10):
            print ('gogogo', _)
            await asyncio.sleep(1)

        
    async def uploaderx(self):
        logging.debug(f'🧵 uploader start!!!')
        for _ in range(self.queue_upload.qsize()):
            data = self.queue_upload.get()
            counter = 0
            source_id = data['source_data'][0]
            left = len(data['left_images'])
            logging.debug(f'🧵 start upload source: {source_id}, num_images: {left}')
            self.queue_action.put({
                'type':'upload_source',
                'source_id': source_id,
            })
            for image in data['left_images']:
                if self.is_uploading:
                    counter += 1
                    logging.debug(f'🧵 uploading: {image[0]}')


                    #time.sleep(1)
                    object_id = image[14]
                    thumb_paths = get_thumb(image[10], image[2], image[1], 'all')
                    for x, path in thumb_paths.items():
                        object_name = f'{object_id}-{x}.jpg'
                        time.sleep(0.5)
                        #self.app.source.upload_to_s3(str(path), object_name)

                    self.event_generate('<<event_image_uploaded>>', when='tail')
                    self.queue_image.put(image[0])
                    self.queue_action.put({
                        'type':'update_image',
                        'source_id': source_id,
                        'image_id': image[0],
                        'counter': counter
                    })
                else:
                    logging.debug(f'🧵 skip uploading: {image[0]}')

            if counter == left:
                self.queue_action.put({
                    'type': 'done_source',
                    'source_id': source_id
                })
            logging.debug(f'🧵 done source: {source_id}')

        logging.debug(f'🧵 upload complete !!!')

    def create_uploader(self):
        logging.debug('create uploader')
        self.is_uploading = True
        # self.uploader_thread = threading.Thread(target=self.uploader)
        #threading.Thread(target=self.uploader).start()
        threading.Thread(target=self._asyncio_thread, args=(self.async_loop,)).start()
        #uploader_thread.start()
        self.polling()

    def terminate_uploader(self):
        logging.debug('terminate uploader')
        self.is_uploading = False
        #self.uploader_thread = None  # ?
        self.refresh()

    def polling(self):
        print(self.is_uploading)
        #print(self.is_uploading, self.uploader_thread, self.uploader_thread.is_alive() if self.uploader_thread else 'xx', self.queue_upload.qsize(), self.queue_action.qsize())
        sql = f"UPDATE image SET upload_status='200' WHERE image_id={1}"
        #res = self.app.db.exec_sql(sql, True)
        print('range !!',)
        if self.is_uploading is False:
            return

        if not self.queue_action.empty():
            action = self.queue_action.get()

            if action['type'] == 'update_image':
                source_id = action['source_id']
                image_id = action['image_id']
                counter = action['counter']

                sql = f"UPDATE image SET upload_status='200' WHERE image_id={image_id}"
                res = self.app.db.exec_sql(sql, True)

                index = self._find_source_index(source_id)
                if index >= 0:
                    # update status
                    if status := self.source_list[index]['source_data'][6]:
                        if status != self.app.source.STATUS_MEDIA_UPLOADING:
                            self.app.source.update_status(source_id, 'MEDIA_UPLOADING')

                    total = self.source_list[index]['source_data'][4]
                    left = len(self.source_list[index]['left_images'])
                    value = total - left + counter
                    # update layout
                    self.progress_bars[source_id]['value'] = value
                    self.canvas.itemconfigure(f'{source_id}-text', text='{:.2f}%'.format((value / total) * 100.0))
                    self.canvas.itemconfigure(f'{source_id}-step', text=f'({value}/{total})')
            elif action['type'] == 'upload_source':
                source_id = action['source_id']
                self.app.source.update_status(source_id, 'START_MEDIA_UPLOAD')
                self.refresh()
            elif action['type'] == 'done_source':
                source_id = action['source_id']
                self.app.source.update_status(source_id, 'DONE_UPLOAD')

                self.terminate_uploader()
                self._find_next_source()

        self.after(1000, self.polling)

    def _layout(self):
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
        self.ok_image = ImageTk.PhotoImage(file='./assets/ok.png')

    def refresh(self):
        logging.debug('~ refresh ~')
        db = self.app.db
        rows = db.fetch_sql_all("SELECT * FROM source WHERE status LIKE 'b%' ORDER BY upload_created")

        start_x = 124 # begin
        start_y = 124
        shift_x = 0 # shift
        shift_y = 0

        # clear
        self.canvas.delete('item')
        self.source_list = []

        # btn = ttk.Button(self.canvas, text='terminate', command=self.terminate_uploader)
        # self.canvas.create_window(
        #    50,
        #    50,
        #    width=261,
        #    height=36,
        #    window=btn,
        #    anchor='nw',
        #    tags=('item')
        #)

        for i, r in enumerate(rows):
            # print(r)
            source_id = r[0]
            total = r[4]
            left = 0
            sql_images = f"SELECT * FROM image WHERE source_id={r[0]} AND upload_status != '200' ORDER BY image_id"
            res_images = self.app.db.fetch_sql_all(sql_images)
            data = {'source_data': r, 'left_images': res_images}
            self.source_list.append(data)
            self._render_box(data, start_x, start_y, shift_x, shift_y)

            shift_x += 316  # 300 + 16
            if i > 0 and (i+1) % 3 == 0:
                shift_y += 162  # 150 + 12
                shift_x = 0

    def _render_box(self, data, start_x, start_y, shift_x, shift_y):
        r = data['source_data']
        source_id = r[0]
        total = r[4]
        left = len(data['left_images'])

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
            #outline="#82fB366",
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
        action_label = ''
        step_label = ''
        progressbar_value = total-left

        '''
        if r[6] == self.app.source.STATUS_DONE_UPLOAD:
            status_text = '資料夾上傳完畢'
            button_text = '確認並歸檔'
            button_cmd = lambda source_id=source_id: self.handle_archive(source_id)
            progressbar_value = total
        elif r[6] in [self.app.source.STATUS_START_MEDIA_UPLOAD, self.app.source.STATUS_MEDIA_UPLOADING]:
            status_text = '資料夾上傳中...'
            button_text = '暫停上傳'
            button_cmd = lambda source_id=source_id: self.handle_stop(source_id)
        elif r[6] == self.app.source.STATUS_STOP_MEDIA_UPLOAD:
            status_text = '資料夾上傳中...'
            button_text = '重啟上傳'
            button_cmd = lambda source_id=source_id: self.handle_start(source_id)
        '''
        status_text = '資料夾上傳中...'
        if self.is_uploading:
            button_text = 'pause'
            button_cmd = lambda source_id=source_id: self.handle_stop(source_id)
        else:
            button_text = 'play'
            button_cmd = lambda source_id=source_id: self.handle_start(source_id)

        self.canvas.create_text(
            x+24,
            gap,
            anchor='nw',
            text=status_text,
            font=(self.app.app_font, 16),
            fill='#464646',
            tags=('item'))

        if r[6] == self.app.source.STATUS_DONE_UPLOAD:
            self.canvas.create_image(
                x+204,
                gap-36,
                image=self.ok_image,
                anchor='nw',
                tags=('item'))
        else:
            self.canvas.create_text(
                x+286,
                gap,
                anchor='ne',
                text='{:.2f}%'.format(((total-left) / total) * 100.0),
                font=(self.app.app_font, 16),
                fill=self.app.app_primary_color,
                tags=('item', f'{source_id}-text'))

            pb = ttk.Progressbar(self.canvas, orient=tk.HORIZONTAL, length=122, value=progressbar_value, mode='determinate', maximum=total)
            pb.grid(row=0, column=0)
            self.progress_bars[r[0]] = pb
            self.canvas.create_window(
                x+160,
                gap+22,
                width=122,
                window=pb,
                anchor='nw',
                tags=('item', f'{source_id}-pb_frame'),
            )

        gap += 22
        self.canvas.create_text(
            x+24,
            gap,
            anchor='nw',
            text=f'({total-left}/{total})',
            font=(self.app.app_font, 16),
            fill='#464646',
            tags=('item', f'{source_id}-step'))

        gap += 22
        btn = ttk.Button(
            self.canvas,
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

    def _find_source_index(self, source_id):
        for i, v in enumerate(self.source_list):
            if v['source_data'][0] == source_id:
                return i
        return -1

    def _find_next_source(self, ):
        for i in self.source_list:
            if i['source_data'][6] == self.app.source.STATUS_MEDIA_UPLOADING:
                self.handle_start(i['source_data'][0])

    def handle_start(self, source_id):
        logging.debug(f'source_id: {source_id}')
        index = self._find_source_index(source_id)
        if index >= 0:
            self.queue_upload.put(self.source_list[index])

        if not self.is_uploading:
            self.create_uploader()

    def handle_stop(self, source_id):
        logging.debug(f'source_id: {source_id}')
        #self.app.source.update_status(source_id, 'STOP_MEDIA_UPLOAD')
        self.terminate_uploader()

    def handle_archive(self, source_id):
        print('on archive', source_id)

    def _asyncio_thread(self, async_loop):
        async_loop.run_until_complete(self.uploader())
        logging.info('asyncio loop complete')
