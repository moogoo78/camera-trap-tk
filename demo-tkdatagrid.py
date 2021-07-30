import tkinter as tk
#import pathlib
import sys
#cwd = pathlib.Path.cwd()
#sys.path.insert(0, cwd)
sys.path.insert(0, '')
from tkdatagrid import DataGrid


HEADER = {
    'a': {
        'label': 'A',
        'width': 30,
        'type': 'text'
    },
    'b': {
        'label': 'B',
        'width': 150,
        'type': 'text',
    },
    'c': {
        'label': 'C',
    },
    'd': {
        'label': 'D',
    },
    'e': {
        'label': 'E',
    }
}


from src.tkintertable.Testing import sampledata
DATA=sampledata()
#DATA = {f'iid:{k}': v for k, v in DATA.items()}
DATA3 = {
    0: {
        'a': 'a',
        'b': 'b',
    },
    1: {
        'a': 'a1',
        'b': 'b1',
    }
}
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

        self.data_grid = DataGrid(self.frame, data=DATA, columns=HEADER, width=100, height=600)

        # redraw another
        #data2=sampledata()
        #self.data_grid.refresh(data2)

        # change style
        #self.data_grid.state['styles']['color']['grid-border'] = 'green'
        # redraw again
        #self.data_grid.update_columns(HEADER2)
        #self.data_grid.refresh(DATA3)

        # remove row
        #self.data_grid.main_table.remove_row(3)

        self.frame.grid(row = 0, column = 0, sticky = "nswe")
        self.data_grid.grid(row = 0, column = 0, sticky = "nswe")
2
app=DemoApp()
app.mainloop()
