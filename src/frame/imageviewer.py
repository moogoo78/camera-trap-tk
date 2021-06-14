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

        # self.back_button = ttk.Button(
        #     self,
        #     text='回上頁',
        #     command=self.on_back)
        # self.back_button.grid(row=2, column=0, pady=20, sticky='n')
        self.annotation_label = ttk.Label(self, text='')
        self.annotation_label.grid(row=3, column=1, sticky='ew', padx=10, pady=10)

    def on_key(self, action):
        if action in ['down', 'right']:
            self.parent.main.move_selection('next')
        elif action in ['up', 'left']:
            self.parent.main.move_selection('prev')
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
        self.parent.bind('<Down>', lambda _: self.on_key('down'))
        self.parent.bind('<Up>', lambda _: self.on_key('up'))
        self.parent.bind('<Left>', lambda _: self.on_key('left'))
        self.parent.bind('<Right>', lambda _: self.on_key('right'))

        main = self.parent.main
        iid = None
        text = None
        for selected_item in main.tree.selection():
            iid = selected_item
            text = main.tree.item(iid, 'text')
            break

        if not iid:
            return False

        row = main.tree_helper.get_data(iid)
        data = main.tree_helper.data

        if not len(data):
            return False

        total = len(data)
        #row = 0
        self.label['text'] = f'{text}/{total}'
        a_conf = main.tree_helper.get_conf(cat='annotation')
        atext_list = []
        for a in a_conf:
            if x := row.get(a[1][0], ''):
                atext_list.append(f'{a[1][1]}: {x}')
        self.annotation_label['text'] = f'Annotation: {", ".join(atext_list)}'

        image_path = row['path']
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
