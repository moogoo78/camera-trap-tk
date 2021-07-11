import tkinter as tk
from tkinter import ttk

"""
mist: #90AFC5
stone: #336B87
shadow: #2A3132
automn leaf: #763626
#https://www.canva.com/design/DADfC5CQ0W4/remix?action2=create&mediaId=DADfC5CQ0W4&signupReferrer=blog&utm_source=blog&utm_medium=content&utm_campaign=100-color-combinations&_branch_match_id=812929534608293691
"""
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
            header_list=None,
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

        self.data = data
        self.num_cols = len(self.data[0])
        self.num_rows = len(self.data)

        # set default
        self.x_start = 2
        self.y_start = 2
        self.cell_width = 100
        self.cell_height = 20

        self.header_list = header_list
        self.x_del_list = [0]
        wx = 0
        if not self.header_list:
            self.header_list = []
            for x in self.data[0].keys():
                self.header_list.append({
                    'key': x,
                    'label': x,
                    'width': self.cell_width
                })
                wx += self.cell_width
                self.x_del_list.append(wx)
        else:
            for i in self.header_list:
                if 'width' not in i:
                    i['width'] = self.cell_width
                wx += i['width']
                self.x_del_list.append(wx)

        #if self.width < wx:
            # expend width if header has larger width
        #    self.width = wx

        self.width = wx

        self.entry_queue = {}
        self.current_rc = [None, None]
        self.selected = {
            'row_start': None,
            'row_end': None,
            'col_start': None,
            'col_end': None,
            'col_list': [],
            'row_list': [],
        }

        # color
        self.color_grid = 'gray'
        self.color_rect = '#ddeeff'


        # binding
        self.bind('<Button-1>',self.handle_mouse_click_left)
        self.bind('<B1-Motion>', self.handle_mouse_drag)
        #self.parentframe.master.bind_all("<Up>", self.handle_arrow_keys)
        ## check master
        self.parent.master.bind_all('<Up>', self.handle_arrow_key)
        self.parent.master.bind_all('<Down>', self.handle_arrow_key)

    def foo(self, e):
        print ('foo', e)

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
        self.render_data()
        self.column_header.render()
        self.row_index.render()

    def render_grid(self):
        self.delete('girdline')

        #476042

        # grid border
        # vertical line
        for i in range(self.num_cols+1): # fixed size
            if i < len(self.x_del_list):
                x = self.x_del_list[i]
            else:
                x = self.x_del_list[-1] + self.cell_width
            x += self.x_start
            self.create_line(x, self.y_start,
                             x, self.y_start + self.num_rows * self.cell_height,
                             tag='gridborder',
                             fill=self.color_grid, width=1)

        # horizontal line
        for i in range(self.num_rows+1):
            y = i * self.cell_height
            y += self.y_start
            self.create_line(self.x_start, y, self.x_del_list[-1]+self.x_start, y,
                             tag='gridborder',
                             fill=self.color_grid, width=1)


    def render_data(self):
        self.delete('text')
        for row_index, row in enumerate(self.data.items()):
            for col_index, col in enumerate(row[1].items()):
                x = self.x_del_list[col_index] + self.header_list[col_index]['width'] / 2
                cell_tag = f'cell-text-{row_index}_{col_index}'
                rect = self.create_text(
                    x + self.x_start,
                    row_index * self.cell_height + self.y_start + self.cell_height/2,
                    text=col[1],
                    tag=('text', cell_tag)
                )
                    #fill=linkcolor,
                    #font=linkfont,
                    #tag=('text','hlink','celltext'+str(col)+'_'+str(row)))

    def render_entry(self, row, col, text):
        cell_tag = f'cell-text-{row}_{col}'
        sv = tk.StringVar()
        sv.set(text)
        if hasattr(self, 'cell_entry'):
            # save data if last entry not Enter or Escape
            if len(self.entry_queue):
                self.save_entry_queue()
            self.cell_entry.destroy()

        x1, y1, x2, y2 = self.get_cell_coords(row, col)

        self.cell_entry = ttk.Entry(
            self.parent,
            width=x2-x1,
            textvariable=sv,
            takefocus=1)

        def callback(e):
            value = sv.get()

            # draw text
            self.delete(cell_tag)
            # self.create_text(
            #     x1+self.cell_width/2,
            #     y1+self.cell_height/2,
            #     text=value,
            #     fill='brown',
            #     anchor='w',
            #     tag=(cell_tag,)
            # )
            #print ('entry-callback', e.keysym, cell_tag, value)
            self.entry_queue[cell_tag] = value

            if e.keysym in ['Return', 'Escape']:
                self.set_data_value(row, col, value)
                #self.entry_queue.pop()
                del self.entry_queue[cell_tag]
                self.delete('entry_win')


        self.cell_entry.icursor(tk.END)
        #self.cell_entry.bind('<Return>', callback)
        self.cell_entry.bind('<KeyRelease>', callback)
        self.cell_entry.focus_set()
        #create_window
        self.create_window(
            x1,
            y1,
            width=x2-x1+self.x_start,
            height=self.cell_height,
            window=self.cell_entry,
            anchor='nw',
            tag='entry_win')

    def handle_enter_drag(self, event):
        print (event, 'entry drag')

    def render_selected(self, row, col):
        self.delete('cell-highlight')
        self.delete('cell-highlight-drag')
        self.delete('row-highlight')

        x1, y1, x2, y2 = self.get_cell_coords(row, col)
        # cell highlight
        self.create_rectangle(
            x1,
            y1,
            x2+self.x_start,
            y2,
            #fill='pink',
            outline='blue',
            width=4,
            tag=('cell-highlight',))
        self.lower('cell-highlight')

        rect_drag = self.create_rectangle(
            x2,
            y2,
            x2+4,
            y2+4,
            fill='pink',
            outline='blue',
            width=1,
            activefill='cyan',
            tag=('cell-highlight-drag',))
        self.lift('cell-highlight-drag')
        rect_drag.bind("<Enter>", self.handle_enter_drag)
        rect_drag.bind("<Leave>", self.handle_enter_drag)

        # render row highlight
        self.create_rectangle(0, y1, self.width + self.x_start, y2,
                                     fill=self.color_rect,
                                     outline='red',
                                     tag='row-highlight')
        self.lower('row-highlight')
        #self.lower('fillrect')
        #self.tablerowheader.drawSelectedRows(self.currentrow)

    def render_box(self, selected):
        self.delete('box-highlight')

        for row in selected['row_list']:
            for col in selected['col_list']:
                x1, y1, x2, y2 = self.get_cell_coords(row, col)
                self.create_rectangle(
                    x1,
                    y1,
                    x2+self.x_start,
                    y2,
                    fill='#c1ceff',
                    #outline='blue',
                    #width=4,
                    tag=('box-highlight',))

        self.lower('box-highlight')

    def clearSelected(self):
        self.delete('rect')
        self.delete('entry')
        self.delete('tooltip')
        self.delete('searchrect')
        self.delete('colrect')
        self.delete('multicellrect')

    def get_cell_coords(self, row, col):
        #print (row, col, self.x_del_list)
        x1 = self.x_start + self.x_del_list[col]
        x2 = self.x_del_list[col+1]
        y1 = self.y_start + (self.cell_height * row)
        y2 = y1 + self.cell_height
        return x1, y1, x2, y2

    def get_data_value(self, row, col):
        return self.data[row][self.header_list[col]['key']]

    def set_data_value(self, row, col, value):
        self.data[row][self.header_list[col]['key']] = value
        print ('save', self.data)
        self.render()
        return

    def get_rc(self, event):
        #print (event.x, event.y)
        x = int(self.canvasx(event.x))
        y = int(self.canvasy(event.y))

        if y > self.num_rows*self.cell_height:
            # 點到表格下面, 不要動作
            return None, None
        elif x > self.x_del_list[-1]:
            # 點到表格右邊, select row
            return int((y-self.y_start)/self.cell_height), -1

        col = None
        for i, v in enumerate(self.x_del_list):
            next_x = self.x_del_list[min(i+1, len(self.x_del_list))]
            if x > v and x <= next_x:
                col = i
                break
        return int((y-self.y_start)/self.cell_height), col

    def save_entry_queue(self):
        for i, v in self.entry_queue.items():
            rc = i.replace('cell-text-', '').split('_')
            self.set_data_value(int(rc[0]), int(rc[1]), v)
            self.entry_queue = {}

    def handle_mouse_drag(self, event):
        #print (event, 'drag')
        row, col = self.get_rc(event)

        if row == None or col == None:
            return

        if row >= self.num_rows:
            #or self.startrow > self.rows:
            return
        else:
            self.selected['row_end'] = row

        if col > self.num_cols:
            #or self.startcol > self.cols:
            return
        else:
            self.selected['col_end'] = col
            if self.selected['col_start'] is None or self.selected['col_end'] is None:
                return
            if self.selected['col_end'] < self.selected['col_start']:
                self.selected['col_list'] = range(self.selected['col_end'], self.selected['col_start']+1)
            else:
                self.selected['col_list'] = range(self.selected['col_start'], self.selected['col_end']+1)


        if self.selected['row_end'] != self.selected['row_start']:
            if self.selected['row_end'] < self.selected['row_start']:
                self.selected['row_list'] = range(self.selected['row_end'], self.selected['row_start']+1)
            else:
                self.selected['row_list'] = range(self.selected['row_start'], self.selected['row_end']+1)

        else:
            self.selected['row_list'] = [self.current_rc[0]]

        self.render_box(self.selected)
        #print (self.selected)

    def handle_mouse_click_left(self, event):
        # flush entry_queue
        if len(self.entry_queue):
            self.save_entry_queue()
            self.render()

        # clear
        self.delete('entry_win')
        self.delete('rect')

        row, col = self.get_rc(event)
        #print (row, col)
        if row == None or col == None:
            return

        # reset selected
        self.selected = {
            'row_start': row,
            'row_end': row,
            'col_start': col,
            'col_end': col,
            'row_list': [row],
            'col_list': [col],
        }
        self.render_box(self.selected)

        if col == -1:
            col = 0 # 預設如點第一格

        # draw selected
        #row = self.currentrow
        x1, y1, x2, y2 = self.get_cell_coords(row, col)
        #x2 = self.tablewidth
        #print (x1, y1, x2, y2)

        text = self.get_data_value(row, col)

        is_render_entry = True
        if self.header_list[col].get('readonly', ''):
            is_render_entry = False

        if is_render_entry:
            self.render_entry(row, col, text)

        self.current_rc = [row, col]
        self.render_selected(row, col)



    def handle_arrow_key(self, event):
        #print ('handle_arrow:', event)
        if event.keysym == 'Up':
            if self.current_rc[0] == 0:
                return
            else:
                self.current_rc[0] = self.current_rc[0] - 1
        elif event.keysym == 'Down':
            if self.current_rc[0] >= self.num_rows - 1:
                return
            else:
                self.current_rc[0] = self.current_rc[0] + 1

        self.render_selected(self.current_rc[0], self.current_rc[1])


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
        for i, v in enumerate(self.data_grid.header_list):

            x = self.data_grid.x_del_list[i] + self.data_grid.header_list[i]['width'] / 2
            self.create_text(
                x + pad, self.data_grid.cell_height/2,
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
        datagrid = DataGrid(f, data=DATA, width=500, header_list=HEADER)
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
