import threading
from datetime import datetime

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

        self.bg = ImageTk.PhotoImage(file='./assets/folder_list_vector.png')
        self.fresh_icon = ImageTk.PhotoImage(file='./assets/source_status_fresh.png')
        self.done_icon = ImageTk.PhotoImage(file='./assets/source_status_done.png')
        self.uploading_icon = ImageTk.PhotoImage(file='./assets/source_status_uploading.png')

        self.canvas.create_image(
            620,
            330,
            image=self.bg,
            anchor='nw',
        )
        self.canvas.create_text(
            50,
            20,
            anchor='nw',
            text='現有資料夾',
            font=(self.app.app_font, 32),
            fill=self.app.app_primary_color,
        )

    def exec_sql_list(self, image_sql_list, source_id):
        for i in image_sql_list:
            self.app.db.exec_sql(i)
        self.app.db.commit()

        self.app.db.exec_sql(f"UPDATE source SET status='{self.app.source.STATUS_DONE_IMPORT}' WHERE source_id={source_id}", True)
        self.refresh_source_list()
        showinfo(message='完成匯入資料夾')

    def add_folder_worker(self, src, source_id, image_list, folder_path):
        image_sql_list = []
        for i, (data, sql) in enumerate(src.gen_import_file(source_id, image_list, folder_path)):
            image_sql_list.append(sql)
            # print(i, sql)
            # print(self.folder_importing)
            self.folder_importing[source_id]['prog_bar']['value'] = i+1
            self.folder_importing[source_id]['label']['text'] = '{} ({}/{})'.format(image_list[i][0].name, i+1, len(image_list))

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

        image_list = src.get_image_list(folder_path)

        source_id = src.create_import_directory(len(image_list), folder_path)
        self.refresh_source_list()
        threading.Thread(target=self.add_folder_worker, args=(src, source_id, image_list, folder_path)).start()

        # show folder_list
        self.app.on_folder_list()

    def refresh_source_list(self):
        self.canvas.delete('prog_bar_win')
        db = self.app.db

        # reset source_list
        #if a := self.source_list:
        #    for i in a:
        #        i.destroy()
        #    #self.source_list = []

        # get all source from db
        rows = db.fetch_sql_all('SELECT * FROM source')

        start_x = 124 # begin
        start_y = 124
        shift_x = 0 # shift
        shift_y = 0
        for i, r in enumerate(rows):
            # print(r)
            timestamp = datetime.fromtimestamp(r[5]).strftime('%Y-%m-%d %H:%M')
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
                tags=('card', source_tag),
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
                    font=(self.app.app_font, title_font_size),
                    fill=self.app.app_primary_color)
                self.canvas.create_text(
                    x+24,
                    gap+10,
                    anchor='nw',
                    text=title2,
                    font=(self.app.app_font, title_font_size),
                    fill=self.app.app_primary_color)
            else:
                self.canvas.create_text(
                    x+24,
                    gap,
                    anchor='nw',
                    text=r[3],
                    font=(self.app.app_font, title_font_size),
                    fill=self.app.app_primary_color)

            gap += 30
            self.canvas.create_text(
                x+24,
                gap,
                anchor='nw',
                text=f'首次上傳時間：{timestamp}',
                font=(self.app.app_font, 14),
                fill='#464646',
            )
            gap += 22
            self.canvas.create_text(
                x+24,
                gap,
                anchor='nw',
                text=f'上次上傳時間：{timestamp}',
                font=(self.app.app_font, 14),
                fill='#464646',
            )
            gap += 22
            self.canvas.create_text(
                x+24,
                gap,
                anchor='nw',
                text=f'上傳狀態：{self.app.source.get_status_label(r[6])}',
                font=(self.app.app_font, 14),
                fill='#464646',
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
                    tags=('prog_bar_win')
                )

            gap += 22
            self.canvas.create_text(
                x+24,
                gap,
                anchor='nw',
                text=f'照片張數：{r[4]}',
                font=(self.app.app_font, 14),
                fill='#464646',
            )
            icon = None
            if r[6] == self.app.source.STATUS_DONE_IMPORT:
                icon = self.fresh_icon
            elif r[6] == self.app.source.STATUS_DONE_UPLOAD:
                icon = self.done_icon
            elif r[6][0] == 'b': #TODO
                icon = self.uploading_icon

            self.canvas.create_image(
                x+228,
                gap-28,
                image=icon,
                anchor='nw',
                tags=('item'))

            self.canvas.tag_bind(
                source_tag,
                '<ButtonPress-1>',
                lambda event, tag=source_tag: self.app.on_folder_detail(event, tag)
            )

            shift_x += 316  # 300 + 16
            if i > 0 and (i+1) % 3 == 0:
                shift_y += 162  # 150 + 12
                shift_x = 0
