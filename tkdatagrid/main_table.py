import logging
import functools

import tkinter as tk
from tkinter import ttk

from PIL import ImageTk, Image

from .utils import check_image
#from .other_classes import (
#    AutoScrollbar,
#)
"""
mist: #90AFC5
stone: #336B87
shadow: #2A3132
automn leaf: #763626
#https://www.canva.com/design/DADfC5CQ0W4/remix?action2=create&mediaId=DADfC5CQ0W4&signupReferrer=blog&utm_source=blog&utm_medium=content&utm_campaign=100-color-combinations&_branch_match_id=812929534608293691
"""

def custom_action(_func=None, *, name=''):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            ret = func(*args, **kwargs)
            if f := args[0].ps['custom_actions'].get(name, None):
                if not None:
                    #print ('ret:', ret)
                    if isinstance(ret, tuple):
                        value = f(*ret)
                    else:
                        value = f(ret)
                return ret
            return
        return wrapper

    if _func is None: # called with argument
        return decorator
    else: # without argument
        return decorator(_func)


class MainTable(tk.Canvas):

    def __init__(
            self,
            parent=None,
            width=None,
            height=None,
            **kwargs):

        self.parent = parent
        self.ps = self.parent.state # parent_state

        self.width = self.ps['width']
        self.height = self.ps['height']

        super().__init__(
            parent,
            bg=self.ps['style']['color']['bg'],
            bd=2,
            relief='groove',
            height=self.height,
            scrollregion=(0,0,560,915)
        )
        # set default
        self.x_start = 0
        self.y_start = 0

        self.width = self.ps['width']
        self.height = self.ps['height']

        self.entry_queue = {}
        self.current_rc = [0, 0]
        self.selected = {
            'row_start': None,
            'row_end': None,
            'col_start': None,
            'col_end': None,
            'col_list': [],
            'row_list': [],
        }
        self.copy_buffer = []
        self.ps['after_row_index_selected'] = self.handle_row_index_selected

        # binding
        self.bind('<Button-1>', self.handle_mouse_button_1)
        self.bind('<Button-3>', self.handle_mouse_click_right)
        self.bind('<B1-Motion>', self.handle_mouse_drag)
        self.bind('<MouseWheel>', self.handle_mouse_wheel)
        self.bind('<Button-4>', self.handle_mouse_wheel)
        self.bind('<Button-5>', self.handle_mouse_wheel)
        #self.bind('<Control-Button-1>', self.handle_ctrl_button_1)
        self.bind_all('<Escape>', self.remove_widgets)
        self.bind_all('<space>', self.handle_space_key)

        # custom bindind
        if custom_binding := self.ps['custom_binding']:
            for bind_key in custom_binding['bind_list']:
                #self.parent.master.bind_all(f'<{bind_key}>', custom_binding['command'])
                self.bind_all(f'<{bind_key}>', custom_binding['command'])
        #self.parent.master.bind_all('<Control-a>', self.handle_sh)
        self.parent.master.bind_all('<Up>', self.handle_arrow_key)
        self.parent.master.bind_all('<Down>', self.handle_arrow_key)
        self.parent.master.bind_all('<Left>', self.handle_arrow_key)
        self.parent.master.bind_all('<Right>', self.handle_arrow_key)

    def handle_space_key(self, event):
        row, col = self.current_rc
        row_key, col_key = self.get_rc_key(row, col)

        col_type = self.ps['columns'][col_key].get('type', 'entry')
        if col_type == 'listbox':
            # if listbox opened close that
            if hasattr(self, 'listbox'):
                self.remove_widgets('listbox')
            else:
                choices = self.ps['columns'][col_key]['choices']
                self.render_listbox(row, col, choices)
        elif col_type == 'entry':
            if hasattr(self, 'text_editor'):
                # text_editor can have space input
                # do nothing
                pass
            else:
                text = self.ps['data'][row_key][col_key]
                self.render_entry(row, col, text)

    def handle_mouse_wheel(self, event):
        #print (event.num, event.delta, self.canvasy(0), self.winfo_height(), self.parent.row_index.winfo_height())
        # event.num exists in linux or mac ?
        if event.num == 5 or event.delta == -120:
            self.yview_scroll(1, 'units')
            if self.ps['row_index_display']:
                self.parent.row_index.yview_scroll(1, 'units')
        elif event.num == 4 or event.delta == 120:
            if self.canvasy(0) < 0: # ?
                return
            self.yview_scroll(-1, 'units')
            if self.ps['row_index_display']:
                self.parent.row_index.yview_scroll(-1, 'units')


    def render(self):
        #print ('render', self.height, self.width, self.ps['height'])
        self.configure(scrollregion=(0,0, self.width, self.ps['height']+30))
        self.render_grid()
        self.render_data()

    def render_grid(self):
        self.delete('cell-border')

        col_w_list = self.ps['column_width_list']
        color = self.ps['style']['color']
        num_rows = self.ps['num_rows']
        num_cols = self.ps['num_cols']

        # vertical line
        for i in range(num_cols+1): # fixed size
            if i < len(col_w_list):
                x = col_w_list[i]
            else:
                x = col_w_list[-1] + self.ps['cell_width']
            x += self.x_start
            self.create_line(
                x, self.y_start,
                x, self.y_start + num_rows * self.ps['cell_height'],
                tags=('cell-border'),
                fill=color['cell-border'], width=1)

        # horizontal line
        for i in range(num_rows+1):
            y = i * self.ps['cell_height']
            y += self.y_start
            self.create_line(
                self.x_start, y,
                col_w_list[-1]+self.x_start, y,
                tag=('cell-border'),
                fill=color['cell-border'], width=1)


    def render_data(self):
        self.delete('cell')

        col_w_list = self.ps['column_width_list']
        for row_counter, (row_key, row) in enumerate(self.ps['data'].items()):
            for col_counter, (col_key, col) in enumerate(self.ps['columns'].items()):
                x_left = col_w_list[col_counter] + self.x_start
                x_center = x_left + col['width'] / 2
                cell_tag = f'cell-text:{row_counter}_{col_counter}'
                col_type = col.get('type', 'entry')
                y_top = row_counter * self.ps['cell_height'] + self.y_start
                y_center = y_top + self.ps['cell_height']/2
                if col_type in ['entry', 'text', 'listbox']:
                    rect = self.create_text(
                        x_center,
                        y_center,
                        text=row.get(col_key, ''),
                        tags=('cell', 'cell-text', cell_tag)
                    )
                elif col_type == 'image':
                    img_path = row.get(col_key, '')
                    if img_path and check_image(img_path):
                        img = Image.open(img_path)
                        img = ImageTk.PhotoImage(img.resize((50, 33)))
                        x_pad = 0
                        if foo:= self.ps.get('cell_image_x_pad', 0):
                            x_pad = int(foo)
                        if foo:= self.ps.get('cell_image_y_pad', 0):
                            y_pad = int(foo)

                        self.ps['image_tmp'][row_key] = img
                        self.create_image(
                            x_left+x_pad, y_top+y_pad,
                            image=img,
                            anchor='nw',
                            tags=('cell','cell-image')
                        )

        self.lift('cell-image')


    def render_listbox(self, row, col, choices, default=0):
        self.remove_widgets()
        x1, y1, x2, y2 = self.get_cell_coords(row, col)
        self.listbox = tk.Listbox(self.parent, background='white', selectmode=tk.SINGLE)#, **self.listbox_args)
        #'activestyle': 'none'
        #exportselection: False
        self.listbox.bind('<ButtonRelease-1>', lambda event: self.handle_listbox_click(event, row, col))

        #choices = filtered_choices if len(filtered_choices) else self.choices
        self.listbox.insert(tk.END, '')
        for i in choices:
            if isinstance(i, tuple):
                self.listbox.insert(tk.END, i[0])
            if isinstance(i, str):
                self.listbox.insert(tk.END, i)
        #self.listbox.grid(row=0, column=0, sticky = 'news')

        self.create_window(
            x1,
            y1,
            width=x2-x1+self.x_start,
            #height=self.ps['cell_height'],
            window=self.listbox,
            anchor='nw',
            tag='listbox_win')


    def render_entry(self, row, col, text):
        cell_tag = f'cell-text:{row}_{col}'
        sv = tk.StringVar()
        sv.set(text)

        self.remove_widgets('entry')

        x1, y1, x2, y2 = self.get_cell_coords(row, col)

        self.text_editor = ttk.Entry(
            self.parent,
            width=x2-x1,
            textvariable=sv,
            takefocus=1)

        def callback(e):
            value = sv.get()

            # draw text
            self.delete(cell_tag)
            # self.create_text(
            #     x1+self.cell_width/2,
            #     y1+self.ps['cell_height']/2,
            #     text=value,
            #     fill='brown',
            #     anchor='w',
            #     tag=(cell_tag,)
            # )
            #print ('entry-callback', e.keysym, cell_tag, value)
            self.entry_queue[cell_tag] = value

            if e.keysym in ['Return', 'Escape']:
                row_key, col_key = self.get_rc_key(row, col)
                self.set_data_value(row_key, col_key, value)
                #self.entry_queue.pop()
                del self.entry_queue[cell_tag]
                self.delete('entry_win')


        self.text_editor.icursor(tk.END)
        #self.cell_entry.bind('<Return>', callback)
        self.text_editor.bind('<KeyRelease>', callback)
        self.text_editor.focus_set()
        #create_window
        self.create_window(
            x1,
            y1,
            width=x2-x1+self.x_start,
            height=self.ps['cell_height'],
            window=self.text_editor,
            anchor='nw',
            tag='entry_win')

    #def handle_enter_drag(self, event):
    #    print (event, 'entry drag')

    def render_row_highlight(self, rows=[]):
        '''use border only & raise over other components
        if args row = None, use self.selected['row_list']
        '''
        self.delete('row-highlight')

        for row in rows:
            _1, row_y1, _2, row_y2 = self.get_cell_coords(row, 0)
            self.create_rectangle(
                0, row_y1, self.width + self.x_start, row_y2,
                fill=self.ps['style']['color']['row-highlight'],
                width=2,
                outline=self.ps['style']['color']['cell-highlight-border'],
                stipple="gray50",
                tags=('row-highlight'))

        #self.lower('row-highlight')
        self.tag_raise('row-highlight')

    def render_selected(self, row, col):
        '''render current_row by mouse selected
        if no args, render multi row by self.selected
        '''
        self.current_rc = [row, col]

        self.delete('cell-highlight')
        self.delete('cell-highlight-border')
        #self.delete('cell-highlight-drag')

        x1, y1, x2, y2 = self.get_cell_coords(row, col)
        # cell highlight
        self.create_rectangle(
            x1,
            y1,
            x2+self.x_start,
            y2,
            outline=self.ps['style']['color']['cell-highlight-border'],
            width=3,
            tag=('cell-highlight',))

        self.tag_raise('cell-highlight')

        #self.render_row_highlight(row)

        if self.ps['row_index_display']:
            self.parent.row_index.render(row)
        self.parent.column_header.render(col)

    def render_box(self, selected):
        '''render rectangle box (multi-row & multi-column)'''
        self.delete('box-highlight')
        self.delete('row-highlight')
        self.parent.row_index.clear_selected()

        xs1, ys1, xs2, ys2 = self.get_cell_coords(selected['row_start'], selected['col_start'])
        xe1, ye1, xe2, ye2 = self.get_cell_coords(selected['row_end'], selected['col_end'])
        box_fill_color = self.ps['style']['color']['box-highlight']
        # don't change color (purple)
        #if len(self.copy_buffer):
        #    box_fill_color = self.ps['style']['color']['box-highlight-buffer']

        if self.ps['box_display_type'] == 'lower':
            self.create_rectangle(
                xs1,
                ys1,
                xe2+self.x_start,
                ye2,
                fill=box_fill_color,
                outline=self.ps['style']['color']['box-border'],
                width=2,
                tags=('box', 'box-highlight',))
            self.tag_lower('box-highlight')
        elif self.ps['box_display_type'] == 'raise':
            self.create_rectangle(
                xs1,
                ys1,
                xe2+self.x_start,
                ye2,
                fill=box_fill_color,
                stipple="gray50",
                outline=self.ps['style']['color']['box-border'],
                width=2,
                tags=('box', 'box-highlight',))
            self.tag_raise('box-highlight')

    def clear(self):
        self.delete('cell')
        self.delete('cell-border')
        self.delete('box')
        self.delete('row-highlight')
        self.delete('entry_win')

    def get_cell_coords(self, row, col):
        #print (row, col, self.ps['column_width_list'])
        x1 = self.x_start + self.ps['column_width_list'][col]
        x2 = self.ps['column_width_list'][col+1]
        y1 = self.y_start + (self.ps['cell_height'] * row)
        y2 = y1 + self.ps['cell_height']
        return x1, y1, x2, y2

    def get_rc_key(self, row, col):
        iid = self.ps['row_keys'][row]
        col_key = self.ps['col_keys'][col]
        return (iid, col_key)

    @custom_action(name='set_data')
    def set_data_value(self, row_key, col_key, value):
        self.ps['data'][row_key][col_key] = value
        logging.debug('MainTable.save_data_value: {}, {}: {}'.format(row_key, col_key, value))
        self.render()

        #if func := self.ps.get('after_set_data_value', ''):
        #    return func(row_key, col_key, value)
        return row_key, col_key, value

    def get_rc(self, event_x, event_y):
        result = {
            'row': None,
            'col': None,
            'row_key': None,
            'col_key': None,
            'is_available': False,
        }

        x = int(self.canvasx(event_x))
        y = int(self.canvasy(event_y))

        if x < 1 or y < 1:
            return result

        """get row, column (number) for giving mouse position: x ,y"""
        if y > self.ps['num_rows']*self.ps['cell_height']:
            # 點到表格下面, 不要動作
            return result
        elif x > self.ps['column_width_list'][-1]:
            # 點到表格右邊
            #select row, or return?
            #return int((y-self.y_start)/self.ps['cell_height']), -1
            return result

        col = None
        for i, v in enumerate(self.ps['column_width_list']):
            next_x = self.ps['column_width_list'][min(i+1, len(self.ps['column_width_list']))]
            if x > v and x <= next_x:
                col = i
                break
        row = int((y-self.y_start)/self.ps['cell_height'])
        row_key, col_key = self.get_rc_key(row, col)
        result.update({
            'row': row,
            'col': col,
            'row_key': row_key,
            'col_key': col_key,
            'is_available': True
        })
        return result

    def save_entry_queue(self):
        for i, v in self.entry_queue.items():
            rc = i.replace('cell-text:', '').split('_')
            row_key, col_key = self.get_rc_key(int(rc[0]), int(rc[1]))
            self.set_data_value(row_key, col_key, v)
            self.entry_queue = {}

    def handle_mouse_drag(self, event):
        #print (event, 'drag')

        res_rc = self.get_rc(event.x, event.y)
        if not res_rc['is_available']:
            return

        row = res_rc['row']
        col = res_rc['col']

        self.selected.update({
            'mode': 'drag',
            'row_end': row,
            'col_end': col,
            'row_list': list(range(self.selected['row_start'], row+1)),
            'col_list': list(range(self.selected['col_start'], col+1))
        })
        ''' TODO
        if row >= self.ps['num_rows']:
            #or self.startrow > self.rows:
            return
        else:
            self.selected['row_end'] = row

        if col > self.ps['num_cols']:
            #or self.startcol > self.cols:
            return
        else:
            self.selected['col_end'] = col
            if self.selected['col_start'] is None or self.selected['col_end'] is None:
                return
            if self.selected['col_end'] < self.selected['col_start']:
                self.selected['col_list'] = range(self.selected['col_end'], self.selected['col_start']+1)
            else:
                self.selected['col_list'] = range(self.selected['col_start'], self.selected['col_end']+1)


        if self.selected['row_end'] != self.selected['row_start']:
            if self.selected['row_end'] < self.selected['row_start']:
                self.selected['row_list'] = range(self.selected['row_end'], self.selected['row_start']+1)
            else:
                self.selected['row_list'] = range(self.selected['row_start'], self.selected['row_end']+1)

        else:
            self.selected['row_list'] = [self.current_rc[0]]

        if len(self.selected['row_list']) > 1 and len(self.selected['col_list']):
        '''
        self.render_box(self.selected)

    def remove_widgets(self, widget='all'):
        if widget in ['all', 'entry'] and hasattr(self, 'text_editor'):
            # save data if last entry not Enter or Escape
            if len(self.entry_queue):
                self.save_entry_queue()
            self.text_editor.destroy()
            del self.text_editor
        self.delete('entry_win')

        if widget in ['all', 'listbox'] and hasattr(self, 'listbox'):
            self.listbox.destroy()
            del self.listbox
        self.delete('listbox_win')

    def handle_mouse_click_right(self, event):
        if hasattr(self, 'popup_menu'):
            self.popup_menu.destroy()

        res_rc = self.get_rc(event.x, event.y)
        if not res_rc['is_available']:
            return

        row = res_rc['row']
        col = res_rc['col']
        self.current_rc = [row, col]

        self.remove_widgets()

        #self.render_selected(row, col)

        self.popup_menu = tk.Menu(self)
        #self.popup_menu.add_command(label='複製一列', command=lambda: self.clone_row(res_rc['row_key']))
        self.popup_menu.add_command(label='複製一列', command=self.clone_rows)
        self.popup_menu.add_command(label='刪除一列', command=self.remove_rows)

        # custom menus
        self.popup_menu.add_separator()
        for m in self.ps['custom_menus']:
            if m['type'] == 'normal':
                self.popup_menu.add_command(label=m['label'], command=m['command'])
            elif m['type'] == 'menu':
                submenu = tk.Menu(self.popup_menu)
                for subm_choice in m['choices']:
                    submenu.add_command(label=subm_choice, command=lambda x=subm_choice: m['command'](x))
                self.popup_menu.add_cascade(label=m['label'], menu=submenu, underline=0)
        # end custom menus
        self.popup_menu.add_separator()

        self.popup_menu.add_command(label='複製內容', command=self.copy_to_buffer)
        self.popup_menu.add_command(label='貼上內容', command=self.paste_from_buffer)
        #self.popup_menu.add_command(label='清除 pattern', command=self.clear_pattern)
        x1, y1, x2, y2 = self.get_cell_coords(row, col)
        self.popup_menu.post(event.x_root, event.y_root)
        #print (y1, y2, int((y1+y2)/2), event.y_root)

    @custom_action(name='mouse_click')
    def handle_mouse_button_1(self, event):
        # flush entry_queue
        #if len(self.entry_queue):
        #    self.save_entry_queue()
        #    self.render()

        # clear
        #self.delete('entry_win')
        self.remove_widgets()
        self.parent.row_index.clear_selected()
        self.delete('row-highlight')
        self.delete('box-highlight')

        res_rc = self.get_rc(event.x, event.y)
        if not res_rc['is_available']:
            return

        row = res_rc['row']
        col = res_rc['col']
        row_key = res_rc['row_key']
        col_key = res_rc['col_key']

        self.current_rc[0] = row
        self.current_rc[1] = col

        # reset selected
        self.selected = {
            'mode': 'click',
            'row_start': row,
            'row_end': row,
            'col_start': col,
            'col_end': col,
            'row_list': [row],
            'col_list': [],
        }
        #self.render_box(self.selected)

        self.render_selected(row, col)

        # draw entry if not readonly
        if not row_key or not col_key:
            return

        #text = self.ps['data'][row_key][col_key]
        #col_type = self.ps['columns'][col_key].get('type', 'entry')
        # if col_type == 'entry':
        #     self.render_entry(row, col, text)
        # elif col_type == 'listbox':
        #     choices = self.ps['columns'][col_key].get('choices', [])
        #     self.render_listbox(row, col, choices)
        # else:
        #     self.remove_widgets()

        logging.debug('click: {}'.format(self.current_rc))
        return self.current_rc

    def handle_ctrl_button_1(self, event):
        #print ('ctrl_b1', event)

        # clear
        self.delete('entry_win')

        res_rc = self.get_rc(event.x, event.y)
        if not res_rc['is_available']:
            return

        row = res_rc['row']
        col = res_rc['col']
        #row_key = res_rc['row_key']
        #col_key = res_rc['col_key']
        #print (row, col, row_key, col_key)
        # reset selected

        row_selected = self.selected['row_list']
        if row_selected == None:
            row_selected = []

        if len(row_selected) == 0:
            row_selected.append(row)
        elif row not in row_selected:
            row_selected.append(row)
        else:
            row_selected.remove(row)

        self.selected.update({
            'row_start': None,
            'row_end': None,
            'col_start': None,
            'col_end': None,
            'row_list': row_selected,
        })

        #self.render_row_highlight()

    @custom_action(name='arrow_key')
    def handle_arrow_key(self, event):
        #print ('handle_arrow:', event, self.current_rc)
        row, col = self.current_rc

        if row == None:
            return

        if event.keysym in ('Up', 'Down', 'Left', 'Right'):
            self.remove_widgets()

        if event.keysym == 'Up':
            if row == 0:
                return
            else:
                row -= 1
        elif event.keysym == 'Down':
            if row >= self.ps['num_rows'] - 1:
                return
            else:
                row += 1

        elif event.keysym == 'Left':
            #text = self.ps['data'][row_key][col_key]
            if col == 0:
                return
            else:
                col -= 1

        elif event.keysym == 'Right':
            if col >= self.ps['num_cols'] - 1:
                return
            else:
                col += 1

        self.selected.update({
            'row_start': None,
            'row_end': None,
            'col_start': None,
            'col_end': None,
            'row_list': [row],
            'col_list': [col],
        })
        #if event.keysym in ('Up', 'Down'):
        self.render_selected(row, col)
        #elif event.keysym in ('Left', 'Right'):
        # create text_editor
            #row_key, col_key = self.get_rc_key(row, col)
            #if self.ps['columns'][col_key].get('type', 'entry') == 'entry':
                #text = self.ps['data'][row_key][col_key]
                #self.render_text_editor(row, col, text)

        self.current_rc[0] = row
        self.current_rc[1] = col
        return self.current_rc

    @custom_action(name='clone_row')
    def clone_rows(self):
        #rows = self.parent.row_index.get_selected_rows()
        rows = self.parent.get_row_list()
        logging.debug(f'rows: {rows}')

        if len(rows) == 0:
            return

        new_data = {}
        res = []
        insert_map = {}
        keys = list(self.ps['data'].keys())
        for row in rows:
            row_key, col_key = self.get_rc_key(row, 0)
            clone_data = dict(self.ps['data'][row_key])
            iid_key = row_key[4:] # remove "iid:"
            prefix = f'iid:{iid_key}-'
            clone_iid = f'iid:{iid_key}-0' # default add new branch

            sibling_counter = 0
            insert_to = 0
            for counter, k in enumerate(keys):
                if prefix in k:
                    sibling_counter += 1
                    insert_to = counter + 1

            if sibling_counter > 0: # already has branch, sibling
                clone_iid = f'{prefix}{sibling_counter}'
            else:
                insert_to = keys.index(row_key)

            insert_map[insert_to] = (clone_iid, clone_data)
            res.append((row_key, clone_iid))
        #print (insert_map)
        #new_data = self.ps['data']

        for _, (iid, clone_data) in insert_map.items():
            self.ps['data'][iid] = clone_data
        for d in sorted(self.ps['data'].items(), key=lambda x: x):
            new_data[d[0]] = d[1]

        self.parent.refresh(new_data)
        self.parent.row_index.clear_selected()
        #if func := self.ps.get('after_clone_row', ''):
        #    return func(row_key, clone_iid)
        #return row_key, clone_iid
        return res

    @custom_action(name='remove_row')
    def remove_rows(self):
        rows = self.parent.get_row_list()
        logging.debug(f'remove_rows: {rows}')

        # only do first row
        if len(rows) > 0:
            row = rows[0]
            row_key, col_key = self.get_rc_key(row, 0)
            del self.ps['data'][row_key]
            self.parent.refresh(self.ps['data'])

            return row
        return rows

    def get_selected_list(self):
        '''return rows depends on selected mode'''
        s = self.selected
        result = {
            'rows': [],
            'cols': [],
        }

        mode = s.get('mode', '')
        if mode == 'drag':
            if s['row_end'] >= 0 or s['row_start'] >= 0:
                diff = s['row_end'] - s['row_start']
                result['rows'] = list(range(s['row_start'], s['row_start'] + diff + 1))

            if s['col_end'] >= 0 or s['col_start'] >= 0:
                diff = s['col_end'] - s['col_start']
                result['cols'] = list(range(s['col_start'], s['col_start'] + diff + 1))
        elif mode == 'ctrl-click':
            result['rows'] = s['row_list']

        return result

    def copy_to_buffer(self):
        logging.debug('selected: {}'.format(self.selected))
        buf = []
        res = self.get_selected_list()

        for row in res['rows']:
            row_values = []
            for col in res['cols']:
                row_key, col_key = self.get_rc_key(row, col)
                v = self.ps['data'][row_key][col_key]
                row_values.append(v)
            buf.append(row_values)

        self.copy_buffer = buf
        logging.debug('buf: {}'.format(buf))

    #@custom_action(name='apply_pattern')
    def paste_from_buffer(self):
        logging.debug('copy_buffer:'.format(self.copy_buffer))
        res = self.get_selected_list()
        buf = self.copy_buffer
        num_buf_rows = len(buf)
        num_buf_cols = len(buf[0])
        for i, row in enumerate(res['rows']):
            buf_i = i % num_buf_rows
            for j, col in enumerate(res['cols']):
                buf_j = j % num_buf_cols
                row_key, col_key = self.get_rc_key(row, col)
                value = buf[buf_i][buf_j]
                self.set_data_value(row_key, col_key, value)

        self.copy_buffer = []
        #return (buf, res)

    def clear_pattern(self):
        self.pattern_copy = []

    def handle_row_index_selected(self, rows):
        self.render_row_highlight(rows)

    def handle_listbox_click(self, event, row, col):
        cur_sel = self.listbox.curselection()
        if cur_sel:
            text = self.listbox.get(cur_sel)
            row_key, col_key = self.get_rc_key(row, col)
            self.set_data_value(row_key, col_key, text)
        self.remove_widgets('listbox')

    def init_data(self):
        logging.debug('init_data')
        self.current_rc = [0, 0]
        self.selected = {}
        self.render_selected(0, 0)

    def clear_selected(self):
        self.delete('cell-highlight')
        self.delete('cell-highlight-border')
        self.selected = {}
        self.parent.refresh(self.ps['data'])
