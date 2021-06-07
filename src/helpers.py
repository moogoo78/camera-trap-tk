import tkinter as tk
from tkinter import ttk

import json
from datetime import datetime

'''
key, label, type, choices in ini
'''
HEADING = (
    ('index', '#', 'readonly'),
    ('status', '標注/上傳狀態', 'readonly'),
    ('filename', '檔名', 'readonly'),
    ('datetime','日期時間', 'readonly'),
    ('species', '物種', 'freesolo', 'AnnotationFieldSpecies'),
    ('lifestage', '年齡', 'freesolo', 'AnnotationFieldLifeStage'),
    ('sex', '性別', 'freesolo', 'AnnotationFieldSex'),
    ('antler', '角況', 'freesolo', 'AnnotationFieldAntler'),
    ('remark', '備註', 'freesolo'),
    ('animal_id', '個體 ID', 'freesolo')
)

def _get_status_display(code):
    status_map = {
        '10': 'new',
        '20': 'viewed',
        '30': 'annotated',
        '100': 'start',
        '110': '-',
        '200': 'uploaded',
    }
    return status_map.get(code, '-')

def image_list_to_table(image_list):
    rows = []

    counter = 0
    for i in image_list:
        filename = i[2]
        dtime_display = str(datetime.fromtimestamp(i[3]))
        alist = json.loads(i[7])
        path = i[1]
        status_display = '{} / {}'.format(
            _get_status_display(i[5]),
            _get_status_display(i[12]),
        )
        image_id = i[0]
        if len(alist) >= 1:
            for j in alist:
                counter += 1
                species = j.get('species', '')
                lifestage = j.get('lifestage', '')
                sex = j.get('sex', '')
                antler = j.get('antler', '')
                animal_id = j.get('animal_id', '')
                remarks = j.get('remarks', '')
                rows.append([
                    counter,
                    status_display,
                    filename,
                    dtime_display,
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
                        'time': i[3],
                        'seq': 0,
                    }
                ])
        else:
            counter += 1
            rows.append([
                counter,
                status_display,
                filename,
                dtime_display,
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
                    'time': i[3],
                    'seq': 0
                },
            ])
    return rows

def get_tree_rc(tree):
    pxy = tree.winfo_pointerxy()
    adjust_x = pxy[0] - tree.winfo_rootx()
    adjust_y = pxy[1] - tree.winfo_rooty()

    rows_num =len(tree.get_children())
    if adjust_y > ((rows_num +1) * tree.row_height):
        # click out ouf tree data area,
        # tree.focus remains last row that we don't want
        return False

    iid = tree.focus()
    col_id = tree.identify_column(adjust_x)
    #print (adjust_x, adjust_y, pxy)
    #print (tree.winfo_height(), tree['height'])

    if iid and col_id:
        r = int(iid)
        if c := col_id.replace('#', ''):
            c = int(c) - 1
        return (
            (iid, col_id),
            (r, c),
        )
    return None

def get_tree_rc_place(tree, r, c):
    to_w = 0
    for i in HEADING[0:c]:
        if w := tree.column(i[0]).get('width', ''):
            to_w += w
    return (to_w, (r+1)*tree.row_height)


class FreeSolo_(ttk.Entry, object):
    def __init__(
            self,
            parent,
            choices=None,
            value=None,
            entry_args={},
            entry_on_trace=None,
            entry_on_update=None,
            listbox_args={},
    ):
        #autocomplete_function=None, , ignorecase_match=False, startswith_match=True, vscrollbar=True, hscrollbar=True, value_callback=None, **kwargs):
        self.choices = choices
        self.filtered_choices = []

        entry_args['textvariable'] = tk.StringVar()
        self.value = entry_args['textvariable']
        if value:
            print ('set_val')
            self.value.set(value)

        default_listbox_args = {
            'width': None,
            'height': 9,
            'background': 'white',
            'selectmode': tk.SINGLE,
            'activestyle': 'none',
            'exportselection': False,
        }
        self.listbox_args = {**default_listbox_args, **listbox_args}

        ttk.Entry.__init__(
            self,
            parent,
            **entry_args)

        self.value_trace_id = self.value.trace('w', lambda name, index, mode: entry_on_trace(name, index, mode))
        self.on_update = entry_on_update
        #self.bind('<Return>', self._update_entry)
        self.bind('<Return>', self.on_update)
        self.bind('<Escape>', self.on_update)
        self.bind('<Down>', lambda event: self.create_listbox())

        self.listbox = None
        #self.build_listbox()


    def filter_listbox_choices(self, val):
        if val and self.choices:
            filtered = [i for i in self.choices if i.startswith(val)]
            print ('filtered:', filtered, self.listbox)
            if len(filtered) > 0:
                if self.listbox is None:
                    self.create_listbox(filtered)
                else:
                    self.listbox.delete(0, tk.END)
                    for i in filtered:
                        self.listbox.insert(tk.END, i)
        return []

    def on_change(self, name, index, mode):
        val = self.value.get()
        if val == '':
            #self.unpost_listbox()
            #self.focus()
            # TODO post_listbox
            pass
        else:
            # filter choices
            filtered_choices = [i for i in self.choices if i.startswith(val)]
            if len(filtered_choices) > 0:
                if self.listbox is None:
                    self.build_listbox()
                else:
                    self.listbox.delete(0, tk.END)

                    height = min(self.listbox_args.get('height', 0), len(filtered_choices))
                    self.listbox.configure(height=height)

                    for item in filtered_choices:
                        self.listbox.insert(tk.END, item)
            else:
                #self.unpost_listbox()
                #self.focus()
                self.remove_listbox()

    def create_listbox(self, filtered_choices=[]):
        listbox_frame = tk.Frame()
        self.listbox = tk.Listbox(listbox_frame, **self.listbox_args)
        self.listbox.grid(row=0, column=0, sticky = 'news')

        self.listbox.bind("<ButtonRelease-1>", self.update_from_listbox)
#        self.listbox.bind("<Return>", self._update_entry)
        self.listbox.bind("<Escape>", lambda event: self.unpost_listbox())

        listbox_frame.grid_columnconfigure(0, weight= 1)
        listbox_frame.grid_rowconfigure(0, weight= 1)

        #x = -self.cget("borderwidth") - self.cget("highlightthickness")
        x = 0
        #y = self.winfo_height()-self.cget("borderwidth") - self.cget("highlightthickness")
        y = self.winfo_height()

        if self.listbox_args.get('width', ''):
            width = self.listbox_width
        else:
            width = self.winfo_width()
        #print (x, y, width, self.winfo_height(),self.cget("borderwidth"),self.cget("highlightthickness"))
        y = 22
        width = 120
        listbox_frame.place(in_=self, x=x, y=y, width=width)

        #self.update_listbox_choices(filtered_choices)

        #def update_listbox_choices(self, filtered_choices=[]):
        #print ('update list', filtered_choices)

        choices = filtered_choices if len(filtered_choices) else self.choices
        for i in choices:
            self.listbox.insert(tk.END, i)

            #height = min(self._listbox_height, len(values))
            #        self._listbox.configure(height=height)

    def update_from_listbox(self, event):
        '''event eat by focusout'''
        pass
        #print ('update_from listbox')
        # if self.listbox is not None:
        #     current_selection = self.listbox.curselection()
        #     if current_selection:
        #         text = self.listbox.get(current_selection)
        #         if text:
        #             self.value.set(text)

        #     self.remove_listbox()

    def set_value(self, text):
        '''event eat by focusout'''
        pass
        #print ('set_val', text)
        #self._set_var(text)
        #self.value.trace_vdelete('w', self.value_trace_id)
        #self.value.set(text)
        #self.value_trace_id = self.value.trace('w', self.on_change)

        #if close_dialog:
        #    self.unpost_listbox()

        #self.icursor(tk.END)
        #self.xview_moveto(1.0)

    def remove_listbox(self):
        if self.listbox is not None:
            self.listbox.master.destroy()
            self.listbox = None

    def terminate(self):
        self.remove_listbox()
        self.value.set('')
        self.destroy()


class FreeSolo(ttk.Entry, object):
    def __init__(
            self,
            parent,
            choices=None,
            value=None,
            entry_args={},
            listbox_args={},
    ):
        #autocomplete_function=None, , ignorecase_match=False, startswith_match=True, vscrollbar=True, hscrollbar=True, value_callback=None, **kwargs):
        self.choices = choices
        self.filtered_choices = []

        if not value:
            entry_args['textvariable'] = tk.StringVar()
        else:
            self.value = entry_args['textvariable'] = value

        default_listbox_args = {
            'width': None,
            'height': 9,
            'background': 'white',
            'selectmode': tk.SINGLE,
            'activestyle': 'none',
            'exportselection': False,
        }
        self.listbox_args = {**default_listbox_args, **listbox_args}

        ttk.Entry.__init__(
            self,
            parent,
            **entry_args)

        self.value_trace_id = self.value.trace('w', self.handle_trace)
        #self.bind('<Return>', self.handle_update) # next?
        #self.bind('<Escape>', self.handle_update)
        self.bind('<Down>', lambda event: self.create_listbox())

        self.listbox = None
        #self.build_listbox()

    def handle_trace(self, name, index, mode):
        val = self.value.get()

        if val and self.choices:
            filtered = [i for i in self.choices if i.startswith(val)]
            #print ('filtered:', filtered, self.listbox)
            if len(filtered) > 0:
                if self.listbox is None:
                    self.create_listbox(filtered)
                else:
                    self.listbox.delete(0, tk.END)
                    for i in filtered:
                        self.listbox.insert(tk.END, i)

    def handle_update(self, event):
        if listbox := self.listbox:
            current_selection = listbox.curselection()
            if current_selection:
                text = listbox.get(current_selection)
                self.value.set(text)
                print ('update', event)


        # destroy listbox
        self.remove_listbox()

        self.focus()
        self.icursor(tk.END)
        self.xview_moveto(1.0)

    def create_listbox(self, filtered_choices=[]):
        listbox_frame = tk.Frame()
        self.listbox = tk.Listbox(listbox_frame, **self.listbox_args)
        self.listbox.grid(row=0, column=0, sticky = 'news')

        self.listbox.bind("<ButtonRelease-1>", self.handle_update)
#        self.listbox.bind("<Return>", self._update_entry)
        self.listbox.bind("<Escape>", lambda event: self.unpost_listbox())

        listbox_frame.grid_columnconfigure(0, weight= 1)
        listbox_frame.grid_rowconfigure(0, weight= 1)

        #x = -self.cget("borderwidth") - self.cget("highlightthickness")
        x = 0
        #y = self.winfo_height()-self.cget("borderwidth") - self.cget("highlightthickness")
        y = self.winfo_height()

        if self.listbox_args.get('width', ''):
            width = self.listbox_width
        else:
            width = self.winfo_width()
        #print (x, y, width, self.winfo_height(),self.cget("borderwidth"),self.cget("highlightthickness"))
        y = 22
        width = 120
        listbox_frame.place(in_=self, x=x, y=y, width=width)

        #self.update_listbox_choices(filtered_choices)

        #def update_listbox_choices(self, filtered_choices=[]):
        #print ('update list', filtered_choices)

        choices = filtered_choices if len(filtered_choices) else self.choices
        for i in choices:
            self.listbox.insert(tk.END, i)

            #height = min(self._listbox_height, len(values))
            #        self._listbox.configure(height=height)

    def remove_listbox(self):
        if self.listbox is not None:
            self.listbox.master.destroy()
            self.listbox = None

    def terminate(self):
        self.remove_listbox()
        self.value.set('')
        self.destroy()
