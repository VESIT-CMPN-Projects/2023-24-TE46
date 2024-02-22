import io
import os
import tkinter as tk
import tkinter.font as tkFont
from datetime import datetime
from tkinter import filedialog, scrolledtext

import piexif
import sane
from PIL import Image, ImageTk

from app_gui import AppGUI
from window_size import WinSize


class ScanningApp:
    def __init__(self, root, rel1, rel2, w_size):
        """
        Constructor for Scanning App
        :param root: tk window
        :param rel1: Name of default resources folder
        :param rel2: Name of default outputs folder
        :param w_size: window size selection based on screen size
        """
        self.root = root
        self.w_size = w_size
        self.resources = rel1
        self.outs = rel2
        self.sharpness_var = 1
        self.brightness_var = 1
        self.default_scan_res = 3200
        self.font_size = 12
        self.root.title("Scanner App")
        self.root.geometry("%dx%d" % (w_size.scan_window[0], w_size.scan_window[1]))
        self.connection_status = "UNCONNECTED"
        self.scanner_status = "UNKNOWN"
        self.last_scanned_add = None
        self.outs = os.path.abspath(os.path.relpath(rel2))

        # Initialize image path variable
        self.image_path_var = tk.StringVar(root, value="preview.jpg")
        template_path = "pretemplate.png"
        template_path = os.path.join(os.path.abspath(os.path.relpath('buttons')), template_path)
        self.connection_paths = ['connected.png', 'disconnected.png', 'connecting.png']
        self.connection_paths = [os.path.join(os.path.abspath(os.path.relpath('buttons')), file) for file in
                                 self.connection_paths]
        self.scanner_logo_paths = ['scanner-unconnected.png', 'scanner-idle.png', 'scanner-busy.png']
        self.scanner_logo_paths = [os.path.join(os.path.abspath(os.path.relpath('buttons')), file) for file in
                                   self.scanner_logo_paths]

        # 1. Big Image Preview field
        self.preview_image = tk.Label(root, text="Preview Image")
        self.preview_image.grid(row=0, column=0, rowspan=14, padx=10, pady=10, sticky=tk.W)
        img = Image.open(template_path)
        img.thumbnail((617, 870))
        # Convert the PIL Image to Tkinter PhotoImage
        tk_image = ImageTk.PhotoImage(img)
        self.preview_image.config(image=tk_image)
        self.preview_image.image = tk_image

        # 2. "Connect Scanner" Button and Label and Logo
        self.connect_scanner_button = tk.Button(root, text="Connect\nScanner", command=self.connect_scanner, height=2,
                                                font=("Helvetica", self.font_size))
        self.connect_scanner_button.grid(row=0, column=1, pady=5, sticky=tk.W)
        self.update_connection_logo()

        # 3. Button for Fetching Preview and scanner status logo
        self.fetch_button = tk.Button(root, text="Get Preview", command=self.fetch_preview, state="disabled",
                                      font=("Helvetica", self.font_size))
        self.fetch_button.grid(row=1, column=1, pady=10, sticky=tk.W)
        self.update_scanner_logo()

        # 4. Dropdown menu for Set Resolution
        resolutions = [300, 600, 1200, 1600, 2400, 3200]
        self.resolution_var = tk.StringVar(root)
        self.resolution_var.set(self.default_scan_res)  # default value
        self.resolution_menu = tk.OptionMenu(root, self.resolution_var, *resolutions)
        self.resolution_menu.config(font=tkFont.Font(family='Helvetica', size=self.font_size))
        tk.Label(root, text="Set Resolution", font=("Helvetica", self.font_size)).grid(row=2, column=1, pady=0,
                                                                                       sticky=tk.W)
        self.resolution_menu.grid(row=2, column=2, pady=1, sticky=tk.W)
        self.resolution_menu.config(state="disabled")

        # 5. 4 text input fields for scan area
        self.tl_x_var = tk.StringVar(root, value="10")
        self.tl_y_var = tk.StringVar(root, value="10")
        self.br_x_var = tk.StringVar(root, value="220")
        self.br_y_var = tk.StringVar(root, value="190")

        tk.Label(root, text="Top Left \t\tx", font=("Helvetica", self.font_size)).grid(row=4, column=1, pady=5,
                                                                                       sticky=tk.W)
        self.tl_x_entry = tk.Entry(root, textvariable=self.tl_x_var, width=5, state="disabled",
                                   font=("Helvetica", self.font_size))
        self.tl_x_entry.grid(row=4, column=2, pady=1, sticky=tk.W)
        # tk.Entry(root, textvariable=self.tl_x_var, width=5, state="disabled").grid(row=4, column=2, pady=5, sticky=tk.W)
        tk.Label(root, text="y", anchor=tk.W, font=("Helvetica", self.font_size)).grid(row=4, column=3, pady=5,
                                                                                       sticky=tk.E)
        self.tl_y_entry = tk.Entry(root, textvariable=self.tl_y_var, width=5, state="disabled",
                                   font=("Helvetica", self.font_size))
        self.tl_y_entry.grid(row=4, column=4, pady=1, sticky=tk.W)
        # tk.Entry(root, textvariable=self.tl_y_var, width=5, state="disabled").grid(row=4, column=4, pady=5, sticky=tk.W)

        tk.Label(root, text="Bottom Right \tx", font=("Helvetica", self.font_size)).grid(row=5, column=1, pady=5,
                                                                                         sticky=tk.W)
        self.br_x_entry = tk.Entry(root, textvariable=self.br_x_var, width=5, state="disabled",
                                   font=("Helvetica", self.font_size))
        self.br_x_entry.grid(row=5, column=2, pady=1, sticky=tk.W)
        # tk.Entry(root, textvariable=self.br_x_var, width=5, state="disabled").grid(row=5, column=2, pady=5, sticky=tk.W)
        tk.Label(root, text="y", anchor=tk.W, font=("Helvetica", self.font_size)).grid(row=5, column=3, pady=5,
                                                                                       sticky=tk.E)
        self.br_y_entry = tk.Entry(root, textvariable=self.br_y_var, width=5, state="disabled",
                                   font=("Helvetica", self.font_size))
        self.br_y_entry.grid(row=5, column=4, pady=1, sticky=tk.W)
        # tk.Entry(root, textvariable=self.br_y_var, width=5, state="disabled").grid(row=5, column=4, pady=5, sticky=tk.W)

        # 6. File Save location
        self.file_save_label = tk.Label(root, text="File Save Path", font=("Helvetica", self.font_size))
        self.file_save_label.grid(row=6, column=1, pady=5, sticky=tk.W)
        self.file_save_var = tk.StringVar(root, value="./" + str(self.resources) + '/')
        self.file_save_entry = tk.Entry(root, textvariable=self.file_save_var, width=19, state="disabled",
                                        font=("Helvetica", self.font_size))
        self.file_save_entry.grid(row=6, column=2, pady=5, columnspan=2, sticky=tk.W)
        tk.Button(root, text="Browse", command=self.browse_file_save_location, font=("Helvetica", self.font_size)).grid(
            row=6, column=4, pady=5,
            sticky=tk.W)

        # 7. File Name Entry and Dropdown for File Format
        initial_file_name = datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
        self.file_name_var = tk.StringVar(root, value=initial_file_name)
        file_formats = [".jpeg", ".png"]
        self.file_format_var = tk.StringVar(root)
        self.file_format_var.set(file_formats[0])  # default value
        self.file_format_menu = tk.OptionMenu(root, self.file_format_var, *file_formats)
        self.file_format_menu.config(font=tkFont.Font(family='Helvetica', size=self.font_size))
        tk.Label(root, text="File Name", font=("Helvetica", self.font_size)).grid(row=8, column=1, pady=5, sticky=tk.W)
        self.file_name_field = tk.Entry(root, textvariable=self.file_name_var, width=19, state="disabled",
                                        font=("Helvetica", self.font_size))
        self.file_name_field.grid(row=8, column=2, pady=5, columnspan=2, sticky=tk.W)
        # tk.Entry(root, textvariable=self.file_name_var, width=15, state="disabled").grid(row=8, column=2, pady=5,
        #                                                                                 sticky=tk.W)
        self.file_format_menu.grid(row=8, column=4, columnspan=2, pady=5, sticky=tk.W)
        self.file_format_menu.config(state="disabled")

        # 8. Buttons for Scan Now and Switching to ML
        self.scan_button = tk.Button(root, text="Scan\nNow", command=self.scan_now, width=6, height=2, state="disabled",
                                     font=("Helvetica", self.font_size))
        self.scan_button.grid(row=9, column=2, pady=10, sticky=tk.W)
        # tk.Button(root, text="Scan\nNow", command=self.scan_now, height=2, state="normal").grid(row=9, column=2,
        #                                                                                          pady=10, sticky=tk.W)
        tk.Button(root, text="Perform\nML", command=self.next_stage, height=2, state="normal",
                  font=("Helvetica", self.font_size)).grid(row=9, column=4,
                                                           pady=10,
                                                           sticky=tk.W)

        # 9. Button for Quit Scanner
        tk.Button(root, text="Back", command=self.quit_scanner, height=2, font=("Helvetica", self.font_size)).grid(
            row=9, column=1, pady=10,
            sticky=tk.W)

        # 10. Log Window
        self.log_text = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=50, height=28)
        self.log_text.grid(row=10, column=1, pady=10, columnspan=5, sticky=tk.SE)
        # self.log_text.pack(fill="both", expand=True)

    def browse_file_save_location(self):
        directory = filedialog.askdirectory(initialdir="./" + str(self.resources) + '/',
                                            title="Select File Save Directory")
        if directory:
            self.file_save_var.set(directory + '/')

    def fetch_preview(self):
        # Get a low resoulution(300 dpi) scan of entire scanbed

        # Get the image path from the variable
        image_path = self.image_path_var.get()

        # try:
        self.scanner_status = "BUSY"
        self.update_scanner_logo()
        self.log_text.insert(tk.END, "\nFetching a low resolution(300 dpi) preview scan of entire scan bed\n")
        # self.log_text.config(state="disabled")
        self.resolution_var.set(300)
        self.root.update()

        # Open the image using PIL
        self.s_dev.resolution = 300
        self.s_dev.tl_x = 0
        self.s_dev.tl_y = 0
        self.s_dev.br_x = 236  # Dimensions of an A4 sheet
        self.s_dev.br_y = 298  # Dimensions of an A4 sheet
        self.s_dev.start()
        self.img_pil = self.s_dev.snap()
        self.img_exif = self.gen_exif_bytes(self.img_pil)
        self.img_pil.save("preview.jpg", quality=88, exif=self.img_exif)
        img = Image.open(image_path)
        print(img.width, img.height)
        img.thumbnail((617, 870))
        # Convert the PIL Image to Tkinter PhotoImage
        tk_image = ImageTk.PhotoImage(img)

        # Update the preview label with the loaded image
        self.preview_image.config(image=tk_image)
        self.preview_image.image = tk_image
        self.scanner_status = "IDLE"
        self.update_scanner_logo()
        self.resolution_var.set(self.default_scan_res)
        self.log_text.insert(tk.END, "Preview Scan finished!\n")

        # Dynamically resize the window based on the image size
        new_width = img.width + 460  # Add some padding
        new_height = img.height + 30  # Add some padding
        self.root.geometry(f"{new_width}x{new_height}")

        # except Exception as e:
        #    print(f"Error loading image: {e}")

    def quit_scanner(self):
        # Disconnect sane port if it exists and Exit
        try:
            try:
                self.s_dev.close()
            except:
                print("No sane port open to close")
            sane.exit()
            self.root.destroy()
            print("Scanner Disconnected and App Closed")

        except:
            print("Error in Disconnecting Scanner")

    def scan_now(self):
        # Scan a new image using current configured settings
        print("Scanning Now")
        self.scanner_status = "BUSY"
        self.update_scanner_logo()
        self.log_text.insert(tk.END, "\nPerforming a Scan using the following Parameters:")
        self.log_text.insert(tk.END, "\n\tResolution: {}".format(self.resolution_var.get()))
        self.root.update()
        self.s_dev.resolution = int(self.resolution_var.get())
        self.s_dev.tl_x = int(self.tl_x_var.get())
        self.s_dev.sharpness = int(self.sharpness_var)
        self.s_dev.brightness = int(self.brightness_var)
        self.s_dev.tl_y = int(self.tl_y_var.get())
        self.s_dev.br_x = int(self.br_x_var.get())
        self.s_dev.br_y = int(self.br_y_var.get())
        try:
            self.s_dev.start()
            self.img_scan = self.s_dev.snap()
            self.img_exif = self.gen_exif_bytes(self.img_scan)
            self.img_scan.save(
                self.file_save_var.get() + str(self.file_name_var.get()) + str(self.file_format_var.get()),
                quality=85, exif=self.img_exif)
            self.last_scanned_add = self.file_save_var.get() + str(self.file_name_var.get()) + str(
                self.file_format_var.get())
            self.img_scan = self.pad_image_to_aspect_ratio(self.img_scan, 0.71)
            self.img_scan.thumbnail((617, 870))
            # Convert the PIL Image to Tkinter PhotoImage
            tk_image = ImageTk.PhotoImage(self.img_scan)

            # Update the preview label with the loaded image
            self.preview_image.config(image=tk_image)
            self.preview_image.image = tk_image
            self.scanner_status = "IDLE"
            self.update_scanner_logo()

            # Dynamically resize the window based on the image size
            new_width = self.img_scan.width + 460  # Add some padding
            new_height = self.img_scan.height + 30  # Add some padding
            self.root.geometry(f"{new_width}x{new_height}")

            self.log_text.insert(tk.END, "\n\tFile saved at: {}\n\tFile saved as: {}".format(self.file_save_var.get(),
                                                                                             self.file_name_var.get() + self.file_format_var.get()))
            self.log_text.insert(tk.END, "\nScan Finished Successully!")
            print("Scanning Finished successfully")
        except Exception as e:
            print(f"Error loading image: {e}")

    def connect_scanner(self):
        # Connect to scanner using sane. Change appropriate logos
        self.connection_status = "CONNECTING"
        self.update_connection_logo()
        self.log_text.insert(tk.END, "Attempting to connect to Scanner")
        self.root.update()
        try:
            self.sane_ver = sane.init()
            self.s_dev_list = sane.get_devices(True)
            # self.log_text.insert(tk.END, "Sane Device List: "+str(self.s_dev_list))
            print(self.s_dev_list)
            self.s_dev = sane.open(self.s_dev_list[0][0])
            self.s_dev.mode = 'Color'
            self.connection_status_label.config(text="Scanner\nConnected")
            print("Scanner Connected")
            # print(self.s_dev.opt)
            self.connection_status = "CONNECTED"
            self.update_connection_logo()
            self.log_text.insert(tk.END, "\nScanner Connected Successfully!")
            self.connect_scanner_button.config(state="disabled")
            self.scanner_status = "IDLE"
            self.update_scanner_logo()

            # Enable buttons and fields after connection
            self.fetch_button.config(state="normal")
            self.resolution_menu.config(state="normal")
            self.tl_x_entry.config(state="normal")
            self.tl_y_entry.config(state="normal")
            self.br_x_entry.config(state="normal")
            self.br_y_entry.config(state="normal")
            # self.brightness_menu.config(state="normal")
            # self.sharpness_menu.config(state="normal")
            self.file_name_field.config(state="normal")
            self.file_format_menu.config(state="normal")
            self.scan_button.config(state="normal")
            self.file_save_entry.config(state="normal")


        except:
            print("Scanner couldn't be connected")

    def next_stage(self):
        # Stop with scanning and start ML app
        print("Moving to Next Stage")
        self.log_text.insert(tk.END, "\nDisconnecting Scanner and Exiting")
        try:
            self.s_dev.close()
            sane.exit()
        except:
            print("No sane port open to exit")
        self.root.destroy()
        rel1 = "resources"
        rel2 = "outs"
        model_path = "training"
        ml_app = AppGUI(rel1, rel2, model_path, self.last_scanned_add)
        ml_app.mainloop()

    def update_connection_logo(self):
        # Update status indicators based on state variables
        if self.connection_status == "UNCONNECTED":
            self.connection_status_label = tk.Label(self.root, text="Scanner\nUnconnected",
                                                    font=("Helvetica", self.font_size))
            self.connection_logo = Image.open(self.connection_paths[1])
        elif self.connection_status == "CONNECTING":
            self.connection_status_label.config(text="Connecting...", font=("Helvetica", self.font_size))
            self.connection_logo = Image.open(self.connection_paths[2])
        elif self.connection_status == "CONNECTED":
            self.connection_status_label.config(text="Scanner\nConnected", font=("Helvetica", self.font_size))
            self.connection_logo = Image.open(self.connection_paths[0])
        self.connection_status_label.grid(row=0, column=3, columnspan=1, pady=5, sticky=tk.W)
        self.connection_logo.thumbnail((30, 30))
        self.connection_logo = ImageTk.PhotoImage(self.connection_logo)
        self.connection_logo_label = tk.Label(self.root, image=self.connection_logo)
        self.connection_logo_label.grid(row=0, column=2, padx=10, pady=5, sticky=tk.E)
        self.connection_logo_label.config(image=self.connection_logo)
        self.connection_logo_label.image = self.connection_logo

    def update_scanner_logo(self):
        # Update status indicators based on state variables
        try:
            # Destroy label to force an update. There were a few update issues without this
            self.scanner_status_text_label.destroy()
        except:
            # To prevent error during initialization
            pass
        if self.scanner_status == "IDLE":
            self.scanner_status_text_label = tk.Label(self.root, text="Scanner\nIdle",
                                                      font=("Helvetica", self.font_size))
            self.scanner_logo = Image.open(self.scanner_logo_paths[1])
        elif self.scanner_status == "BUSY":
            self.scanner_status_text_label = tk.Label(self.root, text="Scanner\nBusy",
                                                      font=("Helvetica", self.font_size, 'bold'))
            self.scanner_logo = Image.open(self.scanner_logo_paths[2])
        elif self.scanner_status == "UNKNOWN":
            self.scanner_status_text_label = tk.Label(self.root, text="Scanner\nUnknown",
                                                      font=("Helvetica", self.font_size))
            self.scanner_logo = Image.open(self.scanner_logo_paths[0])
        else:
            print("Invalid state")
        self.scanner_status_text_label.grid(row=1, column=3, columnspan=1, pady=5, sticky=tk.W)
        self.scanner_logo.thumbnail((30, 30))
        self.scanner_logo = ImageTk.PhotoImage(self.scanner_logo)
        self.scanner_status_label = tk.Label(self.root, image=self.scanner_logo)
        self.scanner_status_label.grid(row=1, column=2, padx=10, pady=5, sticky=tk.E)
        self.scanner_status_label.config(image=self.scanner_logo)
        self.scanner_status_label.image = self.scanner_logo

    def gen_exif_bytes(self, source_img):
        """
        Generates EXIF bytes to save to exported files
        :return: exif ordered byte object
        """
        o = io.BytesIO()
        image = source_img.copy()
        image.thumbnail((50, 50))
        image.save(o, "jpeg")
        thumbnail = o.getvalue()
        zeroth_ifd = {piexif.ImageIFD.Make: u"Epson V850",
                      piexif.ImageIFD.XResolution: (int(self.s_dev.resolution), 1),
                      piexif.ImageIFD.YResolution: (int(self.s_dev.resolution), 1),
                      piexif.ImageIFD.Software: str(self.sane_ver),
                      piexif.ImageIFD.DateTime: str(datetime.now()),
                      piexif.ImageIFD.ActiveArea: [int(self.s_dev.tl_x), int(self.s_dev.tl_y), int(self.s_dev.br_x),
                                                   int(self.s_dev.br_y)],
                      piexif.ImageIFD.ResolutionUnit: 2
                      }
        exif_ifd = {piexif.ExifIFD.DateTimeOriginal: str(datetime.now()),
                    piexif.ExifIFD.BrightnessValue: [self.s_dev.brightness, 1]
                    }
        gps_ifd = {piexif.GPSIFD.GPSVersionID: (2, 0, 0, 0),
                   piexif.GPSIFD.GPSAltitudeRef: 1,
                   piexif.GPSIFD.GPSDateStamp: u"1999:99:99 99:99:99",
                   }

        exif_dict = {"0th": zeroth_ifd, "Exif": exif_ifd, "GPS": gps_ifd, "thumbnail": thumbnail}
        exif_bytes = piexif.dump(exif_dict)
        return exif_bytes

    def pad_image_to_aspect_ratio(self, pil_img, aspect_ratio, color=(255, 255, 255)):
        """
        Pads the given PIL image evenly along all sides to achieve the specified aspect ratio.

        Args:
        - pil_img: PIL image object.
        - aspect_ratio: Desired aspect ratio (width / height).
        - color: Tuple representing the RGB color for the padding. Default is white.

        Returns:
        - PIL image object with the specified aspect ratio achieved by padding.
        """
        # Get the dimensions of the original image
        width, height = pil_img.size

        # Calculate the aspect ratio of the original image
        original_aspect_ratio = width / height
        new_width = width
        new_height = height
        # Calculate the new dimensions for the padded image based on the aspect ratio
        if original_aspect_ratio > aspect_ratio:
            # Image is wider than desired aspect ratio, so padding is needed on top and bottom
            new_height = int(width / aspect_ratio)
            pad_height = (new_height - height) // 2
            padding = (0, pad_height, 0, pad_height)
        else:
            # Image is taller than desired aspect ratio, so padding is needed on left and right
            new_width = int(height * aspect_ratio)
            pad_width = (new_width - width) // 2
            padding = (pad_width, 0, pad_width, 0)

        # Create a new image with the desired aspect ratio and fill it with the specified color
        padded_img = Image.new(pil_img.mode, (new_width, new_height), color)

        # Calculate the paste coordinates for the original image
        paste_coords = (
            padding[0],
            padding[1],
            width + padding[0],
            height + padding[1]
        )

        # Paste the original image onto the padded image at the appropriate position
        padded_img.paste(pil_img, paste_coords)

        return padded_img

    # Example usage:
    # Load your image using PIL
    # pil_img = Image.open("your_image_path.jpg")

    # Call the method to pad the image to the desired aspect ratio
    # padded_img = pad_image_to_aspect_ratio(pil_img, aspect_ratio=16/9)

    # Show the padded image
    # padded_img.show()


if __name__ == "__main__":
    root = tk.Tk()
    rel1 = "resources"
    rel2 = "outs"
    if root.winfo_screenheight() >= 1200:
        w_size = WinSize("large")
    elif root.winfo_screenheight() >= 800:
        w_size = WinSize("medium")
    else:
        w_size = WinSize("small")
    app = ScanningApp(root, rel1, rel2, w_size)
    root.mainloop()

# Disabled for now. Dropdown menu for Brightness
# brightness_values = [-4, -3, -2, -1, 0, 1, 2, 3]
# self.brightness_var = tk.StringVar(root)
# self.brightness_var.set(0)  # default value
# self.brightness_menu = tk.OptionMenu(root, self.brightness_var, *brightness_values)
# tk.Label(root, text="Brightness").grid(row=6, column=1, pady=5, sticky=tk.W)
# self.brightness_menu.grid(row=6, column=2, pady=5, sticky=tk.W)
# self.brightness_menu.config(state="disabled")

# Disabled for now. Dropdown menu for Sharpness
# sharpness_values = [-2, -1, 0, 1, 2]
# self.sharpness_var = tk.StringVar(root)
# self.sharpness_var.set(0)  # default value
# self.sharpness_menu = tk.OptionMenu(root, self.sharpness_var, *sharpness_values)
# tk.Label(root, text="Sharpness").grid(row=7, column=1, pady=5, sticky=tk.W)
# self.sharpness_menu.grid(row=7, column=2, pady=5, sticky=tk.W)
# self.sharpness_menu.config(state="disabled")
