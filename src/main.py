import tkinter as tk
from tkinter import ttk

from helpers import (
    HEADING,
    image_list_to_table,
    get_tree_rc,
    get_tree_rc_point,
)

from autocomplete_widget import FreeSolo

class Main(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)

        #self.parent = parent
        self.app = parent

        self.source_data = {}
        self.projects = self.app.server.projects
        self.id_map = {
            'project': {},
            'studyarea': {},
            'deployment': {},
            'sa_to_d': {}
        }
        self.id_map['project'] = {x['name']: x['project_id'] for x in self.projects}

        # layout
        #self.grid_propagate(False)
        self.layout()
        self.config_ctrl_frame()
        self.config_table_frame()

    def layout(self):
        '''
        ====================
        | ctrl_frame       |
        |-------------+----|
        | table_frame | *1 |  <- panned window
        ====================
        *1 thumbnail_frame
        '''
        self.grid_rowconfigure(0, weight=0) # fix
        #self.grid_rowconfigure(1, weight=1) # expand vertical
        self.grid_columnconfigure(0, weight=1)
        #self.grid_columnconfigure(1, weight=0) # fix
        #self.grid_columnconfigure(2, weight=0) # fix



        self.panedwindow = ttk.PanedWindow(self, orient=tk.HORIZONTAL)
        self.panedwindow.pack(fill=tk.BOTH, expand=True)
        self.panedwindow.grid_rowconfigure(0, weight=1)
        self.panedwindow.grid_columnconfigure(0, weight=1)

        self.ctrl_frame = tk.Frame(self, bg='#ef8354')
        self.table_frame = tk.Frame(self.panedwindow, bg='#2d3142')
        #self.right_frame = tk.Frame(self.panedwindow, bg='brown')

        self.panedwindow.add(self.table_frame)
        self.panedwindow.add(self.ctrl_frame)

        #self.panedwindow.configure(self.thumbnail_frame, width=200, height=400, sticky='ewsn')

    def config_ctrl_frame(self):
        # project menu
        self.label_project = ttk.Label(self.ctrl_frame,  text='計畫')
        self.label_project.grid(row=0, column=0)
        self.project_options = [x['name'] for x in self.projects]
        self.project_var = tk.StringVar(self)
        self.project_menu = tk.OptionMenu(
            self.ctrl_frame,
            self.project_var,
            '-- 選擇計畫 --',
            *self.project_options,
            command=self.project_option_changed)
        self.project_menu.grid(row=0, column=1, sticky=tk.W)

        # studyarea menu
        self.label_studyarea = ttk.Label(self.ctrl_frame,  text='| 樣區')
        self.label_studyarea.grid(row=0, column=2)
        self.studyarea_var = tk.StringVar()
        self.studyarea_options = []
        self.studyarea_menu = tk.OptionMenu(
            self.ctrl_frame,
            self.studyarea_var,
            '')
        self.studyarea_var.trace('w', self.studyarea_option_changed)
        self.studyarea_menu.grid(row=0, column=3, sticky=tk.W)

        # deployment menu
        self.label_deployment = ttk.Label(self.ctrl_frame,  text=' | 相機位置')
        self.label_deployment.grid(row=0, column=4)
        self.deployment_options = []
        self.deployment_var = tk.StringVar(self.ctrl_frame)
        self.deployment_var.trace('w', self.deployment_option_changed)
        self.deployment_menu = tk.OptionMenu(
            self.ctrl_frame,
            self.deployment_var,
            '')
        self.deployment_menu.grid(row=0, column=5, sticky=tk.W)

        # upload button
        self.upload_button = ttk.Button(
            self.ctrl_frame,
            text='上傳',
            command=self.on_upload)
        self.upload_button.grid(row=0, column=6, padx=20, sticky='w')

        # save button
        self.save_button = ttk.Button(
            self.ctrl_frame,
            text='儲存',
            command=self.on_save)
        self.save_button.grid(row=0, column=7, padx=5, sticky='e')

        # image sequence
        #self.seq_label = ttk.Label(self.ctrl_frame,  text='連拍自動補齊')
        #self.seq_label.grid(row=1, column=0)
        self.seq_checkbox_val = tk.StringVar(self)
        self.seq_checkbox = ttk.Checkbutton(
            self.ctrl_frame,
            text='連拍自動補齊',
	    command=self.on_seq_check,
            variable=self.seq_checkbox_val,
	    onvalue='Y',
            offvalue='N')
        self.seq_checkbox.grid(row=1, column=0)

        self.seq_interval_val = tk.StringVar(self)
        #self.seq_interval_val.trace('w', self.on_seq_interval_changed)
        self.seq_interval_entry = ttk.Entry(
            self.ctrl_frame,
            textvariable=self.seq_interval_val,
            width=4,
            #validate='focusout',
            #validatecommand=self.on_seq_interval_changed
        )
        self.seq_interval_entry.bind("<KeyRelease>", self.on_seq_interval_changed)
        self.seq_interval_entry.grid(row=1, column=1)

        self.seq_unit = ttk.Label(self.ctrl_frame,  text='分鐘 (相鄰照片間隔__分鐘，自動補齊所編輯的欄位資料)')
        self.seq_unit.grid(row=1, column=2)

    def config_table_frame(self):
        self.table_frame.grid_columnconfigure(0, weight=2)
        self.table_frame.grid_columnconfigure(1, weight=0)
        self.table_frame.grid_rowconfigure(0, weight=2)
        self.table_frame.grid_rowconfigure(1, weight=0)
        #print (self.table_frame.grid_info(), self.table_frame.grid_bbox())

        #self.message = ttk.Label(self.table_frame, text="Hello", width=50)
        #self.message.grid(row=0, column=0, sticky='nsew', padx=10, pady=10)

        # treeview

        self.tree = ttk.Treeview(
            self.table_frame,
            columns=[x[0] for x in HEADING],
            show='headings')
        self.tree.bind('<<TreeviewSelect>>', self.select_cell)
        #self.tree.bind('<<TreeviewOpen>>', self.select_open)
        #self.tree.bind('<<TreeviewClose>>', self.select_close)
        self.tree.bind('<ButtonRelease-1>', self.on_click)

        for i in HEADING:
            self.tree.heading(i[0], text=i[1])

        self.tree.column('status', width=40, stretch=False)
        self.tree.column('filename', width=150, stretch=False)
        self.tree.column('datetime', width=150, stretch=False)
        self.tree.column('species', width=150, stretch=False)
        self.tree.column('antler', width=50, stretch=False)
        self.tree.column('sex', width=50, stretch=False)
        self.tree.column('lifestage', width=50, stretch=False)
        self.tree.column('remark', width=50, stretch=False)
        self.tree.column('animal_id', width=50, stretch=False)

        self.tree.grid(row=0, column=0, sticky='nsew')

        scrollbar_x = ttk.Scrollbar(self.table_frame, orient=tk.HORIZONTAL, command=self.tree.xview)
        scrollbar_y = ttk.Scrollbar(self.table_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(
            xscroll=scrollbar_x.set,
            yscroll=scrollbar_y.set
        )
        scrollbar_x.grid(row=1, column=0, sticky='ew')
        scrollbar_y.grid(row=0, column=1, sticky='ns')

    def refresh(self, source_id):
        # get source_data
        self.source_id = source_id
        #self.source_id = self.parent.state.get('source_id', '')
        self.source_data = self.app.source.get_source(source_id)
        self.tree.delete(*self.tree.get_children())
        data = image_list_to_table(self.source_data['image_list'])
        for i in data:
            self.tree.insert('', tk.END, values=i)

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

            # save to db
            sql = "UPDATE source SET description='{}' WHERE source_id={}".format(json.dumps(descr), self.source_id)
            self.app.db.exec_sql(sql, True)

            self.source_id = self.parent.state.get('source_id', '')
            # update source_data (for upload: first time import folder, get no deployment_id even if selected)
            self.source_data = self.app.source.get_source(self.source_id)
            # TODO
            #tk.messagebox.showinfo('info', '已設定相機位置')
    def on_upload(self):
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
            print ('uploaded', i, v)
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

    def on_save(self):
        d = self.sheet.get_sheet_data()
        for i, v in enumerate(d):
            row = {}
            if len(v) >= 4:
                row['species'] = v[3]
            if len(v) >= 5:
                row['lifestage'] = v[4]
            if len(v) >= 6:
                row['sex'] = v[5]
            if len(v) >= 7:
                row['antler'] = v[6]
            if len(v) >= 8:
                row['remarks'] = v[7]
            if len(v) >= 9:
                row['animal_id'] = v[8]

            image_id = self.sheet_data[i][9]['image_id']
            if image_id:
                sql = "UPDATE image SET annotation='[{}]', changed={} WHERE image_id='{}'".format(json.dumps(row), int(time.time()), image_id)
                self.app.db.exec_sql(sql)
        self.app.db.commit()
        tk.messagebox.showinfo('info', '儲存成功')

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

    def on_seq_check(self):
        self.refresh()

    def on_seq_interval_changed(self, *args):
        self.refresh()

    def select_cell(self, event):
        for selected_item in self.tree.selection():
            # dictionary
            item = self.tree.item(selected_item)
            # list
            record = item['values']
            #
            print ('|'.join(record))

    def on_click(self, event):
        username = tk.StringVar()
        self.name = ttk.Entry(self.tree, textvariable=username)

        #self.freesolo = FreeSolo(self.table_frame, ['abba', 'ace of base', 'ac/dc', 'alice in chain'], self.get_freesolo_value, height=20, width=40)
        #self.freesolo.place(x=300, y=300, height=20, width=40)
        r, c = get_tree_rc(self.tree)
        if not r or not c:
            return False
        x, y = get_tree_rc_point(self.tree, r, c)
        #print (x, y)
        self.name.place(x=x, y=y, width=100, height=30)
        self.name.focus_set()
        self.name.bind("<FocusOut>", lambda e: self.focus_out(e))
        #for item in self.tree.selection():
        #    item_text = self.tree.item(item,"values")
            #print(item_text[0])

    def get_freesolo_value(self, text):
        print ('vv', text)

    def focus_out(self, event):
        print (event)
        if self.name:
            self.name.destroy()

