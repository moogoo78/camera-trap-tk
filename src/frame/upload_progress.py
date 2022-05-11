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
            state=tk.DISABLED,
        )
        self.stop_button.grid(row=0, column=1, padx=10, pady=10, sticky='we')

        # break:  while press stop, set break and disable start_button
        # stop: while thread run_untile_complete
        # start: fetch db & start
        # done:
        # pause:
        self.uploading_data = {
            'status': 'stop', # stop/break/start
            'source_list': [],
            'tasks': [],
            'uploaded_que': Queue(),
            'history_que': Queue(),
        }
        self.is_dry_run = False
        self.upload_limit = 2
        self.upload_quota = 2

        self.refresh()
        #self.loop = asyncio.new_event_loop()
        self.async_loop = asyncio.get_event_loop()
        #t = threading.Thread(target=self.start_background_loop, args=(self.loop,), daemon=True)
        #t.start()

    def refresh(self):
        for i in self.uploading_data['source_list']:
            i['frame'].destroy()

        self.uploading_data.update({
            'source_list': [],
            'uploaded_que': Queue(),
            'history_que': Queue(),
        })

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
        self.refresh()
        self.uploading_data['status'] = 'start'
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)

        threading.Thread(target=self._asyncio_thread, args=(self.async_loop,)).start()
        self.polling()


    def handle_stop(self):
        #self.loop.stop() # RuntimeError: Event loop stopped before Future completed
        self.uploading_data['status'] = 'break'
        logging.info('cancel all upload tasks')
        #self.start_button.config(state=tk.DISABLED)
        #self.stop_button.config(state=tk.DISABLED)
        for t in self.uploading_data['tasks']:
            t.cancel()
        logging.info('set status to stop')
        #self.start_button.config(state=tk.NORMAL)
        #self.stop_button.config(state=tk.DISABLED)

    def start_background_loop(self, loop: asyncio.AbstractEventLoop) -> None:
        asyncio.set_event_loop(self.async_loop)
        self.loop.run_forever()

    async def upload_images(self, row):
        # server_image_id = row[11]
        object_id = row[14]
        thumb_paths = get_thumb(row[10], row[2], row[1], 'all')
        #print ('upload_image', row[10])

        for x, path in thumb_paths.items():
            object_name = f'{object_id}-{x}.jpg'
            #time.sleep(0.3)
            if self.is_dry_run == True:
                await asyncio.sleep(0.3)
            else:
                self.app.source.upload_to_s3(str(path), object_name)

            # TODO error return

        return

    async def upload_folder(self, data):
        source_id = None
        uploaded_count = 0

        try:
            start_time = datetime.now()
            for i, row in enumerate(data['image_pending_list']):
                if self.uploading_data['status'] in ['stop', 'break']:
                    break

                if not source_id:
                    source_id = row[10]
                if self.is_dry_run == True:
                    await asyncio.sleep(0.5)
                    #self.uploading_data['uploaded_que'].put(row[0])
                else:
                    if self.uploading_data['status'] == 'stop':
                        return
                    # uploaded_object_id = await self.upload_images(row)
                    await self.upload_images(row)

                    uploaded_count += 1
                    # TODO check if upload not successed
                    self.uploading_data['uploaded_que'].put(row[0])

                    server_image_id = row[11]
                    self.app.server.post_image_status({
                        # 'file_url': f'{uploaded_object_id}.jpg',
                        'has_storage': 'Y',
                        'pk': server_image_id,
                    })

                # update progress display
                value = i + 1 + data['init_value']
                total = data['total']
                try:
                    data['progress_bar'].config(value=value)
                    data['subtitle1'].config(text='{} ({}/{})'.format(row[2], value, total))
                    data['subtitle2'].config(text='{} %'.format(round(value/total*100.0)))
                except:
                    logging.info('progress bar update error')

        except asyncio.CancelledError:
            logging.info('asyncio: cancel ')
            raise
        finally:
            now = datetime.now()
            exec_time = (now - start_time).total_seconds()

            if uploaded_count >= len(data['image_pending_list']):
                self.uploading_data['history_que'].put({
                    'timestamp': str(now),
                    'elapsed': exec_time,
                    'source_id': source_id,
                    'deployment_journal_id': data['source'][12]
                })
                logging.info('task: upload_folder finally')
            else:
                logging.info('task: upload_folder finally - unfinish')

        return data

    async def do_uploads(self):
        limit = self.upload_limit
        res_all = []
        total = len(self.uploading_data['source_list'])
        for i in range(total):
            if self.uploading_data['status'] in ['stop', 'break']:
                break

            task = asyncio.create_task(self.upload_folder(self.uploading_data['source_list'][i]))
            self.uploading_data['tasks'].append(task)
            #self.upload_quota -= 1
            try:
                res = await task
                #res = await asyncio.gather(*self.uploading_data['tasks'])
                logging.info(f'done 1 task')
            except asyncio.CancelledError:
                logging.info('do_uploads: cancel')

        '''
        page_total = round(total / limit)
        page_last_num = total % limit
        print (total,'----------', self.uploading_data['status'], page_total)
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
        '''
        return res_all

    def _asyncio_thread(self, async_loop):
        async_loop.run_until_complete(self.do_uploads())
        logging.info('asyncio loop complete')

        self.uploading_data['status'] = 'stop'
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        #async_loop.run_forever()

    def polling(self):
        '''to save upload progress'''
        q = self.uploading_data['uploaded_que']
        qh = self.uploading_data['history_que']

        if q.qsize() == 0 and qh.qsize() == 0 and self.uploading_data['status'] == 'stop':
            return

        for _ in range(q.qsize()):
            image_id  = q.get()
            sql = f"UPDATE image SET upload_status='200' WHERE image_id = {image_id}"
            self.app.db.exec_sql(sql, True)

            # update table status
            main = self.app.frames['main']
            row_keys = main.data_helper.get_image_row_keys(image_id)
            for k in row_keys:
                main.data_helper.set_status_display(k, '200')
                main.data_grid.main_table.render()

        for _ in range(qh.qsize()):
            item = qh.get()

            sql = 'SELECT * FROM source WHERE source_id={}'.format(item['source_id'])
            if res := self.app.db.fetch_sql(sql):
                #sql_img_count = "SELECT COUNT(*) FROM image WHERE source_id={} AND upload_status='200'".format(item['source_id'])
                #if res2 := self.app.db.fetch_sql(sql_img_count):
                #    print (res2[0], res2[1])

                history = json.loads(res[8]) if res[8] else {'upload': []}
                history['upload'].append({
                    'elapsed': item['elapsed'],
                    'timestamp': item['timestamp'],
                })
                sql_update = "UPDATE source SET history='{}', status='40' WHERE source_id={}".format(json.dumps(history), item['source_id'])
                self.app.db.exec_sql(sql_update, True)

                # send finish upload status to server
                self.app.server.post_upload_history(item['deployment_journal_id'], 'finished')

        self.app.after(1000, self.polling)
