import threading
from datetime import datetime
import logging
import re

import tkinter as tk
from tkinter import (
    ttk,
)

from tkinter import filedialog as fd
from tkinter.messagebox import showinfo

from PIL import (
    Image,
    ImageTk
)

from utils import create_round_polygon


class FolderList(tk.Frame):

    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.app = parent

        self.folder_importing = {}

        self.layout()

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

        # TODO, scroll limit, length, place
        self.scrollbar = ttk.Scrollbar(self, orient=tk.VERTICAL, command=self.canvas.yview)
        self.scrollbar.grid(row=0, column=1, sticky='ewns')
        self.canvas.config(yscrollcommand=self.scrollbar.set)

        #self.bg = ImageTk.PhotoImage(file='./assets/folder_list_vector.png')
        self.fresh_icon = ImageTk.PhotoImage(file='./assets/source_status_fresh.png')
        self.done_icon = ImageTk.PhotoImage(file='./assets/source_status_done.png')
        self.uploading_icon = ImageTk.PhotoImage(file='./assets/source_status_uploading.png')
        self.failed_icon = ImageTk.PhotoImage(file='./assets/source_status_failed.png')
        self.override_icon = ImageTk.PhotoImage(file='./assets/source_status_override.png')
        self.editing_icon = ImageTk.PhotoImage(file='./assets/source_status_editing.png')
        self.override_icon = ImageTk.PhotoImage(file='./assets/source_status_override.png')
        self.status_all_icon = ImageTk.PhotoImage(file='./assets/folder-list-status-all.png')
        self.status_pending_icon = ImageTk.PhotoImage(file='./assets/folder-list-status-pending.png')
        self.status_uploaded_icon = ImageTk.PhotoImage(file='./assets/folder-list-status-uploaded.png')

        # hide background vector
        # self.canvas.create_image(
        #     620,
        #     330,
        #     image=self.bg,
        #     anchor='nw',
        # )
        self.canvas.create_text(
            50,
            20,
            anchor='nw',
            text='現有資料夾',
            font=self.app.get_font('display-2'),
            fill=self.app.app_primary_color,
        )

        self.canvas.create_image(
            580,
            20,
            anchor='nw',
            image=self.status_pending_icon,
            tags=('status_pending'))

        self.canvas.create_image(
            745,
            20,
            anchor='nw',
            image=self.status_uploaded_icon,
            tags=('status_uploaded'))

        self.canvas.create_image(
            910,
            20,
            anchor='nw',
            image=self.status_all_icon,
            tags=('status_all'))

        self.canvas.tag_bind(
            'status_pending',
            '<Button-1>',
            lambda _: self.refresh_source_list('pending'))
        self.canvas.tag_bind(
            'status_uploaded',
            '<Button-1>',
            lambda _: self.refresh_source_list('uploaded'))
        self.canvas.tag_bind(
            'status_all',
            '<Button-1>',
            lambda _: self.refresh_source_list('all'))

    def exec_sql_list(self, image_sql_list, source_id):
        for i in image_sql_list:
            self.app.db.exec_sql(i)
        self.app.db.commit()

        self.app.source.update_status(source_id, 'DONE_IMPORT')
        self.refresh_source_list()
        showinfo(message='完成匯入資料夾')

    def add_folder_worker(self, src, source_id, image_list, folder_path):
        image_sql_list = []
        folder_date_range = [0, 0]
        for i, (data, sql) in enumerate(src.gen_import_file(source_id, image_list, folder_path)):
            image_sql_list.append(sql)
            # print (data)
            if folder_date_range[0] == 0 or folder_date_range[1] == 0:
                folder_date_range[0] = data['timestamp']
                folder_date_range[1] = data['timestamp']
            else:
                if data['timestamp'] < folder_date_range[0]:
                    folder_date_range[0] = data['timestamp']
                elif data['timestamp'] > folder_date_range[1]:
                    folder_date_range[1] = data['timestamp']

            #print(sql, self.folder_importing)
            if source_id in self.folder_importing:
                self.folder_importing[source_id]['prog_bar']['value'] = i+1
                self.folder_importing[source_id]['label']['text'] = '{} ({}/{})'.format(image_list[i][0].name, i+1, len(image_list))

        sql_date_range = f'UPDATE source SET trip_start={folder_date_range[0]}, trip_end={folder_date_range[1]} WHERE source_id={source_id}'
        image_sql_list.append(sql_date_range)
        self.app.after(100, lambda: self.exec_sql_list(image_sql_list, source_id))

    def add_folder(self):
        directory = fd.askdirectory()
        if not directory:
            return False

        src = self.app.source
        folder_path = src.get_folder_path(directory)

        if not folder_path:
            tk.messagebox.showinfo('info', '已經加過此資料夾')
            return False

        # check folder name syntax
        parsed_format = None
        result = src.check_folder_name_format(folder_path.name)
        logging.info(result)

        if err := result.get('error'):
            tk.messagebox.showerror('注意', f'"{folder_path.name}" 目錄格式不符: {err}\n\n[相機位置標號-YYYYmmdd]\n 範例: HC04-20190304-20190506')
            return
        else:
            parsed_format = result

        image_list = src.get_image_list(folder_path)
        if num_images := len(image_list):
            source_id = src.create_import_directory(num_images, folder_path, parsed_format)
            self.refresh_source_list()
            threading.Thread(target=self.add_folder_worker, args=(src, source_id, image_list, folder_path)).start()
        else:
            tk.messagebox.showinfo('info', '資料夾沒有照片')

        # show folder_list
        self.app.on_folder_list()

    def refresh_source_list(self, filter_status='all'):
        logging.debug(f'refresh filter_status: {filter_status}')

        # clear items
        self.canvas.delete('item')
        for _, item in self.folder_importing.items():
            item['prog_bar'].destroy()
            item['label'].destroy()
        self.folder_importing = {}
        row_count = 0

        # get all source from db
        rows = self.app.db.fetch_sql_all('SELECT * FROM source')

        start_x = 124 # begin
        start_y = 124
        shift_x = 0 # shift
        shift_y = 0
        for i, r in enumerate(rows):
            # print(r[0],r[6],  'xxxxxxxxxxxxxxxxxxxx')
            upload_created = datetime.fromtimestamp(r[13]).strftime('%Y-%m-%d %H:%M') if r[13] else ''
            upload_changed = datetime.fromtimestamp(r[14]).strftime('%Y-%m-%d %H:%M') if r[14] else ''
            status_cat = 'other'
            if filter_status != 'all':
                if filter_status == 'uploaded' and \
                   self.app.source.is_done_upload(r[6]) is False:
                    continue
                elif filter_status == 'pending' and \
                     r[6][0] == 'b':
                    continue

            x = start_x + shift_x
            y = start_y + shift_y
            xlist = [x, x + 300, x + 300, x]
            ylist = [y, y, y + 150, y + 150]

            source_tag = f'source_{r[0]}'
            create_round_polygon(
                self.canvas,
                xlist,
                ylist,
                10,
                #width=1,
                #outline="#82B366",
                fill='#FFFFFF',
                tags=('item', source_tag, status_cat),
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
                    x+24,
                    gap-10,
                    anchor='nw',
                    text=title1,
                    font=self.app.get_font('display-4'),
                    fill=self.app.app_primary_color,
                    tags=('item', status_cat, source_tag)
                )
                self.canvas.create_text(
                    x+24,
                    gap+10,
                    anchor='nw',
                    text=title2,
                    font=self.app.get_font('display-4'),
                    fill=self.app.app_primary_color,
                    tags=('item', status_cat, source_tag)
                )
            else:
                self.canvas.create_text(
                    x+24,
                    gap,
                    anchor='nw',
                    text=r[3],
                    font=self.app.get_font('15'),
                    fill=self.app.app_primary_color,
                    tags=('item', status_cat, source_tag)
                )

            gap += 30
            self.canvas.create_text(
                x+24,
                gap,
                anchor='nw',
                text=f'首次上傳時間：{upload_created}',
                font=self.app.get_font('display-4'),
                fill='#464646',
                tags=('item', status_cat, source_tag)
            )
            gap += 22
            self.canvas.create_text(
                x+24,
                gap,
                anchor='nw',
                text=f'上次上傳時間：{upload_changed}',
                font=self.app.get_font('display-4'),
                fill='#464646',
                tags=('item', status_cat, source_tag)
            )
            gap += 22
            self.canvas.create_text(
                x+24,
                gap,
                anchor='nw',
                text=f'上傳狀態：{self.app.source.get_status_label(r[6])}',
                font=self.app.get_font('display-4'),
                fill='#464646',
                tags=('item', status_cat, source_tag)
            )

            if r[6] == self.app.source.STATUS_START_IMPORT:
                # importing progress bar
                box = tk.Frame(self, width=180, background='#FFFFFF')
                prog_bar = ttk.Progressbar(box, orient=tk.HORIZONTAL, length=180, value=0, mode='determinate', maximum=r[4])
                prog_bar.grid(row=0, column=0)
                label = ttk.Label(box, text='', background='#FFFFFF')
                label.grid(row=1, column=0)
                self.folder_importing[r[0]] = {'prog_bar': prog_bar, 'label': label}
                self.canvas.create_window(
                    x+94,
                    gap-1,
                    width=180,
                    window=box,
                    anchor='nw',
                    tags=('item', 'prog_bar_win', status_cat, source_tag)
                )

            gap += 22
            self.canvas.create_text(
                x+24,
                gap,
                anchor='nw',
                text=f'照片張數：{r[4]}',
                font=self.app.get_font('display-4'),
                fill='#464646',
                tags=('item', status_cat, source_tag)
            )
            icon = None
            if r[6] == self.app.source.STATUS_DONE_IMPORT:
                icon = self.fresh_icon
            elif r[6] == self.app.source.STATUS_DONE_UPLOAD:
                icon = self.done_icon
            elif r[6] == self.app.source.STATUS_ANNOTATION_UPLOAD_FAILED:
                icon = self.failed_icon
            elif r[6] == self.app.source.STATUS_START_ANNOTATE:
                icon = self.editing_icon
            elif r[6] == self.app.source.STATUS_DONE_OVERRIDE_UPLOAD:
                icon = self.override_icon
            elif r[6][0] == 'b': #TODO
                icon = self.uploading_icon

            self.canvas.create_image(
                x+228,
                gap-28,
                image=icon,
                anchor='nw',
                tags=('item', status_cat, source_tag))

            self.canvas.tag_bind(
                source_tag,
                '<ButtonPress>',
                lambda event, tag=source_tag: self.app.on_folder_detail(event, tag))


            shift_x += 316  # 300 + 16
            if i > 0 and (i+1) % 3 == 0:
                row_count += 1
                shift_y += 162  # 150 + 12
                shift_x = 0

        # reset scrollregion
        if row_count > 2:
            self.canvas.configure(scrollregion=(0,0,self.app.app_width, (row_count*300)))

        # 不知道可不可以讓 卡片 點擊敏感一點?
        self.update_idletasks()
