import tkinter as tk
from tkinter import (
    ttk,
)
from tkinter import filedialog
from pathlib import Path
import csv
import threading
from collections import deque
import logging
from datetime import datetime
import time
import json

from utils import check_file_type

ERROR_MAP = {
    'NOT_EXIST': '照片不存在',
    'INVALID_FORMAT': '文字標註檔格式不符',
    'UNSUPPORT_TYPE': '不支援的格式',
    'DATETIME_ERROR': '日期時間格式錯誤',
    'UNCONTROLLED_TERM': '內容非控制詞彙',
}
HEADER_MAP = {
    'filename': {
        'label': '檔名',
        'required': True,
    },
    'datetime': {
        'label': '日期時間',
        'required': True,
    },
    'annotation_species': {
        'label': '物種',
        'required': True,
    },
    'annotation_lifestage': {
        'label': '年齡',
    },
    'annotation_sex': {
        'label': '性別',
    },
    'annotation_antler': {
        'label': '角況',
    },
    'annotation_remark': {
        'label': '備註',
    },
    'annotation_animal_id': {
        'label': '個體ID',
    }
}

class ImportData(tk.Toplevel):

    def __init__(self, parent, *args, **kwargs):
        #tk.Frame.__init__(self, parent, *args, **kwargs)
        super().__init__(parent, bg='#eeeeee')
        self.app = parent

        self.protocol('WM_DELETE_WINDOW', self.quit)
        self.geometry('760x300')
        self.title('匯入')
        #self.wm_attributes('-topmost', True)
        #self.lift()
        #self.focus_set()
        self.grab_set()

        self.layout()

        self.image_map = {} # to insert db schema
        self.import_deque = deque() # control import action

    def layout(self):
        s = ttk.Style()
        #s.configure('ctl.TFrame', background='maroon')
        #s.configure('res.TFrame', background='green')

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # container -> control/result
        container = ttk.Frame(self, padding=10)
        container.grid(row=0, column=0, sticky='nwes')
        container.grid_rowconfigure(0, weight=0)
        container.grid_rowconfigure(1, weight=1)
        container.grid_columnconfigure(0, weight=1)

        control_frame = ttk.Frame(container)
        control_frame.grid(row=0, column=0, sticky='nwes')
        result_frame = ttk.Frame(container)
        result_frame.grid(row=1, column=0, sticky='nwes')

        ## control frame
        control_frame.grid_columnconfigure(0, weight=0)
        control_frame.grid_columnconfigure(1, weight=1)
        control_frame.grid_columnconfigure(2, weight=0)

        ### select annotation file
        ttk.Label(
            control_frame,
            text='文字標註檔',
            font=self.app.get_font('display-4'),
        ).grid(row=0, column=0, sticky='we', padx=8, pady=8)

        self.file_path = tk.StringVar(control_frame)
        ttk.Entry(
            control_frame,
            textvariable=self.file_path,
            state='readonly'
        ).grid(row=0, column=1, sticky='we', padx=2)

        ttk.Button(
            control_frame,
            text='選取檔案',
            command=self.open_annotation_file
        ).grid(row=0, column=2, sticky='e', padx=8)

        ## select folder
        folder_label = ttk.Label(
            control_frame,
            text='照片資料夾',
            font=self.app.get_font('display-4'),
        ).grid(row=1, column=0, sticky='e', padx=8, pady=8)

        self.dir_path = tk.StringVar(control_frame)
        dir_entry = ttk.Entry(
            control_frame,
            textvariable=self.dir_path,
            state='readonly'
        ).grid(row=1, column=1, sticky='we', padx=2)

        ttk.Button(
            control_frame,
            text='選取資料夾',
            command=self.open_image_dir
        ).grid(row=1, column=2, sticky='we', padx=8)

        self.progressbar_title = ttk.Label(
            control_frame,
            text=''
        )
        self.progressbar_title.grid(row=2, column=1, sticky='wes', pady=0)

        self.progressbar_label = ttk.Label(
            control_frame,
            text='進度',
            font=self.app.get_font('display-4'),
        )
        self.progressbar_label.grid(row=3, column=0, sticky='e', padx=8)
        self.progressbar = ttk.Progressbar(control_frame, orient=tk.HORIZONTAL, length=500, value=0, mode='determinate', maximum=100)
        self.progressbar.grid(row=3, column=1, sticky='we')

        ttk.Button(
            control_frame,
            text='匯入',
            command=self.on_import
        ).grid(row=3, column=2, sticky='we', padx=8, pady=(0, 8))


        ### result frame
        result_frame.grid_rowconfigure(0, weight=1)
        result_frame.grid_columnconfigure(0, weight=1)

        self.treeview = ttk.Treeview(result_frame, columns=('error_type', 'description'), show='headings')
        self.treeview.heading('error_type', text='錯誤')
        self.treeview.heading('description', text='描述')
        self.treeview.column('error_type', width=120,stretch=False)

        self.treeview.grid(row=1, column=0, sticky='nsew')


    def on_import(self):
        file_path = self.file_path.get()
        if not file_path:
            tk.messagebox.showwarning('注意', '請選檔案')
            return

        image_dir_path = self.dir_path.get()
        if not image_dir_path:
            tk.messagebox.showwarning('注意', '請選資料夾')
            return

        # cast str to Path
        file_path = Path(file_path)
        image_dir_path = Path(image_dir_path)

        # reset error_list
        self.treeview.delete(*self.treeview.get_children())


        src = self.app.source # source.py is much like a helper

        result = src.check_import_folder(image_dir_path)
        if err_msg := result.get('error'):
            tk.messagebox.showinfo('注意', err_msg)
            return

        # check annotation contents

        species_choices = self.app.config.get('AnnotationFieldSpecies', 'choices')
        antler_choices = self.app.config.get('AnnotationFieldAntler', 'choices')
        sex_choices = self.app.config.get('AnnotationFieldSex', 'choices')
        lifestage_choices = self.app.config.get('AnnotationFieldLifeStage', 'choices')
        bird_choices = self.app.config.get('AnnotationSpeciesExtra', 'birds')

        CONTROLLED_TERMS = {
            '物種': species_choices.split(',') + bird_choices.split(','),
            '角況': antler_choices.split(','),
            '性別': sex_choices.split(','),
            '年齡': lifestage_choices.split(','),
        }

        is_utf8 = True
        csvfile = None
        try:
            with open(file_path, encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile, delimiter=',')
                headers = set(reader.fieldnames)
        except UnicodeDecodeError as err:
            logging.info('open csv as utf-8 encoding error: {err}')
            is_utf8 = False
        finally:
            if is_utf8 is True:
                csvfile = open(file_path, encoding='utf-8')
                logging.info(f'import {file_path}, use utf-8 encoding')
            else:
                csvfile = open(file_path) # platform dependent
                logging.info(f'import {file_path}, use platform dependent encoding (big5)')

        if csvfile:
            #next(reader)
            reader = csv.DictReader(csvfile, delimiter=',')
            headers = set(reader.fieldnames)
            req_headers = [v['label'] for k,v in HEADER_MAP.items() if v.get('required', False)]
            req_headers = set(req_headers)
            if req_headers != req_headers.intersection(headers):
                lack_headers = req_headers - req_headers.intersection(headers)
                err_msg = (ERROR_MAP['INVALID_FORMAT'], f'缺少欄位: {lack_headers}')
                self.treeview.insert('', tk.END, values=err_msg)
                #tk.messagebox.showerror('錯誤', ERROR_MAP['INVALID_FORMAT'])
            else:
                annotation_header = []
                for k, v in HEADER_MAP.items():
                    if k[:11] == 'annotation_':
                        annotation_header.append((k[11:], v['label']))

                for index, row in enumerate(reader):
                    index1 = index + 1
                    file_path = Path(image_dir_path, row['檔名'])
                    if not file_path.exists():
                        err_msg = (ERROR_MAP['NOT_EXIST'], file_path)
                        self.treeview.insert('', tk.END, values=err_msg)
                    else:
                        file_type = check_file_type(file_path)
                        if file_type not in ['video', 'image']:
                            err_msg = (ERROR_MAP['UNSUPPORT_TYPE'], file_path)
                            self.treeview.insert('', tk.END, values=err_msg)

                        annotation = {}
                        for col_key, col_label in annotation_header:
                            if value := row.get(col_label):
                                if terms := CONTROLLED_TERMS.get(col_label):
                                    if value in terms:
                                        annotation[col_key] = value
                                    else:
                                        err = f'#{index1}: [{col_label}] {value}, 允許詞彙: {terms}'
                                        err_msg = (ERROR_MAP['UNCONTROLLED_TERM'], err)
                                        self.treeview.insert('', tk.END, values=err_msg)

                                else:
                                    annotation[col_key] = value

                        try:
                            ts = datetime.strptime(row['日期時間'], '%Y-%m-%d %H:%M:%S').timestamp()
                        except ValueError as value_err:
                            err_msg = (ERROR_MAP['DATETIME_ERROR'], f"#{index1}, {row['日期時間']}")
                            self.treeview.insert('', tk.END, values=err_msg)

                        name = row['檔名']
                        if name not in self.image_map:
                            self.image_map[name] = {
                                '_file_path': file_path,
                                '_file_type': file_type,
                                'filename': name,
                                'timestamp': int(ts),
                                'annotation': []
                            }
                        self.image_map[name]['annotation'].append(annotation)


        if len(self.treeview.get_children()) > 0:
            return

        # start process import
        if num_images := len(self.image_map):
            source_id = src.create_import_directory(num_images, image_dir_path, '')

            #self.app.contents['folder_list'].refresh_source_list()
            foo_th = threading.Thread(
                target=self.add_annotation_file_worker,
                args=(src, source_id, self.image_map, image_dir_path))
            foo_th.start()
            #foo_th.join() # this cause app hang... why?

        csvfile.close()


    def add_annotation_file_worker(self, src, source_id, image_map, folder_path):
        self.import_deque.append(source_id)
        sql_list = []
        image_count = 0
        folder_date_range = [0, 0]
        num_images = len(image_map)
        self.progressbar['maximum'] = num_images
        for i, data in enumerate(src.gen_import_file2(source_id, image_map, folder_path)):
            image_count += 1

            ts = data['timestamp']
            if folder_date_range[0] == 0 or folder_date_range[1] == 0:
                folder_date_range[0] = ts
                folder_date_range[1] = ts
            else:
                if ts < folder_date_range[0]:
                    folder_date_range[0] = ts
                elif ts > folder_date_range[1]:
                    folder_date_range[1] = ts


            ts_now = int(time.time())

            if data['_file_type'] == 'image':
                if not data['_img']:
                    tk.messagebox.showerror('error', f"{data['path']} 檔案損毀無法讀取")
                    continue

                sql = "INSERT INTO image (path, name, timestamp, timestamp_via, status, hash, annotation, changed, exif, source_id, sys_note, media_type) VALUES ('{}','{}', {}, '{}', '{}', '{}', '{}', {}, '{}', {}, '{}', 'image')".format(
                    data['_file_path_posix'],
                    data['filename'],
                    ts,
                    'csv',
                    '10',
                    data['_img_hash'],
                    json.dumps(data['annotation']),
                    ts_now,
                    json.dumps(data['_exif']),
                    source_id,
                    '{}')
            elif data['_file_type'] == 'video':
                sql = "INSERT INTO image (path, name, timestamp, timestamp_via, status, hash, annotation, changed, source_id, sys_note, media_type) VALUES ('{}','{}', {}, '{}', '{}', '{}', '{}', {}, {}, '{}', 'video')".format(
                    data['_file_path_posix'],
                    data['filename'],
                    ts,
                    'csv',
                    '10',
                    '',
                    '[]',
                    ts_now,
                    source_id,
                    '{}',
                )
            sql_list.append(sql)

            # update progressbar
            self.progressbar['value'] = i+1
            self.progressbar_title['text'] = '{} ({}/{})'.format(data['filename'], i+1, num_images)


        sql_date_and_count = f'UPDATE source SET trip_start={folder_date_range[0]}, trip_end={folder_date_range[1]}, count={image_count} WHERE source_id={source_id}'
        sql_list.append(sql_date_and_count)

        #self.done_import(sql_list, source_id)
        self.app.after(100, lambda: self.done_import(sql_list, source_id))

    def done_import(self, sql_list, source_id):
        done_source_id = self.import_deque.popleft()

        self.app.source.update_status(source_id, 'DONE_IMPORT')

        for i in sql_list:
            #print(i)
            self.app.db.exec_sql(i)
        self.app.db.commit()

        self.quit()
        self.app.on_folder_list()

        tk.messagebox.showinfo('成功', '匯入成功')


    def open_annotation_file(self):
        annotation_file = filedialog.askopenfilename(
            title='選取標註檔',
            filetypes = (('csv','*.csv'),('tsv', '*.txt'), ('All files', '*.*'))
        )

        if not annotation_file:
            return False

        self.file_path.set(Path(annotation_file))


    def open_image_dir(self):
        directory = filedialog.askdirectory()
        if not directory:
            return False

        self.dir_path.set(Path(directory))


    def quit(self):
        if len(self.import_deque) > 0:
            logging.info('importing file, cannot quit')
        else:
            self.destroy()
            self.app.toplevels['import_data'] = None
