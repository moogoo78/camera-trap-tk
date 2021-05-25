import tkinter as tk
from tkinter import (
    ttk,
)



class Main(tk.Frame):

    def __init__(self, parent, frames, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent

        self.state = {}
        self.frames = {}
        for i, F in frames.items():
            frame = F(self)
            self.frames[i] = frame
            #print (i, frame)
            frame.grid(row=0, column=0, sticky='nsew')

        self.show_frame('landing')

    def show_frame(self, frame_name, **kwargs):
        frame = self.frames[frame_name]
        if kwargs:
            self.state = kwargs

        frame = self.frames[frame_name]
        if hasattr(frame, 'refresh'):
            frame.refresh()
        frame.tkraise()


