import tkinter as tk
from tkinter import ttk

class Autocomplete(ttk.Frame):
    """
    frame:
      - entry
      - frame
        - listbox
    """
    def __init__(self, master=None, choices=[], value=None, freesolo=False,  **kwargs):
        width = kwargs.pop('width', None)
        self.after_update_entry = kwargs.pop('after_update_entry', None)

        self.choices = choices

        ttk.Frame.__init__(self, master, **kwargs)
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        self.sv = tk.StringVar()
        self.sv.set(value)

        self.entry = ttk.Entry(self, width=width, textvariable=self.sv, takefocus=1)
        self.sv.trace('w', self.handle_trace)

        self.listbox_frame = ttk.Frame(self, style='border.TFrame', padding=1)
        self.listbox = tk.Listbox(self.listbox_frame, width=width, selectmode=tk.SINGLE,
                                  highlightthickness=0, relief='flat')
        self.listbox.bind('<<ListboxSelect>>', self._update_entry)
        self.listbox.bind_all('<Down>', lambda event: self.handle_listbox_arrow_key(event, 'down'))
        self.listbox.bind_all('<Up>', lambda event: self.handle_listbox_arrow_key(event, 'up'))
        self.listbox.bind_all('<Return>', self._update_entry)
        self.listbox.pack(fill='both', expand=True)
        self.listbox.grid()

        self.entry.grid(sticky='ew')
        self.listbox_frame.grid(sticky='nsew')

        # render listbox
        self.listbox.insert(tk.END, '')
        for i in choices:
            if isinstance(i, tuple):
                self.listbox.insert(tk.END, i[0])
            if isinstance(i, str):
                self.listbox.insert(tk.END, i)

        self.listbox.activate(0)
        self.listbox.select_set(0)

        self.entry.focus_set()

    def handle_trace(self, name, index, mode):
        val = self.sv.get()
        # print(name, index, mode, val)
        if len(self.choices) > 0:
            item = self.choices[0]
            if isinstance(item, tuple):
                filtered = [i for i in self.choices if val.lower() in i[1].lower()]
            if isinstance(item, str):
                filtered = [i for i in self.choices if val.lower() in i.lower()]

        self.listbox.delete(0, tk.END)
        for i in filtered:
            self.listbox.insert(tk.END, i)
        self.listbox.activate(0)
        self.listbox.select_set(0)

    def _update_entry(self, event):
        val = ''
        if sel := self.listbox.curselection():
            val = self.listbox.get(sel[0])
            self.entry.delete(0, "end")
            self.entry.selection_clear()
            self.entry.icursor("end")
            self.event_generate('<<ItemSelect>>')

        self.after_update_entry(val)

        # caused keyboard up/down erreor
        # self.listbox_frame.destroy()
        # self.listbox_frame.grid_remove()

    def handle_listbox_arrow_key(self, event, direction):
        if not hasattr(self, 'listbox'):
            return

        if sel := self.listbox.curselection():
            select_index = sel[0]
            if direction == 'down':
                self.listbox.yview_scroll(1, 'units')
                select_index += 1
            elif direction == 'up':
                self.listbox.yview_scroll(-1, 'units')
                select_index -= 1

            if select_index >= 0 and select_index < self.listbox.size():
                self.listbox.selection_clear(0, tk.END)
                self.listbox.see(select_index-2)
                self.listbox.activate(select_index)
                self.listbox.select_set(select_index)


class Autocomplete2(ttk.Entry, object):
    def __init__(
            self,
            parent,
            choices=None,
            value=None,
            entry_args={},
            listbox_args={},
    ):
        #autocomplete_function=None, , ignorecase_match=False, startswith_match=True, vscrollbar=True, hscrollbar=True, value_callback=None, **kwargs):
        self.choices = choices
        self.filtered_choices = []
        self.listbox_frame = None

        if not value:
            entry_args['textvariable'] = tk.StringVar()
        else:
            self.value = entry_args['textvariable'] = value

        default_listbox_args = {
            'width': None,
            'height': 9,
            'background': 'white',
            'selectmode': tk.SINGLE,
            'activestyle': 'none',
            'exportselection': False,
        }
        self.listbox_args = {**default_listbox_args, **listbox_args}

        ttk.Entry.__init__(
            self,
            parent,
            **entry_args)

        self.value_trace_id = self.value.trace('w', self.handle_trace)
        self.bind('<Return>', self.handle_update) # next?
        self.bind('<Escape>',  self.handle_update)
        #self.bind('<Down>', lambda event: self.create_listbox())
        #self.bind('<Return>', lambda _: self.create_listbox())
        self.bind('<Return>', self.toggle_listbox)
        #self.bind("<FocusOut>", lambda _: self.remove_listbox()) # will cause listbox gone!
        #self.bind('<FocusOut>', self.haldel_update)

        self.listbox = None
        #self.build_listbox()

    #def set_value(self, value, close_listbox=False):
        #self._entry_var.trace_vdelete("w", self._trace_id)
        #self._entry_var.set(text)
        #self._trace_id = self._entry_var.trace('w', self._on_change_entry_var)
    #    self.value.set(value)
    #    if close_listbox:
    #        self.close_listbox()

    #def test(self, e):
    #    print ('test', e, self.listbox, self)

    def set_focus(self):
        self.focus()

    def handle_trace(self, name, index, mode):
        val = self.value.get()
        #print ('free trace', val)
        #if val == '':
        #    #self.focus() # ?
        #else:
        if val:
            filtered = [i for i in self.choices if i.startswith(val)]
            #print ('filtered:', filtered, self.listbox)
            if len(filtered) > 0:
                if self.listbox is None:
                    self.create_listbox(filtered)
                else:
                    self.listbox.delete(0, tk.END)
                    for i in filtered:
                        self.listbox.insert(tk.END, i)

    def handle_update(self, event):
        #print ('handle_update')
        if listbox := self.listbox:
            current_selection = listbox.curselection()
            if current_selection:
                text = listbox.get(current_selection)
                self.value.set(text)


        # destroy listbox
        self.remove_listbox()

        self.focus()
        self.icursor(tk.END)
        self.xview_moveto(1.0)

    def toggle_listbox(self, event):
        #if not self.list_box_frame:
        #    self
        #if not self.listbox_frame:
        #    self.listbox_frame = tk.Frame()

        if not self.listbox:
            self.create_listbox()
        else:
            print ('pass')

    def create_listbox(self, filtered_choices=[]):
        #print (self.listbox, 'create', self.listbox_frame)
        self.listbox_frame = tk.Frame()
        self.listbox = tk.Listbox(self.listbox_frame, **self.listbox_args)
        self.listbox.grid(row=0, column=0, sticky = 'news')

        self.listbox.bind("<ButtonRelease-1>", self.handle_update)
        #        self.listbox.bind("<Return>", self._update_entry)
        #self.listbox.bind("<Escape>", lambda _: self.unpost_listbox())

        self.listbox_frame.grid_columnconfigure(0, weight= 1)
        self.listbox_frame.grid_rowconfigure(0, weight= 1)

        #x = -self.cget("borderwidth") - self.cget("highlightthickness")
        x = 0
        #y = self.winfo_height()-self.cget("borderwidth") - self.cget("highlightthickness")
        y = self.winfo_height()

        if self.listbox_args.get('width', ''):
            width = self.listbox_width
        else:
            width = self.winfo_width()
        #print (x, y, width, self.winfo_height(),self.cget("borderwidth"),self.cget("highlightthickness"))
        y = 22
        width = 120
        self.listbox_frame.place(in_=self, x=x, y=y, width=width)

        #self.update_listbox_choices(filtered_choices)

        #def update_listbox_choices(self, filtered_choices=[]):
        #print ('update list', filtered_choices)

        choices = filtered_choices if len(filtered_choices) else self.choices
        for i in choices:
            self.listbox.insert(tk.END, i)

            #height = min(self._listbox_height, len(values))
            #        self._listbox.configure(height=height)

    def remove_listbox(self):
        if self.listbox is not None:
            #print (self.listbox.master, 'master')
            self.listbox.master.destroy()
            self.listbox = None

    def terminate(self):
        self.remove_listbox()
        self.value.set('')
        self.destroy()
