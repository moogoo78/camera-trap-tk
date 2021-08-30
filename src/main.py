import json
import time
import pathlib
import sys
import tkinter as tk
from tkinter import ttk
import logging

from PIL import ImageTk, Image

from helpers import (
    FreeSolo,
    TreeHelper,
    DataHelper,
)
from frame import UploadProgress
from image import check_thumb

sys.path.insert(0, '') # TODO: pip install -e .
from tkdatagrid import DataGrid


class Main(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)

        self.parent = parent
        self.app = parent

        self.source_data = {}
        # self.projects = self.app.server.projects
        # self.id_map = {
        #     'project': {},
        #     'studyarea': {},
        #     'deployment': {},
        #     'sa_to_d': {}
        # }
        # self.id_map['project'] = {x['name']: x['project_id'] for x in self.projects}
        self.projects = []
        self.update_project_options()

        self.source_id = None
        self.current_row = 0
        self.current_image_index = 0
        self.thumb_basewidth = 500

        self.tree_helper = TreeHelper()
        self.data_helper = DataHelper(self.app.db)
        self.annotation_entry_list = []
        self.species_copy = []

        # layout
        #self.grid_propagate(False)
        self.layout()

        self.layout_landing()

        #self.config_ctrl_frame()
        #self.config_table_frame()

        #self.queue = queue.Queue()
        self.upload_status = 0 # 0: stop, 1: start, 2: pause
        #self.thread = threading.Thread(target=self.worker)
        #self.polling()

    def handle_panedwindow_release(self, event):
        w = self.right_frame.winfo_width()
        # border: 8, padx: 10
        self.thumb_basewidth = w - 36
        data = self.get_current_item('data')

        '''210730
        if data:
            self.show_image(data['thumb'], data['path'])
        elif self.tree_helper.data:
            # when default no selection
            self.show_thumb(self.tree_helper.data[0]['thumb'], self.tree_helper.data[0]['path'])
        '''

    def layout_landing(self):
        self.landing_frame = tk.Frame(self.parent, background='#2d3142')
        self.message = ttk.Label(self.landing_frame, text="Welcome !!")
        self.message.grid(row=0, column=0, sticky='nsew', padx=10, pady=10)
        self.landing_frame.grid(row=2, column=1, sticky='nsew')

    def layout(self):
        self.grid_rowconfigure(0, weight=0)
        self.grid_columnconfigure(0, weight=0)

        self.notebook = ttk.Notebook(self)
        self.notebook.grid(row=0, column=0)

        #panedwindow_style = ttk.Style()
        self.panedwindow = ttk.PanedWindow(self.notebook, orient=tk.VERTICAL)
        #panedwindow_style = configure('PanedWindow', sashpad=5)
        self.panedwindow.pack(fill=tk.BOTH, expand=True)
        self.panedwindow.grid_rowconfigure(0, weight=1)
        self.panedwindow.grid_columnconfigure(0, weight=1)
        #self.panedwindow.bind("<ButtonRelease-1>", self.handle_panedwindow_release)
        self.top_paned_frame = tk.Frame(self.panedwindow, bg='#2d3142')
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
        self.image_thumb_label = ttk.Label(self.image_thumb_frame, border=2, relief='raised')
        self.image_thumb_label.grid(row=0, column=0, sticky='ns', padx=4, pady=4)


        self.ctrl_frame = tk.Frame(self.top_paned_frame)
        self.ctrl_frame.grid(row=0, column=1, sticky='nw')

        self.config_ctrl_frame()

        # bottom_paned
        self.bottom_paned_frame.grid_rowconfigure(0, weight=1)
        self.bottom_paned_frame.grid_columnconfigure(0, weight=1)
        self.table_frame = tk.Frame(self.bottom_paned_frame)
        self.table_frame.grid(row=0, column=0, sticky='news')

        self.config_table_frame()

        self.upload_progress = UploadProgress(self)
        self.upload_progress.grid(row=0,column=0)
        self.notebook.add(self.panedwindow, text='輸入資料')
        self.notebook.add(self.upload_progress, text='上傳進度')
        self.notebook.bind('<<NotebookTabChanged>>', self.handle_notebook_change)
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
        self.ctrl_frame.grid_rowconfigure(0, weight=0)
        self.ctrl_frame.grid_columnconfigure(0, weight=0)


        self.label_folder = ttk.Label(
            self.ctrl_frame,
            text='',
            font=self.app.nice_font['h2'])

        self.label_folder.grid(row=0, column=0, padx=4, pady=10, sticky='nw')
        image_viewer_button = ttk.Button(
            self.ctrl_frame,
            text='看大圖',
            command=self.handle_image_viewer
        )
        image_viewer_button.grid(row=0, column=0, padx=4, pady=4, sticky='ne')

        sep = ttk.Separator(self.ctrl_frame, orient='horizontal')
        sep.grid(row=1, column=0, pady=(0, 8), sticky='ew')

        self.ctrl_frame2 = tk.Frame(self.ctrl_frame)
        self.ctrl_frame2.grid_rowconfigure(0, weight=0)
        self.ctrl_frame2.grid_rowconfigure(1, weight=0)
        self.ctrl_frame2.grid_rowconfigure(2, weight=0)
        self.ctrl_frame2.grid_columnconfigure(0, weight=0)
        self.ctrl_frame2.grid_columnconfigure(1, weight=1)
        self.ctrl_frame2.grid(row=2, column=0, sticky='ew')

        # project menu
        self.label_project = ttk.Label(self.ctrl_frame2, text='計畫')
        self.label_project.grid(row=0, column=0)
        self.project_options = [x['name'] for x in self.projects]
        self.project_var = tk.StringVar(self)
        self.project_menu = tk.OptionMenu(
            self.ctrl_frame2,
            self.project_var,
            '-- 選擇計畫 --',
            *self.project_options,
            command=self.project_option_changed)
        self.project_menu.grid(row=0, column=1, sticky=tk.W, padx=(6, 16))

        # studyarea menu
        self.label_studyarea = ttk.Label(self.ctrl_frame2,  text='樣區')
        self.label_studyarea.grid(row=1, column=0)
        self.studyarea_var = tk.StringVar()
        self.studyarea_options = []
        self.studyarea_menu = tk.OptionMenu(
            self.ctrl_frame2,
            self.studyarea_var,
            '')
        self.studyarea_var.trace('w', self.studyarea_option_changed)
        self.studyarea_menu.grid(row=1, column=1, sticky=tk.W,padx=(6, 20))

        # deployment menu
        self.label_deployment = ttk.Label(self.ctrl_frame2,  text='相機位置')
        self.label_deployment.grid(row=2, column=0)
        self.deployment_options = []
        self.deployment_var = tk.StringVar(self.ctrl_frame)
        self.deployment_var.trace('w', self.deployment_option_changed)
        self.deployment_menu = tk.OptionMenu(
            self.ctrl_frame2,
            self.deployment_var,
            '')
        self.deployment_menu.grid(row=2, column=1, sticky=tk.W, padx=(6, 20))

        sep2 = ttk.Separator(self.ctrl_frame, orient='horizontal')
        sep2.grid(row=3, column=0, pady=6, sticky='ew')

        self.ctrl_frame3 = tk.Frame(self.ctrl_frame)
        self.ctrl_frame3.grid_rowconfigure(0, weight=0)
        self.ctrl_frame3.grid_columnconfigure(0, weight=0)
        self.ctrl_frame3.grid_columnconfigure(1, weight=0)
        self.ctrl_frame3.grid_columnconfigure(2, weight=0)
        self.ctrl_frame3.grid(row=4, column=0, sticky='nw', pady=10)

        # image sequence
        self.seq_checkbox_val = tk.StringVar(self)
        self.seq_checkbox = ttk.Checkbutton(
            self.ctrl_frame3,
            text='連拍分組',
	    command=self.refresh,
            variable=self.seq_checkbox_val,
	    onvalue='Y',
            offvalue='N')
        self.seq_checkbox.grid(row=0, column=0, padx=(4, 10), sticky='w')

        self.seq_interval_val = tk.StringVar(self)
        #self.seq_interval_val.trace('w', self.on_seq_interval_changed)
        self.seq_interval_entry = ttk.Entry(
            self.ctrl_frame3,
            textvariable=self.seq_interval_val,
            width=4,
            #validate='focusout',
            #validatecommand=self.on_seq_interval_changed
        )
        self.seq_interval_entry.bind(
            "<KeyRelease>", lambda _: self.refresh())
        self.seq_interval_entry.grid(row=0, column=1, sticky='w')

        self.seq_unit = ttk.Label(self.ctrl_frame3,  text='分鐘 (相鄰照片間隔__分鐘，顯示分組)')
        self.seq_unit.grid(row=0, column=2, sticky='we')

        sep = ttk.Separator(self.ctrl_frame, orient='horizontal')
        sep.grid(row=5, column=0, pady=6, sticky='ew')

        self.ctrl_frame4 = tk.Frame(self.ctrl_frame)
        self.ctrl_frame4.grid_rowconfigure(0, weight=0)
        self.ctrl_frame4.grid_rowconfigure(1, weight=0)
        self.ctrl_frame4.grid_columnconfigure(0, weight=0)
        self.ctrl_frame4.grid(row=6, column=0, sticky='w')

        # upload button
        self.upload_button = ttk.Button(
            self.ctrl_frame4,
            text='上傳',
            #command=self.handle_upload
            #command=lambda: self.foo_worker.do_work()
            command=self.handle_upload2
        )
        self.upload_button.grid(row=0, column=0, padx=20, pady=4, sticky='w')

        self.delete_button = ttk.Button(
            self.ctrl_frame4,
            text='刪除資料夾',
            command=self.handle_delete)
        self.delete_button.grid(row=1, column=0, padx=20, pady=4, sticky='w')


    def config_table_frame(self):
        self.table_frame.grid_columnconfigure(0, weight=0)
        self.table_frame.grid_rowconfigure(0, weight=1)
        #print (self.table_frame.grid_info(), self.table_frame.grid_bbox())

        menus = [
            {
                'label': '複製物種',
                'command': self.copy_cloned_species,
            },
            {
                'label': '貼上物種',
                'command': self.paste_cloned_species,
            }
        ]
        self.data_grid = DataGrid(self.table_frame, data={}, columns=self.data_helper.columns, height=760-400, row_index_display='sn', custom_menus=menus)
        # TODO: 400 是湊出來的
        self.data_grid.state.update({
            'cell_height': 35,
            'cell_image_x_pad': 3,
            'cell_image_y_pad': 1,
            'custom_actions': {
                'remove_row': self.custom_remove_row,
                'clone_row': self.custom_clone_row,
                'mouse_click': self.custom_mouse_click,
                'arrow_key': self.custom_arrow_key,
                'set_data': self.custom_set_data,
                'apply_pattern': self.custom_apply_pattern,
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

    def from_source(self, source_id=None):
        # no need landing
        self.landing_frame.destroy()

        self.app.begin_from_source()
        self.update_project_options()
        self.source_id = source_id
        self.refresh()


    def refresh(self):
        logging.debug('refresh: {}'.format(self.source_id))

        if not self.source_id:
            return

        self.notebook.select(self.panedwindow)

        self.source_data = self.app.source.get_source(self.source_id)
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

        # update upload_button
        source_status = self.source_data['source'][6]
        if source_status == '20':
            self.upload_button['text'] = '上傳中'
        elif source_status == '40':
            self.upload_button['text'] = '已上傳'
        else:
            self.upload_button['text'] = '上傳'

        if source_status != '10':
            self.upload_button['state'] = 'disabled'
        else:
            self.upload_button['state'] = 'normal'

        # data list
        data = self.data_helper.read_image_list(self.source_data['image_list'])
        #print (data)
        self.seq_info = None
        seq_int = self.seq_interval_val.get()
        if self.seq_checkbox_val.get() == 'Y' and seq_int:
            self.seq_info = self.data_helper.group_image_sequence(seq_int)

        # show first image if no select
        first_key = next(iter(data))
        first_item = data[first_key]
        self.show_image(first_item['thumb'], first_item['path'], 'm')

        self.data_grid.main_table.delete('row-img-seq')
        self.data_grid.refresh(data)
        # draw img_seq
        for i, (iid, row) in enumerate(data.items()):
            tag_name = row.get('img_seq_tag_name', '')
            color = row.get('img_seq_color', '')
            y1 = self.data_grid.state['cell_height'] * i
            y2 = self.data_grid.state['cell_height'] * (i+1)
            if tag_name and color:
                self.data_grid.main_table.create_rectangle(
                    0, y1, self.data_grid.main_table.width + self.data_grid.main_table.x_start, y2,
                    fill=color,
                    tags=('row-img-seq', 'row-img-seq_{}'.format(tag_name)))

        self.data_grid.main_table.lower('row-img-seq')
        self.data_grid.main_table.render_row_highlight()

        # folder name
        self.label_folder['text'] = self.source_data['source'][3]


    def project_option_changed(self, *args):
        name = self.project_var.get()
        id_ = self.id_map['project'].get(name,'')
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

    def handle_upload2(self):
        # check deployment
        deployment_id = ''
        if descr := self.source_data['source'][7]:
            d = json.loads(descr)
            deployment_id = d.get('deployment_id', '')

        if deployment_id == '':
            tk.messagebox.showinfo('info', '末設定相機位置，無法上傳')
            return False

        image_list = self.source_data['image_list']
        source_id = self.source_id
        data = {
            'source': self.source_data['source'],
            'image_list': image_list,
            'deployment_id': deployment_id
        }

        # 1. post annotation to server
        sql = "UPDATE image SET upload_status='100' WHERE image_id IN ({})".format(','.join([str(x[0]) for x in image_list]))
        self.app.db.exec_sql(sql, True)

        account_id = self.app.config.get('Installation', 'account_id')
        # post to server
        payload = {
            'image_list': image_list,
            'key': f'{account_id}-{source_id}',
            'deployment_id': deployment_id,
        }
        res = self.app.server.post_annotation(payload)
        if res['error']:
            tk.messagebox.showerror('上傳失敗 (server error)', f"{res['error']}")
            return

        server_image_map = res['data']
        if self.source_data['source'][6] == '10':
            sql = f"UPDATE source SET status='20' WHERE source_id={source_id}"
            self.app.db.exec_sql(sql, True)

        for image_id, server_image_id in server_image_map.items():
            sql = f"UPDATE image SET upload_status='100', server_image_id={server_image_id} WHERE image_id={image_id}"
            self.app.db.exec_sql(sql)
        self.app.db.commit()

        self.upload_progress.create_upload_process(data)

        self.upload_button['text'] = '上傳中'
        self.upload_button['state'] = 'disabled'

    def handle_notebook_change(self, event):
        tab = event.widget.tab('current')['text']
        if tab == '輸入資料':
            self.refresh()

    def handle_upload(self):
        #self.app.source.do_upload(self.source_data)
        ans = tk.messagebox.askquestion('上傳確認', '確定要上傳?')
        if ans == 'no':
            return False

        image_list = self.source_data['image_list']
        source_id = self.source_data['source'][0]
        deployment_id = ''

        if descr := self.source_data['source'][7]:
            d = json.loads(descr)
            deployment_id = d.get('deployment_id', '')

        if deployment_id == '':
            tk.messagebox.showinfo('info', '末設定相機位置，無法上傳')
            return False

        pb = self.app.statusbar.progress_bar
        start_val = len(image_list) * 0.05 # 5% for display pre s3 upload
        pb['maximum'] = len(image_list) + start_val
        pb['value'] = start_val
        self.update_idletasks()

        res = self.app.source.upload_annotation(image_list, source_id, deployment_id)

        if res['error']:
            tk.messagebox.showerror('上傳失敗', f"{res['error']}")
            return False

        saved_image_ids = res['data']
        for i, v in enumerate(self.app.source.gen_upload_file(image_list, source_id, deployment_id, saved_image_ids)):
            #print ('uploaded', i, v)
            if v:
                # update progress bar
                pb['value'] = i+1
                self.update_idletasks()

                local_image_id = v[0]
                server_image_id = v[1]
                s3_key = v[2]
                sql = 'UPDATE image SET upload_status="200", server_image_id={} WHERE image_id={}'.format(server_image_id, local_image_id)
                self.app.db.exec_sql(sql, True)

                # update server image status
                self.app.server.post_image_status({
                    'file_url': s3_key,
                    'pk': server_image_id,
                })

        # finish upload
        pb['value'] = 0
        self.update_idletasks()
        tk.messagebox.showinfo('info', '上傳成功')

    def handle_delete(self):
        ans = tk.messagebox.askquestion('確認', f"確定要刪除資料夾: {self.source_data['source'][3]}?")
        if ans == 'no':
            return False

        self.app.source.delete_folder(self.source_id)
        self.app.sidebar.refresh_source_list()
        self.layout_landing()

    def get_status_display(self, code):
        status_map = {
            '10': 'new',
            '20': 'viewed',
            '30': 'annotated',
            '100': 'start',
            '110': '-',
            '200': 'uploaded',
        }
        return status_map.get(code, '-')

    def custom_set_data(self, row_key, col_key, value):
        #print ('custom_set_data', value)
        self.data_helper.update_annotation(row_key, col_key, value, self.seq_info)
        if self.seq_info:
            # has seq_info need re-render
            self.refresh()

    def select_item(self, rc):
        if rc == None:
            return

        item = self.data_helper.get_item(rc[0])
        #self.current_image_index = self.data_helper.get_image_index(rc[0])
        self.current_row = rc[0]
        if item and item['status'] == '10':
            image_id = item['image_id']
            sql = f"UPDATE image SET status='20' WHERE image_id={image_id}"
            self.app.db.exec_sql(sql, True)
            row_key, col_key = self.data_grid.main_table.get_rc_key(rc[0], rc[1])
            #self.data_grid.main_table.set_data_value(row_key, col_key, 'vv')
            self.data_grid.state['data'][row_key]['status'] = self.get_status_display('20')
            self.data_grid.main_table.render()

        self.show_image(item['thumb'], item['path'], 'm')

    def custom_arrow_key(self, rc):
        #print ('arrow', rc)
        self.select_item(rc)

    def custom_mouse_click(self, rc):
        #print ('handle click', rc)
        self.select_item(rc)

    def begin_edit_annotation(self, iid):
        record = self.tree.item(iid, 'values')
        a_conf = self.tree_helper.get_conf('annotation')
        for i, v in enumerate(self.annotation_entry_list):
            a_index = a_conf[i][0]
            v[1].set(record[a_index])
            if a_conf[i][1][3]['widget'] == 'freesolo':
                if v[0].listbox:
                    v[0].remove_listbox()

        # set first entry focus
        #self.annotation_entry_list([0][0].focus()) # not work ?
        # !!
        #print (self.annotation_entry_list[0][0].set_focus())

    def show_image(self, thumb_path, image_path, size_key=''):
        if size_key:
            thumb_path = thumb_path.replace('-q.jpg', '-{}.jpg'.format(size_key))

        real_thumb_path = check_thumb(thumb_path, image_path)
        image = Image.open(real_thumb_path)
        # aspect ratio
        basewidth = self.thumb_basewidth
        wpercent = (basewidth/float(image.size[0]))
        hsize = int((float(image.size[1])*float(wpercent)))
        img = image.resize((basewidth, hsize))
        #img = image.resize((300,300), Image.ANTIALIAS)
        photo = ImageTk.PhotoImage(img)
        self.image_thumb_label.configure(image=photo)
        self.image_thumb_label.image = photo
        self.update_idletasks()

    def _get_alist(self, iid, iid_parent):
        annotation_iid = iid if iid_parent == '' else iid_parent
        row = self.tree_helper.get_data(annotation_iid)
        return row.get('alist', [])

    #def custom_clone_row(self, row_key, clone_iid):
    def custom_clone_row(self, res):
        #print ('clone', row_key, clone_iid)
        for (row_key, clone_iid) in res:
            iid_list = row_key[4:].split('-')
            row_key_root = 'iid:{}-{}'.format(iid_list[0], iid_list[1])
            item = self.data_helper.data[row_key_root]
            image_id = item['image_id']
            alist = self.data_helper.annotation_data[image_id]
            # no need to copy annotation, clone has different annotation
            alist.append({})
            json_alist = json.dumps(alist)
            sql = f"UPDATE image SET annotation='{json_alist}' WHERE image_id={image_id}"
            self.app.db.exec_sql(sql, True)
            self.refresh()

    def custom_remove_row(self, row_key):
        #print ('rm row_key', row_key)

        item = self.data_helper.data[row_key]
        image_id = item['image_id']
        adata = self.data_helper.annotation_data[image_id]
        annotation_index = int(row_key.split('-')[1])
        adata_item = adata[annotation_index]
        sql = ''
        if annotation_index == 0:
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
        if sql:
            self.app.db.exec_sql(sql, True)
        self.refresh()

    def handle_image_viewer(self):
        image_viewer = self.app.image_viewer
        sidebar = self.app.sidebar
        if image_viewer.winfo_viewable():
            image_viewer.grid_remove()
            # unbind key event
            self.app.unbind('<Left>')
            self.app.unbind('<Up>')
            self.app.unbind('<Right>')
            self.app.unbind('<Down>')
        else:
            image_viewer.grid(row=2, column=1, sticky='nsew')
            image_viewer.refresh()

        # sidebar
        if sidebar.winfo_viewable():
            sidebar.grid_remove()
        else:
            sidebar.grid()

    def custom_apply_pattern(self, pattern_copy, selected):
        #print (pattern_copy, selected)
        num_pattern = len(pattern_copy)
        for counter, row in enumerate(selected['row_list']):
            pat_index = counter%num_pattern
            rc_key = self.data_helper.get_rc_key(row, selected['col_list'][0])
            self.custom_set_data(rc_key[0], rc_key[1], pattern_copy[pat_index])

        self.data_grid.main_table.pattern_copy = []
        self.refresh()


    def copy_cloned_species(self):
        selected = self.data_grid.main_table.selected
        for row in selected['row_list']:
            item = self.data_helper.get_item(row)
            species = item['annotation_species']
            self.species_copy.append(species)

    def paste_cloned_species(self):
        selected = self.data_grid.main_table.selected
        num_species_copy = len(self.species_copy)
        for row in selected['row_list']:
            row_key, col_key = self.data_helper.get_rc_key(row, 4) # 4 is fixed to annotation_species
            #print self.data_helper.update_annotation(row_key, 'annotation_species', value)

        for counter, row in enumerate(selected['row_list']):
            index = counter % num_species_copy
            rc_key = self.data_helper.get_rc_key(row, selected['col_list'][0])
            self.data_helper.update_annotation(rc_key[0], 'annotation_species', self.species_copy[index])

        self.species_copy = []
        self.refresh()
