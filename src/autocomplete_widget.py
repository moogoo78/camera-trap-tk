import re

import tkinter as tk
'''
via: https://code.activestate.com/recipes/580770-combobox-autocomplete/
'''
def autoscroll(sbar, first, last):
    """Hide and show scrollbar as needed."""
    first, last = float(first), float(last)
    if first <= 0 and last >= 1:
        sbar.grid_remove()
    else:
        sbar.grid()
    sbar.set(first, last)

class Combobox_Autocomplete(tk.Entry, object):
    def __init__(self, master, list_of_items=None, autocomplete_function=None, listbox_width=None, listbox_height=9, ignorecase_match=False, startswith_match=True, vscrollbar=True, hscrollbar=True, edit_func=None, **kwargs):

        if hasattr(self, "autocomplete_function"):
            if autocomplete_function is not None:
                raise ValueError("Combobox_Autocomplete subclass has 'autocomplete_function' implemented")
        else:
            if autocomplete_function is not None:
                self.autocomplete_function = autocomplete_function
            else:
                if list_of_items is None:
                    raise ValueError("If not guiven complete function, list_of_items can't be 'None'")

                if ignorecase_match:
                    if startswith_match:
                        def matches_function(entry_data, item):
                            return item.startswith(entry_data)
                    else:
                        def matches_function(entry_data, item):
                            return item in entry_data

                    self.autocomplete_function = lambda entry_data: [item for item in self.list_of_items if matches_function(entry_data, item)]
                else:
                    if startswith_match:
                        def matches_function(escaped_entry_data, item):
                            if re.match(escaped_entry_data, item, re.IGNORECASE):
                                return True
                            else:
                                return False
                    else:
                        def matches_function(escaped_entry_data, item):
                            if re.search(escaped_entry_data, item, re.IGNORECASE):
                                return True
                            else:
                                return False

                    def autocomplete_function(entry_data):
                        escaped_entry_data = re.escape(entry_data)
                        return [item for item in self.list_of_items if matches_function(escaped_entry_data, item)]

                    self.autocomplete_function = autocomplete_function

        self._listbox_height = int(listbox_height)
        self._listbox_width = listbox_width

        self.list_of_items = list_of_items

        self._use_vscrollbar = vscrollbar
        self._use_hscrollbar = hscrollbar

        kwargs.setdefault("background", "white")

        if "textvariable" in kwargs:
            self._entry_var = kwargs["textvariable"]
        else:
            self._entry_var = kwargs["textvariable"] = tk.StringVar()

        tk.Entry.__init__(self, master, **kwargs)

        self._trace_id = self._entry_var.trace('w', self._on_change_entry_var)

        self._listbox = None

        self.bind("<Tab>", self._on_tab)
        self.bind("<Up>", self._previous)
        self.bind("<Down>", self._next)
        self.bind('<Control-n>', self._next)
        self.bind('<Control-p>', self._previous)

        self.bind("<Return>", self._update_entry_from_listbox)
        self.bind("<Escape>", lambda event: self.unpost_listbox())

        # moogoo
        self.edit_func = edit_func

    def _on_tab(self, event):
        self.post_listbox()
        return "break"

    def _on_change_entry_var(self, name, index, mode):

        entry_data = self._entry_var.get()

        if entry_data == '':
            self.unpost_listbox()
            self.focus()
        else:
            values = self.autocomplete_function(entry_data)
            if values:
                if self._listbox is None:
                    self._build_listbox(values)
                else:
                    self._listbox.delete(0, tk.END)

                    height = min(self._listbox_height, len(values))
                    self._listbox.configure(height=height)

                    for item in values:
                        self._listbox.insert(tk.END, item)

            else:
                self.unpost_listbox()
                self.focus()

        if self.edit_func:
            self.edit_func(entry_data)

    def _build_listbox(self, values):
        listbox_frame = tk.Frame()

        self._listbox = tk.Listbox(listbox_frame, background="white", selectmode=tk.SINGLE, activestyle="none", exportselection=False)
        self._listbox.grid(row=0, column=0,sticky = 'news')

        self._listbox.bind("<ButtonRelease-1>", self._update_entry_from_listbox)
        self._listbox.bind("<Return>", self._update_entry_from_listbox)
        self._listbox.bind("<Escape>", lambda event: self.unpost_listbox())

        self._listbox.bind('<Control-n>', self._next)
        self._listbox.bind('<Control-p>', self._previous)

        if self._use_vscrollbar:
            vbar = tk.Scrollbar(listbox_frame, orient=tk.VERTICAL, command= self._listbox.yview)
            vbar.grid(row=0, column=1, sticky='ns')

            self._listbox.configure(yscrollcommand= lambda f, l: autoscroll(vbar, f, l))

        if self._use_hscrollbar:
            hbar = tk.Scrollbar(listbox_frame, orient=tk.HORIZONTAL, command= self._listbox.xview)
            hbar.grid(row=1, column=0, sticky='ew')

            self._listbox.configure(xscrollcommand= lambda f, l: autoscroll(hbar, f, l))

        listbox_frame.grid_columnconfigure(0, weight= 1)
        listbox_frame.grid_rowconfigure(0, weight= 1)

        x = -self.cget("borderwidth") - self.cget("highlightthickness")
        y = self.winfo_height()-self.cget("borderwidth") - self.cget("highlightthickness")

        if self._listbox_width:
            width = self._listbox_width
        else:
            width=self.winfo_width()

        listbox_frame.place(in_=self, x=x, y=y, width=width)

        height = min(self._listbox_height, len(values))
        self._listbox.configure(height=height)

        for item in values:
            self._listbox.insert(tk.END, item)

    def post_listbox(self):
        if self._listbox is not None: return

        entry_data = self._entry_var.get()
        if entry_data == '': return

        values = self.autocomplete_function(entry_data)
        if values:
            self._build_listbox(values)

    def unpost_listbox(self):
        if self._listbox is not None:
            self._listbox.master.destroy()
            self._listbox = None

    def get_value(self):
        return self._entry_var.get()

    def set_value(self, text, close_dialog=False):
        self._set_var(text)

        if close_dialog:
            self.unpost_listbox()

        self.icursor(END)
        self.xview_moveto(1.0)

    def _set_var(self, text):
        self._entry_var.trace_vdelete("w", self._trace_id)
        self._entry_var.set(text)
        self._trace_id = self._entry_var.trace('w', self._on_change_entry_var)

    def _update_entry_from_listbox(self, event):
        if self._listbox is not None:
            current_selection = self._listbox.curselection()

            if current_selection:
                text = self._listbox.get(current_selection)
                self._set_var(text)

            self._listbox.master.destroy()
            self._listbox = None

            self.focus()
            self.icursor(tk.END)
            self.xview_moveto(1.0)
        
        return "break"

    def _previous(self, event):
        if self._listbox is not None:
            current_selection = self._listbox.curselection()

            if len(current_selection)==0:
                self._listbox.selection_set(0)
                self._listbox.activate(0)
            else:
                index = int(current_selection[0])
                self._listbox.selection_clear(index)

                if index == 0:
                    index = END
                else:
                    index -= 1

                self._listbox.see(index)
                self._listbox.selection_set(first=index)
                self._listbox.activate(index)

        return "break"

    def _next(self, event):
        if self._listbox is not None:

            current_selection = self._listbox.curselection()
            if len(current_selection)==0:
                self._listbox.selection_set(0)
                self._listbox.activate(0)
            else:
                index = int(current_selection[0])
                self._listbox.selection_clear(index)

                if index == self._listbox.size() - 1:
                    index = 0
                else:
                    index +=1

                self._listbox.see(index)
                self._listbox.selection_set(index)
                self._listbox.activate(index)
        return "break"


class FreeSolo(tk.Frame):
    def __init__(self, parent, options, edit_func):
        tk.Frame.__init__(self, parent)
        self.parent = parent
        self.autocomplete = Combobox_Autocomplete(
            parent,
            options,
            edit_func=edit_func,
            highlightthickness=1)

        self.autocomplete.grid(row=0, column=0, sticky='nswe')
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.grid_propagate(False) #?
        self.autocomplete.focus_set()
