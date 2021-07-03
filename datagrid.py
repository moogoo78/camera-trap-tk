import tkinter as tk

"""
mist: #90AFC5
stone: #336B87
shadow: #2A3132
automn leaf: #763626
#https://www.canva.com/design/DADfC5CQ0W4/remix?action2=create&mediaId=DADfC5CQ0W4&signupReferrer=blog&utm_source=blog&utm_medium=content&utm_campaign=100-color-combinations&_branch_match_id=812929534608293691
"""
HEADER = {
    'a': {
        'label': 'A',
    },
    'b': {
        'label': 'B',
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

from tkintertable.Testing import sampledata
DATA=sampledata()


class DataGrid(tk.Canvas):
    """A tkinter class """

    def __init__(
            self,
            parent=None,
            model=None,
            data=None,
            read_only=False,
            width=None,
            height=None,
            bgcolor='#F7F7FA',
            fgcolor='black',
            header=None,
            **kwargs):
        # super().__init__(
        #     self,
        #     parent,
        #     bg=bgcolor,
        #     width=width,
        #     height=height,
        #     relief=tk.GROOVE,
        #     scrollregion=(0,0,300,200))
        self.parent = parent
        #tk.Canvas.__init__(self, parent)
        super().__init__(parent, bg='gray75',bd=2, relief='groove')
        self.width = width
        self.height = height

        self.num_cols = len(data[0])
        self.num_rows = len(data)
        self.cell_width = 150
        self.cell_height = 20

        self.header = header
        self.col_pos_list = []
        if not self.header:
            self.header = {
                {
                    'label': x,
                    'width': self.cell_width
                } for x in self.data[0].keys()
            }
        wx = 0
        for i, v in header.items():
            self.col_pos_list.append(wx)
            wx += v.get('width', self.cell_width)

        if self.width < wx:
            # expend width if header has larger width
            self.width = wx

        self.color_grid = 'gray'

        self.data = data

    def render(self):
        self.column_header = ColumnHeader(self.parent, self)
        self.row_index = RowIndex(self.parent, self)
        self.scrollbar_y = AutoScrollbar(self.parent,orient=tk.VERTICAL, command=self.yview)
        self.scrollbar_y.grid(row=1, column=2, rowspan=1, sticky='news',pady=0, ipady=0)
        self.scrollbar_x = AutoScrollbar(self.parent, orient=tk.HORIZONTAL, command=self.xview)
        self.scrollbar_x.grid(row=2, column=1, columnspan=1, sticky='news')

        self.parent.rowconfigure(1,weight=1)
        self.parent.columnconfigure(1,weight=1)


        self.column_header.grid(row=0, column=1, rowspan=1, sticky='news', pady=0, ipady=0)
        self.row_index.grid(row=1, column=0, rowspan=1, sticky='news', pady=0, ipady=0)
        self.grid(row=1, column=1, sticky='news', rowspan=1, pady=0, ipady=0)



        self.render_grid()
        self.column_header.render()
        self.row_index.render()

    def render_grid(self):
        # draw_grid
        self.delete('girdline')

        x_start = 2
        y_start = 2
        #476042

        # grid border
        # vertical line
        for i in range(self.num_cols+1): # fixed size
            if i < len(self.col_pos_list):
                x = self.col_pos_list[i]
            else:
                x = self.col_pos_list[-1] + self.cell_width
            x += x_start
            self.create_line(x, y_start,
                             x, y_start + self.num_rows * self.cell_height,
                             tag='gridborder',
                             fill=self.color_grid, width=1)

        # horizontal line
        for i in range(self.num_rows+1):
            y = i * self.cell_height
            y += y_start
            self.create_line(x_start, y, self.width, y,
                             tag='gridborder',
                             fill=self.color_grid, width=1)

        for row_index, row in enumerate(self.data.items()):
            for col_index, col in enumerate(row[1].items()):
                x = self.col_pos_list[col_index]
                rect = self.create_text(
                    x + x_start + self.cell_width/2,
                    row_index * self.cell_height + y_start + self.cell_height/2,
                    text=col[1])
                    #fill=linkcolor,
                    #font=linkfont,
                    #tag=('text','hlink','celltext'+str(col)+'_'+str(row)))



class ColumnHeader(tk.Canvas):

    def __init__(self, parent, data_grid):
        super().__init__(parent, bg='#336B87', width=500, height=20, bd=0)
        self.data_grid = data_grid
        self.config(width=self.data_grid.width)

    def render(self):
        #self.configure(scrollregion=(0,0, self.table.tablewidth+self.table.x_start, self.height))
        #self.delete('gridline','text')
        #self.delete('rect')
        pad = 4
        for i, v in enumerate(self.data_grid.header.items()):

            x = self.data_grid.col_pos_list[i]
            self.create_text(
                x + pad, self.data_grid.cell_height/2,
                text=v[1]['label'],
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

    def __init__(self, parent, data_grid, width=None):
        if not width:
            self.width = 40
        else:
            self.width = width
        super().__init__(parent, bg='#2A3132', width=self.width, bd=0, relief='flat')

        self.data_grid = data_grid

    def render(self):
        for i, v in enumerate(self.data_grid.data.items()):
            x = self.width - 10
            y1 = i * self.data_grid.cell_height
            y2 = (i+1) * self.data_grid.cell_height
            self.create_rectangle(0, y1, self.width-1, y2,
                              outline='white',
                              width=1,
                              tag='rowheader')

            self.create_text(x, i*self.data_grid.cell_height + self.data_grid.cell_height/2,
                             text=i+1,
                             fill='white',
                             #font=self.table.thefont,
                             tag='text', anchor='e')


class TestApp(tk.Tk):
    """Basic test frame for the table"""

    def __init__(self):
        super().__init__()
        #tk.Tk.__init__(self)
        self.geometry('800x500+200+100')
        self.title('Test')
        f = tk.Frame(self)
        f.pack(fill=tk.BOTH,expand=1)
        datagrid = DataGrid(f, data=DATA, width=500, header=HEADER, bd=0)
        #datagrid.grid()
        datagrid.render()
        return


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


app=TestApp()
app.mainloop()


#root = tk.Tk()
#foo = DataGrid(root, data=DATA)
#foo.render()

#root.columnconfigure(0, weight=1)
#root.rowconfigure(0, weight=1)
