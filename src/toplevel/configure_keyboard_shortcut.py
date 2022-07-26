import tkinter as tk
from tkinter import ttk

class ConfigureKeyboardShortcut(tk.Toplevel):
    INIT_WIDTH = 560
    INIT_HEIGHT = 430

    def __init__(self, app):
        super().__init__(background='#FFFFFF')
        self.app = app
        self.geometry(f'{self.INIT_WIDTH}x{self.INIT_HEIGHT}')

        self.title(f'Camera Trap Desktop - 設定鍵盤快捷鍵')

        choices = self.app.config.get('AnnotationFieldSpecies', 'choices')
        species_choices = choices.split(',')

        self.data = {}
        for i in range(1, 11):
            # let '0' append to last
            index = i if i < 10 else 0
            v = self.app.config.get('KeyboardShortcut', f'Control-Key-{index}')
            sv = tk.StringVar(self)
            sv.set(v)
            self.data[str(index)] = {
                'default': v,
                'var': sv
            }

        head_label = ttk.Label(
            self,
            background='#FFFFFF',
            foreground=self.app.app_primary_color,
            font=self.app.get_font('display-2'),
            text='快捷鍵組合',
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

        for i, key in enumerate(self.data):
            item_frame = tk.Frame(
                container_frame,
                background='yellow')

            item_row = i if i < 5 else i-5
            item_column = 0 if i < 5 else 1
            item_frame.grid(row=item_row, column=item_column, padx=(0, 40), pady=20, sticky='w')

            label = ttk.Label(
                item_frame,
                background='green',
                font=self.app.get_font('display-3'),
                text=f'Ctrl-{key}',
            )

            menu = tk.OptionMenu(
                item_frame,
                self.data[key]['var'],
                # command=lambda *args, key=key: self.handle_option_change(args, key),
                *species_choices
            )
            label.grid(row=0, column=0, sticky='nw', padx=20)
            menu.grid(row=0, column=1, sticky='ns', padx=10)

        save_button = ttk.Button(
            self,
            text='儲存設定',
            command=self.handle_save,
        )
        save_button.grid(row=2, column=0, sticky='nw', padx=20)

    def handle_option_change(self, *args):
        values = args[0]
        key = args[1]
        # print(key, values)

    def handle_save(self):
        for key, value in self.data.items():
            self.app.config.set('KeyboardShortcut', f'Control-Key-{key}', value['var'].get())
        self.app.config.overwrite()
        tk.messagebox.showinfo('info', '已儲存快捷鍵設定')

        # re bind new shorcut value
        self.app.contents['main'].rebind_keyboard_shortcut()
        self.destroy()
