import logging
import math
#import copy

import tkinter as tk
from tkinter import ttk
from .main_table import MainTable

from .other_classes import (
    ColumnHeader,
    RowIndex,
    AutoScrollbar,
    Footer,
)

class DataGrid(tk.Frame):
    def __init__(self,
                 parent,
                 data,
                 columns,
                 width=None,
                 height=None,
                 row_index_display='',
                 num_per_page=1000,
                 custom_menus=[],
                 custom_binding=None,
    ):
        """include MainTable, ColumnHeader, RowIndex"""
        super().__init__(parent, width=width, height=height)
        logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.DEBUG)

        num_per_page = min(int(num_per_page), 2000) # 2000 is max limit
        self.state = {
            'data': data,
            'data_keys': {},
            'columns': columns,
            'width': width,
            'height': height,
            'pagination': {
                'num_per_page': num_per_page,
                'current_page': 1,
                'num_pages': 0,
                'total': 0,
            },
            'cell_height': 20,
            'cell_width': 100,
            'style': {
                'color': {
                    'bg': '#f7f7fa',
                    'row_index_bg': '#2a3132', #'#2A3132'
                    'column_header_bg': '#336b87', #'#2c3e50', #'#336B87'
                    'cell-border': '#d3d3d3',
                    'row-highlight': 'brown',
                    'box-highlight': '#e8edf7',
                    'outline-dark': '#4772c4',
                    'row-index-highlight': '#b90504',
                }
            },
            'image_tmp': {}, # for canvas image, will deleted by garbage collect
            'column_header_height': 20,
            'column_width_list': [], # count by update_columns()
            'num_rows': 0, # count by refresh()
            'num_cols': 0, # count by update_columns()
            'is_row_index_selected': False,
            'after_row_index_selected': None,
            'custom_actions': {
                'mouse_click_left': None,
                'arrow_key': None,
                'set_data_value': None,
                'clone_row': None,
                'remove_row': None,
                'to_page': None,
                'paste_from_buffer': None,
            },
            'custom_menus': custom_menus,
            'custom_binding': custom_binding,
            'row_index_display': row_index_display,
            'box_display_type': 'lower',
        }
        #self.current_rc = [0, 0]

        # other not default
        # cell_image_x_pad
        # cell_image_y_pad
        self.update_columns(columns)
        #logging.debug(self.state)

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self.main_table = MainTable(self)
        self.column_header = ColumnHeader(self, bg=self.state['style']['color']['column_header_bg'])
        self.footer = Footer(self)

        if self.state['row_index_display']:
            self.row_index = RowIndex(self, bg=self.state['style']['color']['row_index_bg'])

        self.scrollbar_y = AutoScrollbar(self,orient=tk.VERTICAL, command=self.handle_yviews)
        self.scrollbar_y.grid(row=1, column=2, rowspan=1, sticky='news',pady=0, ipady=0)
        self.scrollbar_x = AutoScrollbar(self, orient=tk.HORIZONTAL, command=self.handle_xviews)
        self.scrollbar_x.grid(row=2, column=1, columnspan=1, sticky='news')
        self.main_table.config(
            xscrollcommand=self.scrollbar_x.set,
            yscrollcommand=self.scrollbar_y.set)

        if self.state['row_index_display']:
            self.row_index.config(
                xscrollcommand=self.scrollbar_x.set,
                yscrollcommand=self.scrollbar_y.set
            )

        self.column_header.grid(row=0, column=1, rowspan=1, sticky='news', padx=2, pady=0, ipady=0)
        if self.state['row_index_display']:
            self.row_index.grid(row=1, column=0, rowspan=1, sticky='news', pady=2)
        self.main_table.grid(row=1, column=1, sticky='news', rowspan=1, pady=0)

        self.footer.grid(row=3, column=1, sticky='news')

        if len(self.state['data']):
            self.refresh(data)

    def to_page(self, page):
        self.refresh(page=page)
        self.footer.render()

        # TODO, failed
        #self.main_table.yview_moveto(0.0)
        #self.main_table.yview('moveto', 0.0)

        # after refresh
        if func := self.state['custom_actions']['to_page']:
            func()

    def refresh(self, new_data={}, keep_row_highlight=False, page=None):
        """now, only consider MainTable"""
        self.clear()
        #print(page, 'refresh')

        # use iid:{original_key} as data dict key
        # add iid:{key} if has no "iid:" prefix
        #count = 0
        new_data_iid = {}
        data_visible = {}

        rows = new_data if len(new_data) > 0 and page == None else self.state['data_all']
        total = len(rows)
        num = self.state['pagination']['num_per_page']
        num_pages = math.ceil(total / num)
        cur_page = self.state['pagination']['current_page'] if not page else page
        start = (cur_page - 1) * num
        end = cur_page * num

        for count, (k, v) in enumerate(rows.items()):
            key = str(k)
            iid = k if 'iid:' in key else f'iid:{key}'

            if count >= start and count < end:
                data_visible[iid] = v

            new_data_iid[iid] = v

        row_keys = list(new_data_iid.keys())

        self.state.update({
            'data': data_visible, # only visible in certain page
            'data_all': new_data_iid,
            'num_rows': len(data_visible),
            'row_keys': row_keys,
            'height': len(data_visible) * self.state['cell_height'],
            'pagination': {
                'current_page': cur_page,
                'num_pages': num_pages,
                'total': total,
                'num_per_page': self.state['pagination']['num_per_page'],
            },
        })

        #self.main_table.render_selected(0, 0)
        self.main_table.render()
        if self.state['row_index_display']:
            self.row_index.render()
        self.column_header.render()
        self.footer.render()

    def clear(self):
        self.main_table.clear()
        self.row_index.clear_selected()

    def update_columns(self, columns):
        # count coulmn_width_list and set new width
        last_x = 0
        self.state['column_width_list'] = [0]
        if len(columns) == 0:
            # not test yat, must failed
            for x in data[0].keys():
                columns.append({
                    'key': x,
                    'label': x,
                    'width': self.state['cell_width']
                })
                last_x += self.state['cell_width']
                self.state['column_width_list'].append(last_x)
        else:
            for k, v in columns.items():
                if 'width' not in v:
                    v['width'] = self.state['cell_width']
                last_x += v['width']
                self.state['column_width_list'].append(last_x)

        logging.info('set width: {} -> {}'.format(self.state['width'], last_x))

        col_keys = list(columns.keys())
        self.state.update({
            'columns': columns,
            'width': last_x,
            'num_cols': len(columns),
            'col_keys': col_keys
        })

    def handle_yviews(self, *args):
        #print ('yviews', *args, args)
        self.main_table.yview(*args)
        #print(*args)
        if self.state['row_index_display']:
            self.row_index.yview(*args)
        #print (self.main_table.canvasy(0))
        #print (self.row_index.canvasy(0))

    def handle_xviews(self, *args):
        self.main_table.xview(*args)
        if self.state['row_index_display']:
            self.row_index.xview(*args)

    def get_row_list(self):
        row_list = []
        if mt := self.main_table.selected:
            row_list = mt.get('row_list', [])
        else:
            row_list = self.row_index.get_selected_rows()
        #elif ri := self.row_index.selected:
        #    row_list = ri.get('row_list', [])

        return row_list

    def update_state(self, key, value):
        if key in self.state and self.state[key] != value:
            logging.debug(f'update state: {key}: {value}')
            self.state[key] = value
            return True

        return False
