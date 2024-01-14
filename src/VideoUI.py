from threading import Thread
from PIL import Image, ImageTk
import os
from os import *
import time
import tkinter as tk
import numpy as np


class RepeatedTimer(Thread):
    def __init__(self, speed, function):
        super().__init__()

        self.speed = speed
        self.function = function
        self.pause = False

    def run(self):
        while not self.pause:
            time.sleep(60 / (self.speed * 16) -
                       (time.monotonic() % (60 / (self.speed * 16)))) # fix the distortion in time.sleep
            if not self.pause:
                self.function()

    def stop(self):
        self.pause = True


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        
        # Setting data and parameters
        self.timer = RepeatedTimer(1, lambda: self.display('next'))
        
        # default path and stage to be displayed
        self.path = 'Conventionally_named_holes'
        self.stage = 2

        self.names = np.array(os.listdir(self.path))
        self.hole_number = 0
        
        # Setting the title for window
        self.title("Video")

        # Main frame that holds the app
        self.main_frame = tk.Frame()
        # self.main_frame = tk.Frame(width=800, height=500)
        # self.main_frame.rowconfigure([0, 1], minsize=250)
        # self.main_frame.columnconfigure(0, minsize=800)
        self.main_frame.pack()

        # frame that displays the stage
        self.stage_label = tk.Label(
            master=self.main_frame, text=f"Stage {self.stage}", 
        )
        self.stage_label.grid(row=0, column=1)

        # Frame that displays the images
        self.frame_images = tk.Frame(
            master=self.main_frame, relief=tk.RIDGE, borderwidth=3
        )
        # self.frame_images.grid(row=0)
        self.frame_images.grid(row=1, column=1)

        # Frame that holds the controls
        self.frame_controls = tk.Frame(
            master=self.main_frame, relief=tk.RIDGE, borderwidth=3
        )
        # self.frame_controls.grid(row=1)
        self.frame_controls.grid(row=2, column=1)

        # Label that displays the name of the currently displayed image
        self.lbl_imname = tk.Label(
            master=self.frame_images,
            text="", padx=10, pady=6
        )
        # self.lbl_imname.grid(row=1)
        self.lbl_imname.grid(row=2)

        # Label that holds the static image
        self.lbl_image = tk.Label(
            master=self.frame_images,
            padx=10, pady=6, width=300, height=300
        )
        # self.lbl_image.grid(row=0)
        self.lbl_image.grid(row=1)

        self.display()

        # stage controls

        self.prev_stage_img = Image.open('./Buttons/previous.png', 'r').resize((50, 50))
        self.prev_stage_img_tk = ImageTk.PhotoImage(image=self.prev_stage_img)
        self.btn_prev_stage = tk.Button(
            master=self.main_frame, 
            image=self.prev_stage_img_tk,
            command=lambda: self.prev_stage()
        )
        self.btn_prev_stage.grid(row=1, column=0)

        self.next_stage_img = Image.open('./Buttons/previous.png', 'r').resize((50, 50))
        self.next_stage_img_tk = ImageTk.PhotoImage(image=self.next_stage_img)
        self.btn_next_stage = tk.Button(
            master=self.main_frame, 
            image=self.next_stage_img_tk, 
            command=lambda: self.next_stage()
        )
        self.btn_next_stage.grid(row=1, column=2)

        # Spinner that helps control the speed of the slideshow
        self.spn_speed = tk.Spinbox(
            master=self.frame_controls, from_=1, to=4, command=self.set_speed
        )
        self.spn_speed.grid(row=0, column=0)

        # Button that shows the previously shown image
        self.prev_btn_img = Image.open('./Buttons/previous.png', 'r').resize((25, 25))
        self.prev_btn_img_tk = ImageTk.PhotoImage(image=self.prev_btn_img)
        self.btn_prev = tk.Button(
            master=self.frame_controls,
            image=self.prev_btn_img_tk,
            relief=tk.GROOVE, borderwidth=2, padx=5, pady=3.5, command=lambda: self.display('previous')
        )
        self.btn_prev.grid(row=0, column=1)

        # Button that shows the next image on the disk
        self.next_btn_img = Image.open(path.join(
            os.getcwd(), 'Buttons', 'next.png'), 'r').resize((25, 25))
        self.next_btn_img_tk = ImageTk.PhotoImage(image=self.next_btn_img)
        self.btn_next = tk.Button(
            master=self.frame_controls,
            image=self.next_btn_img_tk,
            relief=tk.GROOVE, borderwidth=2, padx=5, pady=3.5, command=lambda: self.display('next')
        )
        self.btn_next.grid(row=0, column=2)

        # Button that starts the slideshow
        self.play_btn_img = Image.open(path.join(
            os.getcwd(), 'Buttons', 'play.png'), 'r').resize((25, 25))
        self.play_btn_img_tk = ImageTk.PhotoImage(image=self.play_btn_img)
        self.btn_play = tk.Button(
            master=self.frame_controls,
            image=self.play_btn_img_tk,
            relief=tk.GROOVE, borderwidth=2, padx=5, pady=3.5, command=lambda: self.play_imshow()
        )
        self.btn_play.grid(row=0, column=3)

        # Button that pauses the slideshow
        self.pause_btn_img = Image.open(path.join(
            os.getcwd(), 'Buttons', 'pause.png'), 'r').resize((25, 25))
        self.pause_btn_img_tk = ImageTk.PhotoImage(image=self.pause_btn_img)
        self.btn_pause = tk.Button(
            master=self.frame_controls,
            image=self.pause_btn_img_tk,
            relief=tk.GROOVE, borderwidth=2, padx=5, pady=3.5, command=lambda: self.pause_imshow()
        )
        self.btn_pause.grid(row=0, column=4)

    def display(self, direction='current'):
            try:
                if direction == 'next':
                    self.hole_number += 1
                    if self.hole_number == len(os.listdir(self.path)):
                        self.hole_number = 0

                elif direction == 'previous':
                    if not self.timer.pause:
                        self.pause_imshow()

                    self.hole_number -= 1
                    if self.hole_number == -1:
                        self.hole_number = len(os.listdir(self.path)) - 1

                self.update_img()

            except Exception as err:
                print(err)
    
    def next_stage(self):
        if self.stage < 3:
            self.stage += 1
            self.update_items()
        

    def prev_stage(self):
        if self.stage > 1:
            self.stage -= 1
            self.update_items()

    def update_items(self):
        self.update_path()
        self.hole_number = 0
        self.stage_label['text'] = f'Stage {self.stage}'
        self.update_img()

    def update_img(self):
        path = os.path.join(self.path, self.names[self.hole_number])
        self.img = Image.open(path, 'r').resize((300, 300))
        self.img_tk = ImageTk.PhotoImage(image=self.img)
        
        self.lbl_imname['text'] = f"{self.names[self.hole_number]}"
        self.lbl_image['image'] = self.img_tk
        
    def set_speed(self):
        self.timer.speed = int(self.spn_speed.get())

    def update_path(self):
        if self.stage == 1:
            self.path = 'images'
        elif self.stage == 2:
            self.path = 'Conventionally_named_holes'
        else:
            self.path = 'Buttons'
        print(self.path)
        self.names = os.listdir(self.path)
        print(self.names)
        
    def play_imshow(self):
        self.speed = int(self.spn_speed.get())
        self.timer.start()

    def pause_imshow(self):
        self.timer.stop()
        self.timer = RepeatedTimer(
            int(self.spn_speed.get()), lambda: self.display('next'))



if __name__ == '__main__':
    app = App()
    app.mainloop()

