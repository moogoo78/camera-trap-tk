import tkinter as tk
from tkinter import ttk

from PIL import (
    Image,
    ImageTk
)

class ImageDetail(tk.Toplevel):
    def __init__(self, parent, image_path):
        super().__init__(parent)

        self.geometry('900x600')

        self.title(f'Image Detail Window - {image_path}')
        self.bind('<Configure>', self.resize)
        self.bind('<MouseWheel>', self.set_zoom)
        self.image_path = image_path
        self.zoom_img_id = None
        self.bg_img_id = None
        self.orig_img = Image.open(image_path)
        self.zoom_step = 1
        self.delta_value = 0
        self.resize_ratio = 1

        self.layout()

    def layout(self):
        self.canvas = tk.Canvas(
            self,
            width=1200,
            height=760,
            bg='#777777',
            bd=0,
            highlightthickness=0,
            relief='ridge',
        )
        self.canvas.grid(row=0, column=0, sticky='ewns')

        self.canvas.bind('<Enter>', self.enter)
        self.canvas.bind('<Motion>', self.motion)

        self.bg = ImageTk.PhotoImage(file=self.image_path)
        self.bg_img_id = self.canvas.create_image(
            0,
            0,
            image=self.bg,
            anchor='nw',
        )


    # via: https://stackoverflow.com/questions/5436810/adding-zooming-in-and-out-with-a-tkinter-canvas-widget
    def set_zoom(self, event):
        if event.delta > 0:
            self.zoom_step += 1
        elif event.delta < 0:
            self.zoom_step -= 1
        # keep value between 1 and 5
        self.zoom_step = min(max(1, self.zoom_step), 10)
        # print('=>', self.zoom_step)
        self.motion(event)

    def enter(self, event):
        # print(event)
        pass

    def motion(self, event):

        if self.zoom_img_id:
            self.canvas.delete(self.zoom_img_id)

        x = event.x / self.resize_ratio
        y = event.y / self.resize_ratio
        c = int(150 / self.zoom_step)
        tmp = self.orig_img.crop((x-c,y-c,x+c,y+c))
        self.zoom_img = ImageTk.PhotoImage(tmp.resize((300, 300)))
        self.zoom_img_id = self.canvas.create_image(
            event.x,
            event.y,
            image=self.zoom_img)

    def resize(self, event):
        #print (event.height, event.width)
        if event.height < 10 or event.width < 10:
            return

        if self.bg_img_id:
            self.canvas.delete(self.bg_img_id)

        # aspect ratio
        tmp = self.orig_img
        basewidth = event.width
        print (basewidth, tmp.size)
        self.resize_ratio = (basewidth/float(tmp.size[0]))
        hsize = int((float(tmp.size[1])*float(self.resize_ratio)))
        self.bg_img = ImageTk.PhotoImage(tmp.resize((basewidth,hsize)))
        self.bg_img_id = self.canvas.create_image(
            0,
            0,
            image=self.bg_img,
            anchor='nw',
        )
