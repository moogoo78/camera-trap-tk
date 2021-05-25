import json
from datetime import datetime
from pathlib import Path

import tkinter as tk
from tkinter import (
    Label,
    ttk,
    PhotoImage,
)

from tksheet import Sheet
from PIL import ImageTk, Image

from . import SourceListPage

HEADER2_FONT =("Verdana", 24)
class ImageListPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller

        button = ttk.Button(
            self,
            text ='回目錄頁',
            command = lambda : controller.show_frame('SourceListPage'))

        button.grid(row = 0, column = 0, padx = 10, pady = 10)

    def refresh(self):
        if state := self.controller.state:
            source_name = state['source'][3]
            label = ttk.Label(self, text=source_name, font=HEADER2_FONT)

            label.grid(row = 1, column = 0, padx = 10, pady = 10)
            idx = 0
            #print (self.foo, 'foo')
            #for i in self.foo:
            #    i.grid_forget()
            data = []
            for i in state['image_list']:
                filename = i[2]
                dtime = str(datetime.fromtimestamp(i[3]))
                alist = json.loads(i[7])
                if len(alist) >= 1:
                    for j in alist:
                        print (j)
                        species = j.get('species', '')
                        lifestage = j.get('lifestage', '')
                        data.append([
                            filename,
                            dtime,
                            species,
                            lifestage])
                else:
                    data.append([
                        filename,
                        dtime,
                        '',
                        ''])
            #    label.grid(row=3+idx, column=0)
            #    self.foo.append(label)

            #print (self.grid_slaves())
            ## render sheet
            self.grid_columnconfigure(0, weight = 1)
            self.grid_rowconfigure(0, weight = 1)
            self.frame = tk.Frame(self)
            self.frame.grid_columnconfigure(0, weight = 1)
            self.frame.grid_rowconfigure(0, weight = 1)
            self.sheet = Sheet(
                self.frame,
                data=data,
                headers=['filename', 'time', '物種', '年齡'])
            self.sheet.enable_bindings()
            self.frame.grid(row = 2, column = 0, sticky = "nswe")
            self.sheet.grid(row = 2, column = 0, sticky = "nswe")
            self.sheet.enable_bindings(('row_select', 'cell_select'))
            self.sheet.extra_bindings([
                ('row_select', self.row_select),
                ('cell_select', self.cell_select)
            ])
            for i in range(0, len(data)):
                self.sheet.create_dropdown(i, 2, values='測試,空拍,山羌,山羊,水鹿'.split(','), set_value='', destroy_on_select = False, destroy_on_leave = False, see = False)
                self.sheet.create_dropdown(i, 3, values='成體,亞成體,幼體,無法判定'.split(','), set_value='', destroy_on_select = False, destroy_on_leave = False, see = False)
                #self.sheet.create_dropdown(i, 3, values='雄性,雌性,無法判定'.split(','), set_value='', destroy_on_select = False, destroy_on_leave = False, see = False)
                #初茸,茸角一尖,茸角一岔二尖,茸角二岔三尖,茸角三岔四尖,硬角一尖,硬角一岔二尖,硬角二岔三尖,硬角三岔四尖,解角

            # thumb
            self.image_thumb = ttk.Label(self, border = 25)
            self.image_thumb.grid(row=2, column=1)
            self.image_thumb_button = ttk.Button(self, text='看大圖',
                                                 command=lambda: self.controller.show_frame('ImageViewer'))
            self.image_thumb_button.grid(row=2, column=2)
        else:
            print ('no state')

    #def column_select(self, response):
    #    print (response)
    def cell_select(self, response):
        #print (response)
        state = self.controller.state
        pp = state['image_list'][response[1]][1]

        image = Image.open(pp)
        image = image.resize((300,300), Image.ANTIALIAS)
        photo = ImageTk.PhotoImage(image)

        self.image_thumb.configure(image=photo, width=300 )
        self.image_thumb.image = photo
        #self.image_thumb.grid(row=2, column=1)

    def row_select(self, response):
        #print (response)

        state = self.controller.state
        pp = state['image_list'][response[1]][1]

        image = Image.open(pp)
        image = image.resize((300,300), Image.ANTIALIAS)
        photo = ImageTk.PhotoImage(image)

        self.image_thumb.configure(image=photo, width=300 )
        self.image_thumb.image = photo
        self.image_thumb.grid(row=2, column=1)
