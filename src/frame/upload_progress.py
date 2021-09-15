import tkinter as tk
from tkinter import (
    ttk,
)
import queue
import logging
import json

import threading
import time
import random
import asyncio
import concurrent.futures
from queue import Queue

from worker import UploadTask
from image import get_thumb


class UploadProgress(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, background='#2d3142', *args, **kwargs)
        self.parent = parent
        self.app = self.parent.app

        self.start_button = ttk.Button(
            self,
            text='Start',
            command=self.handle_start,
            takefocus=0,
        )
        self.start_button.grid(row=0, column=0, padx=10, pady=10, sticky='we')

        self.stop_button = ttk.Button(
            self,
            text='Stop',
            command=self.handle_stop,
            takefocus=0,
        )
        self.stop_button.grid(row=0, column=1, padx=10, pady=10, sticky='we')

        self.uploading_data = {
            'status': 'stop', # stop/start
            'source_list': [],
            'tasks': [],
            'limit': 2,
            'uploaded_que': Queue(),
        }
        self.is_dry_run = True

        self.refresh()
        #self.loop = asyncio.new_event_loop()
        self.async_loop = asyncio.get_event_loop()
        #t = threading.Thread(target=self.start_background_loop, args=(self.loop,), daemon=True)
        #t.start()

    def refresh(self):
        for i in self.uploading_data['source_list']:
            i['frame'].destroy()

        self.uploading_data['source_list'] = []

        sql = "SELECT * FROM source WHERE status in ('20', '30')"
        res = self.app.db.fetch_sql_all(sql)

        pb_style = ttk.Style()
        pb_style.configure("green.Horizontal.TProgressbar", foreground='#5eba7d', background='#6fca64')
        self.progress_bar_wrapper = tk.Frame(self)
        self.progress_bar_wrapper.grid()
        for i, v in enumerate(res):
            sql_images = f"SELECT * FROM image WHERE source_id={v[0]} AND upload_status != '200' ORDER BY image_id"
            res_images = self.app.db.fetch_sql_all(sql_images)

            frame = tk.LabelFrame(self, text=f'{v[3]}', width='300')
            total = v[4] # real left image TODO
            #value = round(((total-i[8])/total) * 100.0)
            value = total - len(res_images)
            subtitle1_label = ttk.Label(frame, text=f'{value}/{total}')
            subtitle1_label.grid(row=0, column=0, sticky='nw', padx=4)
            subtitle2_label = ttk.Label(frame, text='{} %'.format(round(value/total*100.0)))
            subtitle2_label.grid(row=0, column=0, sticky='ne', padx=4)
            pb = ttk.Progressbar(frame, orient=tk.HORIZONTAL, length=600, mode='determinate', value=value, style='green.Horizontal.TProgressbar', maximum=total)
            pb.grid(row=1, column=0, padx=4, pady=4)
            frame.grid(row=1+i, column=0, pady=10, columnspan=3)

            self.uploading_data['source_list'].append({
                'frame': frame,
                'progress_bar': pb,
                'subtitle1': subtitle1_label,
                'subtitle2': subtitle2_label,
                'total': total,
                'source': v,
                'init_value': value,
                'image_pending_list': res_images,
            })

    def handle_start(self):
        self.uploading_data['status'] = 'start'
        self.refresh()
        threading.Thread(target=self._asyncio_thread, args=(self.async_loop,)).start()
        self.polling()
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)

    def handle_stop(self):
        #self.loop.stop() # RuntimeError: Event loop stopped before Future completed
        self.uploading_data['status'] = 'stop'
        for t in self.uploading_data['tasks']:
            t.cancel()
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)

    def start_background_loop(self, loop: asyncio.AbstractEventLoop) -> None:
        asyncio.set_event_loop(self.async_loop)
        self.loop.run_forever()

    async def upload_images(self, row):
        server_image_id = row[11]
        thumb_paths = get_thumb(row[10], row[2], row[1], 'all')
        #print ('upload_image', row[10])
        for x, path in thumb_paths.items():
            object_name = f'{server_image_id}-{x}.jpg'
            print (object_name)
            #time.sleep(0.3)
            if self.is_dry_run == True:
                await asyncio.sleep(0.3)
            else:
                #self.app.source.upload_to_s3(str(path), object_name)
                pass

            # TODO error return

    async def upload_folder(self, data):
        try:
            for i, row in enumerate(data['image_pending_list']):
                if self.is_dry_run == True:
                    await asyncio.sleep(0.5)
                    self.uploading_data['uploaded_que'].put(row[0])
                else:
                    await self.upload_images(row)
                    # TODO check if upload not successed
                    self.uploading_data['uploaded_que'].put(row[0])

                # update progress display
                value = i + 1 + data['init_value']
                total = data['total']
                data['progress_bar'].config(value=value)
                data['subtitle1'].config(text='{} ({}/{})'.format(row[2], value, total))
                data['subtitle2'].config(text='{} %'.format(round(value/total*100.0)))
        except asyncio.CancelledError:
            logging.debug('asyncio: cancel ')
            raise
        finally:
            logging.debug('task: upload_folder done')

        return data

    async def do_uploads(self):
        limit = self.uploading_data['limit']
        res_all = []
        total = len(self.uploading_data['source_list'])
        page_total = round(total / limit)
        page_last_num = total % limit

        # TODO 改成 1 次 1 個, 總共 2 個
        for i in range(0, page_total):
            step = i * limit
            self.uploading_data['tasks'] = []
            page_end = limit if i+1 < page_total or page_last_num == 0 else page_last_num

            if self.uploading_data['status'] == 'stop':
                break

            for j in range(0, page_end):
                index = j + step
                task = asyncio.create_task(self.upload_folder(self.uploading_data['source_list'][index]))
                self.uploading_data['tasks'].append(task)
            res = []
            try:
                res = await asyncio.gather(*self.uploading_data['tasks'])
                #print (res)
                logging.debug('done 2 tasks')
            except asyncio.CancelledError:
                logging.debug('do_uploads: cancel')

        return res_all

    def _asyncio_thread(self, async_loop):
        async_loop.run_until_complete(self.do_uploads())
        logging.debug('asyncio loop complete')
        #async_loop.run_forever()

    def polling(self):
        '''to save upload progress'''
        if self.uploading_data['status'] != 'start':
            return

        q = self.uploading_data['uploaded_que']
        for _ in range(q.qsize()):
            image_id = q.get()
            sql = f"UPDATE image SET upload_status='200' WHERE image_id = {image_id}"
            self.app.db.exec_sql(sql)
        self.app.db.commit()

        self.app.after(1000, self.polling)
