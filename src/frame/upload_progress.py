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

        self.STATE_INIT = 0
        self.STATE_PENDING = 1
        self.STATE_RUNNING = 2
        self.STATE_PAUSE = 3
        self.STATE_DONE = 4

        self.LABEL_PLAY = '重啟上傳'
        self.LABEL_PAUSE = '暫停上傳'

        self.app = parent
        self._layout()

        # self.async_loop = asyncio.get_event_loop()
        self.is_running = False
        self.progress_bars = {} # don't how to get canvas window widget to configure

        self.source_list = []
        self.has_pending = False

        self.action_queue = Queue()

        self.bind('<<event_action>>', self.event_action_callback)

        self.refresh()

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

        # self.foo = ttk.Button(
        #     self.canvas,
        #     text='terminate',
        #     command=self.handle_foo)
        # self.canvas.create_window(
        #     150,
        #     150,
        #     width=100,
        #     window=self.foo
        # )

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

    def fetch_source(self):
        prev_states = {}
        for row in self.source_list:
            prev_states[row['source_data'][0]] = row['state']

        self.source_list = []
        rows = self.app.db.fetch_sql_all("SELECT * FROM source WHERE status LIKE 'b%' ORDER BY upload_created") # wait... start media upload
        #rows = self.app.db.fetch_sql_all("SELECT * FROM source ORDER BY upload_created") # wait... start media upload

        for source_data in rows:
            # TODO
            sql_images = f"SELECT image_id, path, name, upload_status, object_id, server_image_id FROM image WHERE source_id={source_data[0]} AND upload_status != '200' ORDER BY image_id"
            #sql_images = f"SELECT image_id, upload_status FROM image WHERE source_id={source_data[0]} ORDER BY image_id"
            result_images = self.app.db.fetch_sql_all(sql_images)

            self.source_list.append({
                'source_data': source_data,
                'images': result_images,
                'progressbar': None,  # widget
                'action_button': None,  # widget
                'state': prev_states[source_data[0]] if source_data[0] in prev_states else self.STATE_INIT,
                'thread': None,
            })


    def refresh(self):
        logging.debug('~ refresh ~')

        start_x = 124 # begin
        start_y = 124
        shift_x = 0 # shift
        shift_y = 0

        # clear
        self.canvas.delete('item')
        # some progressbar, or button not delete by tags
        #for i in self.canvas.winfo_children():
        #    i.destroy()

        for row in self.source_list:
            if pb := row['progressbar']:
                pb.destroy()
            if btn := row['action_button']:
                btn.destroy()

        self.fetch_source() # update source_list

        self.progress_bars = {}

        for i, row in enumerate(self.source_list):
            # print(row)
            self._render_box(row, start_x, start_y, shift_x, shift_y)

            shift_x += 316  # 300 + 16
            if i > 0 and (i+1) % 3 == 0:
                shift_y += 162  # 150 + 12
                shift_x = 0

    def _render_box(self, row, start_x, start_y, shift_x, shift_y):
        r = row['source_data']
        source_id = r[0]
        total = r[4]
        num = len(row['images'])

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
        progressbar_value = total - num

        # different state display
        status_text = '資料夾上傳中...'
        # print('!!!',row['source_data'][6], row['state'])
        if row['source_data'][6] == self.app.source.STATUS_DONE_UPLOAD:
            status_text = '資料夾上傳完畢'
            button_text = '確認並歸檔'
            button_cmd = lambda source_id=source_id: self.handle_archive(source_id)
        elif row['state'] in [self.STATE_PAUSE, self.STATE_INIT]:
            button_text = self.LABEL_PLAY

            button_cmd = lambda source_id=source_id: self.handle_start(source_id)
        else:
            button_text = self.LABEL_PAUSE
            button_cmd = lambda source_id=source_id: self.handle_stop(source_id)

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
                text='{:.2f}%'.format(((progressbar_value) / total) * 100.0),
                font=(self.app.app_font, 16),
                fill=self.app.app_primary_color,
                tags=('item', f'{source_id}-text'))

            pb = ttk.Progressbar(self.canvas, orient=tk.HORIZONTAL, length=122, value=progressbar_value, mode='determinate', maximum=total)
            #pb.grid(row=0, column=0)
            self.progress_bars[r[0]] = pb #TODO
            row['progressbar'] = pb
            tmp = self.canvas.create_window(
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
            text=f'({progressbar_value}/{total})',
            font=(self.app.app_font, 16),
            fill='#464646',
            tags=('item', f'{source_id}-step'))

        gap += 22
        btn = ttk.Button(
            self.canvas,
            text=button_text,
            command=button_cmd)
        row['action_button'] = btn
        self.canvas.create_window(
            x+20,
            gap+4,
            width=261,
            height=36,
            window=btn,
            anchor='nw',
            tags=('item')
        )

    def _find_source(self, source_id):
        for i, v in enumerate(self.source_list):
            if v['source_data'][0] == source_id:
                return v
        return None

    def handle_archive(self, source_id):
        print('on archive', source_id)

    # def handle_foo(self):
    #     if not self.is_uploading:
    #         print('play')
    #         self.foo['text'] = 'terminate'
    #         self.is_uploading = True
    #         self.canvas.update_idletasks()
    #         '''self.ut = UploadTask()
    #         t = threading.Thread(target=self.ut.run, args=(10, ))
    #         t.start()
    #         #.terminate()
    #         t.join()
    #         print('finally!!!')
    #         #self.is_uploading = False
    #         #self.foo['text'] = 'play'
    #         '''
    #     else:
    #         self.foo['text'] = 'play'
    #         self.canvas.update_idletasks()
    #         self.is_uploading = False
    #         print('term')
    #         #self.upload_task.terminate()

    def handle_start(self, source_id):
        logging.info(f'click upload: {source_id}')
        self.app.source.update_status(source_id, 'MEDIA_UPLOAD_PENDING')
        self.refresh()
        item = self._find_source(source_id)
        item['action_button']['state'] = tk.DISABLED
        item['state'] = self.STATE_PENDING

        if not self.check_running():
            item = self._find_source(source_id)
            item['action_button'].configure(
                text=self.LABEL_PAUSE,
                command=lambda source_id=source_id: self.handle_stop(source_id),
                state=tk.NORMAL)

            item['state'] = self.STATE_RUNNING
            self.app.source.update_status(source_id, 'MEDIA_UPLOADING')
            t = threading.Thread(target=self.upload_task, args=(item, ))
            item['thread'] = t
            t.start()


    def handle_stop(self, source_id):
        logging.info(f'click pause: {source_id}')
        item = self._find_source(source_id)
        item['action_button'].configure(
            text=self.LABEL_PLAY,
            command=lambda source_id=source_id: self.handle_start2(source_id))
        item['state'] = self.STATE_PAUSE

    def check_pending(self):
        has_pending = False
        for item in self.source_list:
            if item['state'] == self.STATE_PENDING:
                has_pending = True

        return has_pending

    def check_running(self):

        for item in self.source_list:
            logging.debug(f"source_id: {item['source_data'][0]}, state: {item['state']}, thread: {item['thread']}")

            if item['state'] == self.STATE_PENDING:
                self.has_pending = True

            if item['thread']:
                logging.debug(f"thread is_alive: {item['thread'].is_alive()}")
            if item['state'] == self.STATE_RUNNING:
                logging.debug(f"return True")
                return True
        logging.debug(f"return False")
        return False

    def upload_task(self, item):
        print(f"🧵 upload source_id: {item['source_data'][0]}")

        num = len(item['images'])
        source_id = item['source_data'][0]
        counter = 0
        for i, v in enumerate(item['images']):
            if item['state'] == self.STATE_RUNNING:
                print(f'🧵 uploading: {source_id}-{counter}/{num}')
                counter = i + 1
                path = v[1]
                name = v[2]
                object_id = v[4]
                server_image_id = v[5]
                thumb_paths = get_thumb(source_id, name, path, 'all')
                for x, path in thumb_paths.items():
                    object_name = f'{object_id}-{x}.jpg'
                    # print (object_name)
                    # time.sleep(1) # fake upload
                    self.app.source.upload_to_s3(str(path), object_name)
                self.action_queue.put({
                    'type':'update_image',
                    'source_id': source_id,
                    'image_id': v[0],
                    'counter': counter,
                })
                self.event_generate('<<event_action>>', when='tail')

                self.app.server.post_image_status({
                    # 'file_url': f'{uploaded_object_id}.jpg',
                    'has_storage': 'Y',
                    'pk': server_image_id,
                })

            else:
                print(f'🧵 skip {source_id}-{counter}/{num}')

        logging.debug(f'🧵 done source: {source_id}')
        self.action_queue.put({
            'type': 'done_source',
            'source_id': source_id,
            'is_complete': True if counter == num else False,
            'name': source_id, #data['source_data'][3],
        })
        self.event_generate('<<event_action>>', when='tail')

    def event_action_callback(self, event):
        '''
        do actions: update database, refresh layout
        '''
        for _ in range(self.action_queue.qsize()):
            action = self.action_queue.get_nowait()
            # print(f'do : {action}' )
            source_id = action['source_id']
            item = self._find_source(source_id)
            if action['type'] == 'update_image':
                image_id = action['image_id']
                source_id = action['source_id']
                counter = action['counter']

                sql = f"UPDATE image SET upload_status='200' WHERE image_id={image_id}"
                res = self.app.db.exec_sql(sql, True)

                # may refresh, changed the images num
                has_pending = self.check_pending()
                num_count = 0
                if has_pending is True:
                    sql_count = f"SELECT COUNT(*) FROM image WHERE source_id={source_id} AND upload_status != '200' ORDER BY image_id"
                    res_count = self.app.db.fetch_sql(sql_count)
                    num_count = res_count[0]

                # update layout
                item = self._find_source(source_id)
                total = item['source_data'][4]

                if has_pending:
                    num = num_count
                    value = total - num
                else:
                    num = len(item['images'])
                    value = total - num + counter

                # print('***', total, num, counter)
                # update layout
                item['progressbar']['value'] = value
                self.canvas.itemconfigure(f'{source_id}-text', text='{:.2f}%'.format((value / total) * 100.0))
                self.canvas.itemconfigure(f'{source_id}-step', text=f'({value}/{total})')

                # update main table layout
                main = self.app.contents['main']
                row_keys = main.data_helper.get_image_row_keys(image_id)
                for k in row_keys:
                    main.data_helper.set_status_display(k, '200')
                    main.data_grid.main_table.render()

            elif action['type'] == 'done_source':
                source_id = action['source_id']
                is_complete = action['is_complete']
                name = action['name']
                deployment_journal_id = item['source_data'][12]
                if is_complete:
                    self.app.source.update_status(source_id, 'DONE_UPLOAD')
                    tk.messagebox.showinfo('info', f'資料夾 {name}: 上傳成功')
                else:
                    if item['state'] != self.STATE_PAUSE:
                        self.app.source.update_status(source_id, 'MEDIA_UPLOAD_FAILED')
                        tk.messagebox.showinfo('info', f'資料夾 {name}: 上傳照片不完整')

                # send finish upload status to server

                self.app.server.post_upload_history(deployment_journal_id, 'finished')

                if item['state'] != self.STATE_PAUSE:
                    item['state'] = self.STATE_DONE

                item['thread'] = None

                if is_complete:
                    self.try_next_source()

                #self.refresh()

    def try_next_source(self):
        logging.debug('try next')
        no_pending = True
        for item in self.source_list:
            # print(item['source_data'][0], item['state'])
            if item['state'] == self.STATE_PENDING:
                no_pending = False
                self.handle_start(item['source_data'][0])

        if no_pending:
            logging.info('no pending, do refresh')
            self.refresh()

    def terminate_upload_task(self):
        for item in self.source_list:
            if item['state'] in [self.STATE_RUNNING, self.STATE_PAUSE]:
                item['state'] = self.STATE_INIT

