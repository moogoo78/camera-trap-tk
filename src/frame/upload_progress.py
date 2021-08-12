import tkinter as tk
from tkinter import (
    ttk,
)
import queue
import logging
import json

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
        self.start_button.grid()

        self.stop_button = ttk.Button(
            self,
            text='stop',
            command=self.stop_upload
        )
        self.stop_button.grid()

        self.process_limit = 2 # conf
        self.queue = queue.Queue()
        self.process_queue = queue.Queue() # control process sequence and done
        self.state = {
            'status': 'stop',
            'uploading': {},
            'process_count': 0,
            'process_end': self.process_limit,
        }
        self.refresh()

    def refresh(self):
        # reset list
        if uplist:= self.state['uploading']:
            for i in uplist:
                i['frame'].destroy()
            self.state['uploading'] = []

        # get all source from db
        sql = "SELECT source.*, COUNT(*) AS img_count FROM image LEFT JOIN source ON image.source_id = source.source_id WHERE source.status != '10' AND (image.upload_status is NULL OR image.upload_status != 44) GROUP BY image.source_id ORDER BY source.status, source.source_id"
        res = self.app.db.fetch_sql_all(sql)

        # 不信任 i[4], 重新 count
        sql2 = "SELECT source.source_id, COUNT(*) AS img_all_count FROM image LEFT JOIN source ON image.source_id = source.source_id WHERE source.status != '10' GROUP BY image.source_id ORDER BY source.status, source.source_id"
        res2 = self.app.db.fetch_sql_all(sql2)
        src_img_count = {}
        for (src_id, count) in res2:
            src_img_count[src_id] = count

        #print(src_img_count, '---')
        pb_style = ttk.Style()
        pb_style.configure("green.Horizontal.TProgressbar", foreground='#5eba7d', background='#6fca64')
        #count = 0
        for i in res:
            #print (i)
            #count += 1
            frame = tk.LabelFrame(self, text=i[3], width='600')
            label_text = '--'
            percent_text = '0 %'
            total = src_img_count.get(i[0], 0) #i[4]
            #print (i[0], total)
            value = round(((total-i[8])/total) * 100.0)
            if i[6] == '20':
                label_text = f'等待上傳:{i[8]} {total}'
                percent_text = f'{value} %'
            if i[6] == '30':
                label_text = f'上傳中: {i[8]} {total}'
                percent_text = '{value} %'
            elif i[6] == '40':
                label_text = '已上傳完成'
                percent_text = '100 %'
                value = 100

            label = ttk.Label(frame, text=label_text)
            label.grid(row=0, column=0, sticky='nw', padx=4)
            pb_percent_label = ttk.Label(frame, text=percent_text)
            pb_percent_label.grid(row=0, column=0, sticky='ne', padx=4)
            pb = ttk.Progressbar(frame, orient=tk.HORIZONTAL, length=600, mode='determinate', value=value, style='green.Horizontal.TProgressbar', maximum=100)
            pb.grid(row=1, column=0, padx=4, pady=4)
            frame.progress_bar = pb
            frame.grid(pady=10)

            self.state['uploading'][i[0]] = {
                'frame': frame,
                'pb': pb,
                'state': i[6],
                'source_id': i[0],
                'value': value,
                'total': total,
                'count': total-i[8],
            }

            deployment_id = ''
            if descr := i[7]:
                d = json.loads(descr)
                deployment_id = d.get('deployment_id', '')

            if i[6] in ['20', '30']:
                data = {
                    'image_list': [],
                    'source': i,
                    'deployment_id': '',
                }
                self.queue.put(data)

    def create_upload_progress(self, data):
        source_id = data['source'][0]
        source_status = data['source'][6]
        if source_status == '10':
            sql = f"UPDATE source SET status='20' WHERE source_id={source_id}"
            self.app.db.exec_sql(sql, True)

        self.queue.put(data)

    def start_upload(self):
        self.state['status'] = 'start'
        self.process_upload()
        self.polling()

    def stop_upload(self):
        self.state['status'] = 'stop'

    def process_upload(self):
        #print ('process', self.queue.qsize())
        if self.queue.qsize() <= 0:
            return False

        process_num = min(self.queue.qsize(), self.process_limit)
        logging.info(f'process_upload: {process_num} x thread')
        self.state['process_end'] = process_num
        for _ in range(process_num):
            data = self.queue.get()
            source_id = data['source'][0]

            task = UploadTask(
                f'upload-{source_id}',
                self.process_queue,
                self.state['uploading'],
                data,
                {},
                self.app.db
            )
            task.start()

    def polling(self):
        if self.state['status'] != 'start':
            return False

        #print ('render progress UI ~~', self.queue.qsize())
        # update GUI
        for k,v in self.state['uploading'].items():
            print ('polling', k, v)
            count = v['count']
            total = v['total']
            v['pb']['value'] = round((count/total) * 100.0)

        # control process
        if self.process_queue.qsize() == self.state['process_end']:
            if self.queue.qsize() > 0:
                # continue fetch next task
                print ('another fetch')
                self.process_queue = queue.Queue()
                self.process_upload()
            else:
                self.state['status'] = 'stop'

        self.app.after(1000, self.polling)
