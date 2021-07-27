import logging

import tkinter as tk
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
                 height=None
    ):

        super().__init__(parent, width=width, height=height)
        logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.DEBUG)

        self.state = {
            'data': data,
            'columns': columns,
            'width': width,
            'height': height,
            'cell_height': 20,
            'cell_width': 100,
            'column_width_list': [0]
        }

        # count coulmn_width_list and set new width
        wx = 0
        if not self.state['columns']:
            self.state['columns'] = []
            for x in self.state['data'][0].keys():
                self.state['columns'].append({
                    'key': x,
                    'label': x,
                    'width': self.state['cell_width']
                })
                wx += self.state['cell_width']
                self.state['column_width_list'].append(wx)
        else:
            for i in self.state['columns']:
                if 'width' not in i:
                    i['width'] = self.state['cell_width']
                wx += i['width']
                self.state['column_width_list'].append(wx)

        logging.info('set width: {} -> {}'.format(width, wx))
        self.state['width'] = wx

        self.render()

    def render(self):
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self.main_table = MainTable(self)
        logging.debug(self.state)
        self.column_header = ColumnHeader(self)
        self.row_index = RowIndex(self)
        #self.scrollbar_y = AutoScrollbar(self,orient=tk.VERTICAL, command=self.yview)
        #self.scrollbar_y.grid(row=1, column=2, rowspan=1, sticky='news',pady=0, ipady=0)
        #self.scrollbar_x = AutoScrollbar(self, orient=tk.HORIZONTAL, command=self.xview)
        #self.scrollbar_x.grid(row=2, column=1, columnspan=1, sticky='news')
        #self['xscrollcommand'] = self.Xscrollbar.set
        #self['yscrollcommand'] = self.Yscrollbar.set

        self.column_header.grid(row=0, column=1, rowspan=1, sticky='news', pady=0, ipady=0)
        self.row_index.grid(row=1, column=0, rowspan=1, sticky='news', pady=0, ipady=0)
        self.main_table.grid(row=1, column=1, sticky='news', rowspan=1, pady=0, ipady=0)
