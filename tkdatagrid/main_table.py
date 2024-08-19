import logging
import functools

import tkinter as tk
from tkinter import ttk

from PIL import ImageTk, Image

from .utils import check_image
from .autocomplete_widget import Autocomplete
"""
mist: #90AFC5
stone: #336B87
shadow: #2A3132
automn leaf: #763626
#https://www.canva.com/design/DADfC5CQ0W4/remix?action2=create&mediaId=DADfC5CQ0W4&signupReferrer=blog&utm_source=blog&utm_medium=content&utm_campaign=100-color-combinations&_branch_match_id=812929534608293691
"""


def custom_action(_func=None, *, name='', hook=''):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            if act := args[0].ps['custom_actions'].get(name, None):
                if act[0] == 'after':
                    ret = func(*args, **kwargs)
                    if ret is None:
                        pass
                    elif isinstance(ret, tuple):
                        act[1](*ret)
                    else:
                        act[1](ret)
                    return ret

                elif act[0] == 'bind':
                    act[1]()
            else:
                return func(*args, **kwargs)

        return wrapper

    if _func is None:  # called with argument
        return decorator
    else:  # without argument
        return decorator(_func)


CLONE_ROWS_KEY_DELIMETER = '-_-'

class MainTable(tk.Canvas):

    def __init__(
            self,
            parent=None,
            width=None,
            height=None,
            **kwargs):

        self.parent = parent
        self.ps = self.parent.state  # parent_state

        self.width = self.ps['width']
        self.height = self.ps['height']

        super().__init__(
            parent,
            bg=self.ps['style']['color']['bg'],
            bd=2,
            relief='groove',
            height=self.height,
            scrollregion=(0, 0, 560, 915),
        )
        # set default
        self.x_start = 0
        self.y_start = 0

        self.entry_queue = {}

        self.ps['after_row_index_selected'] = self.handle_row_index_selected

        self.init_data()

        # binding
        # -------
        # mouse
        self.bind('<Button-1>', self.handle_mouse_button_1)
        self.bind('<Button-2>', self.handle_mouse_button_2) # macOS
        self.bind('<Button-3>', self.handle_mouse_button_3) # Windows
        self.bind('<B1-Motion>', self.handle_mouse_move)
        self.bind('<MouseWheel>', self.handle_mouse_wheel)
        self.bind('<Button-4>', self.handle_mouse_wheel)
        self.bind('<Button-5>', self.handle_mouse_wheel)
        self.bind('<Double-Button-1>', self.start_edit)
        self.bind('<ButtonRelease-1>', self.handle_mouse_release_1)
        # key
        self.bind_all('<Escape>', self.remove_widgets)
        self.bind_all('<space>', self.start_edit)
        #self.bind_all('<KeyPress>', self.handle_key_press)
        # self.bind_all('<KeyRelease>', self.handle_key_release)
        # composite
        self.bind_all('<Control-c>', self.handle_ctrl_c)
        self.bind_all('<Control-v>', self.handle_ctrl_v)
        self.bind('<Control-Button-1>', self.handle_ctrl_button_1)
        self.bind('<Shift-Button-1>', self.handle_shift_button_1)
        #self.bind("<Configure>", self.resize)

        self.apply_custom_binding(self.ps['custom_binding'])

        self.set_keyboard_control(True)

    def apply_custom_binding(self, custom_binding, is_unbind=False):

        if payload := custom_binding:
            for bind_key in payload['bind_list']:
                # self.parent.master.bind_all(f'<{bind_key}>', custom_binding['command'])
                if is_unbind is False:
                    self.bind_all(f'<{bind_key}>', payload['command'])
                else:
                    self.unbind_all(f'<{bind_key}>')

    def handle_key_press(self, event):
        print('key press', event)

    # def handle_key_release(self, event):
    #    print('re', event)

    def set_keyboard_control(self, to_bind=True):
        if to_bind is True:
            self.bind_all('<Return>', self.start_edit)
            self.bind_all('<Up>', self.handle_arrow_key)
            self.bind_all('<Down>', self.handle_arrow_key)
            self.bind_all('<Left>', self.handle_arrow_key)
            self.bind_all('<Right>', self.handle_arrow_key)
        else:
            self.unbind_all('<Return>')
            self.unbind_all('<Up>')
            self.unbind_all('<Down>')
            self.unbind_all('<Left>')
            self.unbind_all('<Right>')

    @custom_action(name='mouse_click')
    def handle_mouse_button_1(self, event):
        logging.debug('mouse click button1, xy: {},{}'.format(event.x, event.y))
        self.selected.update({
            'action': 'click',
            'ctrl_list': [],
        })

        x = int(self.canvasx(event.x))
        y = int(self.canvasy(event.y))
        # print(self.selected)
        if self.selected['box'][2] is not None and self.selected['box'][0] is not None:  # prevent first time click None value
            handle_x_center = self.ps['column_width_list'][self.selected['box'][3]+1]
            handle_y_center = self.ps['cell_height']*(self.selected['box'][2]+1)
            handle_x_range = [handle_x_center-4, handle_x_center+4]
            handle_y_range = [handle_y_center-4, handle_y_center+4]

            if x >= handle_x_range[0] and x <= handle_x_range[1] \
               and y >= handle_y_range[0] and y <= handle_y_range[1]:
                # click on handle
                if self.selected['drag_end'][0] == None or self.selected['drag_end'][1] == None:
                    # previous action is click
                    self.selected.update({'action': 'single-handle'})
                else:
                    self.selected.update({'action': 'box-handle'})
                return

        # click on cell
        return self.click_on_cell(event)

    def click_on_cell(self, event):
        # flush entry_queue
        # if len(self.entry_queue):
        #    self.save_entry_queue()
        #    self.render()

        # clear
        # self.delete('entry_win')
        self.remove_widgets()
        # self.parent.row_index.clear_selected()
        # self.delete('row-highlight')
        # self.delete('box')
        self.delete('drag-box')
        self.delete('fill-box')

        res_rc = self.get_rc(event.x, event.y)
        if not res_rc['is_available']:
            return

        row = res_rc['row']
        col = res_rc['col']
        row_key = res_rc['row_key']
        col_key = res_rc['col_key']

        # draw entry if not readonly
        if not row_key or not col_key:
            return

        self.current_rc[0] = row
        self.current_rc[1] = col

        # reset selected and record drag_start
        self.selected.update({
            'drag_start': [row, col],
            'drag_end': [None, None],
            'box': [row, col, row, col],
        })

        self.render_cell_outline(row, col)

        self.render_fill_handle(res_rc['cell_xy'], col_key)

        # text = self.ps['data'][row_key][col_key]
        # col_type = self.ps['columns'][col_key].get('type', 'entry')
        # if col_type == 'entry':
        #     self.render_entry(row, col, text)
        # elif col_type == 'listbox':
        #     choices = self.ps['columns'][col_key].get('choices', [])
        #     self.render_listbox(row, col, choices)
        # else:
        #     self.remove_widgets()

        logging.debug('clicked cell rc: {}'.format(self.current_rc))
        return self.get_rc_key(row, col)

    def handle_mouse_button_2(self, event):
        self.render_popup_menu(event)

    def handle_mouse_move(self, event):
        logging.debug('mouse move xy: {}, {}'.format(event.x, event.y))

        # if press <Control> do nothing
        if event.state == 260: # tested in macOS
            # event.state display as Control|Button1
            return

        # print(self.selected)
        selected = self.selected
        res_rc = self.get_rc(event.x, event.y)
        if not res_rc['is_available']:
            return

        row = res_rc['row']
        col = res_rc['col']

        r1 = selected['drag_start'][0]
        c1 = selected['drag_start'][1]
        r2 = row
        c2 = col

        if selected['drag_start'][0] is None or selected['drag_start'][1] is None:
            return

        # if action == handle, can only move horizontal
        if row < selected['drag_start'][0]:
            # select from bottom to top, swap value
            r2, r1 = r1, r2

        if col < selected['drag_start'][1]:
            # select from right to left, swap value
            c2, c1 = c1, c2

        self.selected['drag_end'] = [row, col]

        if self.selected['drag_start'][0] != self.selected['drag_end'][0] or \
           self.selected['drag_start'][1] != self.selected['drag_end'][1]:
            # drag in one cell, don't render_box, 只有一格就不用畫了
            #r1, c1, r2, c2 = self.selected['box']
            handle_xy = self.get_cell_coords(r2, c2)
            if self.selected['action'] in ['click', 'drag']:
                #self.selected.update()
                self.selected.update({
                    'action': 'drag',
                    'box': [r1, c1, r2, c2],
                })
                logging.debug('mouse dragging')
                self.render_drag_box(self.selected['box'])
            elif '-handle' in self.selected['action']:  # single-handle/box-handle
                c2 = selected['box'][3] # donnot drag horizontal
                fill = [self.selected['box'][0], selected['box'][1], r2, c2]
                self.render_fill_box(fill)
                self.selected.update({'fill': fill})

            self.render_fill_handle(handle_xy, res_rc['col_key'])

            # scroll if mouse drag down
            # donnot use canvasy(), y will accumulate while scroll down
            #print('----', self.height, event.y, self.ps['height_adjusted'])
            h_limit = self.ps.get('height_adjusted', 0)
            if event.y >= h_limit - 20:
                self.to_scroll('down')
            elif event.y <= 20:
                self.to_scroll('up')

        # print('after move', self.selected)

    def handle_shift_button_1(self, event):
        logging.debug('shift_button_1 <Shift_button-1>'.format(self.selected))

        res_rc = self.get_rc(event.x, event.y)
        if not res_rc['is_available']:
            return

        box = self.selected['box']
        self.selected.update({
            'box': [box[0], box[1], res_rc['row'], box[3]]
        })
        self.render_drag_box(self.selected['box'])
        handle_xy = self.get_cell_coords(res_rc['row'], box[3])
        self.render_fill_handle(handle_xy, res_rc['col_key'])

    def handle_ctrl_button_1(self, event):
        logging.debug('ctrl_button_1 <Control-Button-1>: {}'.format(self.selected))
        ctrl_list = self.selected['ctrl_list']

        res_rc = self.get_rc(event.x, event.y)
        if not res_rc['is_available']:
            return
        row = res_rc['row']
        col = res_rc['col']
        if res_rc['col_key'] in self.ps['cols_on_ctrl_button_1']:
            ctrl_list.append([row, col])
            self.render_cell_outline(row, col, color='#8ca22d', is_delete=False)
            self.selected.update({'ctrl_list': ctrl_list})

    def start_edit(self, event):
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
        elif col_type == 'autocomplete':
            # if listbox opened close that
            if hasattr(self, 'autocomplete'):
                self.remove_widgets('autocomplete')
            else:
                choices = self.ps['columns'][col_key]['choices']
                self.render_autocomplete(row, col, choices)
        elif col_type == 'entry':
            if hasattr(self, 'text_editor'):
                # text_editor can have space input
                # do nothing
                pass
            else:
                text = self.ps['data'][row_key][col_key]
                self.render_entry(row, col, text)

    def handle_mouse_wheel(self, event):
        # print (event.num, event.delta, self.canvasy(0), self.winfo_height(), self.parent.row_index.winfo_height())
        # event.num exists in linux or mac ?
        # print(event, event.num, event.delta) => mac: delta -1/-2/-3/1/2/3
        if event.num == 5 or event.delta == -120:
            self.yview_scroll(1, 'units')
            if self.ps['row_index_display']:
                self.parent.row_index.yview_scroll(1, 'units')
        elif event.num == 4 or event.delta == 120:
            if self.canvasy(0) < 0:  # ?
                return
            self.yview_scroll(-1, 'units')
            if self.ps['row_index_display']:
                self.parent.row_index.yview_scroll(-1, 'units')

    def to_scroll(self, direction):
        logging.debug('on_scroll: {}'.format(direction))
        if direction == 'down':
            self.yview_scroll(1, 'units')
            if self.ps['row_index_display']:
                self.parent.row_index.yview_scroll(1, 'units')
        elif direction == 'up':
            if self.canvasy(0) < 0:  # ?
                return
            self.yview_scroll(-1, 'units')
            if self.ps['row_index_display']:
                self.parent.row_index.yview_scroll(-1, 'units')

    def handle_ctrl_c(self, event):
        self.copy_to_clipboard(self.selected['box'])
        self.render_copy_box(self.selected['box'])

    def handle_ctrl_v(self, event):
        self.paste_from_clipboard()
        self.render_copy_box(self.selected['box'])

    def render(self):
        #print ('render', self.height, self.width, self.ps['height'], self.ps['width'])
        self.configure(scrollregion=(0,0, self.ps['width'], self.ps['height']+30))
        self.render_grid()
        self.render_data()
        #self.render_pagination() # mouse click cause column & rows highlight

    def render_grid(self):
        self.delete('cell-border')

        col_w_list = self.ps['column_width_list']
        color = self.ps['style']['color']
        num_rows = self.ps['num_rows']
        num_cols = self.ps['num_cols']

        # vertical line
        for i in range(num_cols+1):  # fixed size
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


    def update_text(self, rc_keys, value):
        #row = rc[0]
        #col = rc[1]
        #row_key, col_key = self.get_rc_key(row, col)
        tag = f'cell-text:{rc_keys[0]}_{rc_keys[1]}'
        self.delete(tag)

        row = self.get_row_index(rc_keys[0])
        x_left = self.get_col_offset(rc_keys[1])
        width = self.ps['columns'][rc_keys[1]]['width']
        x_center = x_left + 4 #x_left + width / 2
        y_top = row * self.ps['cell_height'] + self.y_start
        y_center = y_top + self.ps['cell_height'] / 2

        a = self.create_text(
            x_center,
            y_center,
            text=value,
            fill='#000000',
            anchor='w',
            font=self.ps['style']['font']['body_text'],
            tags=('cell', 'cell-text', tag)
        )


    def render_data(self):
        self.delete('cell')

        col_w_list = self.ps['column_width_list']

        font_family = self.ps['style']['font']['body_text'][0]
        font_size = self.ps['style']['font']['body_text'][1]

        # measure text width and decide truncate or not
        measurements = {}
        truncate_index = {}
        if trunc_type := self.ps['truncate'].get('type'):
            for c in self.ps['truncate']['columns']:
                measurements = { c: {}}
            if trunc_type == 'measure-all':
                for row_counter, (row_key, row) in enumerate(self.ps['data'].items()):
                    for col in self.ps['truncate']['columns']:
                        if val := row.get(col):
                            text_len = len(val)
                            #if  text_len > measurements[col]['max_len']:
                            if text_len not in measurements[col]:
                                measure_width = tk.font.Font(size=font_size, family=font_family).measure(val)
                                measurements[text_len] = measure_width
                            if measure_width > self.ps['columns'][col]['width'] + 10:
                                if col not in truncate_index:
                                    truncate_index[col] = []
                                truncate_index[col].append(row_counter)

        # render text
        for row_counter, (row_key, row) in enumerate(self.ps['data'].items()):
            for col_counter, (col_key, col) in enumerate(self.ps['columns'].items()):
                x_left = col_w_list[col_counter] + self.x_start
                x_center = x_left + 4 #x_left + col['width'] / 2
                # cell_tag = f'cell-text:{row_counter}_{col_counter}'
                cell_tag = f'cell-text:{row_key}_{col_key}'
                col_type = col.get('type', 'entry')
                y_top = row_counter * self.ps['cell_height'] + self.y_start
                y_center = y_top + self.ps['cell_height']/2
                if col_type in ['entry', 'text', 'listbox', 'autocomplete']:
                    text = row.get(col_key, '')
                    if truncate_col := truncate_index.get(col_key):
                        if row_counter in truncate_col:
                            text = f'{text[0:8]}...{text[-6:]}'

                    rect = self.create_text(
                        x_center,
                        y_center,
                        text=text,
                        anchor='w',
                        font=self.ps['style']['font']['body_text'],
                        fill='#000000',
                        tags=('cell', 'cell-text', cell_tag)
                    )
                elif col_type == 'image':
                    img_path = row.get(col_key, '')
                    if img_path and check_image(img_path):
                        img = Image.open(img_path)
                        img = ImageTk.PhotoImage(img.resize((50, 33)))
                        x_pad = 0
                        y_pad = 0
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


    # def render_pagination(self):
    #     tag = 'pagination'
    #     color = '#D3ECAF'
    #     self.delete(tag)
    #     x1 = self.x_start + 4
    #     y1 = self.y_start + self.ps['num_rows'] * self.ps['cell_height'] + 4;
    #     leg = 30
    #     shift_x = x1
    #     for i in range(0, self.ps['pagination']['num_pages']):
    #         page = i+1
    #         self.create_oval(
    #             shift_x + ( i*leg ), y1,
    #             shift_x + ( page*leg ), y1 + leg,
    #             width=1,
    #             fill=color,
    #             tags=(tag, f'{tag}-{page}'))

    #         self.create_text(
    #             shift_x + ( i*leg ) + leg/2,
    #             y1 + leg/2,
    #             text=page,
    #             fill='#2A7F60',
    #             tags=(tag, f'{tag}-{page}'))
    #         shift_x += 10
    #         self.tag_bind(
    #             f'{tag}-{page}',
    #             '<Button-1>',
    #             lambda _, x=page: self.parent.to_page(x))

    def render_listbox(self, row, col, choices, default=0):
        self.remove_widgets()
        self.set_keyboard_control(False)

        x1, y1, x2, y2 = self.get_cell_coords(row, col)
        style_font = self.ps['style']['font']['body_text']
        font= tk.font.Font(family=style_font[0], size=style_font[1])
        self.listbox = tk.Listbox(self.parent, background='white', selectmode=tk.SINGLE, font=font)#, **self.listbox_args)
        #'activestyle': 'none'
        #exportselection: False
        self.listbox.bind('<ButtonRelease-1>', lambda event: self.handle_listbox_click(event, row, col))
        self.listbox.bind_all('<Escape>', lambda event: self.handle_listbox_click(event, row, col))
        self.listbox.bind_all('<Return>', lambda event: self.handle_listbox_click(event, row, col))
        #self.listbox.bind('<<ListboxSelect>>', lambda event: self.handle_listbox_click(event, row, col)) # virtual event: replace <Return> & <ButtonRelease-1> ?
        self.listbox.bind_all('<Down>', lambda event: self.handle_listbox_arrow_key(event, 'down'))
        self.listbox.bind_all('<Up>', lambda event: self.handle_listbox_arrow_key(event, 'up'))

        #choices = filtered_choices if len(filtered_choices) else self.choices
        self.listbox.insert(tk.END, '')
        for i in choices:
            if isinstance(i, tuple):
                self.listbox.insert(tk.END, i[0])
            if isinstance(i, str):
                self.listbox.insert(tk.END, i)
        #self.listbox.grid(row=0, column=0, sticky = 'news')

        self.listbox.activate(0)
        self.listbox.select_set(0)

        self.create_window(
            x1,
            y1,
            width=x2-x1+self.x_start,
            #height=self.ps['cell_height'],
            window=self.listbox,
            anchor='nw',
            tag='listbox_win')


    def render_entry(self, row, col, text):
        row_key, col_key = self.get_rc_key(row, col)
        cell_tag = f'cell-text:{row_key}{CLONE_ROWS_KEY_DELIMETER}{col_key}'
        sv = tk.StringVar()
        sv.set(text)

        self.selected.update({'is_entry_on': False})

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
                if self.selected['is_entry_on'] is True:
                    # first time callback will get "outer event" if event.keysym = 'Return',
                    # is_entry_on is a workarund for that
                    row_key, col_key = self.get_rc_key(row, col)
                    self.set_data_value(row_key, col_key, value)
                    # self.entry_queue.pop()
                    del self.entry_queue[cell_tag]
                    self.delete('entry_win')

                self.selected.update({'is_entry_on': True})

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

    def render_autocomplete(self, row, col, choices, default=0):
        # print(row, col, choices)
        self.remove_widgets('autocomplete')
        x1, y1, x2, y2 = self.get_cell_coords(row, col)
        row_key, col_key = self.get_rc_key(row, col)

        def after_update_entry(value):
            self.set_data_value(row_key, col_key, value)
            self.delete('autocomplete_win')

            self.remove_widgets('autocomplete')
            self.set_keyboard_control(True)

        self.autocomplete = Autocomplete(self.parent, choices=choices, value='', after_update_entry=after_update_entry)

        self.create_window(
            x1,
            y1,
            width=x2-x1+self.x_start,
            height=self.ps['cell_height']*5,
            window=self.autocomplete,
            anchor='nw',
            tag='autocomplete_win')

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
                outline=self.ps['style']['color']['outline-dark'],
                stipple="gray50",
                tags=('row-highlight'))

        #self.lower('row-highlight')
        self.tag_raise('row-highlight')

    def render_cell_outline(self, row, col, is_delete=True, color=None):
        '''render current_row by mouse selected
        if no args, render multi row by self.selected
        '''
        self.current_rc = [row, col]

        if is_delete:
            self.delete('cell-outline')

        if color is None:
            color = self.ps['style']['color']['outline-dark']

        x1, y1, x2, y2 = self.get_cell_coords(row, col)
        # cell highlight
        self.create_rectangle(
            x1,
            y1,
            x2+self.x_start,
            y2,
            outline=color,
            width=2,
            tag=('cell-outline',),
        )
        self.tag_raise('cell-outline')

        # self.render_row_highlight(row)

        # if self.ps['row_index_display']:
        #    self.parent.row_index.render(row)
        # self.parent.column_header.render(col)

    def render_drag_box(self, box):
        '''render rcfectangle box (multi-row & multi-column)'''
        self.delete('drag-box')
        # self.delete('row-highlight')
        # self.parent.row_index.clear_selected()

        xs1, ys1, xs2, ys2 = self.get_cell_coords(box[0], box[1])
        xe1, ye1, xe2, ye2 = self.get_cell_coords(box[2], box[3])

        box_fill_color = self.ps['style']['color']['box-highlight']
        # don't change color (purple)
        # if len(self.copy_buffer):
        #    box_fill_color = self.ps['style']['color']['box-highlight-buffer']

        if self.ps['box_display_type'] == 'lower':
            self.create_rectangle(
                xs1,
                ys1,
                xe2+self.x_start,
                ye2,
                fill=box_fill_color,
                outline=self.ps['style']['color']['outline-dark'],
                width=2,
                tags=('box', 'drag-box',))
            self.tag_lower('drag-box')
        elif self.ps['box_display_type'] == 'raise':
            self.create_rectangle(
                xs1,
                ys1,
                xe2+self.x_start,
                ye2,
                fill=box_fill_color,
                stipple="gray50",
                outline=self.ps['style']['color']['outline-dark'],
                width=2,
                tags=('box', 'drag-box'))
            self.tag_raise('drag-box')

    def render_fill_box(self, box):
        '''render rectangle box drag (multi-row & multi-column)'''
        self.delete('fill-box')

        # xs1, ys1, xs2, ys2 = self.get_cell_coords(selected['box_top_left'][0], selected['box_top_left'][1])
        # xe1, ye1, xe2, ye2 = self.get_cell_coords(selected['box_bottom_right'][0], selected['box_bottom_right'][1])
        # xs1, ys1, xs2, ys2 = self.get_cell_coords(selected['drag_start'][0], selected['box_top_left'][1])
        # xe1, ye1, xe2, ye2 = self.get_cell_coords(selected['box_bottom_right'][0], selected['box_top_left'][1])

        xs1, ys1, xs2, ys2 = self.get_cell_coords(box[0], box[1])
        xe1, ye1, xe2, ye2 = self.get_cell_coords(box[2], box[3])

        self.create_rectangle(xs1, ys1, xe2+self.x_start, ye2,
                              outline='#009999',
                              width=2,
                              tags=('box', 'fill-box',))
        self.tag_lower('fill-box')

    def render_fill_handle(self, xy, col_key=''):

        # TODO: only certain cols can render_fill? comment this for get lots of bug
        # if len(self.ps['cols_on_fill_handle']) > 0 and col_key not in self.ps['cols_on_fill_handle']:
        #    return

        self.delete('fill-handle')
        # little rect handler on bottom right
        self.create_rectangle(
            xy[2]-4,
            xy[3]-4,
            xy[2]+4,
            xy[3]+4,
            fill=self.ps['style']['color']['outline-dark'],
            outline='white',
            width=1,
            tag=('box, box-highlight', 'fill-handle'),
        )

    def render_copy_box(self, box):
        '''render rectangle box (multi-row & multi-column)'''
        self.delete('copy-box')
        # self.delete('row-highlight')
        self.parent.row_index.clear_selected()

        xs1, ys1, xs2, ys2 = self.get_cell_coords(box[0], box[1])
        xe1, ye1, xe2, ye2 = self.get_cell_coords(box[2], box[3])
        box_fill_color = self.ps['style']['color']['box-highlight']

        pad = 1
        self.create_rectangle(
            xs1-pad,
            ys1-pad,
            xe2+self.x_start+pad,
            ye2+pad,
            outline='#0073E6',
            dash=(3,5),
            width=2,
            tags=('box', 'copy-box')
        )
        self.tag_raise('copy-box')

    def clear(self):
        self.delete('cell')
        self.delete('cell-border')
        self.delete('box')
        self.delete('row-highlight')
        self.delete('entry_win')

    def get_cell_coords(self, row, col):
        # print (row, col, self.ps['column_width_list'], self.selected)
        x1 = self.x_start + self.ps['column_width_list'][col]
        x2 = self.ps['column_width_list'][col+1]
        y1 = self.y_start + (self.ps['cell_height'] * row)
        y2 = y1 + self.ps['cell_height']
        return x1, y1, x2, y2

    def get_rc_key(self, row, col):
        col_key = self.ps['col_keys'][col]

        if self.ps['pagination']['current_page'] > 1:
            row = (self.ps['pagination']['current_page'] - 1) * self.ps['pagination']['num_per_page'] + row

        iid = self.ps['row_keys'][row]

        return (iid, col_key)

    def get_col_index(self, col_key):
        col_keys = list(self.ps['columns'])
        return col_keys.index(col_key)

    def get_row_index(self, row_key):
        row_keys = list(self.ps['data'])
        return row_keys.index(row_key)

    def get_col_offset(self, col_key):
        col_w_list = self.ps['column_width_list']
        col = self.get_col_index(col_key)
        return col_w_list[col] + self.x_start

    @custom_action(name='set_data')
    def set_data_value(self, row_key, col_key, value):
        self.ps['data_all'][row_key][col_key] = value
        logging.debug('MainTable.save_data_value: {}, {}: {}'.format(row_key, col_key, value))
        #self.render()
        #self.update_text(self.current_rc, value)
        self.update_text([row_key, col_key], value)

        #if func := self.ps.get('after_set_data_value', ''):
        #    return func(row_key, col_key, value)
        return row_key, col_key, value

    def get_rc(self, event_x, event_y):
        result = {
            'row': None,
            'col': None,
            'row_key': None,
            'col_key': None,
            'xy': [None, None, None, None],
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
            'is_available': True,
            'cell_xy': self.get_cell_coords(row, col),
            'xy': [x, y],
        })
        return result

    def save_entry_queue(self):
        for i, v in self.entry_queue.items():
            rc_keys = i.replace('cell-text:', '').split(CLONE_ROWS_KEY_DELIMETER)
            #row_key, col_key = self.get_rc_key(int(rc[0]), int(rc[1]))
            row_key = rc_keys[0]
            col_key = rc_keys[1]

            self.set_data_value(row_key, col_key, v)
            self.entry_queue = {}

    def handle_mouse_release_1(self, event):
        logging.debug('mouse release {}, {}'.format(event.x, event.y))
        # print(self.selected)
        if '-handle' in self.selected['action']:
            self.copy_to_clipboard(self.selected['box'])
            self.paste_from_clipboard(self.selected['fill'])
            self.clipboard = {}
            self.render_drag_box(self.selected['fill'])
            #handle_xy = self.get_cell_coords(self.selected['fill'][2], self.selected['fill'][3])
            #self.render_box_handle(handle_xy)

    def remove_widgets(self, widget='all'):
        if widget in ['all', 'entry'] and hasattr(self, 'text_editor'):
            # save data if last entry not Enter or Escape
            if len(self.entry_queue):
                self.save_entry_queue()
            self.text_editor.destroy()
            del self.text_editor

        if widget in ['all', 'listbox'] and hasattr(self, 'listbox'):
            self.listbox.destroy()
            del self.listbox

        if widget in ['all', 'autocomplete'] and hasattr(self, 'autocomplete'):
            self.autocomplete.destroy()
            del self.autocomplete

        self.delete('entry_win')
        self.delete('autocomplete_win')
        self.delete('listbox_win')
        # give keyboard control back to table (override widget's bind)
        self.set_keyboard_control(True)

    def render_popup_menu(self, event):
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

        if self.ps['rows_delete_type'] in ['ALL', 'CLONED', 'ASK-CLONED']:
            self.popup_menu.add_command(label='刪除列', command=self.remove_rows)

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
        if self.ps['custom_menus']:
            self.popup_menu.add_separator()

        self.popup_menu.add_command(label='複製內容', command=self.copy_to_clipboard)
        self.popup_menu.add_command(label='貼上內容', command=self.paste_from_clipboard)
        #self.popup_menu.add_command(label='清除 pattern', command=self.clear_pattern)
        x1, y1, x2, y2 = self.get_cell_coords(row, col)
        self.popup_menu.post(event.x_root, event.y_root)
        #print (y1, y2, int((y1+y2)/2), event.y_root)

    def handle_mouse_button_3(self, event):
        self.render_popup_menu(event)

    @custom_action(name='arrow_key')
    def handle_arrow_key(self, event):
        row, col = self.current_rc
        last_rc = self.current_rc
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
            # text = self.ps['data'][row_key][col_key]
            if col == 0:
                return
            else:
                col -= 1

        elif event.keysym == 'Right':
            if col >= self.ps['num_cols'] - 1:
                return
            else:
                col += 1


        # scroll while key up/down or left/right
        num_rows_display = int(self.ps['height_adjusted'] / self.ps['cell_height'])
        num_rows_display_middle = (num_rows_display / 2)
        # print(row, self.ps['height'], self.ps['height_adjusted'], num_rows_display)
        # print(self.canvasx(0), self.canvasy(0), self.canvasx(self.winfo_width()), self.canvasy(self.winfo_height()))

        # adjust verticle scrollbar
        #if row >= num_rows_display_middle:
        if len(self.ps['data']) >= num_rows_display:  # don't scroll if data less than num_rows_display
            v_args = ('moveto',  (row - num_rows_display_middle) / self.ps['num_rows'])
            self.parent.handle_yviews(*v_args)

        # adjust horizontal scrollbar
        if self.ps['width_adjusted'] < self.width:
            right_width = self.ps['column_width_list'][col+1]+self.ps['row_index_width']
            left_width = self.ps['column_width_list'][col]+self.ps['row_index_width']
            if col == 0 or right_width <= self.ps['width_adjusted']:
                h_args = ('moveto', 0)
            else:
                h_args = ('moveto',  right_width / self.width)
            self.parent.handle_xviews(*h_args)
            # print(left_width, right_width, self.ps['width_adjusted'], self.width)

        self.selected.update({
            'action': 'key-arrow',
            'drag_start': [row, col],
            'drag_end': [None, None],
            'box': [row, col, row, col],
        })
        # if event.keysym in ('Up', 'Down'):
        logging.debug(f'{event.keysym}, last_rc: {last_rc} -> {row}, {col}')
        self.render_cell_outline(row, col)
        x1, y1, x2, y2 = self.get_cell_coords(row, col)
        self.render_fill_handle([x1, y1, x2, y2])

        # elif event.keysym in ('Left', 'Right'):
        # create text_editor
            # row_key, col_key = self.get_rc_key(row, col)
            # if self.ps['columns'][col_key].get('type', 'entry') == 'entry':
                # text = self.ps['data'][row_key][col_key]
                # self.render_text_editor(row, col, text)

        self.current_rc[0] = row
        self.current_rc[1] = col
        # return self.current_rc
        return self.get_rc_key(row, col)

    @custom_action(name='clone_row')
    def clone_rows(self):
        # rows = self.parent.row_index.get_selected_rows()
        rows = self.parent.get_row_list()
        logging.debug(f'clone rows: {rows}')

        if len(rows) == 0:
            return

        all_data = {}
        all_keys = []
        for iid, v in self.ps['data_all'].items():
            all_data[iid] = v
            all_keys.append(iid)

        for row in rows:
            row_key, col_key = self.get_rc_key(row, 0)
            cloned_data = dict(self.ps['data_all'][row_key])
            iid_num = row_key.replace('iid:', '')   # remove "iid:"
            iid_num_main = iid_num.split(CLONE_ROWS_KEY_DELIMETER)[0]
            prefix = f'iid:{iid_num_main}-'
            num_sibling = len(list(filter(lambda x: prefix in x, all_keys)))
            target_iid = f'iid:{iid_num_main}{CLONE_ROWS_KEY_DELIMETER}{num_sibling}'
            all_data[target_iid] = cloned_data
            # res.append((row_key, clone_iid))

        # sorted dict
        new_data = {}
        for iid, v in sorted(all_data.items(), key=lambda x: x[0]):
            new_data[iid] = v
        self.parent.refresh(new_data)

        # self.parent.row_index.clear_selected()
        # if func := self.ps.get('after_clone_row', ''):
        #    return func(row_key, clone_iid)
        # return row_key, clone_iid
        return []

    @custom_action(name='remove_rows')
    def remove_rows(self):
        rows = self.parent.get_row_list()
        logging.debug(f'remove_rows: {rows}')

        # only do first row
        # if len(rows) > 0:
        #     row = rows[0]
        #     row_key, col_key = self.get_rc_key(row, 0)
        #     del self.ps['data'][row_key]
        #     self.parent.refresh(self.ps['data'])
        #     return row
        if self.ps['rows_delete_type'] == 'NO':
            return []

        deleted_row_keys = []
        ignore = self.ps['remove_rows_key_ignore_pattern']
        for row in rows:
            row_key, col_key = self.get_rc_key(row, 0)
            if self.ps['rows_delete_type'] == 'CLONED':
                if ignore == '':
                    if delimeter in row_key:
                        # cloned rows has "{CLONE_ROWS_KEY_DELIMETER}" in row_key
                        deleted_row_keys.append(row_key)
                        del self.ps['data'][row_key]
                else:
                    if ignore not in row_key:
                        deleted_row_keys.append(row_key)
                        del self.ps['data'][row_key]

            elif self.ps['rows_delete_type'] == 'ALL':
                deleted_row_keys.append(row_key)
                del self.ps['data'][row_key]
            elif self.ps['rows_delete_type'] == 'ASK-CLONED':
                # TODO
                pass

        self.parent.refresh(self.ps['data'])
        logging.debug(f"actual remove_rows: {deleted_row_keys} (mode: {self.ps['rows_delete_type']})")
        return deleted_row_keys

    def copy_to_clipboard(self, box=None):
        logging.debug('selected: {}'.format(self.selected))
        clip = {}
        source = box if box is not None else self.selected['box']
        for row in range(source[0], source[2] + 1):
            for col in range(source[1], source[3] + 1):
                row_key, col_key = self.get_rc_key(row, col)
                v = self.ps['data'][row_key][col_key]
                if row_key not in clip:
                    clip[row_key] = {}
                clip[row_key][col_key] = v
        self.clipboard = clip
        logging.debug('clipboard: {}'.format(clip))

    @custom_action(name='paste_from_buffer')
    def paste_from_clipboard(self, box=None):
        logging.debug('clipboard: :'.format(self.clipboard))
        clip = self.clipboard
        clip_keys = list(clip)
        num_clip_row = len(clip)
        num_clip_col = len(clip[clip_keys[0]])
        source = box if box is not None else self.selected['box']
        # excel paste box pattern (ex: choose A, B paste A B C => A B)
        # elif selected['rect_bottom_right'][0] - selected['rect_top_left'][0] < num_clip_row or \
        #     selected['rect_bottom_right'][1] - selected['rect_top_left'][1] < num_clip_col:
        #    # or drag area smaller than cilpboard
        #    rect_start = selected['drag_start']
        #    rect_end =  [
        #        selected['drag_start'][0] + num_clip_row - 1,
        #        selected['drag_start'][1] + num_clip_col - 1
        #    ]

        # prevent no source error, source: [None, None, None]
        if None in source:
            return

        for i, row in enumerate(range(source[0],source[2] + 1)):
            row_key = clip_keys[i % num_clip_row]
            for j, col in enumerate(range(source[1], source[3] + 1)):
                col_keys = list(clip[row_key])
                col_key = col_keys[j % num_clip_col]
                value = clip[row_key][col_key]
                target_row_key, target_col_key = self.get_rc_key(row, col)
                self.set_data_value(target_row_key, target_col_key, value)
        self.delete('copy-box')

        # should return tuple to activate custom_action wrapper
        return (clip, )

    def clear_pattern(self):
        self.pattern_copy = []

    def handle_row_index_selected(self, rows):
        self.render_row_highlight(rows)

    def handle_listbox_click(self, event, row, col):
        if not hasattr(self, 'listbox'):
            return

        cur_sel = self.listbox.curselection()
        logging.debug('curselection: {}'.format(cur_sel[0]))
        if cur_sel:
            text = self.listbox.get(cur_sel)
            row_key, col_key = self.get_rc_key(row, col)
            self.set_data_value(row_key, col_key, text)
        self.remove_widgets('listbox')
        self.set_keyboard_control(True)

    def handle_listbox_arrow_key(self, event, direction):
        # print(event, 'listbox')
        #if not self.listbox: # will cause error (python3.10)
        if not hasattr(self, 'listbox'):
            return

        if sel := self.listbox.curselection():
            select_index = sel[0]
            if direction == 'down':
                self.listbox.yview_scroll(1, 'units')
                select_index += 1
            elif direction == 'up':
                self.listbox.yview_scroll(-1, 'units')
                select_index -= 1

            if select_index >= 0 and select_index < self.listbox.size():
                self.listbox.selection_clear(0, tk.END)
                self.listbox.see(select_index-2)
                self.listbox.activate(select_index)
                self.listbox.select_set(select_index)


    def init_highlight(self):
        self.render_cell_outline(0, 0)
        handle_xy = self.get_cell_coords(0, 0)

        self.render_fill_handle(handle_xy, self.ps['col_keys'][0])

    def init_data(self):
        logging.debug('init_data')
        self.current_rc = [0, 0]
        self.selected = {
            'drag_start': [None, None],
            'drag_end': [None, None],
            'box': [None, None, None, None],
            'fill': [None, None, None, None],
            'ctrl_list': [],
            'action': '', # click, drag, single-handle/box-handle
            'is_ctrl_on': False,
            'is_entry_on': False,
        }
        self.clipboard = {}

        self.init_highlight()

        pagination = self.ps['pagination']
        self.ps['pagination'].update({
            'num_per_page': self.ps['pagination']['num_per_page'],
            'current_page': 1,
            'num_pages': 0,
            'total': 0,
        })

    def clear_selected(self, to_refresh=True):
        self.delete('cell-highlight')
        self.delete('cell-highlight-border')
        self.selected = {}
        if to_refresh is True:
            self.parent.refresh(self.ps['data'])

