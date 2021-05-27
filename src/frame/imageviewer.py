import tkinter as tk
from tkinter import (
    ttk,
)

from PIL import ImageTk, Image


class ImageViewer(tk.Frame):

    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent

        self.label = ttk.Label(self, text='')
        self.label.grid(row=0, column=0, sticky='ew', padx=10, pady=10)

        self.image_label = ttk.Label(self, border=8, relief='raised')
        self.image_label.grid(row=1, column=1, sticky='nswe')

        self.left_button = ttk.Button(
            self,
            text='<',
            command=lambda: self.on_key('left'))
        self.left_button.grid(row=1, column=0, pady=5, sticky='w')
        self.right_button = ttk.Button(
            self,
            text='>',
            command=lambda: self.on_key('right'))
        self.right_button.grid(row=1, column=2, pady=5, sticky='e')

        self.back_button = ttk.Button(
            self,
            text='回上頁',
            command=self.on_back)
        self.back_button.grid(row=2, column=0, pady=20, sticky='n')


    def on_key(self, action):
        row = self.parent.state.get('current_row', '')
        print ('key', action, row)
        if row == '':
            return False

        if action in ['down', 'right']:
            row += 1
        elif action in ['up', 'left']:
            row -= 1

        if row < len(self.parent.state['alist']) and \
           row >= 0:
            #print ('goto', row)
            self.parent.state['current_row'] = row
            self.refresh()
        else:
            #print ('limit', row)
            pass

    def on_back(self):
        self.parent.state['current_row'] = 0
        self.parent.show_frame('datatable')
        # unbind key event
        self.parent.parent.unbind('<Left>')
        self.parent.parent.unbind('<Up>')
        self.parent.parent.unbind('<Right>')
        self.parent.parent.unbind('<Down>')


    def refresh(self):
        # bind key event
        self.parent.parent.bind('<Down>', lambda _: self.on_key('down'))
        self.parent.parent.bind('<Up>', lambda _: self.on_key('up'))
        self.parent.parent.bind('<Left>', lambda _: self.on_key('left'))
        self.parent.parent.bind('<Right>', lambda _: self.on_key('right'))

        state = self.parent.state
        #print ('refresh', state)
        total = len(state['alist'])
        row = state['current_row']
        self.label['text'] = f'{row+1}/{total}'

        image_path = state['alist'][state['current_row']][9]['path']
        image = Image.open(image_path)
        # aspect ratio
        basewidth = 800
        wpercent = (basewidth/float(image.size[0]))
        hsize = int((float(image.size[1])*float(wpercent)))
        img = image.resize((basewidth,hsize))
        #img = image.resize((300,300), Image.ANTIALIAS)
        photo = ImageTk.PhotoImage(img)
        self.image_label.configure(image=photo)
        self.image_label.image = photo
        self.update_idletasks()
