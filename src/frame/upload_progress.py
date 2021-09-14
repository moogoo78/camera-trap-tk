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

HIDE = -1
STOP = -2
DONE = -3
BREAK = -4
PAUSE = -5

class UploadProgress(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, background='#2d3142', *args, **kwargs)
        self.parent = parent
        self.app = self.parent.app

        #self.message = ttk.Label(self, text="uploading!")
        #self.message.grid(row=0, column=0, sticky='nsew', padx=10, pady=10)
        self.start_button = ttk.Button(
            self,
            text='Start',
            #command=self.start_upload
            command=self.handle_start
        )
        self.start_button.grid(row=0, column=0, padx=10, pady=10, sticky='we')

        self.stop_button = ttk.Button(
            self,
            text='Stop',
            #command=self.stop_upload
            #command=self.foo_handle_pause,
            command=self.handle_stop,
        )
        self.stop_button.grid(row=0, column=1, padx=10, pady=10, sticky='we')


        #self.app_que = Queue()
        #self.dialog_que = Queue()
        #self.thread = threading.Thread(target=self.worker, daemon=True)
        #self.thread.start()

        #self.is_running = False
        #self.is_finished = True
        self.uploading_list = []

        self.refresh()
        #self.loop = asyncio.new_event_loop()
        #t = threading.Thread(target=self.start_background_loop, args=(self.loop,), daemon=True)
        #t.start()

    def refresh(self):
        sql = "SELECT * FROM source WHERE status in ('10', '20')"
        res = self.app.db.fetch_sql_all(sql)

        pb_style = ttk.Style()
        pb_style.configure("green.Horizontal.TProgressbar", foreground='#5eba7d', background='#6fca64')
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

            self.uploading_list.append({
                'progress_bar': pb,
                'subtitle1': subtitle1_label,
                'subtitle2': subtitle2_label,
                'total': total,
                'source': v,
                'init_value': value,
                'image_pending_list': res_images,
            })

    def test_stop(self):
        if self.is_running or self.is_finished:
            self.dialog_que.put(HIDE)

        self.stop_btn.config(state=tk.DISABLED)
        self.start_btn.config(state=tk.NORMAL)

    def handle_start(self):
        # if self.uploading[0]['progress_bar']['value'] < self.uploading[0]['progress_bar']['maximum']:
        #     text = self.stop_button.cget('text')
        #     text = 'Resume' if text == 'Pause' else 'Pause'
        #     self.start_button.config(text=text)
        #     self.app_que.put(PAUSE)
        # else:
        #     #self.Start_button.config(text='Pause')
        #     self.stop_btn.config(state=tk.DISABLED)
        threading.Thread(target=self._asyncio_thread, args=(self.app.async_loop,)).start()

    def handle_stop(self):
        if self.running or self.finished:
            self.dialog_que.put(HIDE)

        self.stop_button.config(state=tk.DISABLED)
        self.start_button.config(state=tk.NORMAL)

    def app_worker(self):
        #self.dlg.cancel_btn.config(text='Cancel')
        #self.dlg.pause_btn.config(state=tk.NORMAL)

        for count in range(0, self.uploading[0]['total']+1):
            try:
                message = self.app_que.get_nowait()
                if message:
                    if message == PAUSE:
                        message = self.app_que.get()

                    if message == BREAK:
                        self.stop_btn.config(state=tk.DISABLED)
                        break
                    elif message == STOP:
                        #self.destroy()
                        pass
            except queue.Empty:
                pass

            time.sleep(1)  # Simulate work.
            self.dialog_que.put(count)

        self.dialog_que.put(DONE)
        #self.dlg.cancel_btn.config(text='Close')

        self.is_finished = True
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)

    def worker(self):
        while True:
            message = self.dialog_que.get()
            print(message)
            if message == HIDE:
                #self.hide()
                pass
            elif message == STOP:
                self.app_que.put(DONE)
                break
            elif message == DONE:
                #self.pause_btn.config(state=tk.DISABLED)
                pass
            else:
                item = self.uploading[0]
                item['progress_bar']['value'] = message
                item['label']['text'] = '{}/{}'.format(message, item['total'])
                item['pb_percent_label'] = '{} %'.format(round((message/item['total'])*100.0))

    def start_background_loop(self, loop: asyncio.AbstractEventLoop) -> None:
        asyncio.set_event_loop(self.loop)
        self.loop.run_forever()

    def foo_start_loop(self):
        t = threading.Thread(target=self.start_background_loop, args=(self.loop,), daemon=True)
        t.start()

    def __init2__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, background='#2d3142', *args, **kwargs)
        self.parent = parent
        self.app = self.parent.app

        #self.message = ttk.Label(self, text="uploading!")
        #self.message.grid(row=0, column=0, sticky='nsew', padx=10, pady=10)
        self.start_button = ttk.Button(
            self,
            text='start',
            #command=self.start_upload
            command=self.foo_handle_start
        )
        self.start_button.grid(row=0, column=0, padx=10, pady=10, sticky='we')

        self.stop_button = ttk.Button(
            self,
            text='stop',
            #            command=self.stop_upload
            command=self.foo_handle_pause,
        )
        self.stop_button.grid(row=0, column=1, padx=10, pady=10, sticky='we')

        #self.refresh_button = ttk.Button(
        #    self,
        #    text='refresh',
        #    command=self.handle_refresh
        #)
        #self.refresh_button.grid(row=0, column=3, padx=10, pady=10 ,sticky='we')

        self.TASK_LIMIT = 2 # conf
        self.NUM_UPLOADED_SAVE = 10 # conf
        #self.queue = queue.Queue()
        #self.uploaded_queue = queue.Queue()
        self.state = {
            'status': 'stop',
            'upload_map': {},
            'task_end': -1,
            'task_counter': -1,
            'done_list': [],
            'is_thread_running': False,
            'num_queue_process': 0,
        }
        #self.async_loop = asyncio.get_event_loop()
        #self.semaphore = asyncio.Semaphore(value=2)
        #self.async_q = asyncio.Queue()

        self.counter1 = 0 # num of process_upload
        self.counter2 = 0 # num of each process_upload tick

        self.refresh2()
        #self.refresh()
        self.foo_can = False

    def refresh2(self):
        for i in range(0, 2):
            _thread = threading.Thread(target=self.foo_long, kwargs={'source_id':i})
            _thread.start()
            print ('ahh thread')
        print ('ohoh')

    def handle_refresh(self):
        self.refresh()


    def create_upload_process(self, data):
        self.refresh()
        self.start_upload()

    async def task_upload_source(self, name, queue):
        logging.info(f'task upload source: {name}, start')
        data = await queue.get()

        source_id = data['source_id']
        sql_images = f"SELECT * FROM image WHERE source_id={source_id} AND status!='200'"
        res = self.app.db.fetch_sql_all(sql_images)
        for i in res:
            data['count'] += 1
            await asyncio.sleep(3)

            data['pb']['value'] = round((data['count']/data['total']) * 100.0)
            self.update_idletasks()

            sql = f"UPDATE image SET status='44' WHERE image_id={i[0]}"
            self.app.db.exec_sql(sql, True)
        '''
        for i in range(data['num_not_uploaded']):
            #print ('uploading', data['source_id'], i, data['total'])
            data['count'] += 1
            await asyncio.sleep(3)
            data['pb']['value'] = round((data['count']/data['total']) * 100.0)
            self.update_idletasks()
        '''
        sql = f'UPDATE source SET status="40" WHERE source_id={source_id}'
        self.app.db.exec_sql(sql, True)
        queue.task_done()
        logging.info(f'task upload source:{name}, done')

    async def do_upload(self):
        #print (self.state['upload_map'])
        process_list = []
        source_ids = []
        counter = 0
        for source_id, item in self.state['upload_map'].items():
            if item['status'] == '20':
                process_list.append(asyncio.create_task(self.my_worker(source_id)))
        #for source_id, item in self.state['upload_map'].items():
        #    if counter < self.process_limit and item['status'] == '20': # find pending upload source
        #counter += 1
        #        source_ids.append(item['source_id'])
            #process_list.append(self.task_upload_source(f'task-{counter}: source-{source_id}', self.async_q))
        #        await self.async_q.put(item)

        await asyncio.gather(*process_list)
        #await self.async_q.join()
        logging.info('all task done')

        #for i in source_ids:
        #    sql = f'UPDATE source SET status="40" WHERE source_id={i}'
        #    self.app.db.exec_sql(sql, True)

    def start_upload(self):
        self.state['status'] = 'start'
        logging.info('START UPLOAD')
        self.process_upload()
        self.polling()


    def stop_upload(self):
        self.state.update({
            'status': 'stop',
            'is_thread_running': False
        })

    #def _asyncio_thread(self, item):
    #    print ('thread source:', item)
    #    self.async_loop.run_until_complete(self.do_uploads(item))
    #self.state['doing'] = False
    #    print ('thread complete!!')

    async def one_url(self, url):
        """ One task. """
        import random
        sec = random.randint(1, 8)
        await asyncio.sleep(sec)
        print (url, sec)
        return 'url: {}\tsec: {}'.format(url, sec)

    async def do_uploads(self, item):
        tasks = [self.one_url(item['source_id']) for x in range(int(item['n']))]
        completed, pending = await asyncio.wait(tasks)
        print ('CP', completed, pending)
        results = [task.result() for task in completed]
        print('done uploads')
        print('\n'.join(results))

        #tasks = [self.one_url(url) for url in range(10)]
        #completed, pending = await asyncio.wait(tasks)

        #results = [task.result() for task in completed]
        #print('\n'.join(results))

    def process_upload(self):
        process_counter = 0
        process_map = {}
        for source_id, item in self.state['upload_map'].items():
            if process_counter < self.TASK_LIMIT:
                if item['status'] in ['20', '30']:
                    process_counter += 1
                    process_map[source_id] = item
            else:
                break

        if process_counter <= 0:
            self.state['status'] = 'stop'
            self.state['num_queue_process'] = 0
            return False
        logging.info(f'process_upload: {process_counter} x thread')
        self.state.update({
            'task_end': process_counter,
            'task_counter': 0,
            'is_thread_running': True,
        })
        #print (process_map, process_counter)
        for source_id, item in process_map.items():
            item['process_step'] = 1
            item['status'] = '30'
            sql = f"UPDATE source SET status='30' WHERE source_id={source_id}"
            self.app.db.exec_sql(sql, True)

            sql = f"SELECT * FROM image WHERE source_id={source_id} AND (upload_status IS NULL OR upload_status!='200')"
            image_list = self.app.db.fetch_sql_all(sql)
            #print (image_list)
            task = UploadTask(
                f'upload-{source_id}',
                item,
                image_list,
                self.state,
                self.app.source.upload_to_s3,
            )
            task.start()

            # will block
            #task.join()
            #print ('tasks ok', task)

    def update_progressbar(self, data):
        for k, v in data.items():
            count = v['count']
            total = v['total']
            value = round((count/total) * 100.0)
            #print ('gui', count, total, value, v['current_text'], v['status'])
            #if v['status'] == '20':
            v['label']['text'] = '上傳中: {}'.format(v['current_text'])
            v['percent_label']['text'] = f'{value} % ({count}/{total})'
            v['progressbar']['value'] = value
        self.update_idletasks()

    def polling(self):

        if self.state['status'] != 'start':
            return False

        self.counter2 += 1

        print (f'polling {self.counter1}-{self.counter2}', self.state['done_list'], self.state['num_queue_process'])

        if self.state['num_queue_process'] == 0:
            self.state['status'] = 'stop'
            return False
        else:
            # save status, if accumulated some uploaded
            for k,v in self.state['upload_map'].items():
                if num_uploaded := len(v['uploaded']):
                    if num_uploaded % self.NUM_UPLOADED_SAVE == 0:
                        image_ids = ','.join([str(x) for x in v['uploaded']])
                        sql = f"UPDATE image SET upload_status='200' WHERE image_id IN ({image_ids})"
                        self.app.db.exec_sql(sql, True)
                        # clear
                        v['uploaded'] = []

            self.update_progressbar(self.state['upload_map'])

            # control process
            if self.state['task_end'] > 0 and \
               self.state['task_end'] == len(self.state['done_list']):

                logging.info('next process_upload')

                ids = []
                for x in self.state['done_list']:
                    ids.append(str(x))
                    self.state['upload_map'][x]['status'] = '40'
                    self.state['num_queue_process'] -= 1

                source_ids = ','.join(ids)
                sql = f"UPDATE source SET status='40' WHERE source_id IN ({source_ids})"
                self.app.db.exec_sql(sql, True)

                # slow done (for debug)
                time.sleep(1)

                # run process again
                # reset counters
                self.counter1 += 1
                self.counter2 = 0
                self.state.update({
                    'done_list': [],
                    'task_end': 0,
                    'task_counter': -1,
                })

                if self.state['num_queue_process'] > 0:
                    self.refresh()
                    self.process_upload()

        self.app.after(1000, self.polling)

    async def do_upload(self, source_id, index):
        await asyncio.sleep(1)

    def process_upload(self, source_id):
        for i in range(0, 11):
            #await asyncio.sleep(1)
            #await do_upload(source_id, i)
            time.sleep(1)
            print (i, source_id)
        print ('processed')

    def foo_start(self, source_id):
        print('start', source_id)
        #self.process_upload(source_id)
        _thread = threading.Thread(target=self.process_upload, kwargs={'source_id':source_id})
        _thread.start()
        print ('end')


    def foo_long(self, **kwargs):
        import random
        r = random.randint(2,7)
        source_id = kwargs.pop('source_id', '')
        for i in range(0, r+1):
            time.sleep(1)
            print (source_id, '{}/{}'.format(i, r), self.foo_can)
            if self.foo_can:
                return

    async def fetch(self, url):
        try:
            # Wait for 1 hour
            r = random.randint(3,5)
            print (url)
            for i in range(0, r):
                await asyncio.sleep(0.3*i)
                print (url, '{}/{}'.format(i, r))
        except asyncio.CancelledError:
            print('cancel_me(): cancel sleep')
            raise
        finally:
            print('cancel_me(): after sleep')

        return url, 200

    async def upload_image_list(self, row):
        #print (row)
        server_image_id = row[11]
        thumb_paths = get_thumb(row[10], row[2], row[1], 'all')
        for x, path in thumb_paths.items():
            object_name = f'{server_image_id}-{x}.jpg'
            print (object_name)
            time.sleep(0.3)
            #res = self.func_to_s3(str(path), object_name)

    async def upload_folder(self, data):
        try:
            for i, image in enumerate(data['image_pending_list']):
            #for i in range(0, len(data['image_pending_list'])+1):
                await asyncio.sleep(0.5)
                #await self.upload_image_list(data['image_pending_list'][i])
                # update progress display
                value = i + 1 + data['init_value']
                total = data['total']
                data['progress_bar']['value'] = value
                data['subtitle1']['text'] = '{} ({}/{})'.format(image[2], value, total)
                data['subtitle2']['text'] = '{} %'.format(round(value/total*100.0))
        except asyncio.CancelledError:
            logging.debug('asyncio: cancel ')
            raise
        finally:
            logging.debug('task: upload_folder done')

        return data

    async def do_uploads(self, uploading_list):

        limit = 2
        res_all = []
        total = len(uploading_list)
        page_total = round(total / limit)
        page_last_num = total % limit

        for i in range(0, page_total):
            step = i * limit
            tasks = []
            page_end = limit if i+1 < page_total or page_last_num == 0 else page_last_num
            #print (m2)
            for j in range(0, page_end):
                index = j + step
                task = asyncio.create_task(self.upload_folder(uploading_list[index]))
                #await asyncio.sleep(10)
                #t.cancel()
                tasks.append(task)
            res = []
            try:
                res = await asyncio.gather(*tasks)
                print (res)
            except asyncio.CancelledError:
                logging.debug('do_uploads: cancel')

        return res_all

    def _asyncio_thread(self, async_loop):
        async_loop.run_until_complete(self.do_uploads(self.uploading_list))
        print ('fin asyncio_thread')
        #async_loop.run_forever()

    def foo_handle_start(self):
        #thread = threading.Thread(target=self.app_worker, daemon=True)
        #thread.start()
        '''
        #self.foo_start_loop()
        t = threading.Thread(target=self.start_background_loop, args=(self.loop,), daemon=True)
        t.start()
        '''
        #self.loop = asyncio.new_event_loop()
        #t = threading.Thread(target=self.start_background_loop, args=(self.loop,), daemon=True)
        #t.start()
        threading.Thread(target=self._asyncio_thread, args=(self.app.async_loop,), daemon=True).start()
        #task = asyncio.run_coroutine_threadsafe(self.hard_works(URLS), self.app.async_loop)
        #print ('star wait')
        #print (task.result())
        self.loop.stop()


    def foo_handle_pause(self):
        #self.foo_can = False
        print (asyncio.Task.all_tasks())
