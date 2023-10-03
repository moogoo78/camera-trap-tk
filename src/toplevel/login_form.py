import tkinter as tk
from tkinter import (
    ttk,
)
from tkinter import filedialog


class LoginForm(tk.Toplevel):

    def __init__(self, parent, *args, **kwargs):
        #tk.Frame.__init__(self, parent, *args, **kwargs)
        super().__init__(parent, bg='#eeeeee')
        self.app = parent

        self.protocol('WM_DELETE_WINDOW', self.quit)
        self.geometry('300x160')
        self.title('登入')
        #self.wm_attributes('-topmost', True)
        #self.lift()
        #self.focus_set()
        #self.grab_set()

        self.layout()


    def layout(self):
        s = ttk.Style()
        #s.configure('ctl.TFrame', background='maroon')
        #s.configure('res.TFrame', background='green')

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # container
        container = ttk.Frame(self, padding=10)
        container.grid(row=0, column=0, sticky='nwes')
        container.grid_rowconfigure(0, weight=0)
        #container.grid_rowconfigure(1, weight=0)
        #container.grid_rowconfigure(2, weight=0)
        container.grid_columnconfigure(0, weight=0)
        #container.grid_columnconfigure(1, weight=1)

        # create widgets
        # username_label = ttk.Label(
        #     container,
        #     text='使用者名稱',
        #     font=self.app.get_font('display-4'),
        # )
        # self.username_entry = ttk.Entry(
        #     container,
        # )
        # password_label = ttk.Label(
        #     container,
        #     text='密碼',
        #     font=self.app.get_font('display-4'),
        # )
        # self.password_entry = ttk.Entry(
        #     container,
        # )
        # submit_button = ttk.Button(
        #     container,
        #     text='送出',
        #     command=self.on_submit
        # )
        submit_button = ttk.Button(
            container,
            text='ORCID登入',
            command=self.on_submit
        )

        # place widgets, padx=4, pady=43
        #login_label.grid(row=0, column=0, columnspan=2)
        # username_label.grid(row=0, column=0, sticky='e', padx=4, pady=(8, 4))
        # self.username_entry.grid(row=0, column=1, sticky='we', padx=4)
        # password_label.grid(row=1, column=0, sticky='e', padx=4, pady=4)
        # self.password_entry.grid(row=1, column=1, sticky='we', padx=4)
        # submit_button.grid(row=2, column=0, columnspan=2, sticky='e', padx=4, pady=12)
        submit_button.grid(row=0, column=0, padx=4, pady=12)


    def on_submit(self):
        # print(self.username_entry.get(), self.password_entry.get(), 'xxxx')
        pass

    def quit(self):
        self.destroy()
        #self.app.import_data = None
