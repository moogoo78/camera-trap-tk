import logging
from pathlib import Path
import functools

import tkinter as tk
from tkinter import ttk

from PIL import ImageTk, Image

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
        self.current_rc = [None, None]
        self.selected = {
            'row_start': None,
            'row_end': None,
            'col_start': None,
            'col_end': None,
            'col_list': [],
            'row_list': [],
        }
        self.has_box = False


        # binding
        self.bind('<Button-1>', self.handle_mouse_click_left)
        self.bind('<Button-3>', self.handle_mouse_click_right)
        self.bind('<B1-Motion>', self.handle_mouse_drag)
        self.parent.master.bind_all('<Up>', self.handle_arrow_key)
        self.parent.master.bind_all('<Down>', self.handle_arrow_key)


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
                col_type = col.get('type', 'text')
                y_top = row_counter * self.ps['cell_height'] + self.y_start
                y_center = y_top + self.ps['cell_height']/2
                if col_type == 'text':
                    rect = self.create_text(
                        x_center,
                        y_center,
                        text=row.get(col_key, ''),
                        tags=('cell', 'cell-text', cell_tag)
                    )
                elif col_type == 'image':
                    img_path = row.get(col_key, '')
                    if img_path: # TODO check exist
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


    def render_text_editor(self, row, col, text):
        cell_tag = f'cell-text:{row}_{col}'
        sv = tk.StringVar()
        sv.set(text)

        self.remove_entry()

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

    def handle_enter_drag(self, event):
        print (event, 'entry drag')

    def render_selected(self, row, col):
        self.current_rc = [row, col]

        self.delete('cell-highlight')
        self.delete('cell-highlight-border')
        self.delete('cell-highlight-drag')
        self.delete('row-highlight')

        x1, y1, x2, y2 = self.get_cell_coords(row, col)
        # cell highlight
        self.create_rectangle(
            x1,
            y1,
            x2+self.x_start,
            y2,
            outline=self.ps['style']['color']['cell-highlight-border'],
            width=4,
            tag=('cell-highlight',))
        self.lower('cell-highlight')


        # render row highlight
        self.create_rectangle(
            0, y1, self.width + self.x_start, y2,
            fill=self.ps['style']['color']['row-highlight'],
            tags=('row-highlight'))

        self.lower('row-highlight')


    def render_box(self, selected):
        self.delete('box-highlight')

        xs1, ys1, xs2, ys2 = self.get_cell_coords(selected['row_start'], selected['col_start'])
        xe1, ye1, xe2, ye2 = self.get_cell_coords(selected['row_end'], selected['col_end'])
        self.create_rectangle(
            xs1,
            ys1,
            xe2+self.x_start,
            ye2,
            fill=self.ps['style']['color']['box-highlight'],
            outline=self.ps['style']['color']['box-border'],
            width=2,
            tags=('box', 'box-highlight',))
        self.lower('box-highlight')

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
            return False

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
            self.has_box = True
            # box don't need this
            self.delete('row-highlight')
            self.delete('entry_win')
            self.delete('cell-highlight')
            self.render_box(self.selected)

    def remove_entry(self):
        if hasattr(self, 'text_editor'):
            # save data if last entry not Enter or Escape
            if len(self.entry_queue):
                self.save_entry_queue()
            self.text_editor.destroy()
        self.delete('entry_win')

    def handle_mouse_click_right(self, event):
        if hasattr(self, 'popup_menu'):
            self.popup_menu.destroy()

        res_rc = self.get_rc(event.x, event.y)
        if not res_rc['is_available']:
            return

        row = res_rc['row']
        col = res_rc['col']
        self.current_rc = [row, col]

        self.remove_entry()
        self.render_selected(row, col)

        self.popup_menu = tk.Menu(self)
        self.popup_menu.add_command(label='複製一列', command=lambda: self.clone_row(res_rc['row_key']))
        self.popup_menu.add_command(label='刪除一列', command=lambda: self.remove_row(res_rc['row_key']))
        x1, y1, x2, y2 = self.get_cell_coords(row, col)
        self.popup_menu.post(event.x_root, event.y_root)
        #print (y1, y2, int((y1+y2)/2), event.y_root)

    @custom_action(name='mouse_click')
    def handle_mouse_click_left(self, event):
        # flush entry_queue
        if len(self.entry_queue):
            self.save_entry_queue()
            self.render()

        # clear
        self.delete('entry_win')

        res_rc = self.get_rc(event.x, event.y)
        if not res_rc['is_available']:
            return

        row = res_rc['row']
        col = res_rc['col']
        row_key = res_rc['row_key']
        col_key = res_rc['col_key']

        # reset selected
        self.selected = {
            'row_start': row,
            'row_end': row,
            'col_start': col,
            'col_end': col,
            'row_list': [row],
            'col_list': [col],
        }
        self.render_box(self.selected)

        if col == -1:
            col = 0 # 預設如點第一格

        self.render_selected(row, col)

        # draw entry if not readonly
        text = self.ps['data'][row_key][col_key]
        if self.ps['columns'][col_key].get('type', 'entry') == 'entry':
            self.render_text_editor(row, col, text)
        else:
            self.remove_entry()

        return self.current_rc
        #if func := self.ps.get('after_click', ''):
        #    return func(self.current_rc)

    @custom_action(name='arrow_key')
    def handle_arrow_key(self, event):
        #print ('handle_arrow:', event, self.current_rc)
        if self.current_rc[0] == None:
            return
        if event.keysym == 'Up':
            self.remove_entry()
            if self.current_rc[0] == 0:
                return
            else:
                self.current_rc[0] = self.current_rc[0] - 1
        elif event.keysym == 'Down':
            self.remove_entry()
            if self.current_rc[0] >= self.ps['num_rows'] - 1:
                return
            else:
                self.current_rc[0] = self.current_rc[0] + 1

        self.render_selected(self.current_rc[0], self.current_rc[1])
        #if func := self.ps.get('after_arrow_key', ''):
        #    return func(self.current_rc)
        return self.current_rc

    @custom_action(name='clone_row')
    def clone_row(self, row_key):
        #print (row, 'clone')
        new_data = {}
        is_cloned = False
        clone_data = dict(self.ps['data'][row_key])
        keys = list(self.ps['data'].keys())
        iid_key = row_key[4:] # remove "iid:"
        prefix = f'iid:{iid_key}-'
        clone_iid = f'iid:{iid_key}-0' # default add new branch

        sibling_counter = 0
        insert_to = 0
        for counter, k in enumerate(keys):
            if prefix in k:
                sibling_counter += 1
                insert_to = counter+1

        if sibling_counter > 0: # already has branch, sibling
            clone_iid = f'{prefix}{sibling_counter}'
        else:
            insert_to = keys.index(row_key) + 1

        #print (sibling_counter, insert_to)
        for counter, (iid, row_data) in enumerate(self.ps['data'].items()):
            if not is_cloned and counter == insert_to:
                trimed_clone_iid = clone_iid[4:]
                new_data[trimed_clone_iid] = clone_data
            trimed_iid = iid[4:]
            new_data[trimed_iid] = row_data

        logging.debug(f'clone row: {row_key} -> {clone_iid}, insert to {insert_to}')
        self.parent.refresh(new_data)

        #if func := self.ps.get('after_clone_row', ''):
        #    return func(row_key, clone_iid)
        return row_key, clone_iid

    @custom_action(name='remove_row')
    def remove_row(self, row_key=''):
        logging.debug(f'remove_row: {row_key}')

        del self.ps['data'][row_key]
        self.parent.refresh(self.ps['data'])
        return row_key
