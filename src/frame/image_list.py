import json
from datetime import datetime

import tkinter as tk
from tkinter import (
    ttk,
)

from PIL import ImageTk, Image
from tksheet import Sheet


class ImageList(tk.Frame):

    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent

        self.app = self.parent.parent

        self.ctrl_data = []

        # sheet
        self.sheet = Sheet(
            self,
            data=[],
            headers=['status', 'filename', 'time', '物種', '年齡'])
        self.sheet.enable_bindings()
        self.sheet.grid(row = 2, column = 0, sticky = "nswe")
        self.sheet.enable_bindings(('cell_select'))
        self.sheet.extra_bindings([
            #('row_select', self.row_select),
            ('cell_select', self.cell_select)
        ])

        # thumb
        self.image_thumb = ttk.Label(self, border=25)
        self.image_thumb.grid(row=2, column=1)


    def refresh(self):
        source_id = self.parent.state.get('source_id', '')
        ret = self.app.source.get_source(source_id)

        sheet_data = []
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
                    sheet_data.append([
                        status,
                        filename,
                        dtime,
                        species,
                        lifestage])
                    ctrl_data.append([
                        path,
                    ])
            else:
                sheet_data.append([
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
            data=sheet_data,
            redraw=True,
        )
        for i in range(0, len(sheet_data)):
            self.sheet.create_dropdown(i, 3, values='測試,空拍,山羌,山羊,水鹿'.split(','), set_value='', destroy_on_select = False, destroy_on_leave = False, see = False)
            self.sheet.create_dropdown(i, 4, values='成體,亞成體,幼體,無法判定'.split(','), set_value='', destroy_on_select = False, destroy_on_leave = False, see = False)
                #self.sheet.create_dropdown(i, 3, values='雄性,雌性,無法判定'.split(','), set_value='', destroy_on_select = False, destroy_on_leave = False, see = False)
                #初茸,茸角一尖,茸角一岔二尖,茸角二岔三尖,茸角三岔四尖,硬角一尖,硬角一岔二尖,硬角二岔三尖,硬角三岔四尖,解角

        #self.image_thumb_button = ttk.Button(self, text='看大圖',
        #                                     command=lambda: self.controller.show_frame('ImageViewer'))
        #self.image_thumb_button.grid(row=2, column=2)

    def cell_select(self, response):
        image_path = self.ctrl_data[response[1]][0]
        image = Image.open(image_path)
        img = image.resize((300,300), Image.ANTIALIAS)
        photo = ImageTk.PhotoImage(img)
        self.image_thumb.configure(image=photo, width=300 )
        self.image_thumb.image = photo
