import json
from datetime import datetime
import time

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

        self.ctrl_frame = tk.Frame(self)
        self.table_frame = tk.Frame(self)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.table_frame.rowconfigure(0, weight=1)
        self.table_frame.rowconfigure(1, weight=5)

        #self.table_frame.grid_columnconfigure(0, weight=1)
        #self.table_frame.grid_rowconfigure(0, weight=1)

        ctrl_pad = {
            'padx': 4,
            'pady': 8,
        }
        self.ctrl_frame.grid(row=0, column=0, sticky='w', **ctrl_pad)
        self.table_frame.grid(row=1, column=0, sticky='w')

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
        self.upload_button.grid(row=0, column=6, padx=20, sticky='w')

        # save button
        self.save_button = ttk.Button(
            self.ctrl_frame,
            text='儲存',
            command=self.on_save)
        self.save_button.grid(row=0, column=7, padx=5, sticky='e')

        # sheet
        self.sheet = Sheet(
            self.table_frame,
            data=[],
            headers=['標注/上傳狀態', 'filename', 'time', '物種', '年齡', '性別', '角況', '備註', '個體 ID'],
            width=650,
            height=620,
            displayed_columns=[0,1,2,3,4,5,6,7,8],
            all_columns_displayed=False,
        )
        self.sheet.enable_bindings()
        self.sheet.grid(row=0, column=0, rowspan=2, sticky='nswe')
        self.sheet.enable_bindings(('cell_select'))
        self.sheet.highlight_rows(rows=[1], bg='#def') #TODO-EN
        self.sheet.highlight_rows(rows=[2], bg='#eeeeee') #TODO-EN
        self.sheet.extra_bindings([
            ('cell_select', self.cell_select)
        ])

        # thumb
        self.image_thumb = ttk.Label(self.table_frame, border=8, relief='raised')
        self.image_thumb.grid(row=0, column=1, sticky='n')
        self._show_thumb()

        self.image_viewer_button = ttk.Button(
            self.table_frame,
            text='看大圖',
            command=lambda: self.app.main.show_frame('image-viewer')
        )

        #self.image_viewer_button.grid(row=1, column=1, sticky='nw', padx=20)
        self.image_viewer_button.grid(row=1, column=1, sticky='n')

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
        for i in ret['image_list']:
            filename = i[2]
            dtime = str(datetime.fromtimestamp(i[3]))
            alist = json.loads(i[7])
            path = i[1]
            status_display = '{} / {}'.format(
                self.get_status_display(i[5]),
                self.get_status_display(i[12]),
            )
            image_id = i[0]
            if len(alist) >= 1:
                for j in alist:
                    species = j.get('species', '')
                    lifestage = j.get('lifestage', '')
                    sex = j.get('sex', '')
                    antler = j.get('antler', '')
                    animal_id = j.get('animal_id', '')
                    remarks = j.get('remarks', '')
                    self.sheet_data.append([
                        status_display,
                        filename,
                        dtime,
                        species,
                        lifestage,
                        sex,
                        antler,
                        remarks,
                        animal_id,
                        {
                            'image_id': image_id,
                            'path': path,
                            'status': i[5],
                            'upload_status': i[12],
                        }
                    ])
            else:
                self.sheet_data.append([
                    status_display,
                    filename,
                    dtime,
                    '',
                    '',
                    '',
                    '',
                    '',
                    '',
                    {
                        'image_id': image_id,
                        'path': path,
                        'status': i[5],
                        'upload_status': i[12],
                    },
                ])

        # save to main.state
        self.parent.state['alist'] = self.sheet_data

        self.sheet.set_sheet_data(
            data=self.sheet_data,
            redraw=True,
        )

        sp_options = self.app.config.get('AnnotationFieldSpecies', 'choices').split(',')
        ls_options = self.app.config.get('AnnotationFieldLifeStage', 'choices').split(',')
        sx_options = self.app.config.get('AnnotationFieldSex', 'choices').split(',')
        an_options = self.app.config.get('AnnotationFieldAntler', 'choices').split(',')

        #refresh_dropdowns
        self.sheet.delete_dropdown('all')
        for row in range(0, len(self.sheet_data)):
            default_sp = self.sheet_data[row][3] or ''
            self.sheet.create_dropdown(row, 3, values=sp_options, set_value=default_sp, destroy_on_select=False, destroy_on_leave =False, see=False, set_cell_on_select=False)
            default_ls = self.sheet_data[row][4] or ''
            self.sheet.create_dropdown(row, 4, values=ls_options, set_value=default_ls, destroy_on_select = False, destroy_on_leave = False, see = False)
            default_sx = self.sheet_data[row][5] or ''
            self.sheet.create_dropdown(row, 5, values=sx_options, set_value=default_sx, destroy_on_select = False, destroy_on_leave = False, see = False)
            default_an = self.sheet_data[row][6] or ''
            self.sheet.create_dropdown(row, 6, values=an_options, set_value=default_an, destroy_on_select = False, destroy_on_leave = False, see = False)

        # disable mousewheel scroll change value in dropdown
        # this method error!!
        #print (self.sheet.get_dropdowns())
        for k, v in self.sheet.MT.cell_options:
            if 'dropdown' in self.sheet.MT.cell_options[(k,v)]:
                self.sheet.MT.cell_options[(k,v)]['dropdown'][0].unbind_class("TCombobox", "<MouseWheel>")

        self.sheet.refresh()

    def _show_thumb(self, row=0):
        if not hasattr(self, 'sheet_data') or len(self.sheet_data) <= 0:
            return False

        image_path = self.sheet_data[row][9]['path']
        image = Image.open(image_path)
        # aspect ratio
        basewidth = 350
        wpercent = (basewidth/float(image.size[0]))
        hsize = int((float(image.size[1])*float(wpercent)))
        img = image.resize((basewidth,hsize))
        #img = image.resize((300,300))
        #img = image.resize((300,300), Image.ANTIALIAS)
        photo = ImageTk.PhotoImage(img)
        self.image_thumb.configure(image=photo)
        self.image_thumb.image = photo
        self.update_idletasks()

    def cell_select(self, response):
        self.parent.state['current_row'] = response[1]
        self._show_thumb(response[1])
        status = self.sheet_data[response[1]][9]['status']
        upload_status = self.sheet_data[response[1]][9]['upload_status']
        image_id = self.sheet_data[response[1]][9]['image_id']
        #print (status, image_id)
        if status == '10':
            next_status = '20'
            sql = 'UPDATE image SET status="{}" WHERE image_id={}'.format(next_status, image_id)
            self.app.db.exec_sql(sql, True)

            status_display = '{} / {}'.format(
                self.get_status_display(next_status),
                self.get_status_display(upload_status),
            )
            self.sheet.set_cell_data(response[1], 0, status_display)


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
            '10': '🗀',
            '20': '👀',
            '30': '☑️',
            '100': '🔥',
            '110': '-',
            '200': '✅',
        }
        return status_map.get(code, '-')
