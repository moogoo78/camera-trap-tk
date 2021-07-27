import tkinter as tk

class ColumnHeader(tk.Canvas):

    def __init__(self, parent):
        super().__init__(parent, bg='#336B87', width=500, height=20, bd=0)
        self.ps = parent.state
        self.config(width=self.ps['width'])

    #def render(self):
        #self.configure(scrollregion=(0,0, self.table.tablewidth+self.table.x_start, self.height))
        #self.delete('gridline','text')
        #self.delete('rect')
        pad = 0
        for i, v in enumerate(self.ps['columns']):

            x = self.ps['column_width_list'][i] + self.ps['columns'][i]['width'] / 2

            self.create_text(
                x + pad, self.ps['cell_height']/2,
                text=v['label'],
                anchor='w',
                fill='white',
                #font=self.thefont,
                #tag='text')
            )

        #x=self.table.col_positions[col+1]
        #self.create_line(x,0, x,h, tag='gridline',
        #                fill='white', width=2)
        return

class RowIndex(tk.Canvas):

    def __init__(self, parent, width=None):
        if not width:
            self.width = 40
        else:
            self.width = width
        super().__init__(parent, bg='#2A3132', width=self.width, bd=0, relief='flat')

        self.ps = parent.state

        # render
        for i, v in enumerate(self.ps['data'].items()):
            x = self.width - 10
            y1 = i * self.ps['cell_height']
            y2 = (i+1) * self.ps['cell_height']
            self.create_rectangle(0, y1, self.width-1, y2,
                              outline='white',
                              width=1,
                              tag='rowheader')

            self.create_text(x, i*self.ps['cell_height'] + self.ps['cell_height']/2,
                             text=i+1,
                             fill='white',
                             #font=self.table.thefont,
                             tag='text', anchor='e')

class AutoScrollbar(tk.Scrollbar):
    """a scrollbar that hides itself if it's not needed.  only
       works if you use the grid geometry manager."""

    def set(self, lo, hi):
        if float(lo) <= 0.0 and float(hi) >= 1.0:
            # grid_remove is currently missing from Tkinter!
            self.tk.call("grid", "remove", self)
        else:
            self.grid()
        tk.Scrollbar.set(self, lo, hi)
    #def pack(self, **kw):
    #    raise TclError, "cannot use pack with this widget"
    #def place(self, **kw):
    #    raise TclError, "cannot use place with this widget"
