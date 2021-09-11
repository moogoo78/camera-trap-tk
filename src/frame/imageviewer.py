import tkinter as tk
from tkinter import (
    ttk,
)

from PIL import ImageTk, Image


class ImageViewer(tk.Frame):

    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent
        self.app = parent
        self.helper = self.parent.main.data_helper

        self.all_annotation_data = None
        self.current_annotation_num = 0
        self.annotation_columns = {}

        self.unsaved_entry = [] # x, y, row_key, col_key, value

        self.layout()

    def layout(self):
        # layout
        '''
        +-----------------------+
        |     image      | info |
        +-----------------------+
        |    annotation frame   |
        +-----------------------+
        '''
        #self.grid_rowconfigure(0, weight=1)
        #self.grid_rowconfigure(1, weight=0)
        #self.grid_rowconfigure(2, weight=0)
        #self.grid_columnconfigure(0, weight=1)
        #self.grid_columnconfigure(1, weight=0)

        self.left_frame = tk.Frame(
            self,
            width=900,
            height=400,
            bg='gray')
        self.left_frame.grid(row=0, column=0, padx=(6, 2), pady=(10, 2))
        self.right_frame = tk.Frame(
            self,
            width=500,
            height=400)
        self.right_frame.grid(row=0, column=1, padx=2, pady=10, sticky='nw')
        self.bottom_frame = tk.Frame(
            self,
            width=1200,
            height=200,
            #bg='black')
        )

        self.bottom_frame.grid(row=1, column=0, sticky='we', columnspan=2)

        # image
        self.image_label = ttk.Label(
            self.left_frame,
            border=1,
            relief='raised',
        )
        self.image_label.grid(row=0, column=0)

        # right frame
        self.back_button = ttk.Button(
            self.right_frame,
            text='回上頁',
            command=self.handle_back,
            takefocus=0)
        self.back_button.grid(row=0, column=0, pady=(0, 10), sticky='nw')

        self.title_frame = tk.Frame(
            self.right_frame,
            width=500,
            height=300,
            bg='yellow'
        )

        self.right_frame.grid_propagate(0)

        self.title_frame = tk.LabelFrame(self.right_frame, text='', width=280, height=200)
        self.title_frame.grid_propagate(0)
        self.title_frame.grid(row=1, column=0)

        self.title_label = ttk.Label(
            self.title_frame,
            text='',
            font=('Verdana', 12),
        )
        self.title_label.grid(row=0, column=0, sticky='nw')

        self.dtime_label = ttk.Label(
            self.title_frame,
            text='',
            font=('Verdana', 12),
        )
        self.dtime_label.grid(row=2, column=0, sticky='nw')

        self.exif_label = ttk.Label(
            self.title_frame,
            text='EXIF: ',
            font=('Verdana', 12),
        )
        self.exif_label.grid(row=3, column=0, sticky='nw', pady=4)

        self.exif_info = tk.Text(self.title_frame)
        self.exif_info.grid(row=4, column=0, sticky='nw')

        self.ctrl_frame = tk.LabelFrame(self.right_frame, text='control', width=280, height=100)
        self.ctrl_frame.grid_propagate(0)
        self.ctrl_frame.grid(row=2, column=0, pady=10)
        self.left_button = ttk.Button(
            self.ctrl_frame,
            text='<',
            command=lambda: self.handle_key_move('left'),
            width=4,
            takefocus=0)
        self.left_button.grid(row=0, column=0, pady=5, sticky='news')
        self.index_label = ttk.Label(
            self.ctrl_frame,
            text='',
            font=('Verdana', 14),
        )
        self.index_label.grid(row=0, column=1, padx=6, pady=6, sticky='news')
        self.right_button = ttk.Button(
            self.ctrl_frame,
            text='>',
            command=lambda: self.handle_key_move('right'),
            width=4,
            takefocus=0)
        self.right_button.grid(row=0, column=2, pady=5, sticky='news')

        '''
        #self.annotation_label = ttk.Label(self, text='')
        #self.annotation_label.grid(row=3, column=1, sticky='ew', padx=10, pady=10)
        # annotation frame
        self.annotation_frame = tk.Frame(self, bg='#ddeeff')
        #self.annotation_frame.grid(row=1, column=0, columnspan=2, sticky='news', padx=10, pady=10)


        self.sp_label = ttk.Label(self.annotation_frame, text='物種')
        self.sp_label.grid(row=0, column=0, padx=4, sticky='news')
        self.sp_val = tk.StringVar(self)
        self.sp_entry = ttk.Entry(
            self.annotation_frame,
            textvariable=self.sp_val,
            width=16,
        )
        self.sp_entry.grid(row=0, column=1, padx=4, sticky='news')

        self.ls_label = ttk.Label(self.annotation_frame, text='年齡')
        self.ls_label.grid(row=0, column=2, padx=4, sticky='news')
        self.ls_val = tk.StringVar(self)
        self.ls_entry = ttk.Entry(
            self.annotation_frame,
            textvariable=self.ls_val,
            width=16,
        )
        self.ls_entry.grid(row=0, column=3, padx=4, sticky='news')

        self.sx_label = ttk.Label(self.annotation_frame, text='性別')
        self.sx_label.grid(row=0, column=4, padx=4, sticky='news')
        self.sx_val = tk.StringVar(self)
        self.sx_entry = ttk.Entry(
            self.annotation_frame,
            textvariable=self.sx_val,
            width=16,
        )
        self.sx_entry.grid(row=0, column=5, padx=4, sticky='news')
        '''

    def handle_back(self):
        self.parent.main.handle_image_viewer()

    def init_data(self):
        '''init
        - all_annotation_data
        - current_annotation_num
        - annotation_columns
        '''
        self.all_annotation_data = self.helper.annotation_data
        self.current_annotation_num = 0

        # annotation columns
        self.annotation_columns = {}
        for i, col_key in self.helper.annotation_map.items():
            key = col_key.replace('annotation_', '')
            self.annotation_columns[key] = self.helper.columns[col_key]['label']

    def get_last_annotation_num_by_image_id(self, current_image_id):
        last_annotation_num = 0
        for image_id, alist in self.all_annotation_data.items():
            if current_image_id == image_id:
                return last_annotation_num
            last_annotation_num = len(alist)
        return

    def handle_key_move(self, action):
        row = self.parent.main.current_row
        #print(row, self.current_annotation_num, '--->')

        if action in ['down', 'right']:
            row += self.current_annotation_num
        elif action in ['up', 'left']:
            image_id = self.parent.main.current_image_data['image_id']
            n = self.get_last_annotation_num_by_image_id(image_id)
            if n:
                row -= n

        if len(self.unsaved_entry):
            args = self.unsaved_entry
            sv = self.table[args[0]][args[1]+1][0]
            value = sv.get()
            self.helper.update_annotation(args[2], args[3], args[4])

        if row >= 0 and row < len(self.helper.data):
            #print ('to row', row)
            self.parent.main.data_grid.main_table.selected.update({
                'row_start': row,
                'row_end': row,
                'col_start': 0,
                'col_end': 0,
                'row_list': [row],
            })
            self.parent.main.select_item((row, 0))
            self.refresh()

    def refresh(self):
        # bind key event
        self.app.bind('<Down>', lambda _: self.handle_key_move('down'))
        self.app.bind('<Up>', lambda _: self.handle_key_move('up'))
        self.app.bind('<Left>', lambda _: self.handle_key_move('left'))
        self.app.bind('<Right>', lambda _: self.handle_key_move('right'))

        source = self.parent.main.source_data['source']

        row = self.parent.main.current_row
        #row_key, _ = self.helper.get_rc_key(row, 0)

        item = self.helper.get_item(row)
        image_id = item['image_id']
        image_index = item['image_index']
        total = len(self.helper.annotation_data)
        #print (row_key, item)
        if not item:
            return

        self.current_annotation_num = len(self.all_annotation_data[image_id])
        exif_data = self.helper.exif_data

        self.title_frame['text'] = '{} ({})'.format(source[2], total)
        self.title_label['text'] = '檔案名稱: {}'.format(item['filename'])
        self.dtime_label['text'] = '拍攝時間: {}'.format(item['datetime_display'])
        self.index_label['text'] = '{} / {}'.format(image_index+1, total)

        self.exif_info.config(state='normal')
        self.exif_info.delete(1.0,tk.END)
        if exif := exif_data[image_id]:
            for x in ['Make', 'Model', 'DateTime', 'FNumber', 'ISOSpeedRatings', 'ExposureTime', 'FocalLength']:
                if t := exif.get(x, ''):
                    self.exif_info.insert(tk.INSERT, f'{x}: {t}\n')
                    #self.exif_info.insert(tk.END, 'aaa')
            # for readonly, this must set AFTER insert
            self.exif_info.config(state='disabled')

        #print (item['thumb'])

        # annotations
        if hasattr(self, 'annotation_frame'):
            self.annotation_frame.destroy()
        self.annotation_frame = tk.Frame(
            self.bottom_frame,
            height=120,
            width=1000,
            #bg='green',
        )
        self.annotation_frame.grid(row=0, column=0, sticky='news', padx=20)

        for counter, (col_key, col_label) in enumerate(self.annotation_columns.items()):
            lb = ttk.Label(
                self.annotation_frame,
                text=col_label,
                font=('Verdana', 12),
            )
            lb.grid(row=0, column=counter+1)

        # prevent tk widget use last value
        self.table = []
        for i, values in enumerate(self.all_annotation_data[image_id]):
            #print ('alist', i, values)
            self.table.append([])

            lb_index = ttk.Label(
                self.annotation_frame,
                text='{}.'.format(str(i+1)),
                font=('Verdana', 12),
            )
            self.table[i].append(lb_index)
            self.table[i][0].grid(row=i+1, column=0, padx=10, pady=4)

            for j, (col_key, col_label) in enumerate(self.annotation_columns.items()):
                # entry & stringvar
                sv = tk.StringVar(self.annotation_frame)
                #print (sv)
                val = values.get(col_key, '')
                sv.set(val)
                entry = ttk.Entry(
                    self.annotation_frame,
                    width=16,
                    textvariable=sv,
                    state=tk.DISABLED,
                )
                #entry.insert(0, val)
                assembled_row_key = f'iid:{image_id}-{i}'
                entry.bind('<FocusOut>', lambda event, x=i, y=j, row_key=assembled_row_key, col_key=col_key: self.handle_entry_focus_out(event, x, y, row_key, col_key))
                entry.bind('<KeyRelease>', lambda event, x=i, y=j, row_key=assembled_row_key, col_key=col_key: self.handle_entry_key_release(event, x, y, row_key, col_key))

                self.table[i].append([sv, entry])
                self.table[i][j+1][1].grid(row=i+1, column=j+1, padx=6, pady=3)

        # image
        image_path = item['thumb'].replace('-q.jpg', '-l.jpg')
        image = Image.open(image_path)
        #image.subsample(3,3)
        # aspect ratio
        basewidth = 900
        wpercent = (basewidth/float(image.size[0]))
        hsize = int((float(image.size[1])*float(wpercent)))
        img = image.resize((basewidth,hsize))
        photo = ImageTk.PhotoImage(img)
        self.image_label.configure(image=photo)
        self.image_label.image = photo
        #self.update_idletasks()


    def handle_entry_focus_out(self, event, x, y, row_key, col_key):
        sv = self.table[x][y+1][0]
        value = sv.get()
        self.helper.update_annotation(row_key, col_key, value)
        self.unsaved_entry = []

    def handle_entry_key_release(self, event, x, y, row_key, col_key):
        '''if cursor move by keyboard, save last changed entry'''
        sv = self.table[x][y+1][0]
        value = sv.get()
        self.unsaved_entry = [x, y, row_key, col_key, value]
