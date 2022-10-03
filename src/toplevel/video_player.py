import tkinter as tk
from tkinter import ttk

from PIL import (
    Image,
    ImageTk
)
import threading
from time import perf_counter, sleep
import logging

import imageio


class VideoPlayer(tk.Toplevel):
    # INIT_WIDTH = 1200
    # INIT_HEIGHT = 760

    def __init__(self, parent, video_path):
        super().__init__(parent)
        self.parent = parent


        # imageio V2
        self.reader = imageio.get_reader(video_path)
        metadata = self.reader.get_meta_data()
        self.frame_rate = metadata['fps']
        self.video_size = metadata['size']
        logging.info(f'video meta data: {metadata}')

        self.geometry(f'{self.video_size[0]}x{self.video_size[1]}')
        self.title(f'Camera Trap Video Player - {video_path}')
        self.protocol('WM_DELETE_WINDOW', self.quit)
        self.video_label = tk.Label(self, text='- default video player -')
        self.video_label.grid()
        self.is_playing = False
        # player
        thread = threading.Thread(target=self.play, args=(video_path, 1))
        #thread.daemon = 1
        self.is_playing = True
        thread.start()


    def play(self, path, loop):
        '''
        inspired via: https://github.com/huskeee/tkvideo
        '''
        if self.frame_rate > 0:
            frame_duration = float(1 / self.frame_rate)
        else:
            frame_duration = float(0)

        if loop == 1:
            before = perf_counter()
            while self.is_playing:
                image_array = self.reader.get_next_data()
                photo_image = ImageTk.PhotoImage(Image.fromarray(image_array))
                # print(self.is_playing, self.video_label, photo_image)

                if self.is_playing and self.video_label:
                    self.video_label.config(image=photo_image)
                    self.video_label.image = photo_image

                    diff = frame_duration + before
                    after = perf_counter()
                    diff = diff - after
                    if diff > 0:
                        sleep(diff)
                    before = perf_counter()

            logging.debug('video play to the end')
        else:
            before = perf_counter()
            for image in frame_data.iter_data():
                    frame_image = ImageTk.PhotoImage(Image.fromarray(image).resize(self.size))
                    self.video_label.config(image=frame_image)
                    self.video_label.image = frame_image

                    diff = frame_duration + before
                    after = perf_counter()
                    diff = diff - after 
                    if diff > 0:
                        sleep(diff)
                    before = perf_counter()

    def quit(self):
        logging.debug('stop video play')
        self.is_playing = False
        self.parent.data_grid.main_table.set_keyboard_control(True)
        self.video_label.destroy()
        self.video_label = None
        self.destroy()
