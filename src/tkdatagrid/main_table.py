import tkinter as tk
from tkinter import ttk

"""
mist: #90AFC5
stone: #336B87
shadow: #2A3132
automn leaf: #763626
#https://www.canva.com/design/DADfC5CQ0W4/remix?action2=create&mediaId=DADfC5CQ0W4&signupReferrer=blog&utm_source=blog&utm_medium=content&utm_campaign=100-color-combinations&_branch_match_id=812929534608293691
"""

class MainTable(tk.Canvas):

    def __init__(
            self,
            parent=None,
            width=None,
            height=None,
            bgcolor='#F7F7FA',
            fgcolor='black',
            **kwargs):
        super().__init__(parent, bg='gray75',bd=2, relief='groove',scrollregion=(0,0,300,200))
        self.parent = parent
        self.ps = self.parent.state
        self.width = self.ps['width']
        self.height = self.ps['height']

        #self.data = ps['data']
        self.num_cols = len(self.ps['data'][0])
        self.num_rows = len(self.ps['data'])

        # set default
        self.x_start = 0
        self.y_start = 0



        #if self.width < wx:
            # expend width if header has larger width
        #    self.width = wx

        self.width = self.ps['width']

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
        # TODO
        #self.parent.master.bind_all('<Up>', self.handle_arrow_key)
        #self.parent.master.bind_all('<Down>', self.handle_arrow_key)
        self.render()

    def render(self):
        #self.configure(scrollregion=(0,0, self.table.tablewidth+self.table.x_start, self.height))


        self.render_grid()
        self.render_data()
        #self.column_header.render()
        #self.row_index.render()

    def render_grid(self):
        self.delete('girdline')

        #476042

        # grid border
        # vertical line
        for i in range(self.num_cols+1): # fixed size
            if i < len(self.ps['column_width_list']):
                x = self.ps['column_width_list'][i]
            else:
                x = self.ps['column_width_list'][-1] + self.ps['cell_width']
            x += self.x_start
            self.create_line(x, self.y_start,
                             x, self.y_start + self.num_rows * self.ps['cell_height'],
                             tag='gridborder',
                             fill=self.color_grid, width=1)

        # horizontal line
        for i in range(self.num_rows+1):
            y = i * self.ps['cell_height']
            y += self.y_start
            self.create_line(self.x_start, y, self.ps['column_width_list'][-1]+self.x_start, y,
                             tag='gridborder',
                             fill=self.color_grid, width=1)


    def render_data(self):
        self.delete('text')
        for row_index, row in enumerate(self.ps['data'].items()):
            for col_index, col in enumerate(row[1].items()):
                x = self.ps['column_width_list'][col_index] + self.ps['columns'][col_index]['width'] / 2
                cell_tag = f'cell-text-{row_index}_{col_index}'
                rect = self.create_text(
                    x + self.x_start,
                    row_index * self.ps['cell_height'] + self.y_start + self.ps['cell_height']/2,
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
            #     y1+self.ps['cell_height']/2,
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
            height=self.ps['cell_height'],
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
        #rect_drag.bind("<Enter>", self.handle_enter_drag)
        #rect_drag.bind("<Leave>", self.handle_enter_drag)

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

        # for row in selected['row_list']:
        #     for col in selected['col_list']:
        #         x1, y1, x2, y2 = self.get_cell_coords(row, col)
        #         self.create_rectangle(
        #             x1,
        #             y1,
        #             x2+self.x_start,
        #             y2,
        #             fill='#c1ceff',
        #             #outline='purple',
        #             #width=4,
        #             tag=('box-highlight',))
        xs1, ys1, xs2, ys2 = self.get_cell_coords(selected['row_start'], selected['col_start'])
        xe1, ye1, xe2, ye2 = self.get_cell_coords(selected['row_end'], selected['col_end'])
        self.create_rectangle(
            xs1,
            ys1,
            xe2+self.x_start,
            ye2,
            fill='#c1ceff',
            outline='blue',
            width=2,
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
        #print (row, col, self.ps['column_width_list'])
        x1 = self.x_start + self.ps['column_width_list'][col]
        x2 = self.ps['column_width_list'][col+1]
        y1 = self.y_start + (self.ps['cell_height'] * row)
        y2 = y1 + self.ps['cell_height']
        return x1, y1, x2, y2

    def get_data_value(self, row, col):
        return self.ps['data'][row][self.ps['columns'][col]['key']]

    def set_data_value(self, row, col, value):
        self.ps['data'][row][self.ps['columns'][col]['key']] = value
        print ('save', self.ps['data'])
        self.render()
        return

    def get_rc(self, event):
        #print (event.x, event.y)
        x = int(self.canvasx(event.x))
        y = int(self.canvasy(event.y))

        if y > self.num_rows*self.ps['cell_height']:
            # 點到表格下面, 不要動作
            return None, None
        elif x > self.ps['column_width_list'][-1]:
            # 點到表格右邊, select row
            return int((y-self.y_start)/self.ps['cell_height']), -1

        col = None
        for i, v in enumerate(self.ps['column_width_list']):
            next_x = self.ps['column_width_list'][min(i+1, len(self.ps['column_width_list']))]
            if x > v and x <= next_x:
                col = i
                break
        return int((y-self.y_start)/self.ps['cell_height']), col

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
        if self.ps['columns'][col].get('readonly', ''):
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
