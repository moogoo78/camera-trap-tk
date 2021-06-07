import json
import time
import tkinter as tk
from tkinter import ttk

from PIL import ImageTk, Image

from helpers import (
    HEADING,
    image_list_to_table,
    get_tree_rc,
    get_tree_rc_place,
    FreeSolo,
)

#from autocomplete_widget import FreeSolo

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

        self.current_rc = ('', '') # DEPRICATED

        # layout
        #self.grid_propagate(False)
        self.layout()
        self.config_ctrl_frame()
        self.config_table_frame()

    def layout(self):
        '''
           left_frame        right_frame
        +================================+
        |  ctrl_frame     | +----------+ |
        +-----------------+ |thumbnail | |
        |                 | |          | |
        |  table_frame    | +----------+ |
        |                 |  annotation  |
        |                 |              |
        +=================|==============+
        '''
        self.grid_rowconfigure(0, weight=0) # fix
        self.grid_columnconfigure(0, weight=1)

        self.panedwindow = ttk.PanedWindow(self, orient=tk.HORIZONTAL)
        self.panedwindow.pack(fill=tk.BOTH, expand=True)
        self.panedwindow.grid_rowconfigure(0, weight=1)
        self.panedwindow.grid_columnconfigure(0, weight=1)

        self.right_frame = tk.Frame(self.panedwindow)
        self.left_frame = tk.Frame(self.panedwindow)
        #self.right_frame = tk.Frame(self.panedwindow, bg='brown')

        self.panedwindow.add(self.left_frame)
        self.panedwindow.add(self.right_frame)

        # layout: left frame
        self.left_frame.grid_rowconfigure(0, weight=0) # fix
        self.left_frame.grid_rowconfigure(1, weight=1) # expand vertical
        self.left_frame.grid_columnconfigure(0, weight=1)

        self.ctrl_frame = tk.Frame(self.left_frame, bg='#2d3142')
        self.table_frame = tk.Frame(self.left_frame)

        self.ctrl_frame.grid(row=0, column=0, sticky='we')
        self.table_frame.grid(row=1, column=0, sticky='news')

        self.config_ctrl_frame()
        self.config_table_frame()

        # layout: right frame
        self.right_frame.grid_rowconfigure(0, weight=0)
        self.right_frame.grid_rowconfigure(1, weight=0)
        self.right_frame.grid_columnconfigure(0, weight=1)

        # thumb
        self.image_thumb_frame = tk.Frame(self.right_frame, bg='#ef8354')
        self.image_thumb_frame.grid(row=0, column=0, sticky='nswe')

        self.image_thumb = ttk.Label(self.image_thumb_frame, border=8, relief='raised')
        self.image_thumb.grid(row=0, column=0, sticky='nw', padx=10, pady=10)

        ### annotation
        self.annotation_label_frame = ttk.LabelFrame(self.right_frame, text="影像標注")
        self.annotation_label_frame.grid(row=1, column=0, sticky='nw', padx=10, pady=10)

        self.annotation_label_frame.grid_rowconfigure(0, weight=0)
        self.annotation_label_frame.grid_rowconfigure(1, weight=0)
        self.annotation_label_frame.grid_columnconfigure(0, weight=0)
        self.annotation_label_frame.grid_columnconfigure(1, weight=0)
        self.annotation_label_frame.grid_columnconfigure(2, weight=0)

        species_label = ttk.Label(
            self.annotation_label_frame,
            text='物種')
        species_label.grid(row=0, column=0, sticky='we', pady=(6, 0))
        self.species_value = tk.StringVar()
        #self.species_entry = ttk.Entry(
        #    self.annotation_label_frame,
        #    textvariable=self.species_value
        #)
        sp_choices = self.app.config.get('AnnotationFieldSpecies', 'choices').split(',')
        self.species_free = FreeSolo(
            self.annotation_label_frame,
            sp_choices,
            value=self.species_value,
        )
        self.species_free.grid(row=1, column=0, padx=4)

        lifestage_label = ttk.Label(
            self.annotation_label_frame,
            text='年齡')
        lifestage_label.grid(row=0, column=1, sticky='we', pady=(6, 0))
        self.lifestage_value = tk.StringVar()
        #self.lifestage_entry = ttk.Entry(
        #    self.annotation_label_frame,
        #    textvariable=self.lifestage_value
        #)
        ls_choices = self.app.config.get('AnnotationFieldLifeStage', 'choices').split(',')
        self.lifestage_free = FreeSolo(
            self.annotation_label_frame,
            ls_choices,
            value=self.lifestage_value,
        )
        self.lifestage_free.grid(row=1, column=1, padx=4)

        sex_label = ttk.Label(
            self.annotation_label_frame,
            text='性別')
        sex_label.grid(row=0, column=2, sticky='we', pady=(6, 0))
        self.sex_value = tk.StringVar()
        sx_choices = self.app.config.get('AnnotationFieldSex', 'choices').split(',')
        self.sex_free = FreeSolo(
            self.annotation_label_frame,
            sx_choices,
            value=self.sex_value,
        )
        self.sex_free.grid(row=1, column=2, padx=4)

        antler_label = ttk.Label(
            self.annotation_label_frame,
            text='角況')
        antler_label.grid(row=2, column=0, sticky='we', pady=(6, 0))
        self.antler_value = tk.StringVar()
        an_choices = self.app.config.get('AnnotationFieldAntler', 'choices').split(',')
        self.antler_free = FreeSolo(
            self.annotation_label_frame,
            an_choices,
            value=self.antler_value,
        )
        self.antler_free.grid(row=3, column=0, padx=4)

        remark_label = ttk.Label(
            self.annotation_label_frame,
            text='備註')
        remark_label.grid(row=2, column=1, sticky='we', pady=(6, 0))
        self.remark_value = tk.StringVar()
        self.remark_entry = ttk.Entry(
            self.annotation_label_frame,
            textvariable=self.remark_value
        )
        self.remark_entry.grid(row=3, column=1, padx=4)

        animal_id_label = ttk.Label(
            self.annotation_label_frame,
            text='個體 ID')
        animal_id_label.grid(row=2, column=2, sticky='we', pady=(6, 0))
        self.animal_id_value = tk.StringVar()
        self.animal_id_entry = ttk.Entry(
            self.annotation_label_frame,
            textvariable=self.animal_id_value
        )
        self.animal_id_entry.grid(row=3, column=2, padx=4)

        annotation_update_button = ttk.Button(
            self.annotation_label_frame,
            text='update',
            command=self.update_annotation,
        )
        annotation_update_button.grid(row=4, column=0, padx=16, pady=16)
        annotation_clone_button = ttk.Button(
            self.annotation_label_frame,
            text='clone',
            #     command=lambda: self.app.main.show_frame('image-viewer')
        )
        annotation_clone_button.grid(row=4, column=1, padx=12, pady=12)
        #self._show_thumb()

        # self.image_viewer_button = ttk.Button(
        #     self.table_frame,
        #     text='看大圖',
        #     command=lambda: self.app.main.show_frame('image-viewer')
        # )

        #self.image_viewer_button.grid(row=1, column=1, sticky='n') 
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
            command=self.save_annotation)
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
        self.tree.row_height = 20 # TODO guess
        self.tree.bind('<<TreeviewSelect>>', self.select_cell)
        #self.tree.bind('<<TreeviewOpen>>', self.select_open)
        #self.tree.bind('<<TreeviewClose>>', self.select_close)
        self.tree.bind('<ButtonRelease-1>', self.on_click)

        for i in HEADING:
            self.tree.heading(i[0], text=i[1])

        self.tree.column('index', width=25, stretch=False)
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

        self.data = []

        # via: https://stackoverflow.com/questions/56331001/python-tkinter-treeview-colors-are-not-updating
        def fixed_map(option):
            # Returns the style map for 'option' with any styles starting with
            # ("!disabled", "!selected", ...) filtered out

            # style.map() returns an empty list for missing options, so this should
            # be future-safe
            return [elm for elm in style.map("Treeview", query_opt=option)
                    if elm[:2] != ("!disabled", "!selected")]

        style = ttk.Style()
        style.map("Treeview",
                  foreground=fixed_map("foreground"),
                  background=fixed_map("background"))

    def refresh(self, source_id):
        # get source_data
        self.source_id = source_id
        #self.source_id = self.parent.state.get('source_id', '')
        self.source_data = self.app.source.get_source(source_id)
        self.tree.delete(*self.tree.get_children())
        self.data = image_list_to_table(self.source_data['image_list'])

        for i, v in enumerate(self.data):
            if i%2 == 0:
                  self.tree.insert('', tk.END, i, values=v, tags=('even','mytag1'))
            else:
                  self.tree.insert('', tk.END, i, values=v, tags=('odd','mytag2'))
        self.tree.tag_configure('odd', background='#E8E8E8')
        self.tree.tag_configure('even', background='#DFDFDF')

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

    def save_annotation(self):
        for row in self.tree.get_children():
            values = self.tree.item(row, 'values')
            d = {
                'species': values[4],
                'lifestage': values[5],
                'sex': values[6],
                'antler': values[7],
                'remarks': values[8],
                'animal_id': values[9]
            }
            # TODO self.data
            image_id = self.data[int(row)][10]['image_id']
            if image_id:
                sql = "UPDATE image SET annotation='[{}]', changed={} WHERE image_id={}".format(json.dumps(d), int(time.time()), image_id)
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
            values = self.tree.item(selected_item, values)
            #self.species_value.set(values[2])
            if row_id := self.tree.focus():
                # TODO self.data not good
                path = self.data[int(row_id)][10]['path']
                self.show_thumb(path)
            #print ('|'.join(record))

    def on_click(self, event):
        #for item in self.tree.selection():
        #    item_text = self.tree.item(item,"values")

        # !! update current_rc
        self.current_rc = get_tree_rc(self.tree)
        print ('on_click: ', self.current_rc)
        if not self.current_rc:
            return False

        head = HEADING[self.current_rc[1][1]]
        if head[2] == 'readonly':
            # readonly column
            return False

        x, y = get_tree_rc_place(
            self.tree,
            self.current_rc[1][0],
            self.current_rc[1][1])

        # get default value
        item = self.tree.item(self.current_rc[0][0])
        val = None
        if v:= item['values'][self.current_rc[1][1]]:
            val = v

        choices = []
        if head[2] == 'freesolo':
            if len(head) > 3:
                ini_key = head[3]
                choices = self.app.config.get(ini_key, 'choices').split(',')

        #if self.freesolo:
        #    self.freesolo.terminate()
        #self.create_freesolo(x, y, choices, val)


    def create_freesolo(self, x, y, choices, value):
        self.freesolo = FreeSolo(
            self.tree,
            choices,
            value=value)
        #listbox_width=100 #TODO

        self.freesolo.place(x=x, y=y)
        self.freesolo.bind("<FocusOut>", lambda e: self.handle_freesolo_focusout(e))
        self.freesolo.focus()

    def handle_freesolo_update(self, event):
        '''update freesolo value to treeview'''
        print ('update', event)
        self.set_freesolo_value()
        self.freesolo.terminate()

    def handle_freesolo_trace(self, *args):
        print ('trace:', args, self.freesolo.value.get())

        if v:= self.freesolo.value.get():
            print (self.freesolo.listbox)
            self.freesolo.filter_listbox_choices(v)

    def handle_freesolo_focusout(self, event):
        print ('focusout:', event)
        if not self.freesolo:
            return False

        self.set_freesolo_value()
        # tkinder call focusout first then listbox's binding
        self.freesolo.destroy()

    def set_freesolo_value(self):
        if not self.freesolo:
            return False

        #val = None
        # check from listbox
        if listbox := self.freesolo.listbox:
            current_selection = listbox.curselection()
            if current_selection:
                text = listbox.get(current_selection)
                if text:
                    # save to entry
                    self.freesolo.value.set(text)

        val = self.freesolo.value.get()
        #curItem = self.tree.focus()
        # row
        item = self.tree.item(self.current_rc[0][0])
        # column
        #values[self.current_rc[1][1]] = val
        print ('set entry', val)
        self.tree.set(
            self.current_rc[0][0],
            self.current_rc[0][1],
            val)

    def show_thumb(self, image_path):
        #if not hasattr(self, 'sheet_data') or len(self.sheet_data) <= 0:
        #    return False

        #image_path = self.sheet_data[row][9]['path']
        image = Image.open(image_path)
        # aspect ratio
        basewidth = 450
        wpercent = (basewidth/float(image.size[0]))
        hsize = int((float(image.size[1])*float(wpercent)))
        img = image.resize((basewidth,hsize))
        #img = image.resize((300,300))
        #img = image.resize((300,300), Image.ANTIALIAS)
        photo = ImageTk.PhotoImage(img)
        self.image_thumb.configure(image=photo)
        self.image_thumb.image = photo
        self.update_idletasks()

    def update_annotation(self):
        #selected = self.tree.focus()
        #print (selected)
        #self.tree.item(selected, text='', )
        for selected_item in self.tree.selection():
            values = self.tree.item(selected_item, 'values')
            new_values = list(values)
            new_values[4] = self.species_value.get()
            new_values[5] = self.lifestage_value.get()
            new_values[6] = self.sex_value.get()
            new_values[7] = self.antler_value.get()
            new_values[8] = self.remark_value.get()
            new_values[9] = self.animal_id_value.get()
            self.tree.item(selected_item, text='', values=new_values)
        # clear value
        self.species_value.set('')
        self.lifestage_value.set('')
        self.sex_value.set('')
        self.antler_value.set('')
        self.remark_value.set('')
        self.animal_id_value.set('')
