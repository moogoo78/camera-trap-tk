import json
from datetime import datetime

import tkinter as tk
from tkinter import (
    ttk,
)

from PIL import ImageTk, Image
from tksheet import Sheet


class Datatable(tk.Frame):

    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent
        self.app = self.parent.parent

        self.source_data = {}
        projects = self.app.server.projects
        self.id_map = {
            'project': {},
            'studyarea': {},
            'deployment': {},
            'sa_to_d': {}
        }
        self.id_map['project'] = {x['name']: x['project_id'] for x in projects}

        self.ctrl_data = []

        self.ctrl_frame = tk.Frame(self)
        self.table_frame = tk.Frame(self, bg='green')
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        #self.table_frame.grid_columnconfigure(0, weight=1)
        #self.table_frame.grid_rowconfigure(0, weight=1)

        ctrl_pad = {
            'padx': 4,
            'pady': 8,
        }
        self.ctrl_frame.grid(row=0, column=0, sticky='w', **ctrl_pad)
        self.table_frame.grid(row=1, column=0)

        # project menu
        self.label_project = ttk.Label(self.ctrl_frame,  text='計畫')
        self.label_project.grid(row=0, column=0)
        self.project_options = [x['name'] for x in projects]
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
        self.upload_button.grid(row=0, column=6, padx=20)

        # sheet
        self.sheet = Sheet(
            self.table_frame,
            data=[],
            headers=['status', 'filename', 'time', '物種', '年齡'],
            width=800,
            height=640
        )
        self.sheet.enable_bindings()
        self.sheet.grid(row=0, column=0, sticky='nswe')
        self.sheet.enable_bindings(('cell_select'))
        self.sheet.extra_bindings([
            ('cell_select', self.cell_select)
        ])

        # thumb
        self.image_thumb = ttk.Label(self, border=25)
        self.image_thumb.grid(row=0, column=1)


    def refresh(self):
        self.source_id = self.parent.state.get('source_id', '')
        ret = self.app.source.get_source(self.source_id)
        self.source_data = ret

        if ret['source'][7]:
            self.menu_select = json.loads(ret['source'][7])
            self.project_var.set(self.menu_select['project_name'])
            if sa_name := self.menu_select.get('studyarea_name', ''):
                self.studyarea_var.set(sa_name)
            else:
                self.studyarea_var.set('')
            if d_name := self.menu_select.get('deployment_name', ''):
                self.deployment_var.set(d_name)
            else:
                self.deployment_var.set('')
        else:
            self.project_var.set('')
            self.studyarea_var.set('')
            self.deployment_var.set('')

        self.sheet_data = []
        ctrl_data = []
        for i in ret['image_list']:
            filename = i[2]
            dtime = str(datetime.fromtimestamp(i[3]))
            alist = json.loads(i[7])
            path = i[1]
            status = i[5]
            if len(alist) >= 1:
                for j in alist:
                    species = j.get('species', '')
                    lifestage = j.get('lifestage', '')
                    self.sheet_data.append([
                        status,
                        filename,
                        dtime,
                        species,
                        lifestage])
                    ctrl_data.append([
                        path,
                    ])
            else:
                self.sheet_data.append([
                    status,
                    filename,
                    dtime,
                    '',
                    ''])
                ctrl_data.append([
                    path,
                ])

        self.ctrl_data = ctrl_data

        self.sheet.set_sheet_data(
            data=self.sheet_data,
            redraw=True,
        )
        self.sheet.delete_dropdown('all')
        for i in range(0, len(self.sheet_data)):
            self.sheet.create_dropdown(i, 3, values='測試,空拍,山羌,山羊,水鹿'.split(','), set_value='', destroy_on_select=False, destroy_on_leave =False, see=False)
            self.sheet.create_dropdown(i, 4, values='成體,亞成體,幼體,無法判定'.split(','), set_value='', destroy_on_select = False, destroy_on_leave = False, see = False)
                #self.sheet.create_dropdown(i, 3, values='雄性,雌性,無法判定'.split(','), set_value='', destroy_on_select = False, destroy_on_leave = False, see = False)
                #初茸,茸角一尖,茸角一岔二尖,茸角二岔三尖,茸角三岔四尖,硬角一尖,硬角一岔二尖,硬角二岔三尖,硬角三岔四尖,解角

        #self.image_thumb_button = ttk.Button(self, text='看大圖',
        #                                     command=lambda: self.controller.show_frame('ImageViewer'))
        #self.image_thumb_button.grid(row=2, column=2)
        self.sheet.refresh()
    def cell_select(self, response):
        image_path = self.ctrl_data[response[1]][0]
        image = Image.open(image_path)
        img = image.resize((300,300), Image.ANTIALIAS)
        photo = ImageTk.PhotoImage(img)
        self.image_thumb.configure(image=photo, width=300 )
        self.image_thumb.image = photo

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
            print ('deployment_id', deployment_id, d_name, )
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

            # TODO
            #tk.messagebox.showinfo('info', '已設定相機位置')
    def on_upload(self):
        #self.app.source.do_upload(self.source_data)
        image_list = self.source_data['image_list']
        source_id = self.source_data['source'][0]

        pb = self.app.statusbar.progress_bar
        pb['maximum'] = len(image_list)
        self.update_idletasks()
        #print (image_list)
        for i, v in enumerate(self.app.source.gen_upload(image_list, source_id)):
            print (i, 'foo')
            pb['value'] = i+1
            self.update_idletasks()

        pb['value'] = 0
        self.update_idletasks()
        tk.messagebox.showinfo('info', '上傳成功')
