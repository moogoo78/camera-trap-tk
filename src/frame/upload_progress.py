import tkinter as tk
from tkinter import (
    ttk,
)
import queue
import logging
import json


import threading
import time
import asyncio
import concurrent.futures

from worker import UploadTask

class UploadProgress(tk.Frame):

    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, background='#2d3142', *args, **kwargs)
        self.parent = parent
        self.app = self.parent.parent

        #self.message = ttk.Label(self, text="uploading!")
        #self.message.grid(row=0, column=0, sticky='nsew', padx=10, pady=10)
        self.start_button = ttk.Button(
            self,
            text='start',
            command=self.start_upload
        )
        self.start_button.grid(row=0, column=0, padx=10, pady=10, sticky='we')

        self.stop_button = ttk.Button(
            self,
            text='stop',
            command=self.stop_upload
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
        self.refresh()

    def handle_refresh(self):
        self.refresh()

    def refresh(self):
        # fetch sql source status and add to upload queue

        # reset list
        if uploads:= self.state['upload_map']:
            for _, v in uploads.items():
                v['frame'].destroy()
        self.state['upload_map'] = {}

        # get all source from db
        sql = "SELECT source.*, COUNT(*) AS img_count FROM image LEFT JOIN source ON image.source_id = source.source_id WHERE source.status IN ('20', '30') AND (image.upload_status IS NULL OR image.upload_status != '200') GROUP BY image.source_id ORDER BY source.source_id"
        res = self.app.db.fetch_sql_all(sql)

        # 不信任 i[4], 重新 count
        sql2 = "SELECT source.source_id, COUNT(*) AS img_all_count FROM image LEFT JOIN source ON image.source_id = source.source_id WHERE source.status IN ('20', '30') GROUP BY image.source_id ORDER BY source.source_id"
        res2 = self.app.db.fetch_sql_all(sql2)
        src_img_count = {}
        for (src_id, count) in res2:
            src_img_count[src_id] = count

        #print(src_img_count, '---')
        pb_style = ttk.Style()
        pb_style.configure("green.Horizontal.TProgressbar", foreground='#5eba7d', background='#6fca64')
        for i in res:
            self.state['num_queue_process'] += 1
            frame = tk.LabelFrame(self, text=i[3], width='600')
            label_text = '--'
            percent_text = '0 %'
            total = src_img_count.get(i[0], 0) #i[4]
            #print (i[0], total)
            value = round(((total-i[8])/total) * 100.0)
            if i[6] == '20':
                label_text = f'等待上傳'
                percent_text = f'{value} % ({total-i[8]}/{total})'
            if i[6] == '30':
                label_text = f'上傳中'
                percent_text = f'{value} % ({total-i[8]}/{total})'
            #elif i[6] == '40':
            #    label_text = '已上傳完成'
            #    percent_text = '100 %'
            #    value = 100

            label = ttk.Label(frame, text=label_text)
            label.grid(row=0, column=0, sticky='nw', padx=4)
            pb_percent_label = ttk.Label(frame, text=percent_text)
            pb_percent_label.grid(row=0, column=0, sticky='ne', padx=4)
            pb = ttk.Progressbar(frame, orient=tk.HORIZONTAL, length=600, mode='determinate', value=value, style='green.Horizontal.TProgressbar', maximum=100)
            pb.grid(row=1, column=0, padx=4, pady=4)
            frame.grid(pady=10)

            item = {
                'frame': frame, # for destroy next process
                'progressbar': pb,
                'label': label,
                'percent_label': pb_percent_label,
                'status': i[6],
                'source_id': i[0],
                'value': value,
                'total': total,
                'current_text': '',
                'count': total-i[8], # num of already uploaded
                #'num_not_uploaded': i[8],
                'enable_upload': False,
                'uploaded': [],
                'process_step': 0, # 0: init, 1: processing, 2: done
            }

            if descr := i[7]:
                d = json.loads(descr)
                if dep_id := d.get('deployment_id', ''):
                    if item['status'] == '20':
                        item['enable_upload'] = True
            self.state['upload_map'][i[0]] = item


        '''
        if is_init:
            for source_id, item in self.state['upload_map'].items():
                if item['status'] in ['20', '30']:
                    #self.queue.put(item)
                    self.state['upload_list'].append({
                        'data': item,
                        'status': '',
                    })
        '''
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

    def _asyncio_thread(self, item):
        print ('thread source:', item)
        self.async_loop.run_until_complete(self.do_uploads(item))
        self.state['doing'] = False
        print ('thread complete!!')

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
