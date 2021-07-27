import tkinter as tk
from tkdatagrid import DataGrid

HEADER = [
    {
        'key': 'a',
        'label': 'A',
        'width': 30,
        'readonly': 1,
    }, {
        'key': 'b',
        'label': 'B',
        'width': 150,
        'readonly': 1,
    }, {
        'key': 'c',
        'label': 'C',
    }, {
        'key': 'd',
        'label': 'D',
    }, {
        'key': 'e',
        'label': 'E',
    }
]

from tkintertable.Testing import sampledata
DATA=sampledata()

class DemoApp(tk.Tk):
    """Basic test frame for the table"""

    def __init__(self):
        super().__init__()
        #tk.Tk.__init__(self)
        self.geometry('800x500+200+100')
        self.title('Test')

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.frame = tk.Frame(self)
        self.data_grid = DataGrid(self.frame, data=DATA, columns=HEADER, width=100, height=100)
        #datagrid.render()
        self.frame.grid(row = 0, column = 0, sticky = "nswe")
        self.data_grid.grid(row = 0, column = 0, sticky = "nswe")

app=DemoApp()
app.mainloop()
