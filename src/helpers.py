import tkinter as tk
from tkinter import ttk

import json
from datetime import datetime
import random
import colorsys

'''
key, label, type, choices in ini
'''

HEADING = (
    #('index', '#',
    # {'width': 25, 'stretch': False}),
    ('status_display', '標注/上傳狀態',
     {'width': 40, 'stretch': False}),
    ('filename', '檔名',
     {'width': 150, 'stretch': False}),
    ('datetime_display','日期時間',
     {'width': 150, 'stretch': False}),
    ('annotation_species', '物種',
     {'width': 80, 'stretch': False},
     {'widget': 'freesolo',
      'config_section': 'AnnotationFieldSpecies'}),
    ('annotation_lifestage', '年齡',
     {'width': 50, 'stretch': False},
     {'widget': 'freesolo',
      'config_section': 'AnnotationFieldLifeStage'}),
    ('annotation_sex', '性別',
     {'width': 50, 'stretch': False},
     {'widget': 'freesolo',
      'config_section': 'AnnotationFieldSex'}),
    ('annotation_antler', '角況',
     {'width': 50, 'stretch': False},
     {'widget': 'freesolo',
      'config_section': 'AnnotationFieldAntler'}),
    ('annotation_remark', '備註',
     {'width': 50, 'stretch': False},
     {'widget': 'entry',
          'config_section': 'AnnotationFieldRemarks'}),
    ('annotation_animal_id', '個體 ID',
     {'width': 50, 'stretch': False},
     {'widget': 'entry',
      'config_section': 'AnnotationFieldAnimalID'}),
)

class TreeHelper(object):
    def __init__(self):
        self.heading = HEADING
        self.annotation_item = [3, 4, 5, 6, 7, 8]
        self.data = []
        self.current_index = 0

    def get_annotation_dict(self, entry_list):
        d = {}
        for i, v in enumerate(self.annotation_item):
            key = self.heading[v][0]
            key = key.replace('annotation_', '')
            d[key] = entry_list[i][1].get()

        return d

    def set_data(self, iid, alist):
        for i, v in enumerate(self.data):
            if v['iid'] == iid:
                self.data[i]['alist'] = alist
        #print (self.data)
        #found = self.get_data(iid)

    def get_data(self, iid):
        return list(filter(lambda x: x['iid'] == iid, self.data))[0]

    def get_conf(self, cat='annotation'):
        '''
        return [(index, conf)...]
        '''
        #return list(filter(lambda x: x[0] == key, self.conf))[0] or None
        if cat == 'annotation':
            return [(x, self.heading[x]) for x in self.annotation_item]

    def set_data_from_list(self, image_list):
        '''
        iid rule: `iid:{image_index}:{annotation_index}`
        '''
        rows = []
        counter = 0
        for i_index, i in enumerate(image_list):
            alist = json.loads(i[7])
            status_display = '{} / {}'.format(
                _get_status_display(i[5]),
                _get_status_display(i[12]),
            )
            row_basic = {
                'status_display': status_display,
                'filename': i[2],
                'datetime_display': str(datetime.fromtimestamp(i[3])),
                'image_id': i[0],
                'path': i[1],
                'status': i[5],
                'upload_status': i[12],
                'time': i[3],
                'seq': 0,
                'sys_note': json.loads(i[13]),
            }

            if len(alist) >= 1:
                for a_index, a in enumerate(alist):
                    counter += 1
                    row_multi = {
                        'counter': counter,
                        'iid': f'iid:{i_index}:{a_index}',
                        'iid_parent': '',
                        'alist': [],
                    }
                    for head_index in self.annotation_item:
                        key = self.heading[head_index][0]
                        k = key.replace('annotation_', '')
                        row_multi[key] = a.get(k, '')

                    if a_index == 0:
                        row_multi['alist'] = alist
                    else:
                        row_multi['iid_parent'] = f'iid:{i_index}:0'

                    rows.append({**row_basic, **row_multi})
            else:
                counter += 1
                row_multi = {
                    'counter': counter,
                    'iid': 'iid:{}:0'.format(i_index),
                    'iid_parent': '',
                    'alist': alist,
                }
                for head_index in self.annotation_item:
                    key = self.heading[head_index][0]
                    row_multi[key] = ''
                rows.append({**row_basic, **row_multi})

        self.data = rows
        tree_data = []
        for i in rows:
            values = [i.get(h[0], '')
                      for h_index, h in enumerate(self.heading)]
            #print (i['iid'], i.get('iid_parent', ''))
            #print (values)
            tree_data.append(values)

        return tree_data

    def group_image_sequence(self, time_interval, highlight='', seq_tag=''):
        seq_info = {
            'group_prev': False,
            'group_next': False,
            'map': {},
            'idx': 0,
            'salt': random.random(),
            'int': int(time_interval) * 60,
        }
        # via: https://martin.ankerl.com/2009/12/09/how-to-create-random-colors-programmatically/
        golden_ratio_conjugate = 0.618033988749895

        for i, v in enumerate(self.data):
            tag_name = ''
            next_idx = min(i+1, len(self.data)-1)
            this_time = self.data[i]['time']
            next_time = self.data[next_idx]['time'] if i < next_idx else 0
            seq_info['group_prev'] = seq_info['group_next']
            if next_time and \
               (next_time - this_time) <= seq_info['int']:
                seq_info['group_next'] = True
            else:
                seq_info['group_next'] = False

            if seq_info['group_next'] == True and not seq_info['group_prev']:
                seq_info['idx'] += 1
                seq_info['salt'] += golden_ratio_conjugate
                seq_info['salt'] %= 1

            if seq_info['group_next'] or seq_info['group_prev']:
                tag_name = 'tag{}'.format(seq_info['idx'])
            else:
                seq_num = ''

            rgb_hex = ''
            if tag_name:
                rgb = colorsys.hls_to_rgb(seq_info['salt']*265, 0.8, 0.5)
                rgb_hex = f'#{int(rgb[0]*255):02x}{int(rgb[1]*255):02x}{int(rgb[2]*255):02x}'
                if seq_info['idx'] not in seq_info['map']:
                    seq_info['map'][tag_name] = {
                        'color': rgb_hex,
                        'rows': []
                    }
                seq_info['map'][tag_name]['rows'].append(i)

            if highlight:
                v[highlight] = rgb_hex
            if seq_tag:
                v[seq_tag] = tag_name

        return seq_info

    # via: https://stackoverflow.com/questions/56331001/python-tkinter-treeview-colors-are-not-updating
    def fixed_map(self, style, option):
        # Returns the style map for 'option' with any styles starting with
        # ("!disabled", "!selected", ...) filtered out

        # style.map() returns an empty list for missing options, so this should
        # be future-safe
        return [elm for elm in style.map("Treeview", query_opt=option)
                if elm[:2] != ("!disabled", "!selected")]


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

def data_to_tree_values(data):
    rows = []
    for i in data:
        values = [i.get(h[0], '')for h in HEADING]
        rows.append(values)
    return rows

def image_list_to_table(image_list):
    rows = []
    counter = 0
    for i in image_list:
        alist = json.loads(i[7])
        path = i[1]
        status_display = '{} / {}'.format(
            _get_status_display(i[5]),
            _get_status_display(i[12]),
        )
        basic_item = {
            'status_display': status_display,
            'filename': i[2],
            'datetime_display': str(datetime.fromtimestamp(i[3])),
        }
        ctrl_item = {
            'image_id': i[0],
            'path': i[1],
            'status': i[5],
            'upload_status': i[12],
            'time': i[3],
            'seq': 0,
        }
        if len(alist) >= 1:
            for j in alist:
                counter += 1
                basic_item['index'] = counter
                annotation_item = {
                    'species': j.get('species', ''),
                    'lifestage': j.get('lifestage', ''),
                    'sex': j.get('sex', ''),
                    'antler':j.get('antler', ''),
                    'animal_id':j.get('animal_id', ''),
                    'remarks': j.get('remarks', ''),
                }
                rows.append({
                    **basic_item,
                    **annotation_item,
                    **ctrl_item,
                })
        else:
            counter += 1
            annotation_item = {
                'species': '',
                'lifestage': '',
                'sex': '',
                'antler': '',
                'animal_id': '',
                'remarks': '',
            }
            rows.append({
                **basic_item,
                **annotation_item,
                **ctrl_item,
            })
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
        #self.bind('<Down>', lambda event: self.create_listbox())
        self.bind('<Return>', lambda _: self.create_listbox())
        #self.bind("<FocusOut>", lambda _: self.remove_listbox()) # will cause listbox gone!

        self.listbox = None
        #self.build_listbox()

    #def set_value(self, value, close_listbox=False):
        #self._entry_var.trace_vdelete("w", self._trace_id)
        #self._entry_var.set(text)
        #self._trace_id = self._entry_var.trace('w', self._on_change_entry_var)
    #    self.value.set(value)
    #    if close_listbox:
    #        self.close_listbox()

    def set_focus(self):
        self.focus()

    def handle_trace(self, name, index, mode):
        val = self.value.get()
        #print ('free trace', val)
        #if val == '':
        #    #self.focus() # ?
        #else:
        if val:
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
        #print ('handle_update')
        if listbox := self.listbox:
            current_selection = listbox.curselection()
            if current_selection:
                text = listbox.get(current_selection)
                self.value.set(text)


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
        self.listbox.bind("<Escape>", lambda _: self.unpost_listbox())

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
