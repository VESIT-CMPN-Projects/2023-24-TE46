from timer import RepeatedTimer
from extractor import Extractor
from PIL import Image, ImageTk
import os
import numpy as np
import tkinter as tk

class AppGUI(tk.Tk):
    def __init__(self, rel1, rel2, model_path):
        super().__init__()

        Image.MAX_IMAGE_PIXELS = None
        self.model_path = model_path
        
        # Setting data and parameters
        self.timer = RepeatedTimer(1, lambda: self.display('next'))
        
        # Getting files and values
        self.resources = rel1
        self.outs = rel2
        
        self.hole_number = 0
        self.stage = 1
        self.from_stage = 0
        self.update_names()
        
        # Setting the title for window
        self.title("VideoUI")

        ########################## GUI FRAMES ##########################

        # Main frame that holds the app
        self.main_frame = tk.Frame()
        self.main_frame.rowconfigure([0, 1, 2], minsize=50)
        self.main_frame.columnconfigure(0, minsize=500)
        self.main_frame.pack()

        # Frame that holds the controls for the stages
        self.frame_stage_controls = tk.Frame(
            master=self.main_frame, relief=tk.RIDGE, borderwidth=3
        )
        self.frame_stage_controls.grid(row=0, column=0)

        # Frame that displays the images
        self.frame_images = tk.Frame(
            master=self.main_frame, relief=tk.RIDGE, borderwidth=3
        )
        self.frame_images.grid(row=1, column=0)

        # Frame that holds the controls for the images
        self.frame_im_controls = tk.Frame(
            master=self.main_frame, relief=tk.RIDGE, borderwidth=3
        )
        self.frame_im_controls.grid(row=2, column=0)
        
        ########################## GUI LABELS ##########################

        # Label that displays the stage
        self.lbl_stage = tk.Label(
            master=self.frame_stage_controls, text=f"Stage {self.stage}", 
        )
        self.lbl_stage.grid(row=0, column=1)

        # Label that holds the static image
        self.lbl_image = tk.Label(
            master=self.frame_images,
            padx=10, pady=6, width=340, height=468
        )
        self.lbl_image.grid(row=1)


        ########################## STAGE CONTROLS ##########################

        self.btn_images, self.btn_tk_images, self.imc_btns, self.ims_btns = [], [], [], []
        btn_image_paths = ['back.png', 'next.png', 'play.png', 'pause.png']
        btn_image_paths = [os.path.join(os.path.abspath(os.path.relpath('buttons')), file) for file in btn_image_paths]

        # Go to previous stage
        self.button(master=self.frame_stage_controls, row=0, col=0, im_path=btn_image_paths[0], shape=(25, 25), function=self.previous_stage)

        # Go to next stage
        self.button(master=self.frame_stage_controls, row=0, col=3, im_path=btn_image_paths[1], shape=(25, 25), function=self.next_stage)


        ########################## IMAGE CONTROLS ##########################

        # Button that shows the previously shown image
        self.button(master=self.frame_im_controls, im_path=btn_image_paths[0], shape=(25, 25), function=lambda: self.display('previous'), relief=tk.GROOVE, borderwidth=2, padx=5, pady=3.5)

        # Button that shows the next image on the disk
        self.button(master=self.frame_im_controls, im_path=btn_image_paths[1], shape=(25, 25), function=lambda: self.display('next'), relief=tk.GROOVE, borderwidth=2, padx=5, pady=3.5)

        # Button that starts the slideshow
        self.button(master=self.frame_im_controls, im_path=btn_image_paths[2], shape=(25, 25), function=self.play_imshow, relief=tk.GROOVE, borderwidth=2, padx=5, pady=3.5)

        # Button that pauses the slideshow
        self.button(master=self.frame_im_controls, im_path=btn_image_paths[3], shape=(25, 25), function=self.pause_imshow, relief=tk.GROOVE, borderwidth=2, padx=5, pady=3.5)

        # Spinner that helps control the speed of the slideshow
        self.spn_speed = tk.Spinbox(
            master=self.frame_im_controls, from_=1, to=4, command=self.set_speed
        )

        # Getting all the images for hole extraction
        self.update_resources()
        self.display()

        self.dropdown = tk.OptionMenu(self.frame_im_controls, self.main_im_path, *self.choices)
        self.main_im_path.trace_add("write", self.update_img)

        self.update_controls()


        ########################## FIRST DISPLAY ##########################

        self.display()




    ################################# Update Functions #################################

    def update_controls(self):
        if self.stage == 1:
            self.to_stage1()
        elif self.from_stage == 1: 
            self.from_stage1()


    def from_stage1(self):
        self.dropdown.grid_forget()
        self.spn_speed.grid(row=0, column=1)
        [btn.grid(row=0, column=index if index == 0 else index + 1) for (index, btn) in enumerate(self.imc_btns)]
        self.lbl_image["width"]=300
        self.lbl_image["height"]=400
        
        try:
            os.mkdir(self.paths[0])
        except Exception as err:
            print(err)

        try:
            os.mkdir(self.paths[1])
        except Exception as err:
            print(err)

        im_path = self.main_im_path.get()
        Extractor(self.main_im, self.outs, [im_path.split('.')[0], im_path.split('.')[0] + '--S'], self.model_path)


    def to_stage1(self):
        self.spn_speed.grid_forget()
        [btn.grid_forget() for btn in self.imc_btns]
        self.dropdown.grid(row=0, column=1)
        self.lbl_image["width"]=340
        self.lbl_image["height"]=468


    def update_resources(self):
        self.choices = np.array(os.listdir(os.path.abspath(os.path.relpath(self.resources))))
        self.choices = [choice for choice in self.choices if choice.endswith('.jpg') or choice.endswith('.png') or choice.endswith('.jpeg')]
        self.main_im_path = tk.StringVar(self.frame_images)
        self.main_im_path.set(self.choices[0])


    def update_stage(self):
        self.update_names()
        self.lbl_stage['text'] = f'Stage {self.stage}'
        self.update_img()
        self.update_controls()


    def update_img(self, *args):
        if self.stage == 1:
            im_path = self.main_im_path.get()
            self.relpath = os.path.abspath(os.path.relpath(self.outs))
            self.paths = [os.path.join(self.relpath, im_path.split('.')[0]), os.path.join(self.relpath, im_path.split('.')[0] + '--S')]

            path = os.path.join(os.path.abspath(os.path.relpath(self.resources)), im_path)

            self.main_im = Image.open(path, mode="r")
            self.main_resized_im = self.main_im.resize((340, 468))
            self.main_tk_im = ImageTk.PhotoImage(image=self.main_resized_im)
            self.lbl_image["image"] = self.main_tk_im

        else:
            path = os.path.join(self.paths[self.stage - 2], self.names[self.hole_number])
            self.img = Image.open(path, 'r').resize((300, 400))
            self.img_tk = ImageTk.PhotoImage(image=self.img)
            self.lbl_image['image'] = self.img_tk
    

    def update_names(self):
        self.names = None if self.stage == 1 else os.listdir(self.paths[self.stage - 2])
        

    ################################# Control Functions #################################
        
    def set_speed(self):
        self.timer.speed = int(self.spn_speed.get())


    def play_imshow(self):
        self.speed = int(self.spn_speed.get())
        self.timer.start()


    def pause_imshow(self):
        self.timer.stop()
        self.timer = RepeatedTimer(
            int(self.spn_speed.get()), lambda: self.display('next'))


    def next_stage(self):
        if self.stage < 3:
            self.from_stage = self.stage
            self.stage += 1
            self.update_stage()
        

    def previous_stage(self):
        if self.stage > 1:
            self.from_stage = self.stage
            self.stage -= 1
            self.update_stage()


    ################################# Display Function #################################

    def display(self, direction='current'):
        try:
            if direction == 'next':
                self.hole_number += 1
                if self.hole_number == len(self.names):
                    self.hole_number = 0

            elif direction == 'previous':
                if not self.timer.pause:
                    self.pause_imshow()

                self.hole_number -= 1
                if self.hole_number == -1:
                    self.hole_number = len(self.names) - 1

            self.update_img()
        except Exception as err:
            print(err)


    ################################# Component Function #################################

    def button(self, master, row=None, col=None, text=None, im_path=None, shape=None, function=None, **kwargs):
        try:
            if im_path is not None and shape is not None:
                self.btn_images.append(Image.open(im_path, 'r').resize(shape))
                self.btn_tk_images.append(ImageTk.PhotoImage(image=self.btn_images[-1]))

                btn = tk.Button(
                    master=master,
                    image=self.btn_tk_images[-1],
                    **kwargs
                )
            
            else:
                btn = tk.Button(
                    master=master,
                    text=text if text is not None else "",
                    **kwargs
                )

            if function is not None:
                btn["command"]=function
            
            if row is not None and col is not None:
                btn.grid(row=row, column=col)
                self.ims_btns.append(btn)

            else: self.imc_btns.append(btn)

            return btn
        
        except Exception as err:
            print(err)
            