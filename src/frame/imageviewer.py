import tkinter as tk
from tkinter import (
    ttk,
)

from PIL import ImageTk, Image


class ImageViewer(tk.Frame):

    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent
        self.app = parent

        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=1)
        self.grid_rowconfigure(2, weight=0)
        self.grid_rowconfigure(3, weight=0)
        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure(2, weight=0)

        self.label = ttk.Label(self, text='', font=('Verdana', 12))
        self.label.grid(row=0, column=0, sticky='news', pady=4, columnspan=3)

        self.image_label = ttk.Label(self, border=1, relief='raised')
        self.image_label.grid(row=1, column=1, sticky='n')

        self.left_button = ttk.Button(
            self,
            text='<',
            command=lambda: self.on_key('left'),
            width=4)
        self.left_button.grid(row=1, column=0, pady=5, sticky='news')
        self.right_button = ttk.Button(
            self,
            text='>',
            command=lambda: self.on_key('right'),
            width=4)
        self.right_button.grid(row=1, column=2, pady=5, sticky='news')

        self.back_button = ttk.Button(
            self,
            text='回上頁',
            command=self.on_back)
        self.back_button.grid(row=0, column=0, padx=4, pady=10, sticky='en', columnspan=3)
        #self.annotation_label = ttk.Label(self, text='')
        #self.annotation_label.grid(row=3, column=1, sticky='ew', padx=10, pady=10)

        self.annotation_frame = tk.Frame(self, bg='#ddeeff')
        self.annotation_frame.grid(row=3, column=0, columnspan=3, sticky='news', padx=10, pady=10)


        self.sp_label = ttk.Label(self.annotation_frame, text='物種')
        self.sp_label.grid(row=0, column=0, padx=4, sticky='news')
        self.sp_val = tk.StringVar(self)
        self.sp_entry = ttk.Entry(
            self.annotation_frame,
            textvariable=self.sp_val,
            width=16,
        )
        self.sp_entry.grid(row=0, column=1, padx=4, sticky='news')

        self.ls_label = ttk.Label(self.annotation_frame, text='年齡')
        self.ls_label.grid(row=0, column=2, padx=4, sticky='news')
        self.ls_val = tk.StringVar(self)
        self.ls_entry = ttk.Entry(
            self.annotation_frame,
            textvariable=self.ls_val,
            width=16,
        )
        self.ls_entry.grid(row=0, column=3, padx=4, sticky='news')

        self.sx_label = ttk.Label(self.annotation_frame, text='性別')
        self.sx_label.grid(row=0, column=4, padx=4, sticky='news')
        self.sx_val = tk.StringVar(self)
        self.sx_entry = ttk.Entry(
            self.annotation_frame,
            textvariable=self.sx_val,
            width=16,
        )
        self.sx_entry.grid(row=0, column=5, padx=4, sticky='news')


    def on_back(self):
        self.parent.main.handle_image_viewer()

    def on_key(self, action):
        if action in ['down', 'right']:
            self.parent.main.current_row += 1
        elif action in ['up', 'left']:
            self.parent.main.current_row -= 1
        self.refresh()

    # def on_back(self):
    #     self.parent.state['current_row'] = 0
    #     self.parent.show_frame('datatable')
    #     # unbind key event
    #     self.parent.parent.unbind('<Left>')
    #     self.parent.parent.unbind('<Up>')
    #     self.parent.parent.unbind('<Right>')
    #     self.parent.parent.unbind('<Down>')


    def refresh(self):
        # bind key event
        self.app.bind('<Down>', lambda _: self.on_key('down'))
        self.app.bind('<Up>', lambda _: self.on_key('up'))
        self.app.bind('<Left>', lambda _: self.on_key('left'))
        self.app.bind('<Right>', lambda _: self.on_key('right'))

        row = self.parent.main.current_row
        item = self.parent.main.data_helper.get_item(row)
        total = len(self.parent.main.data_helper.data)

        if not item:
            return
        self.label['text'] = '{} ({}) --- {}/{}'.format(
            item['path'],
            item['datetime_display'],
            self.parent.main.current_row+1,
            total)
        #print (item['thumb'])

        # annotations
        self.sp_val.set(item['annotation_species'])
        self.ls_val.set(item['annotation_lifestage'])
        self.sx_val.set(item['annotation_sex'])

        # image
        image_path = item['thumb'].replace('-q.jpg', '-l.jpg')
        image = Image.open(image_path)
        # aspect ratio
        basewidth = 860
        wpercent = (basewidth/float(image.size[0]))
        hsize = int((float(image.size[1])*float(wpercent)))
        img = image.resize((basewidth,hsize))
        photo = ImageTk.PhotoImage(img)
        self.image_label.configure(image=photo)
        self.image_label.image = photo
        #self.update_idletasks()
