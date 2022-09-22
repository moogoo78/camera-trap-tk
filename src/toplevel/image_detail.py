import tkinter as tk
from tkinter import ttk

from PIL import (
    Image,
    ImageTk
)
from image import aspect_ratio


class ImageDetail(tk.Toplevel):
    INIT_WIDTH = 1200
    INIT_HEIGHT = 900

    def __init__(self, parent, image_path):
        super().__init__(parent)
        self.parent = parent

        self.geometry(f'{self.INIT_WIDTH}x{self.INIT_HEIGHT}+100+100')

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
        self.to_width = self.INIT_WIDTH
        self.protocol('WM_DELETE_WINDOW', self.quit)

        self.layout()

    def layout(self):
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        self.canvas = tk.Canvas(
            self,
            width=self.INIT_WIDTH,
            height=self.INIT_HEIGHT,
            bg='#777777',
            bd=0,
            highlightthickness=0,
            relief='ridge',
        )
        self.canvas.grid(sticky='ewns')

        self.canvas.bind('<Enter>', self.enter)
        self.canvas.bind('<Motion>', self.motion)

        #self.bg = ImageTk.PhotoImage(file=self.image_path)
        #self.bg_img_id = self.canvas.create_image(
        #    0,
        #    0,
        #    image=self.bg,
        #    anchor='nw',
        #)

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
        # print ('resize', event.height, event.width, event)
        if event.height < 10 or event.width < 10:
            return

        if self.bg_img_id:
            self.canvas.delete(self.bg_img_id)

        self.to_width = event.width
        self.fit_aspect_ratio(event.width)

    def fit_aspect_ratio(self, to_width):
        tmp = self.orig_img
        to_size = aspect_ratio(tmp.size, width=to_width)
        self.resize_ratio = to_width / float(tmp.size[0])
        self.bg_img = ImageTk.PhotoImage(tmp.resize(to_size))
        self.bg_img_id = self.canvas.create_image(
            0,
            0,
            image=self.bg_img,
            anchor='nw',
        )

    def quit(self):
        self.parent.data_grid.main_table.set_keyboard_control(True)
        self.destroy()

    def change_image(self, image_path):
        self.orig_img = Image.open(image_path)
        self.fit_aspect_ratio(self.to_width)
