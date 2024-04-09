## MODULES ##
import os
import tkinter as tk
from tkinter import filedialog
from ttkbootstrap.toast import ToastNotification
from threading import Thread
import tkthread

import cv2
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
        self.applied_rotation = 0
        self.orientation = True  # vertical

        # Setting default folders and values
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
        self.frame_im_controls.grid(row=1, column=1)

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

        # Label for selecting image via dropdown
        self.lbl_select_img = tk.Label(
            master=self.frame_im_controls, text="Select Image", padx=5, pady=3.5
        )

        # Label for orientation radio button
        self.lbl_orient = tk.Label(
            master=self.frame_im_controls, text="Orientation", padx=5, pady=3.5
        )

        # Label for browing resource path radio button
        self.lbl_resource = tk.Label(
            master=self.frame_im_controls, text="Resource Path", padx=5, pady=3.5
        )
        
        # Label for browing output path radio button
        self.lbl_out = tk.Label(
            master=self.frame_im_controls, text="Output Path",  padx=5, pady=3.5
        )
        
        self.lbl_list = [self.lbl_select_img, self.lbl_orient, self.lbl_resource, self.lbl_out]

        ########################## STAGE CONTROLS ##########################

        self.btn_images, self.btn_tk_images, self.toggles, self.imc_btns, self.ims_btns, self.dir_setters = [], [], [], [], [], []
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
        
        ########################## VARIABLES ##########################

        # Variables for the Radio Button
        self.current_value = tk.IntVar(value=1)
        self.current_value.trace_add(mode="write", callback=self.set_speed)
        self.orient_var = tk.StringVar(self.frame_im_controls, value="horizontal")

        # Variables for Browsing Paths
        self.var_resources = tk.StringVar(self.frame_im_controls, value="./" + str(self.resources) + '/')
        self.var_outs = tk.StringVar(self.frame_im_controls, value="./" + str(self.outs) + '/')
        self.var_main_img_path = tk.StringVar(self.frame_images)

        ########################## OTHER CONTROLS ##########################

        # Spinner that helps control the speed of the slideshow
        self.spn_speed = tk.Entry(master=self.frame_im_controls, textvariable=self.current_value)

        # Radio buttons for Orientation
        self.rb_orient_horizontal = tk.Radiobutton(master=self.frame_im_controls, text="Horizontal", variable=self.orient_var, 
                       value="horizontal", command=self.update_orientation)

        self.rb_orient_vertical = tk.Radiobutton(master=self.frame_im_controls, text="Vertical", variable=self.orient_var, 
                       value="vertical", command=self.update_orientation)

        # Resource path Entry Field
        self.entry_resources = tk.Entry(master=self.frame_im_controls, textvariable=self.var_resources, width=25)

        # Output path Entry Field
        self.entry_outs = tk.Entry(master=self.frame_im_controls, textvariable=self.var_outs, width=25)
        
        self.entry_list = [self.entry_resources, self.entry_outs]

        self.dir_setters = []
        
        # Button that allows rotation of image by 90
        self.button(master=self.frame_im_controls, text="Rotate by 90°", row=0, col=3, shape=(25, 25), function=self.toggle_rotation,
                     btn_list=self.dir_setters, relief=tk.GROOVE, borderwidth=2, padx=5, pady=3.5)
        
        # Button that allows browsing the filesystem for images
        self.button(master=self.frame_im_controls, text="Browse", row=4, col=3, shape=(25, 25), function=self.get_resource_dir,
                     btn_list=self.dir_setters, relief=tk.GROOVE, borderwidth=2, padx=5, pady=3.5)
        
        # Button that allows browsing the output folder for images
        self.button(master=self.frame_im_controls, text="Browse", row=5, col=3, shape=(25, 25), function=self.get_output_dir,
                     btn_list=self.dir_setters, relief=tk.GROOVE, borderwidth=2, padx=5, pady=3.5)

        # Getting all the images for hole extraction -- creating dropdown list
        self.dropdown = None
        self.var_main_img_path.trace_add("write", self.update_img)
        self.update_resources()

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
            # Creating folder to store the Thumbnails for the Images if it doesn't exists
            if not os.path.exists(os.path.abspath(os.path.relpath(".thumbnails"))):
                os.mkdir(os.path.abspath(os.path.relpath(".thumbnails")))
            
            # Paths to the Original Image and it's Thumbnail
            im_path = self.var_main_img_path.get()
            abs_path = os.path.join(os.path.abspath(os.path.relpath(self.resources)), im_path)
            thumbnail_path = os.path.join(os.path.abspath(os.path.relpath(".thumbnails")), im_path)

            # Using Thumbnail if it exists
            if os.path.exists(thumbnail_path):
                # self.main_im = Image.open(thumbnail_path)

                # TODO: get the image from real path iff thumbnail is outdated
                self.main_im = Image.open(abs_path, mode="r")
                self.main_im.thumbnail((340, 468), resample=Image.Resampling.BICUBIC)
                self.main_im.save(thumbnail_path)

            # Else creating Thumbnail
            else:
                self.main_im = Image.open(abs_path, mode="r")
                self.main_im.thumbnail((340, 468), resample=Image.Resampling.BICUBIC)
                self.main_im.save(thumbnail_path)

            # Updating the image in the label
            self.main_tk_im = ImageTk.PhotoImage(image=self.main_im)
            self.lbl_image["image"] = self.main_tk_im

        # Updating image for stages other than stage1
        else:
            
            if len(self.names) == 0:
                # If names list is empty, displaying the default image
                path = os.path.join(os.path.abspath(os.path.relpath('resources')), 'default.png')

            else:
                # Else displaying the image at current hole_number
                path = os.path.join(self.paths[self.stage - 2], self.names[self.hole_number - 1])

            # Loading the image to the label
            self.img = Image.open(path, 'r')
            self.img.thumbnail((300, 400))
            self.img_tk = ImageTk.PhotoImage(image=self.img)
            self.lbl_image['image'] = self.img_tk

    
    def update_orientation(self):
            """Update the orientation boolean as per user's choice"""

            self.orientation = self.orient_var.get() == "horizontal"


    def update_resources(self):
            """ Function to update the dropdown options in stage1 """

            # Getting the options for the dropdown
            options = np.array(os.listdir(os.path.abspath(os.path.relpath(self.resources))))
            options = [option for option in options if (option.endswith('.jpg') or option.endswith('.png') or option.endswith('.jpeg')) and option != 'default.png']

            if len(options) != 0:
                self.var_main_img_path.set(options[0])

                # Options for the images to pick from
                if self.dropdown != None:
                    self.dropdown.destroy()
                    self.display()

                self.dropdown = tk.OptionMenu(self.frame_im_controls, self.var_main_img_path, *options)
                self.dropdown.grid(row=0, column=1)


    ################################# Change Stage Functions #################################

    def from_stage1(self):
        """ Function to update the controls of the ML app while going from stage 1 to stage 2 """

        # Setting initial hole number
        self.hole_number = 1

        # Forgetting the stage 1 controls
        self.dropdown.grid_forget()
        grid_widgets = self.frame_im_controls.grid_slaves()
        for widget in grid_widgets:
            widget.grid_forget()

        # Placing the stage 2 controls
        self.frame_im_controls.grid(row=2, column=0)
        self.spn_speed.grid(row=0, column=1)
        [btn.grid(row=0, column=index if index == 0 else index + 1) for (index, btn) in enumerate(self.imc_btns)]

        # Adjusting image size for stage 2 images
        self.lbl_image["width"] = 300
        self.lbl_image["height"] = 400

        # Setting the paths for output
        im_path = self.var_main_img_path.get()
        self.relpath = os.path.abspath(os.path.relpath(self.outs))
        self.paths = [os.path.join(self.relpath, im_path.split('.')[0]),
                    os.path.join(self.relpath, im_path.split('.')[0] + '--S')]

        # Checking for existence of cropped holes
        cropped_holes_check = os.path.exists(self.paths[0])
        cropped_holes_count = len(os.listdir(self.paths[0])) if cropped_holes_check else 0

        # Checking for existence of processed holes
        processed_holes_check = os.path.exists(self.paths[1])
        processed_holes_count = len(os.listdir(self.paths[1])) if processed_holes_check else 0

        if cropped_holes_count == 92 and processed_holes_count == 92:
            # Displaying dialog box if all the cropped holes and processed holes are present
            self.display_dialog_box(self.start_process)

        else:
            # Else creating new folders for cropped holes and processed holes if not created
            if not cropped_holes_check:
                os.mkdir(self.paths[0])

            if not processed_holes_check:
                os.mkdir(self.paths[1])

            self.start_process()


    def to_stage1(self):
        """ Function to update the controls of the ML app while going back from stage 2 to stage 1 """

        # Forgetting stage2 controls
        self.spn_speed.grid_forget()
        [btn.grid_forget() for btn in self.imc_btns]

        # Placing the stage1 controls
        self.frame_im_controls.grid(row=1, column=1)
        self.dropdown.grid(row=0, column=1)
        [btn.grid(row=index + 1 if index != 0 else 0, column=2) for (index, btn) in enumerate(self.dir_setters)]
        [label.grid(row=index, column=0) for (index, label) in enumerate(self.lbl_list)]
        self.rb_orient_horizontal.grid(row=1, column=1)
        self.rb_orient_vertical.grid(row=1, column=2)
        [entry.grid(row=2 + index, column=1) for (index, entry) in enumerate(self.entry_list)]

        # Adjusting image size for stage1
        self.lbl_image["width"] = 340
        self.lbl_image["height"] = 468

        # Pausing the im_show and resetting the starting hole_number
        self.pause_imshow()
        self.hole_number = 0


    ################################# Control Functions #################################

    def set_speed(self, *args):
        """ Function to set the speed for image playback """

        try:
            if self.current_value.get() != "":
                self.retimer.speed = int(self.current_value.get())
        except:
            pass


    def play_imshow(self):
        """ Function to start the image playback """

        self.speed = int(self.current_value.get())
        self.retimer.start()


    def pause_imshow(self):
        """ Function to pause the image playback """

        self.retimer.stop()
        self.retimer = RepeatedTimer(
            int(self.current_value.get()), lambda: self.display('next'))


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


    ################################# Display Function #################################

    def display(self, direction='current'):
        """ Function to display images in the image label """

        # Udating names
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
    
    
    def display_dialog_box(self, callback):
        """Function to display a top-level consent requesting dialog box"""

        ## HELPER FUNCTIONS ##
        def process():
            callback()
            win.destroy()

        # Setting the GUI for the dialog box
        win = tk.Toplevel(height=300, width=100)
        win.title('Confirmation')
        tk.Label(win, text="Do you want to run the model?").grid(row=0, column=0, columnspan=2, padx=10, pady=5)
        tk.Button(win, text='Run', command=process).grid(row=1, column=0,  padx=10, pady=5)
        tk.Button(win, text='Cancel', command=win.destroy).grid(row=1, column=1,  padx=10, pady=5)
    

    def show_toast_message(self, msg_num):
        """Function to show the toast messages"""

        if msg_num == 1:
            self.ext_end_toast.show_toast()
        else:
            self.det_end_toast.show_toast()


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


    ################################# Toggles #################################

    def toggle_rotation(self):
        """ Function to toggle the rotation of the image by -90deg """

        self.applied_rotation = (self.applied_rotation + 90) % 360
        self.main_im = Image.fromarray(cv2.rotate(np.array(self.main_im), cv2.ROTATE_90_CLOCKWISE))
        self.main_tk_im = ImageTk.PhotoImage(image=self.main_im)
        self.lbl_image["image"] = self.main_tk_im


    ################################# Path Function #################################

    def get_resource_dir(self):
        """Function to get the resource directory"""

        temp_path = self.resources
        try:
            self.resources = filedialog.askdirectory(initialdir=self.var_resources.get())
            self.update_resources()
        except Exception as err:
            self.resources = temp_path
            print(err)
        
        self.var_resources.set(self.resources)


    def get_output_dir(self):
        """Function to get the output directory"""

        temp_path = self.outs
        try:
            self.outs = filedialog.askdirectory(initialdir=self.var_outs.get())
        except Exception as err:
            self.outs = temp_path
            print(err)

        self.var_outs.set(self.outs)

    ################################# ML Call Function #################################
        
    def start_process(self):
        """Function to start processing of the board"""

        # Getting the name for the image selected for processing
        im_path = self.var_main_img_path.get()

        # Starting the processing of board in a separate thread
        thread = Thread(target=self.process_board, args=(
            self.resources, im_path, self.outs, [im_path.split('.')[0], im_path.split('.')[0] + '--S'], self.model_path,
            self.conf, self.applied_rotation))
        thread.setDaemon(True)
        thread.start()


    def process_board(self, *args):
        """Function to process the board"""

        # Storing the variables here to avoid race conditions with main thread
        # With these set here, user can start ML process on multiple images at once
        resources = args[0]
        im_path = args[1]
        outs = os.path.abspath(os.path.relpath(args[2]))
        paths = args[3]
        model_path = os.path.relpath(args[4])
        conf = args[5]
        rotation = args[6]

        # Importing the image
        img = Image.open(os.path.join(os.path.abspath(os.path.relpath(resources)), im_path))

        # Creating objects for required ML classes
        exporter = Exporter(outs, paths)
        extractor = Extracter(exporter)
        detector = Detector(exporter, model_path, conf)

        # # Getting DPI for the image from exif
        # exif = {
        #     ExifTags.TAGS[k]: v
        #     for k, v in img._getexif().items()
        #     if k in ExifTags.TAGS
        # }
        # DPI = int(exif['XResolution'])  # Take X Resolution as DPI. X resolution is generally lower than Y in scanners
        DPI=1200
        print(f"Image DPI: {DPI}")
        
        img = np.array(img)

        # Converting img from being rgb to bgr
        img = np.flip(img, axis=-1)

        # Adjusting rotation for the main image
        if rotation == 90:
            img = cv2.rotate(img, cv2.ROTATE_90_CLOCKWISE)
        elif rotation == 180:
            img = cv2.rotate(img, cv2.ROTATE_180)
        elif rotation == 270:
            img = cv2.rotate(img, cv2.ROTATE_90_COUNTERCLOCKWISE)

        # Using vertical detection for the image orientation is set to true
        if not self.orientation:
            holes = detector.get_holes_fv(img, DPI)
        else:
            holes = detector.get_holes(img, DPI)

        # Annotating all the holes obtained to the original image
        _ = exporter.annotate_holes(img, holes, DPI)
        extractor.extract_holes(img, holes, DPI, path=paths[0])

        # Updating the names and img to update GUI in stages other than stage1
        if self.stage == 2 or self.stage == 3:
            tkthread.call_nosync(lambda: self.show_toast_message(1))
            self.update_names()
            self.update_img()

        # getting the detection results for signal pads from detector
        detection_results, data_offset = detector.start_detections(DPI)
        tkthread.call_nosync(lambda: self.show_toast_message(2))

        # exporting the offsets.csv
        data_offset_full, _ = exporter.export_offsets(data_offset, holes, DPI)

        # exporting the strips.json
        exporter.export_strip_offsets(img, DPI, holes, data_offset_full, width=300)

        # exporting the strips.xlsx
        exporter.json_to_excel()

        # exporting the area.csv
        extractor.get_area(detection_results, DPI)

        # Exporting videos for stage2 and stage3 images
        exporter.get_vid(paths[0], "video.avi")
        exporter.get_vid(paths[1], "video--s.avi")
