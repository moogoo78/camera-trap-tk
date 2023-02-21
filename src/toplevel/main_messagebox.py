import tkinter as tk
from tkinter import ttk

import time
import threading
import logging

class MainMessagebox(tk.Toplevel):
    def __init__(self, parent, app, deployment_journal_id):
        super().__init__(parent, bg='#eeeeee')

        self.app = app
        self.deployment_journal_id = deployment_journal_id
        self.protocol('WM_DELETE_WINDOW', self.quit)

        # layout
        self.geometry('200x100')
        self.title('server processing...')
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=0)

        self.label = ttk.Label(
            self,
            text='上傳文字處理中...'
        )
        self.label.grid(row=0, column=0, sticky='nsew', padx=10, pady=10)
        self.btn = ttk.Button(
            self,
            text='關閉',
            command=self.destroy,
            state=tk.DISABLED
        )
        self.btn.grid(row=1, column=0, sticky='nsew', padx=10, pady=10)

        t = threading.Thread(target=self.check_task, args=('bar',))
        t.start()

    def quit(self):
        self.destroy()
        logging.debug('server process annotation not finished')

    def check_task(self, b):
        img_ids = {}
        for i in range(0, 65): # wait: ~=300s (1*5 + 3*5 + 5*55)
            if i < 5:
                time.sleep(1)
            elif i >= 5 and i < 10:
                time.sleep(3)
            else:
                time.sleep(5)

            logging.debug(f'wait server process image annotation: {i}')

            if res := self.app.server.check_upload_history(self.deployment_journal_id):
                if err := res['error']:
                    tk.messagebox.showerror('server error', err)

                elif res['json'].get('status', '') == 'uploading':
                    #res = self.app.server.post_upload_history(self.deployment_journal_id, 'uploading')
                    if img_ids := res['json'].get('saved_image_ids', None):
                        #self.app.contents['main'].handle_upload_start(self.deployment_journal_id, img_ids)
                        self.app.contents['main'].tmp_uploading = {
                            'deployment_journal_id': self.deployment_journal_id,
                            'saved_image_ids': img_ids,

                        }
                        self.app.contents['main'].event_generate('<<event_action>>', when='tail')
                        self.quit()
                        return

        self.btn['state'] = tk.NORMAL
        self.label['text'] = '文字上傳未完成'
