import logging
#import copy

import tkinter as tk
from tkinter import ttk
from .main_table import MainTable

from .other_classes import (
    ColumnHeader,
    RowIndex,
    AutoScrollbar,
)

class DataGrid(tk.Frame):
    def __init__(self,
                 parent,
                 data,
                 columns,
                 width=None,
                 height=None,
                 row_index_display='',
                 custom_menus=[],
                 custom_binding=None,
    ):
        """include MainTable, ColumnHeader, RowIndex"""
        super().__init__(parent, width=width, height=height)
        logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.DEBUG)

        self.state = {
            'data': data,
            'data_keys': {},
            'columns': columns,
            'width': width,
            'height': height,
            'cell_height': 20,
            'cell_width': 100,
            'style': {
                'color': {
                    'bg': '#f7f7fa',
                    'row_index_bg': '#2a3132', #'#2A3132'
                    'column_header_bg': '#336b87', #'#2c3e50', #'#336B87'
                    'cell-border': '#d3d3d3',
                    'cell-highlight-border': '#6699ff',
                    'row-highlight': '#ddeeff',
                    'box-highlight': '#fff2cc',
                    'box-highlight-buffer': '#776485',
                    'box-border': '#ffcc33',
                    'row-index-highlight': '#b90504',
                }
            },
            'image_tmp': {}, # for canvas image, will deleted by garbage collect
            'column_header_height': 20,
            'column_width_list': [], # count by update_columns()
            'num_rows': 0, # count by refresh()
            'num_cols': 0, # count by update_columns()
            'after_row_index_selected': None,
            'custom_actions': {
                'mouse_click_left': None,
                'arrow_key': None,
                'set_data_value': None,
                'clone_row': None,
                'remove_row': None,
            },
            'custom_menus': custom_menus,
            'custom_binding': custom_binding,
            'row_index_display': row_index_display,
        }
        # other not default
        # cell_image_x_pad
        # cell_image_y_pad
        self.update_columns(columns)
        #logging.debug(self.state)

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self.main_table = MainTable(self)
        self.column_header = ColumnHeader(self, bg=self.state['style']['color']['column_header_bg'])

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

        if len(self.state['data']):
            self.refresh(data)

    def refresh(self, new_data={}):
        """now, only consider MainTable"""
        self.clear()

        # use iid:{original_key} as data dict key
        # add iid:{key} if has no "iid:" prefix
        new_data_iid = {}
        for k, v in new_data.items():
            key = str(k)
            iid = k if 'iid:' in key else f'iid:{key}'
            new_data_iid[iid] = v

        row_keys = list(new_data_iid.keys())
        self.state.update({
            'data': new_data_iid,
            'num_rows': len(new_data_iid),
            'row_keys': row_keys,
            'height': len(new_data_iid) * self.state['cell_height']
        })

        self.main_table.render()
        if self.state['row_index_display']:
            self.row_index.render()
        self.column_header.render()


    def clear(self):
        self.main_table.clear()

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
        if self.state['row_index_display']:
            self.row_index.yview(*args)
        #print (self.main_table.canvasy(0))
        #print (self.row_index.canvasy(0))

    def handle_xviews(self, *args):
        self.main_table.xview(*args)
        if self.state['row_index_display']:
            self.row_index.xview(*args)
