import tkinter as tk
from tkinter import ttk

class ConfigureFont(tk.Toplevel):
    INIT_WIDTH = 560
    INIT_HEIGHT = 430

    def __init__(self, app):
        super().__init__(background='#FFFFFF')
        self.app = app
        self.geometry(f'{self.INIT_WIDTH}x{self.INIT_HEIGHT}')

        self.title(f'Camera Trap Desktop - 設定字體大小')

        self.string_var = tk.StringVar(self)
        context_size = ''
        if x := self.app.db.get_state('context_size'):
            context_size = x
        else:
            context_size = 'S'

        self.string_var.set(context_size)

        head_label = ttk.Label(
            self,
            background='#FFFFFF',
            foreground=self.app.app_primary_color,
            font=self.app.get_font('display-2'),
            text='字體',
        )
        head_label.grid(row=0, column=0, sticky='nw', padx=20, pady=(20, 0))

        container_frame = tk.Frame(self, background='#FFFFFF')
        container_frame.grid(row=1, column=0, sticky='nw')
        label_grid = {
            'sticky': 'w',
            'padx': 14,
            'pady': 3,
        }
        #self.frame.grid_rowconfigure(0, weight=0)
        #self.frame.grid_rowconfigure(1, weight=0)

        item_frame = tk.Frame(
            container_frame,
            background='#FFFFFF')  # yellow

        item_frame.grid(row=0, column=0, padx=(0, 40), pady=10, sticky='w')

        label = ttk.Label(
            item_frame,
            background='#FFFFFF',  # green
            font=self.app.get_font('display-3'),
            text=f'編輯區字體大小',
        )

        menu = tk.OptionMenu(
            item_frame,
            self.string_var,
            # command=lambda *args, key=key: self.handle_option_change(args, key),
            *['小', '中', '大']
        )
        label.grid(row=0, column=0, sticky='nw', padx=(20, 10))
        menu.grid(row=0, column=1, sticky='ns', padx=10)

        save_button = ttk.Button(
            self,
            text='儲存設定',
            command=self.handle_save,
        )
        save_button.grid(row=2, column=0, sticky='nw', padx=20, pady=(20, 0))

    def handle_save(self):
        label_map = {
            '小': 'S',
            '中': 'M',
            '大': 'L',
        }
        label = self.string_var.get()
        context_size = label_map[label]
        self.app.db.set_state('context_size', context_size)
        self.app.app_context_size = context_size
        tk.messagebox.showinfo('info', '已儲存')

        self.app.contents['main'].refresh(True)
        self.destroy()

