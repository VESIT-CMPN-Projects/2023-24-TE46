## MODULES ##
import os
import tkinter as tk
from threading import Thread

import numpy as np
from PIL import Image, ImageTk, ExifTags

from detector import Detector
from exporter import Exporter
from extracter import Extracter
from preprocessor import Preprocessor

## CUSTOM MODULES ##
from retimer import RepeatedTimer


## AppGUI class ##
class AppGUI(tk.Tk):
    def __init__(self, rel1, rel2, model_path, conf=0.54):
        super().__init__()

        Image.MAX_IMAGE_PIXELS = None
        self.model_path = model_path
        self.conf = conf

        # Setting data and parameters
        self.retimer = RepeatedTimer(1, lambda: self.display('next'))
        self.crop = False
        self.rotate = False
        self.orientation = False  # horizontal

        # Getting files and values
        self.resources = rel1
        self.outs = rel2

        self.hole_number = 0
        self.stage = 1
        self.from_stage = 0
        self.update_names()

        # Setting the title for window
        self.title("VideoUI")

        # defining image preprocessor
        self.preprocessor = Preprocessor(os.path.abspath(os.path.relpath(self.outs)))

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

        self.btn_images, self.btn_tk_images, self.toggles, self.imc_btns, self.ims_btns = [], [], [], [], []
        btn_image_paths = ['back.png', 'next.png', 'play.png', 'pause.png']
        btn_image_paths = [os.path.join(os.path.abspath(os.path.relpath('buttons')), file) for file in btn_image_paths]

        # Go to previous stage
        self.button(master=self.frame_stage_controls, row=0, col=0, im_path=btn_image_paths[0], shape=(25, 25),
                    function=self.previous_stage)

        # Go to next stage
        self.button(master=self.frame_stage_controls, row=0, col=3, im_path=btn_image_paths[1], shape=(25, 25),
                    function=self.next_stage)

        ########################## IMAGE CONTROLS ##########################

        # Button that shows the previously shown image
        self.button(master=self.frame_im_controls, im_path=btn_image_paths[0], shape=(25, 25),
                    function=lambda: self.display('previous'), relief=tk.GROOVE, borderwidth=2, padx=5, pady=3.5)

        # Button that shows the next image on the disk
        self.button(master=self.frame_im_controls, im_path=btn_image_paths[1], shape=(25, 25),
                    function=lambda: self.display('next'), relief=tk.GROOVE, borderwidth=2, padx=5, pady=3.5)

        # Button that starts the slideshow
        self.button(master=self.frame_im_controls, im_path=btn_image_paths[2], shape=(25, 25),
                    function=self.play_imshow, relief=tk.GROOVE, borderwidth=2, padx=5, pady=3.5)

        # Button that pauses the slideshow
        self.button(master=self.frame_im_controls, im_path=btn_image_paths[3], shape=(25, 25),
                    function=self.pause_imshow, relief=tk.GROOVE, borderwidth=2, padx=5, pady=3.5)

        # Spinner that helps control the speed of the slideshow
        self.spn_speed = tk.Spinbox(
            master=self.frame_im_controls, from_=1, to=4, command=self.set_speed
        )

        # Getting all the images for hole extraction
        self.update_resources()

        # Options for the images to pick from
        self.dropdown = tk.OptionMenu(self.frame_im_controls, self.main_im_path, *self.choices)

        # Button that allows cropping of images
        self.button(master=self.frame_im_controls, text="Crop", shape=(25, 25), function=self.toggle_crop,
                    btn_list=self.toggles, relief=tk.GROOVE, borderwidth=2, padx=5, pady=3.5)

        # Button that allows rotation of images
        self.button(master=self.frame_im_controls, text="Rotate", shape=(25, 25), function=self.toggle_rotation,
                    btn_list=self.toggles, relief=tk.GROOVE, borderwidth=2, padx=5, pady=3.5)

        # Button that allows selecting orientation of images
        self.button(master=self.frame_im_controls, text="Vertical", shape=(25, 25), function=self.toggle_orientation,
                    btn_list=self.toggles, relief=tk.GROOVE, borderwidth=2, padx=5, pady=3.5)

        self.main_im_path.trace_add("write", self.update_img)

        self.update_controls()

        ########################## FIRST DISPLAY ##########################

        self.display()

    ################################# Update Functions #################################
        
    def update_stage(self):
        """ Function to update the GUI when the stage changes """

        self.update_controls()
        self.lbl_stage['text'] = f'Stage {self.stage}'
        self.update_names()
        self.update_img()


    def update_controls(self):
        """ Function to update the controls of the ML app """

        if self.stage == 1:
            self.to_stage1()
        elif self.from_stage == 1:
            self.from_stage1()
    
    
    def update_names(self):
        """ Function to update the names for cropped holes in stage2 in ML app """

        self.names = None if self.stage == 1 else os.listdir(self.paths[self.stage - 2])
        if self.names is not None: self.names.sort()
    

    def update_img(self, *args):
        """ Function to update the image for any stage in ML app """

        # Updating image for stage1
        if self.stage == 1:
            im_path = self.main_im_path.get()
            self.relpath = os.path.abspath(os.path.relpath(self.outs))
            self.paths = [os.path.join(self.relpath, im_path.split('.')[0]),
                          os.path.join(self.relpath, im_path.split('.')[0] + '--S')]

            # Creating folder to store the thumbnails for the images if it doesn't exists
            # if not os.path.exists(os.path.abspath(os.path.relpath(".thumbnails"))):
            #     os.mkdir(os.path.abspath(os.path.relpath(".thumbnails")))
            
            # Creating thumbnail
            abs_path = os.path.join(os.path.abspath(os.path.relpath(self.resources)), im_path)
            self.main_im = Image.open(abs_path, mode="r")
            self.main_im.thumbnail((340, 468), resample=Image.Resampling.BICUBIC)

            # Updating the image in the label
            self.main_tk_im = ImageTk.PhotoImage(image=self.main_im)
            self.lbl_image["image"] = self.main_tk_im

        # Updating image for stages other than stage1
        else:
            
            if len(self.names) == 0:
                # If names list is empty, displaying the default image
                path = os.path.join(os.path.abspath(os.path.relpath(self.resources)), 'default.png')

            else:
                # Else displaying the image at current hole_number
                path = os.path.join(self.paths[self.stage - 2], self.names[self.hole_number - 1])

            # Loading the image to the label
            self.img = Image.open(path, 'r')
            self.img.thumbnail((300, 400))
            self.img_tk = ImageTk.PhotoImage(image=self.img)
            self.lbl_image['image'] = self.img_tk


    def from_stage1(self):
        """ Function to update the controls of the ML app while going from stage 1 to stage 2 """

        # Setting initial hole number
        self.hole_number = 1

        # Forgetting the stage 1 controls
        self.dropdown.grid_forget()
        [btn.grid_forget() for btn in self.toggles]

        # Placing the stage 2 controls
        self.spn_speed.grid(row=0, column=1)
        [btn.grid(row=0, column=index if index == 0 else index + 1) for (index, btn) in enumerate(self.imc_btns)]

        # Adjusting image size for stage 2 images
        self.lbl_image["width"] = 300
        self.lbl_image["height"] = 400

        # Checking for existence of cropped holes
        cropped_holes_check = os.path.exists(self.paths[0])
        cropped_holes_count = len(os.listdir(self.paths[0])) if cropped_holes_check else 0

        # Checking for existence of processed holes
        processed_holes_check = os.path.exists(self.paths[1])
        processed_holes_count = len(os.listdir(self.paths[1])) if processed_holes_check else 0

        if cropped_holes_count == 92 and processed_holes_count == 92:
            # Displaying dialog box if all the cropped holes and processed holes are present
            # TODO: Dialog box
            pass

        else:
            # Else creating new folders for cropped holes and processed holes if not created
            if not cropped_holes_check:
                os.mkdir(self.paths[0])

            if not processed_holes_check:
                os.mkdir(self.paths[1])

        # Getting the name for the image selected for processing
        im_path = self.main_im_path.get()

        # Starting the processing of board in a separate thread
        thread = Thread(target=self.process_board, args=(
            self.resources, im_path, self.outs, [im_path.split('.')[0], im_path.split('.')[0] + '--S'], self.model_path,
            self.conf))
        thread.daemon = True
        thread.start()


    def to_stage1(self):
        """ Function to update the controls of the ML app while going back from stage 2 to stage 1 """

        # Forgetting stage2 controls
        self.spn_speed.grid_forget()
        [btn.grid_forget() for btn in self.imc_btns]

        # Placing the stage1 controls
        self.dropdown.grid(row=0, column=1)
        [btn.grid(row=0, column=index + 2) for (index, btn) in enumerate(self.toggles)]

        # Adjusting image size for stage1
        self.lbl_image["width"] = 340
        self.lbl_image["height"] = 468


    def update_resources(self):
        """ Function to update the dropdown choices in stage1 """

        self.choices = np.array(os.listdir(os.path.abspath(os.path.relpath(self.resources))))
        self.choices = [choice for choice in self.choices if (
                choice.endswith('.jpg') or choice.endswith('.png') or choice.endswith(
            '.jpeg')) and choice != 'default.png']
        self.main_im_path = tk.StringVar(self.frame_images)
        self.main_im_path.set(self.choices[0])

    ################################# Control Functions #################################

    def set_speed(self):
        """ Function to set the speed for image playback """

        self.retimer.speed = int(self.spn_speed.get())


    def play_imshow(self):
        """ Function to start the image playback """

        self.speed = int(self.spn_speed.get())
        self.retimer.start()


    def pause_imshow(self):
        """ Function to pause the image playback """

        self.retimer.stop()
        self.retimer = RepeatedTimer(
            int(self.spn_speed.get()), lambda: self.display('next'))


    def next_stage(self):
        """ Function to load the next stage """

        if self.stage < 3:
            self.from_stage = self.stage
            self.stage += 1
            self.update_stage()


    def previous_stage(self):
        """ Function to load the previous stage """

        if self.stage > 1:
            self.from_stage = self.stage
            self.stage -= 1
            self.update_stage()

    ################################# Toggles #################################

    def toggle_crop(self):
        """ Function to toggle the cropping of the image """

        self.crop = not self.crop
        self.toggles[-3]['bg'] = 'black' if self.crop else 'white'
        self.toggles[-3]['fg'] = 'white' if self.crop else 'black'
        print("Crop: ", self.crop, self.toggles[-1]['bg'])


    def toggle_rotation(self):
        """ Function to toggle the rotation of the image """

        self.rotate = not self.rotate
        self.toggles[-2].configure(bg='black' if self.rotate else 'white')
        self.toggles[-2].configure(fg='white' if self.rotate else 'black')
        print("Rotation: ", self.rotate, self.toggles[-1]['bg'])


    def toggle_orientation(self):
        """ Function to toggle the orientation of the image """

        self.orientation = not self.orientation
        self.toggles[-1].configure(bg='black' if self.orientation else 'white')
        self.toggles[-1].configure(fg='white' if self.orientation else 'black')
        print("Orientation: ", self.orientation, self.toggles[-1]['bg'])

    ################################# Display Function #################################

    def display(self, direction='current'):
        """ Function to display images in the image label """

        # Udating names
        if self.names is not None:
            self.update_names()

        try:

            # Updating image
            if self.names is not None and len(self.names) != 0:
                if direction == 'next':
                    self.hole_number += 1
                    if self.hole_number == len(self.names):
                        self.hole_number = 0

                elif direction == 'previous':
                    if not self.retimer.pause:
                        self.pause_imshow()

                    self.hole_number -= 1
                    if self.hole_number == -1:
                        self.hole_number = len(self.names) - 1

            self.update_img()
        except Exception as err:
            print(err)

    ################################# Component Function #################################

    def button(self, master, row=None, col=None, text=None, im_path=None, shape=None, function=None, btn_list=None,
               **kwargs):
        """ Function to create buttons """

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
                btn["command"] = function

            if btn_list is not None:
                btn_list.append(btn)

            elif row is not None and col is not None:
                btn.grid(row=row, column=col)
                self.ims_btns.append(btn)

            else:
                self.imc_btns.append(btn)

            return btn

        except Exception as err:
            print(err)

    ################################# ML Call Function #################################

    def process_board(self, *args):

        # Storing the variables here to avoid race conditions with main thread
        # With these set here, user can start ML process on multiple images at once
        resources = args[0]
        im_path = args[1]
        outs = os.path.abspath(os.path.relpath(args[2]))
        paths = args[3]
        model_path = os.path.relpath(args[4])
        conf = args[5]

        # Importing the image
        img = Image.open(os.path.join(os.path.abspath(os.path.relpath(resources)), im_path))

        # Creating objects for required ML classes
        exporter = Exporter(outs, paths)
        extractor = Extracter(exporter)
        detector = Detector(exporter, model_path, conf)

        # Getting DPI for the image from exif
        # exif = {
        #     ExifTags.TAGS[k]: v
        #     for k, v in img._getexif().items()
        #     if k in ExifTags.TAGS
        # }
        # print(exif)
        print(img.info.get('DPI'))
        # DPI = int(exif['XResolution'])  # Take X Resolution as DPI. X resolution is generally lower than Y in scanners
        DPI = 3200
        print("Image DPI is: ", DPI)
        img = np.array(img)

        # Converting img from being rgb to bgr
        img = np.flip(img, axis=-1)

        # Cropping the image if set to true
        if self.crop:
            img = self.preprocessor.focus_board(img, DPI)

        # Rotating the image if set to true
        if self.rotate:
            img = self.preprocessor.rotate_image(img, DPI)

        # Using vertical detection for the image orientation is set to true
        if self.orientation:
            holes = detector.get_holes_fv(img, DPI)
        else:
            holes = detector.get_holes(img, DPI)

        # Annotating all the holes obtained to the original image
        _ = exporter.annotate_holes(img, holes, DPI)
        extractor.extract(img, holes, DPI, path=paths[0])

        # Updatingg the names and img to update GUI in stages other than stage1
        if self.stage == 2 or self.stage == 3:
            self.update_names()
            self.update_img()

        # getting the detection results for signal pads from detector
        detection_results, data_offset = detector.start_detections(DPI)

        # exporting the offsets.csv
        data_offset_full, _ = exporter.export_offsets(data_offset, holes, DPI)

        # exporting the strips.json
        exporter.export_strip_offsets(img, DPI, holes, data_offset_full, width=300)

        # exporting the strips.xlsx
        exporter.json_to_excel()

        # with open("holes.json", mode='w') as out_file:
        #     holes_new = []
        #     for hole in holes:
        #         holes_new.append(list(hole))
        #     out_file.write(json.dumps(holes_new))

        # exporting the area.csv
        extractor.get_area(detection_results, DPI)

        # Exporting videos for stage2 and stage3 images
        exporter.get_vid(paths[0], "video.avi")
        exporter.get_vid(paths[1], "video--s.avi")
