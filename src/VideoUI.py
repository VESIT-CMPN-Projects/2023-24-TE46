from threading import Thread
from PIL import Image, ImageTk
import os
import time
import tkinter as tk


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
    def __init__(self, rel, paths):
        super().__init__()
        
        # Setting data and parameters
        self.timer = RepeatedTimer(1, lambda: self.display('next'))
        
        # Getting files and values
        self.relpath = os.path.abspath(os.path.relpath(rel))
        self.paths = [os.path.join(self.relpath, path) for path in paths]
        
        self.hole_number = 0
        self.stage = 2
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
            padx=10, pady=6, width=300, height=400
        )
        self.lbl_image.grid(row=1)


        ########################## FIRST DISPLAY ##########################

        self.display()


        ########################## STAGE CONTROLS ##########################

        self.btn_images, self.btn_tk_images, self.btns = [], [], []
        btn_image_paths = ['back.png', 'next.png', 'play.png', 'pause.png']
        btn_image_paths = [os.path.join(os.path.abspath(os.path.relpath('resources')), file) for file in btn_image_paths]

        # Go to previous stage
        self.button(master=self.frame_stage_controls, row=0, col=0, im_path=btn_image_paths[0], shape=(25, 25), function=self.prev_stage)

        # Go to next stage
        self.button(master=self.frame_stage_controls, row=0, col=3, im_path=btn_image_paths[1], shape=(25, 25), function=self.next_stage)


        ########################## IMAGE CONTROLS ##########################

        # Button that shows the previously shown image
        self.button(master=self.frame_im_controls, row=0, col=0, im_path=btn_image_paths[0], shape=(25, 25), function=lambda: self.display('previous'), relief=tk.GROOVE, borderwidth=2, padx=5, pady=3.5)

        # Button that shows the next image on the disk
        self.button(master=self.frame_im_controls, row=0, col=2, im_path=btn_image_paths[1], shape=(25, 25), function=lambda: self.display('next'), relief=tk.GROOVE, borderwidth=2, padx=5, pady=3.5)

        # Button that starts the slideshow
        self.button(master=self.frame_im_controls, row=0, col=3, im_path=btn_image_paths[2], shape=(25, 25), function=self.play_imshow, relief=tk.GROOVE, borderwidth=2, padx=5, pady=3.5)

        # Button that pauses the slideshow
        self.button(master=self.frame_im_controls, row=0, col=4, im_path=btn_image_paths[3], shape=(25, 25), function=self.pause_imshow, relief=tk.GROOVE, borderwidth=2, padx=5, pady=3.5)

        # Spinner that helps control the speed of the slideshow
        self.spn_speed = tk.Spinbox(
            master=self.frame_im_controls, from_=1, to=4, command=self.set_speed
        )
        self.spn_speed.grid(row=0, column=1)


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


    def button(self, master, row, col, text=None, im_path=None, shape=None, function=None, **kwargs):
        try:
            if im_path is not None and shape is not None:
                self.btn_images.append(Image.open(im_path, 'r').resize(shape))
                self.btn_tk_images.append(ImageTk.PhotoImage(image=self.btn_images[-1]))

                self.btns.append(tk.Button(
                    master=master,
                    image=self.btn_tk_images[-1],
                    **kwargs
                ))
            
            else:
                self.btns.append(tk.Button(
                    master=master,
                    text=text if text is not None else "",
                    **kwargs
                ))

            if function is not None:
                self.btns[-1]["command"]=function

            self.btns[-1].grid(row=row, column=col)

            return self.btns[-1]
        
        except Exception as err:
            print(err)
        
    
    
    def next_stage(self):
        if self.stage < 3:
            self.stage += 1
            self.update_stage()
        

    def prev_stage(self):
        # TODO: Make the stage 1 GUI and reduce the limit to 1
        if self.stage > 2:
            self.stage -= 1
            self.update_stage()


    def update_stage(self):
        self.update_names()
        self.lbl_stage['text'] = f'Stage {self.stage}'
        self.update_img()


    def update_img(self):
        path = os.path.join(self.paths[self.stage - 1], self.names[self.hole_number])
        self.img = Image.open(path, 'r').resize((300, 400))
        self.img_tk = ImageTk.PhotoImage(image=self.img)
        
        self.lbl_image['image'] = self.img_tk
        

    def set_speed(self):
        self.timer.speed = int(self.spn_speed.get())


    def update_names(self):
        self.names = os.listdir(self.paths[self.stage - 1])


    def play_imshow(self):
        self.speed = int(self.spn_speed.get())
        self.timer.start()


    def pause_imshow(self):
        self.timer.stop()
        self.timer = RepeatedTimer(
            int(self.spn_speed.get()), lambda: self.display('next'))



if __name__ == '__main__':
    rel_dir = "outs"
    # paths = ['images', 'FE_001', 'FE_001--S']
    paths = ['images', 'Conventionally_named_holes', 'Conventionally_named_holes_ctrs']

    app = App(rel_dir, paths)
    app.mainloop()
