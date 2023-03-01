import tkinter as tk
from tkinter import (
    ttk,
)
from PIL import (
    Image,
    ImageTk
)

from image import aspect_ratio

class HelpPage(tk.Toplevel):

    def __init__(self, parent, *args, **kwargs):
        #tk.Frame.__init__(self, parent, *args, **kwargs)
        super().__init__(parent, bg='#eeeeee')
        self.app = parent

        self.protocol('WM_DELETE_WINDOW', self.quit)
        self.geometry(f'{self.app.app_width}x{self.app.app_height-50-25}')
        self.title('說明')
        self.layout()

    def handle_mouse_wheel(self, event):
        # print(event) # TODO
        if event.num == 5 or event.delta == -120:
            self.canvas.yview_scroll(1, 'units')
        elif event.num == 4 or event.delta == 120:
            if self.canvas.canvasy(0) < 0:  # ?
                return
            self.canvas.yview_scroll(-1, 'units')

    def handle_yviews(self, *args):
        self.canvas.yview(*args)

    def layout(self):
        self.grid_rowconfigure(0, weight=0)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=0)

        self.scrollbar_y = ttk.Scrollbar(
            self,orient=tk.VERTICAL,
            command=self.handle_yviews)
        self.scrollbar_y.grid(row=0, column=1, sticky='news',pady=0, ipady=0)


        img = Image.open('./assets/help-content.png')
        to_size = aspect_ratio(img.size, width=self.app.app_width)
        self.photo = ImageTk.PhotoImage(img.resize(to_size))

        self.img_qrcode_app = Image.open('./assets/qrcode-app.png')
        self.img_qrcode_web = Image.open('./assets/qrcode-web.png')
        self.photo = ImageTk.PhotoImage(img.resize(to_size))
        self.photo_qrcode_app = ImageTk.PhotoImage(self.img_qrcode_app)
        self.photo_qrcode_web = ImageTk.PhotoImage(self.img_qrcode_web)
        self.canvas = tk.Canvas(
            self,
            width=self.app.app_width,
            height=self.app.app_height-50-25,
            bg='#CFCFCF',
            bd=0,
            highlightthickness=0,
            relief='ridge',
            scrollregion=(0, 0, to_size[0], to_size[1]),
            yscrollcommand=self.scrollbar_y.set,
        )
        self.canvas.grid(row=0, column=0, sticky='ewns')

        self.canvas.bind('<MouseWheel>', self.handle_mouse_wheel)

        # self.canvas.create_text(
        #     250,
        #     80,
        #     text='~ 教學內容 ~',
        #     font=('Arial', 40),
        #     fill=self.app.app_primary_color,
        # )

        self.canvas.create_image(
            0,
            0,
            image=self.photo,
            anchor='nw',
        )

        self.canvas.create_image(
            184,
            120,
            image=self.photo_qrcode_app,
            anchor='nw',
        )
        self.canvas.create_image(
            760,
            120,
            image=self.photo_qrcode_web,
            anchor='nw',
        )

    def quit(self):
        self.destroy()
        self.app.is_help_open = False
