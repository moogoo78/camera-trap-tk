import re
import json
import time
from pathlib import Path
import sys
import tkinter as tk
from tkinter import ttk
import logging
import queue
import csv
from datetime import datetime
import subprocess

from PIL import ImageTk, Image

from helpers import (
    DataHelper,
)
from frame import (
    UploadProgress,
    Landing,
    ImageViewer,
)
from toplevel import (
    ImageDetail,
    ConfigureKeyboardShortcut,
    VideoPlayer,
)
from image import (
    check_thumb,
    aspect_ratio,
)
from worker import UpdateAction

sys.path.insert(0, '') # TODO: pip install -e .
from tkdatagrid import DataGrid

SPECIES_COL_POS = 4 # species annotation column position

class Main(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)

        self.app = parent #self.parent.app

        self.background_color = kwargs.get('background','')

        self.source_data = {}
        # self.projects = self.app.server.projects
        # self.id_map = {
        #     'project': {},
        #     'studyarea': {},
        #     'deployment': {},
        #     'sa_to_d': {}
        # }
        # self.id_map['project'] = {x['name']: x['project_id'] for x in self.projects}
        # self.bind('<Configure>', self.resize)

        self.projects = []
        self.update_project_options()

        self.source_id = None
        self.current_row = 0
        self.current_image_data = {
            'image_id': 0,
            'image_index': 0,
        }
        # self.thumb_basewidth = 550
        self.thumb_height = 309 # fixed height
        annotate_status_list = (self.app.source.STATUS_DONE_IMPORT, self.app.source.STATUS_START_ANNOTATE)
        self.data_helper = DataHelper(self.app.db, annotate_status_list)
        self.annotation_entry_list = []
        self.species_copy = []
        self.keyboard_shortcuts = {}
        self.is_editing = False  # wrapping 'def refresh' to protect redundant entry update
        species_choices = self.app.config.get('AnnotationFieldSpecies', 'choices')
        antler_choices = self.app.config.get('AnnotationFieldAntler', 'choices')
        sex_choices = self.app.config.get('AnnotationFieldSex', 'choices')
        lifestage_choices = self.app.config.get('AnnotationFieldLifeStage', 'choices')
        species_extra_birds = self.app.config.get('AnnotationSpeciesExtra', 'birds')
        self.data_helper.columns['annotation_species']['choices'] = species_choices.split(',')
        self.data_helper.columns['annotation_species']['extra_choices'] = species_extra_birds.split(',')
        self.data_helper.columns['annotation_antler']['choices'] = antler_choices.split(',')
        self.data_helper.columns['annotation_sex']['choices'] = sex_choices.split(',')
        self.data_helper.columns['annotation_lifestage']['choices'] = lifestage_choices.split(',')

        self.image_detail = None

        # layout
        #self.grid_propagate(False)
        self.layout()

        '''TODO_LAYOUT
        self.app.frames['image_viewer'] = ImageViewer(self)
        #self.app.frames['image_viewer'].grid(row=0, column=0, sticky='nsew')
        self.app.frames['landing'] = Landing(self, width=400, bg=self.background_color)
        self.app.frames['landing'].show()
        #self.landing.grid(row=0, column=0, sticky='nsew')
        '''

        self.upload_status = 0 # 0: stop, 1: start, 2: pause
        #self.thread = threading.Thread(target=self.worker)
        #self.polling()

    def handle_panedwindow_release(self, event):
        w = self.right_frame.winfo_width()
        # border: 8, padx: 10
        self.thumb_basewidth = w - 36
        data = self.get_current_item('data')


    def layout(self):
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        #self.notebook = ttk.Notebook(self)
        #self.notebook.grid(row=0, column=0)

        #panedwindow_style = ttk.Style()
        self.panedwindow = ttk.PanedWindow(self, orient=tk.VERTICAL)
        #panedwindow_style = configure('PanedWindow', sashpad=5)
        #self.panedwindow.pack(fill=tk.BOTH, expand=True)
        self.panedwindow.grid(row=0, column=0, sticky='nsew')
        self.panedwindow.grid_rowconfigure(0, weight=1)
        self.panedwindow.grid_columnconfigure(0, weight=1)
        #self.panedwindow.bind("<ButtonRelease-1>", self.handle_panedwindow_release)
        self.top_paned_frame = tk.Frame(self.panedwindow, bg='#F2F2F2') #bg='#2d3142'
        self.bottom_paned_frame = tk.Frame(self.panedwindow, bg='gray')

        self.panedwindow.add(self.top_paned_frame)
        self.panedwindow.add(self.bottom_paned_frame)

        # top_paned
        self.top_paned_frame.grid_rowconfigure(0, weight=0)
        #self.top_paned_frame.grid_rowconfigure(1, weight=1)
        self.top_paned_frame.grid_columnconfigure(0, weight=0)
        self.top_paned_frame.grid_columnconfigure(1, weight=1)

        self.image_thumb_frame = tk.Frame(self.top_paned_frame, bg='gray')
        self.image_thumb_frame.grid(row=0, column=0, sticky='nswe')
        self.image_thumb_label = ttk.Label(self.image_thumb_frame, border=0, relief='flat')
        self.image_thumb_label.grid(row=0, column=0, sticky='ns')


        self.ctrl_frame = tk.Frame(self.top_paned_frame, width=500, height=self.thumb_height, bg='#F2F2F2')
        self.ctrl_frame.grid(row=0, column=1, sticky='nw', padx=10)
        #self.ctrl_frame.grid_propagate(0)
        self.config_ctrl_frame()

        # bottom_paned
        self.bottom_paned_frame.grid_rowconfigure(0, weight=1)
        self.bottom_paned_frame.grid_columnconfigure(0, weight=1)
        self.table_frame = tk.Frame(self.bottom_paned_frame)
        self.table_frame.grid(row=0, column=0, sticky='news')

        self.config_table_frame()

    def fo_species(self, event):
        #print (self.species_free.listbox, event)
        if self.species_free.listbox:
            self.species_free.handle_update(event)

    def fo_lifestage(self, event):
        if self.lifestage_free.listbox:
            self.lifestage_free.handle_update(event)

    def fo_sex(self, event):
        if self.sex_free.listbox:
            self.sex_free.handle_update(event)

    def fo_antler(self, event):
        if self.antler_free.listbox:
            self.antler_free.handle_update(event)

    def config_ctrl_frame(self):
        #self.ctrl_frame.grid_rowconfigure(0, weight=0)
        #self.ctrl_frame.grid_columnconfigure(0, weight=0)
        #self.ctrl_frame.grid_propagate(0)

        self.label_folder = tk.Label(
            self.ctrl_frame,
            text='',
            font=self.app.get_font('display-2'),
            foreground=self.app.app_primary_color,
            background='#F2F2F2',
        )

        self.label_folder.grid(row=0, column=0, padx=4, pady=10, sticky='nw')

        conf_kb_shortcut_button = tk.Button(
            self,
            text='設定快捷鍵',
            relief='flat',
            command=lambda: ConfigureKeyboardShortcut(self.app),
            takefocus=0,
        )
        conf_kb_shortcut_button.grid(row=0, column=0, padx=4, pady=34, sticky='ne')

        export_button = tk.Button(
            self,
            text='匯出csv',
            #image=self.enlarge_icon,
            relief='flat',
            command=self.export_csv,
            takefocus=0,
        )
        export_button.grid(row=0, column=0, padx=4, pady=4, sticky='ne')

        # foo_button = tk.Button(
        #     self,
        #     text='resize',
        #     relief='flat',
        #     command=self.resize_datagrid,
        #     takefocus=0,
        # )
        # foo_button.grid(row=0, column=0, padx=4, pady=34, sticky='ne')

        self.ctrl_frame2 = tk.Frame(self.ctrl_frame, background='#F2F2F2')
        self.ctrl_frame2.grid_rowconfigure(0, weight=0)
        self.ctrl_frame2.grid_rowconfigure(1, weight=0)
        self.ctrl_frame2.grid_rowconfigure(2, weight=0)
        self.ctrl_frame2.grid_columnconfigure(0, weight=0)
        self.ctrl_frame2.grid_columnconfigure(1, weight=1)
        self.ctrl_frame2.grid(row=2, column=0, sticky='ew')

        label_grid = {
            'sticky': 'w',
            'padx': 14,
            'pady': 3,
        }
        label_args = {
            'font': self.app.get_font('display-4'),
            'background': '#F2F2F2'
        }
        left_spacing = -2  # macOS: 30
        # project menu
        self.label_project = ttk.Label(
            self.ctrl_frame2,
            text='檢視計畫',
            **label_args)

        self.project_options = [x['name'] for x in self.projects]
        self.project_var = tk.StringVar(self)
        self.project_menu = tk.OptionMenu(
            self.ctrl_frame2,
            self.project_var,
            '-- 選擇計畫 --',
            *self.project_options,
            command=self.project_option_changed,
        )

        self.label_project.grid(row=0, column=0, **label_grid)
        self.project_menu.grid(row=0, column=1, sticky='w', padx=(left_spacing+2, 0))

        # studyarea menu
        self.label_studyarea = ttk.Label(
            self.ctrl_frame2,
            text='樣區',
            **label_args)

        self.studyarea_var = tk.StringVar(self)
        self.studyarea_options = []
        self.studyarea_menu = tk.OptionMenu(
            self.ctrl_frame2,
            self.studyarea_var,
            '')
        self.studyarea_var.trace('w', self.studyarea_option_changed)

        self.label_studyarea.grid(row=1, column=0, **label_grid)
        self.studyarea_menu.grid(row=1, column=1, sticky='w', padx=(left_spacing+2, 0))

        # deployment menu
        self.label_deployment = ttk.Label(
            self.ctrl_frame2,
            text='相機位置',
            **label_args)

        self.deployment_options = []
        self.deployment_var = tk.StringVar(self)
        self.deployment_var.trace('w', self.deployment_option_changed)
        self.deployment_menu = tk.OptionMenu(
            self.ctrl_frame2,
            self.deployment_var,
            '')

        self.label_deployment.grid(row=2, column=0, **label_grid)
        self.deployment_menu.grid(row=2, column=1, sticky='w', padx=(left_spacing+2, 0))

        # trip
        self.trip_label = ttk.Label(
            self.ctrl_frame2,
            text='資料夾頭尾照片日期',
            **label_args)
        self.trip_label_sep = ttk.Label(
            self.ctrl_frame2,
            text='-',
            **label_args)
        self.trip_label_tip = ttk.Label(
            self.ctrl_frame2,
            text='format: YYYYmmdd',
            **label_args)

        self.trip_start_var = tk.StringVar(self)
        self.trip_end_var = tk.StringVar(self)
        self.trip_start_entry = ttk.Entry(
            self.ctrl_frame2,
            textvariable=self.trip_start_var,
            width=10,
        )
        self.trip_end_entry = ttk.Entry(
            self.ctrl_frame2,
            textvariable=self.trip_end_var,
            width=10,
        )
        self.trip_start_var.trace('w', lambda *args: self.handle_entry_change(args, 'trip_start'))
        self.trip_end_var.trace('w', lambda *args: self.handle_entry_change(args, 'trip_end'))

        self.trip_label.grid(row=3, column=0, **label_grid)
        self.trip_start_entry.grid(row=3, column=1, sticky='w', padx=(left_spacing+2, 0))
        self.trip_label_sep.grid(row=3, column=1, sticky='w', padx=(left_spacing+102, 20))
        self.trip_end_entry.grid(row=3, column=1, sticky='w', padx=left_spacing+118)
        self.trip_label_tip.grid(row=3, column=1, sticky='w', padx=(left_spacing+222, 0))

        # image sequence
        self.seq_label = ttk.Label(
            self.ctrl_frame2,
            text='連拍補齊設定',
            **label_args)

        self.seq_checkbox_val = tk.StringVar(self)
        self.seq_checkbox = ttk.Checkbutton(
            self.ctrl_frame2,
            text='連拍分組',
	    command=lambda: self.refresh(),
            variable=self.seq_checkbox_val,
	    onvalue='Y',
            offvalue='N')

        self.seq_interval_val = tk.StringVar(self)
        #self.seq_interval_val.trace('w', self.on_seq_interval_changed)
        self.seq_interval_entry = ttk.Entry(
            self.ctrl_frame2,
            textvariable=self.seq_interval_val,
            width=4,
            #validate='focusout',
            #validatecommand=self.on_seq_interval_changed
        )
        self.seq_interval_entry.bind(
            "<KeyRelease>", lambda _: self.refresh())

        self.seq_unit = ttk.Label(
            self.ctrl_frame2,
            text='分鐘分組 (相鄰照片間隔分鐘數，顯示分組)',
            **label_args)

        self.seq_label.grid(row=4, column=0, **label_grid)
        self.seq_checkbox.grid(row=4, column=1, sticky='w', padx=(left_spacing+2, 0))
        self.seq_interval_entry.grid(row=4, column=1, sticky='w', padx=(left_spacing+82, 0))
        self.seq_unit.grid(row=4, column=1, sticky='w', padx=(left_spacing+122, 0))

        # test foto
        self.test_foto_label = ttk.Label(
            self.ctrl_frame2,
            text='整點補齊設定',
            **label_args)
        self.test_foto_tip = ttk.Label(
            self.ctrl_frame2,
            text='的照片皆為補齊為測試照 format: HH:MM:SS',
            **label_args)
        self.test_foto_button = ttk.Button(
            self.ctrl_frame2,
            text='套用',
            command=self.set_test_foto_by_time,
            takefocus=0,
            width=4,
        )
        self.test_foto_val = tk.StringVar(self)

        self.test_foto_entry = ttk.Entry(
            self.ctrl_frame2,
            textvariable=self.test_foto_val,
            width=8,
        )

        self.test_foto_label.grid(row=5, column=0, **label_grid)
        self.test_foto_entry.grid(row=5, column=1, sticky='w', padx=(left_spacing+2, 0))
        self.test_foto_tip.grid(row=5, column=1, sticky='w', padx=(left_spacing+76, 0))
        self.test_foto_button.grid(row=5, column=1, sticky='w', padx=(left_spacing+402, 0))

        # upload button
        self.upload_button = tk.Button(
            self.ctrl_frame2,
            text='上傳資料夾',
            # command=self.handle_upload2
            command=self.handle_upload3,
            foreground='#FFFFFF',
            background=self.app.app_primary_color,
            width=10,
            height=2,
            takefocus=0)

        self.delete_button = tk.Button(
            self.ctrl_frame2,
            text='刪除資料夾',
            command=self.handle_delete,
            foreground='#FFFFFF',
            background=self.app.app_comp_color,
            width=10,
            height=2,
            takefocus=0,
        )

        self.upload_button.grid(row=6, column=1, sticky='e', padx=(0, left_spacing+110), pady=(18,0))
        self.delete_button.grid(row=6, column=1, sticky='e', padx=(20, 0), pady=(18, 0))

        self.enlarge_icon = ImageTk.PhotoImage(file='./assets/enlarge.png')
        self.image_viewer_button = tk.Button(
            self.ctrl_frame2,
            text='看大圖',
            image=self.enlarge_icon,
            #command=self.handle_image_viewer,
            #command=self.app.toggle_image_viewer,
            relief='flat',
            background='#FFFFFF',
            command=self.show_image_detail,
            takefocus=0,
        )
        # self.image_viewer_button.place(x=416, y=270, anchor='nw')
        self.image_viewer_button.grid(row=7, column=0, sticky='sw')

    def config_table_frame(self):
        self.table_frame.grid_columnconfigure(0, weight=1)
        self.table_frame.grid_rowconfigure(0, weight=1)
        #print (self.table_frame.grid_info(), self.table_frame.grid_bbox())
        species_choices = self.app.config.get('AnnotationFieldSpecies', 'choices')
        species_extra_birds = self.app.config.get('AnnotationSpeciesExtra', 'birds')
        menus = [
            # {
            #     'type': 'menu',
            #     'label': '物種清單',
            #     'choices': species_choices.split(','),
            #     'command': self.handle_click_menu_species,
            # },
            {
                'type': 'menu',
                'label': '鳥類清單',
                'choices': species_extra_birds.split(','),
                'command': self.handle_click_menu_species,
            },
        ]

        custom_binding = {
            'bind_list': [],
            'command': self.handle_keyboard_shortcut,
        }
        for n in range(0, 10):
            self.keyboard_shortcuts[str(n)] = self.app.config.get('KeyboardShortcut', f'Control-Key-{n}')
            custom_binding['bind_list'].append(f'Control-Key-{n}')

        num_per_page = int(self.app.config.get('DataGrid', 'num_per_page'))
        self.data_grid = DataGrid(
            self.table_frame,
            data={},
            columns=self.data_helper.columns,
            height= 1600-480, #self.app.app_height - 480, #760-480
            width=1200,
            row_index_display='sn',
            cols_on_ctrl_button_1=['annotation_species'],
            cols_on_fill_handle=['annotation_species', 'annotation_sex', 'annotation_antler', 'annotation_remark', 'annotation_lifestage'],
            custom_menus=menus,
            custom_binding=custom_binding,
            num_per_page=num_per_page,
            rows_delete_type='CLONED',
            remove_rows_key_ignore_pattern='-0',
            column_header_bg= '#5B7464',
            column_header_height=30,
        )

        self.data_grid.update_state({
            'cell_height': 35,
            'cell_image_x_pad': 3,
            'cell_image_y_pad': 1,
            'custom_actions': {
                'remove_rows': ('after', self.custom_remove_rows),
                'clone_row': ('bind', self.custom_clone_row),
                'mouse_click': ('after', self.custom_mouse_click),
                'arrow_key': ('after', self.custom_arrow_key),
                'set_data': ('after', self.custom_set_data),
                'to_page': self.custom_to_page,  # after
                #'apply_pattern': self.custom_apply_pattern,
                # 'paste_from_buffer': self.custom_paste_from_buffer,
            },
        })
        self.data_grid.grid(row=0, column=0, sticky='nsew')


    def update_project_options(self):
        if len(self.projects) <= 0:
            self.projects = self.app.server.get_projects()
            self.id_map = {
                'project': {},
                'studyarea': {},
                'deployment': {},
                'sa_to_d': {}
            }
            self.id_map['project'] = {x['name']: x['project_id'] for x in self.projects}
            logging.info('server: get project options')

    def change_source(self, source_id=None):
        logging.debug('source_id: {}'.format(source_id))

        self.update_project_options()
        self.source_id = source_id

        # reset current_row
        self.current_row_key = ''
        self.current_image_data = {}
        self.data_grid.main_table.init_data()

        # clear image sequence checked
        self.seq_interval_val.set('')
        self.seq_checkbox_val.set('N')

        self.current_row_key = ''
        self.refresh(is_init_highlight=True)


    def refresh(self, is_init_highlight=False):
        self.is_editing = False
        logging.debug(f'refresh: {self.source_id}, current_row_key: {self.current_row_key}')

        #self.data_helper.set_status_display(image_id=35, status_code='300')-
        # let project image group intervel entry off focus
        # or after key in minute then press arrow key, focus will still on entry
        self.app.focus_set()

        if not self.source_id:
            return

        self.source_data = self.app.source.get_source(self.source_id)
        if status := self.source_data['source'][6]:
            self.data_helper.source_id_status = [self.source_id, status]
        if descr := self.source_data['source'][7]:
            d = json.loads(descr)
            # set init value
            self.project_var.set(d.get('project_name', ''))
            self.studyarea_var.set(d.get('studyarea_name', ''))
            self.deployment_var.set(d.get('deployment_name', ''))
        else:
            self.project_var.set('')
            self.studyarea_var.set('')
            self.deployment_var.set('')

        if test_foto_time := self.source_data['source'][11]:
            self.test_foto_val.set(test_foto_time)
            self.data_helper.test_foto_time = test_foto_time
        else:
            self.test_foto_val.set('')

        if trip_start := self.source_data['source'][9]:
            self.trip_start_var.set(trip_start)
        else:
            self.trip_start_var.set('')

        if trip_end := self.source_data['source'][10]:
            self.trip_end_var.set(trip_end)
        else:
            self.trip_end_var.set('')

        # update upload_button
        source_status = self.source_data['source'][6]
        if self.app.source.is_done_upload(source_status):
            self.upload_button['text'] = '更新文字資料'
        else:
            self.upload_button['text'] = '上傳資料夾'
        # if source_status == '20':
        #     self.upload_button['text'] = '上傳中'
        #     self.upload_button['state'] = tk.DISABLED
        #     self.delete_button['state'] = tk.DISABLED
        # elif source_status == '40':
        #     self.upload_button['text'] = '上傳*'
        #     self.delete_button['state'] = tk.NORMAL
        # else:
        #     self.upload_button['text'] = '上傳資料夾'
        #     self.upload_button['state'] = tk.NORMAL
        #     self.delete_button['state'] = tk.NORMAL

        # data list
        data = self.data_helper.read_image_list(self.source_data['image_list'])
        #print (data)

        # consider pagination
        num = self.data_grid.state['pagination']['num_per_page']
        cur_page = self.data_grid.state['pagination']['current_page']
        start = (cur_page - 1) * num
        end = cur_page * num

        self.seq_info = None
        seq_int = self.seq_interval_val.get()
        if self.seq_checkbox_val.get() == 'Y' and seq_int:
            self.seq_info = self.data_helper.group_image_sequence(seq_int)
            # change DataGrid.main_table.render_box color
            self.data_grid.state['box_display_type'] = 'raise'

        # show first image if no select
        if self.current_row_key == '':
            self.current_row_key = next(iter(data))

        if len(data) > 0:
            current_item = data[self.current_row_key]
            if current_item['media_type'] == 'image':
                self.show_image(current_item['thumb'], 'm')
            elif current_item['media_type'] == 'video':
                self.show_video_icon()
        else:
            self.image_thumb_label.image = None

        self.data_grid.main_table.delete('row-img-seq')
        self.data_grid.refresh(data, is_init_highlight=is_init_highlight)
        # draw img_seq
        # print(self.seq_info)
        for i, (iid, row) in enumerate(data.items()):
            if i >= start and i < end:
                index = i - ((cur_page - 1) * num)
                tag_name = row.get('img_seq_tag_name', '')
                color = row.get('img_seq_color', '')
                # print(index, tag_name, color)
                y1 = self.data_grid.state['cell_height'] * index
                y2 = self.data_grid.state['cell_height'] * (index+1)
                if tag_name and color:
                    self.data_grid.main_table.create_rectangle(
                        0, y1, self.data_grid.main_table.width + self.data_grid.main_table.x_start, y2,
                        fill=color,
                        tags=('row-img-seq', 'row-img-seq_{}'.format(tag_name)))

        self.data_grid.main_table.tag_lower('row-img-seq')
        self.data_grid.main_table.render_row_highlight()

        # folder name
        self.label_folder['text'] = self.source_data['source'][3]

        # trip start/end
        if trip_start := self.source_data['source'][9]:
            self.trip_start_var.set(trip_start)
        if trip_end := self.source_data['source'][10]:
            self.trip_end_var.set(trip_end)

        self.is_editing = True

    def project_option_changed(self, *args):
        name = self.project_var.get()
        id_ = self.id_map['project'].get(name,'')
        if id_ == '':
            return

        # reset
        self.studyarea_options = []
        self.id_map['studyarea'] = {}
        self.id_map['deployment'] = {}
        self.id_map['sa_to_d'] = {}

        res = self.app.server.get_projects(id_)
        for i in res['studyareas']:
            self.id_map['studyarea'][i['name']] = i['studyarea_id']
            self.studyarea_options.append(i['name'])

            if i['name'] not in self.id_map['sa_to_d']:
                self.id_map['sa_to_d'][i['name']] = []
            for j in i['deployments']:
                self.id_map['sa_to_d'][i['name']].append(j)
                self.id_map['deployment'][j['name']] = j['deployment_id']
        # refresh
        #print (self.studyarea_options)
        #print (self.id_map['studyarea'], self.id_map['deployment'])
        # refresh studyarea_options
        self.studyarea_var.set('-- 選擇樣區 --')
        menu = self.studyarea_menu['menu']
        menu.delete(0, 'end')
        for sa_name in self.studyarea_options:
            menu.add_command(label=sa_name, command=lambda x=sa_name: self.studyarea_var.set(x))

    def studyarea_option_changed(self, *args):
        selected_sa = self.studyarea_var.get()
        self.deployment_options = []
        for i in self.id_map['sa_to_d'].get('selected_sa', []):
            self.deployment_options.append(i['name'])
        # refresh studyarea_options
        self.deployment_var.set('-- 選擇相機位置 --')
        menu = self.deployment_menu['menu']
        menu.delete(0, 'end')
        for d in self.id_map['sa_to_d'].get(selected_sa, []):
            menu.add_command(label=d['name'], command=lambda x=d['name']: self.deployment_var.set(x))

    def deployment_option_changed(self, *args):
        d_name = self.deployment_var.get()
        if deployment_id := self.id_map['deployment'].get(d_name, ''):
            #print ('set deployment_id: ', deployment_id, d_name, )
            sa_name = self.studyarea_var.get()
            p_name = self.project_var.get()
            descr = {
                'deployment_id': deployment_id,
                'deployment_name': d_name,
                'studyarea_id': self.id_map['studyarea'].get(sa_name, ''),
                'studyarea_name': sa_name,
                'project_id': self.id_map['project'].get(p_name, ''),
                'project_name': p_name,
            }
            #print (descr)
            update_db = False
            if db_descr := self.source_data['source'][7]:
                d = json.loads(db_descr)
                if deployment_id != d['deployment_id']:
                    update_db = True
            else:
                # new
                update_db = True
            if update_db:
                # save to db
                sql = "UPDATE source SET description='{}' WHERE source_id={}".format(json.dumps(descr), self.source_id)
                self.app.db.exec_sql(sql, True)

            # update source_data (for upload: first time import folder, get no deployment_id even if selected)
            self.source_data = self.app.source.get_source(self.source_id)
            # TODO
            #tk.messagebox.showinfo('info', '已設定相機位置')

    def handle_upload3(self):
        # ==============
        # check & notify
        # =============

        # check deployment has set
        deployment_id = ''
        if descr := self.source_data['source'][7]:
            d = json.loads(descr)
            deployment_id = d.get('deployment_id', '')
        if deployment_id == '':
            tk.messagebox.showwarning('注意', '末設定相機位置，無法上傳')
            return False

        # ask check deployment/staudy area/project
        if not tk.messagebox.askokcancel('確認計畫', '請確認計畫、樣區、相機位置是否無誤？'):
            return False

        has_empty = self.data_helper.has_empty_species()
        if has_empty:
            if not tk.messagebox.askokcancel('注意', '尚有照片未填寫物種'):
                return False

        # ======
        # upload
        # ======
        image_list = self.source_data['image_list']
        source_id = self.source_id
        account_id = self.app.config.get('Installation', 'account_id')
        is_first_upload = False

        if not self.source_data['source'][13] and \
           not self.source_data['source'][14]:
            is_first_upload = True

        now = int(time.time())
        if is_first_upload:
            self.app.source.update_status(source_id, 'START_UPLOAD', now=now)
        else:
            self.app.source.update_status(source_id, 'START_OVERRIDE_UPLOAD', now=now)

        payload = {
            'image_list': image_list,
            'key': f'{account_id}/{self.app.user_hostname}/{self.app.version}/{source_id}',
            'deployment_id': deployment_id,
            'trip_start':self.trip_start_var.get(),
            'trip_end': self.trip_end_var.get(),
            'folder_name': self.source_data['source'][3],
            'source_id': self.source_data['source'][0],
            'bucket_name': self.app.config.get('AWSConfig', 'bucket_name'),
        }
        # print(self.source_data['source'][6])
        # check if re-post annotation
        if self.app.source.is_done_upload(self.source_data['source'][6]):
            ans = tk.messagebox.askquestion('上傳確認', '已經上傳過了，確定要重新上傳 ? (只有文字資料會覆蓋)')
            if ans == 'no':
                return False
            elif ans == 'yes':
                res = self.app.server.post_annotation(payload)
                if res['error']:
                    self.app.source.update_status(source_id, 'OVERRIDE_ANNOTATION_UPLOAD_FAILED')
                    tk.messagebox.showerror('上傳失敗 (server error)', f"{res['error']}")
                else:
                    self.app.source.update_status(source_id, 'DONE_OVERRIDE_UPLOAD')
                    tk.messagebox.showinfo('info', '文字資料更新成功 !')

                    # let server send notification again
                    if dj_id := self.source_data['source'][12]:
                        deployment_journal_id = dj_id
                        self.app.server.post_upload_history(deployment_journal_id, 'finished')

                    return # stop uploading images again

        # 1. post annotation to server
        sql = "UPDATE image SET upload_status='100' WHERE image_id IN ({})".format(','.join([str(x[0]) for x in image_list]))
        self.app.db.exec_sql(sql, True)

        res = self.app.server.post_annotation(payload)
        if res['error']:
            self.app.source.update_status(source_id, 'ANNOTATION_UPLOAD_FAILED')
            tk.messagebox.showerror('上傳失敗 (server error)', f"{res['error']}")
            return

        server_image_map = res['data']

        # push info to server uploading start
        deployment_journal_id = None
        if dj_id := self.source_data['source'][12]:
            deployment_journal_id = dj_id
        else:
            if dj_id := res.get('deployment_journal_id'):
                sql = f"UPDATE source SET deployment_journal_id={dj_id} WHERE source_id={source_id}"
                self.app.db.exec_sql(sql, True)
                deployment_journal_id = dj_id

        if deployment_journal_id != None:
            res = self.app.server.post_upload_history(deployment_journal_id, 'uploading')
            if err := res['error']:
                tk.messagebox.showerror('server error', err)
                return

        for image_id, [server_image_id, server_image_uuid] in server_image_map.items():
            sql = f"UPDATE image SET upload_status='110', server_image_id={server_image_id}, object_id='{server_image_uuid}' WHERE image_id={image_id}"
            self.app.db.exec_sql(sql)
        self.app.db.commit()

        self.app.on_upload_progress()
        self.app.contents['upload_progress'].handle_start(source_id)

    def handle_delete(self):
        ans = tk.messagebox.askquestion('確認', f"確定要刪除資料夾: {self.source_data['source'][3]}?")
        if ans == 'no':
            return False

        self.app.source.delete_folder(self.source_id)
        #self.app.frames['folder_list'].refresh_source_list()\

        '''TODO_LAYOUT
        self.app.frames['landing'].show(True)
        '''

    def custom_to_page(self):
        self.refresh()

    def custom_set_data(self, row_key, col_key, value):
        # print('-----', row_key, col_key, value)
        res = self.data_helper.update_annotation(row_key, col_key, value, self.seq_info)
        #if not res:
        #    self.refresh()

        # if self.seq_info:
            # has seq_info need re-render

        self.refresh()

        # always refresh for status display
        #self.refresh() 先不要
        #item = self.data_helper.data[row_key]
        #tmp = item['status_display']
        #status = tmp.split(' / ')
        #self.data_grid.main_table.update_text((rc[0], 0), f'{status[0]} / ')

    def select_item(self, row_key, col_key):
        '''
        current_row is already set by DataGrid
        set current_image_data
        '''
        if row_key is None or col_key is None:
            return

        self.current_row_key = row_key  # for show_image_detail
        item = self.data_helper.data[row_key]

        if item:
            self.current_image_data.update({
                'image_id': item['image_id'],
                'image_index': item['image_index'],
            })
        else:
            return

        # self.current_row = rc[0] NO_NEED_TO
        # print('!!', row_key, col_key)
        if item['media_type'] == 'image':
            self.show_image(item['thumb'], 'm')
        elif item['media_type'] == 'video':
            self.show_video_icon()

        if item['status'] == '10':
            image_id = item['image_id']
            sql = f"UPDATE image SET status='20' WHERE image_id={image_id}"
            self.app.db.exec_sql(sql, True)

            #row_key, col_key = self.data_grid.main_table.get_rc_key(rc[0], rc[1])
            #self.data_grid.main_table.set_data_value(row_key, col_key, 'vv')
            # update status_display
            self.data_helper.set_status_display(row_key, status_code='20')
            self.data_grid.main_table.render()

    def custom_arrow_key(self, row_key, col_key):
        self.select_item(row_key, col_key)
        if self.image_detail:
            item = self.data_helper.data[row_key]
            image_path = item['thumb'].replace('-q.', '-o.')
            self.image_detail.change_image(image_path)

    def custom_mouse_click(self, row_key, col_key):
        self.select_item(row_key, col_key)

    def show_image(self, thumb_path, size_key=''):
        if size_key:
            thumb_path = thumb_path.replace('-q.jpg', '-{}.jpg'.format(size_key))

        if not Path(thumb_path).exists():
            return None

        # 刪 thumbnail 就不重做 thumbnail 了 (盡量跟原圖脫鉤)
        #real_thumb_path = check_thumb(thumb_path, image_path)
        #image = Image.open(real_thumb_path)
        image = Image.open(thumb_path)
        #resize_to = aspect_ratio(image.size, width=self.thumb_basewidth)
        resize_to = aspect_ratio(image.size, height=self.thumb_height)
        img = image.resize(resize_to, Image.ANTIALIAS)

        photo = ImageTk.PhotoImage(img)
        self.image_thumb_label.configure(image=photo)
        self.image_thumb_label.image = photo # 一定要用這樣設，圖片不然出不來

        #self.image_viewer_button.place(x=resize_to[0]-46, y=270, anchor='nw')

        self.update_idletasks()

    def custom_clone_row(self):
        rows = self.data_grid.get_row_list()
        for row in rows:
            row_key, _ = self.data_grid.main_table.get_rc_key(row, 0)
            item = self.data_helper.data[row_key]
            image_id = item['image_id']
            alist = self.data_helper.annotation_data[image_id]
            # no need to copy annotation, clone has different annotation
            alist.append({})
            json_alist = json.dumps(alist)
            sql = f"UPDATE image SET annotation='{json_alist}' WHERE image_id={image_id}"
            self.app.db.exec_sql(sql, True)

        self.refresh()

    def _remove_rows_key_DEPRICATED(self, row_key):
        sql = ''
        item = self.data_helper.data[row_key]
        image_id = item['image_id']
        adata = self.data_helper.annotation_data[image_id]
        annotation_index = int(row_key.split('-')[1])
        adata_item = adata[annotation_index]

        if annotation_index == 0:  # 目前只刪除 cloned rows 所以不會有這個
            if len(adata) > 1:
                # remove root item
                ans = tk.messagebox.askquestion('注意', '刪除此列會將複製出來的資料一併刪除?')
                if ans == 'yes':
                    sql = f"DELETE FROM image WHERE image_id={image_id}"
            else:
                # no clone, just delete
                sql = f"DELETE FROM image WHERE image_id={image_id}"
        else:
            adata.remove(adata_item)
            json_data = json.dumps(adata)
            sql = f"UPDATE image SET annotation='{json_data}' WHERE image_id={image_id}"

        #if sql:
        #    self.app.db.exec_sql(sql, True)

        # self.refresh() # do not refresh, if remove multi rows, cause error

    def custom_remove_rows(self, deleted_row_keys):
        # rows = self.data_grid.get_row_list()
        #self._remove_rows(deleted_row_keys)
        # must be cloned row_keys
        tmp = {}
        # 整理 {image_id: adata} 關係
        for row_key in deleted_row_keys:
            item = self.data_helper.data[row_key]
            image_id = item['image_id']
            if image_id not in tmp:
                alist = self.data_helper.annotation_data[image_id]
                adata = {idx: values for idx, values in enumerate(alist)}
                tmp[str(image_id)] = adata

        # if tmp = {} ( no clone, do nothing, not to remove)
        # print(tmp, deleted_row_keys)

        if len(deleted_row_keys) > 0:
            ok = tk.messagebox.askokcancel('確認刪除', '確認要刪除複製出來的照片?')
            if not ok:
                self.refresh() # DataGrid will delete row when in CLONE mode, do refresh can hide this effect
                return

        # delete adata
        for row_key in deleted_row_keys:
            rk = row_key.split('-')
            image_id = rk[0].replace('iid:', '')
            annotation_index = int(rk[1])
            del tmp[image_id][annotation_index]

        for image_str, adata in tmp.items():
            alist = [x for _, x in adata.items()]
            image_id = int(image_str)
            json_data = json.dumps(alist)
            sql = f"UPDATE image SET annotation='{json_data}' WHERE image_id={image_id}"
            self.app.db.exec_sql(sql, True)

        # update source status & refresh
        sql = f"SELECT COUNT(*) FROM image WHERE source_id = {self.source_id}"
        res = self.app.db.fetch_sql(sql)
        if res:
            sql = f"UPDATE source SET count={res[0]} WHERE source_id={self.source_id}"
            self.app.db.exec_sql(sql, True)
            # self.app.frames['folder_list'].refresh_source_list()
            self.refresh()

    def custom_paste_from_buffer(self, buf, rows):
        #print('paste !!', buf, rows)
        self.refresh()

    # def custom_apply_pattern(self, pattern_copy, selected):
    #     print (pattern_copy, selected)
    #     num_pattern = len(pattern_copy)
    #     for counter, row in enumerate(selected['row_list']):
    #         pat_index = counter%num_pattern
    #         rc_key = self.data_helper.get_rc_key(row, selected['col_list'][0])
    #         self.custom_set_data(rc_key[0], rc_key[1], pattern_copy[pat_index])

    #     self.data_grid.main_table.pattern_copy = []
    #     self.refresh()

    def copy_cloned_species(self):
        rows = self.data_grid.row_index.get_selected_rows()
        self.species_copy = []
        for row in rows:
            item = self.data_helper.get_item(row)
            species = item['annotation_species']
            self.species_copy.append(species)

    def handle_click_menu_species(self, species=''):
        logging.debug('add annotation from menu species: {species} ({self.current_row_key})')
        #if self.current_row < 0:
        #    return

        row_list = self.data_grid.get_row_list()
        for row in row_list:
            # 要用 main_table.get_rc_key (有考慮pagination) 取得 row_key
            row_key, _ = self.data_grid.main_table.get_rc_key(row, 0)
            #row_key, _ = self.data_helper.get_rc_key(row, 0)
            self.data_helper.update_annotation(row_key, 'annotation_species', species, self.seq_info)
        self.refresh()

    def handle_keyboard_shortcut(self, event):
        #print ('key', event)
        #selected = self.data_grid.main_table.selected
        #rows = self.data_grid.row_index.get_selected_rows()
        rows = self.data_grid.get_row_list()
        logging.debug('rows: {}'.format(rows))
        if value := self.keyboard_shortcuts.get(event.keysym, ''):
            for row in rows:
                row_key, col_key = self.data_grid.main_table.get_rc_key(row, SPECIES_COL_POS)
                self.data_helper.update_annotation(row_key, col_key, value, self.seq_info)

        self.refresh()
        cur_page = self.data_grid.state['pagination']['current_page']
        if cur_page > 1:
            self.custom_to_page()

    def set_test_foto_by_time(self):
        time_str = self.test_foto_val.get()
        print(time_str)
        if time_str := self.test_foto_val.get():
            if m := re.search(r'([0-9]{2}):([0-9]{2}):([0-9]{2})', time_str):
                hh = m.group(1)
                mm = m.group(2)
                ss = m.group(3)
                if int(hh) >= 0 and int(hh) <= 24 \
                   and int(mm) >= 0 and int(mm) <= 60 \
                   and int(ss) >= 0 and int(ss) <= 60:
                    #test_foto_ids = []
                    for row_key, item in self.data_helper.data.items():
                        image_hms = datetime.fromtimestamp(item['time']).strftime('%H:%M:%S')

                        if image_hms == time_str:
                            self.data_helper.update_annotation(row_key, 'annotation_species', '測試')


                    sql = "UPDATE source SET test_foto_time='{}' WHERE source_id={}".format(time_str ,self.source_data['source'][0])
                    self.app.db.exec_sql(sql, True)
                    self.refresh()
                    tk.messagebox.showinfo('info', f'已設定測試照 - {time_str}')

    def handle_entry_change(self, *args):
        if self.is_editing is False:
            return

        trace_args = args[0]
        key = args[1]
        col = key
        logging.debug('entry_name: {}'.format(key))
        value = ''
        if key == 'trip_start':
            value = self.trip_start_var.get()
        elif key == 'trip_end':
            value = self.trip_end_var.get()

        if key in ['trip_start', 'trip_end']:  # trace 會出發所有 entry 的動作?
            # save to db
            sql = "UPDATE source SET {}='{}' WHERE source_id={}".format(col, value, self.source_id)
            self.app.db.exec_sql(sql, True)

    def show_image_detail(self):
        row_key = self.current_row_key
        #print(self.current_image_data)
        if item := self.data_helper.data[row_key]:

            if item['media_type'] == 'image':
                # stop tabel keyboard control
                #self.data_grid.main_table.set_keyboard_control(False)

                image_path = item['thumb'].replace('-q.', '-o.')
                self.image_detail = ImageDetail(self, image_path)
            else:
                # VideoPlayer(self, item['path'])
                # pyinstaller build will caused imageoi-ffmpeg not found!
                subprocess.run(['C:\Program Files\Windows Media Player\wmplayer.exe', item['path']])


    def export_csv(self):
        folder_name = self.source_data['source'][3]
        save_as = tk.filedialog.asksaveasfilename(
            defaultextension='csv', initialfile=f'export-{folder_name}')
        if not save_as:
            return False

        with open(f'{save_as}', 'w', newline='') as csvfile:
            spamwriter = csv.writer(
                csvfile,
                delimiter=',',
                quotechar='|',
                quoting=csv.QUOTE_MINIMAL)
            header = []
            for k, v in self.data_helper.columns.items():
                if k != 'thumb':
                    header.append(v['label'])
            spamwriter.writerow(header)
            for _, v in self.data_helper.data.items():
                spamwriter.writerow([v[k] for k, _ in self.data_helper.columns.items() if k != 'thumb'])
        tk.messagebox.showinfo('info', f'匯出 csv 成功! ({save_as})')

    def show_video_icon(self):
        photo = ImageTk.PhotoImage(file='./assets/movie_big.png')
        self.image_thumb_label.configure(image=photo)
        self.image_thumb_label.image = photo

        self.image_viewer_button.place(x=421-46, y=270, anchor='nw')

        self.update_idletasks()

    def rebind_keyboard_shortcut(self):
        custom_binding = {
            'bind_list': [],
            'command': self.handle_keyboard_shortcut,
        }
        self.keyboard_shortcuts = {}
        for n in range(0, 10):
            self.keyboard_shortcuts[str(n)] = self.app.config.get('KeyboardShortcut', f'Control-Key-{n}')
            custom_binding['bind_list'].append(f'Control-Key-{n}')

        self.data_grid.main_table.apply_custom_binding(custom_binding)

    #def resize_datagrid(self):
    #    self.data_grid.update_state({'height': 900})
    #    self.data_grid.main_table.config(height=900)
