#!/home/dhep/GitRepos/Quality-Assurance/venv/bin python
import os
import sys
import tkinter as tk

from PIL import Image, ImageTk

from app_gui import AppGUI
from window_size import WinSize
IS_LINUX = False
if sys.platform.startswith('linux'):
    IS_LINUX = True
    from scanner import ScanningApp


class MainApp:
    def __init__(self, root):
        self.root = root
        # Detect Screen Size for window sizing
        if root.winfo_screenheight() >= 1200:
            self.w_size = WinSize("large")
        elif root.winfo_screenheight() >= 800:
            self.w_size = WinSize("medium")
        else:
            self.w_size = WinSize("small")
        self.root.title("Hexaboard QA Utility")
        # TODO Window positioning like the following for all windows
        self.root.geometry("%dx%d+%d+%d" % (self.w_size.main_window[0], self.w_size.main_window[1],
                                            ((root.winfo_screenwidth() / 2.) - (self.w_size.main_window[0] / 2.)),
                                            ((root.winfo_screenheight() / 2.) - (self.w_size.main_window[1] / 2.))))
        self.root.config(bg='white')

        # Load your image and logos
        logo_paths = ['white-IISER-Mohali_Logo.png', 'white-tifr_logo.png', 'white-VESIT_logo.png']
        logo_paths = [os.path.join(os.path.abspath(os.path.relpath('buttons')), file) for file in logo_paths]
        title_path = "TitleLogo.png"
        title_path = os.path.join(os.path.abspath(os.path.relpath('buttons')), title_path)
        butt_logo_paths = ['Scanner-black.png', 'white-tifr_logo.png', 'exit.png']
        butt_logo_paths = [os.path.join(os.path.abspath(os.path.relpath('buttons')), file) for file in butt_logo_paths]

        # Create and display the image on the left
        self.preview_image = tk.Label(root, text="Application Logo")
        self.preview_image.grid(row=0, column=0, rowspan=3, columnspan=5, padx=10, pady=10, sticky=tk.W)
        img = Image.open(title_path)
        img.thumbnail((self.w_size.main_app_logo[0], self.w_size.main_app_logo[1]))
        # Convert the PIL Image to Tkinter PhotoImage
        tk_image = ImageTk.PhotoImage(img)
        self.preview_image.config(image=tk_image)
        self.preview_image.image = tk_image

        # Create and display logo buttons beneath the image
        for i, logo_path in enumerate(logo_paths):
            logo = Image.open(logo_path)
            logo.thumbnail((self.w_size.main_logos[0], self.w_size.main_logos[1]))
            logo = ImageTk.PhotoImage(logo)
            logo_button = tk.Button(root, image=logo)
            logo_button.grid(row=3, column=i, padx=10, pady=5, sticky="s")
            logo_button.config(image=logo)
            logo_button.image = logo

        # Create and display scan and ML buttons on the right
        scan_butt_img = Image.open(butt_logo_paths[2])
        scan_butt_img.thumbnail((70, 70))
        scan_butt_img = ImageTk.PhotoImage(scan_butt_img)
        if IS_LINUX:
            scan_button = tk.Button(root, text="Scanner", compound="left", command=self.start_scanning_app, width=10,
                                    height=3, font=("Helvetica", 16))
        else:
            scan_button = tk.Button(root, text="Scanner(Linux Only)", compound="left", command=self.start_scanning_app,
                                    width=10,
                                    height=3, font=("Helvetica", 16), state='disabled')
        scan_button.grid(row=0, column=5, padx=10, pady=25, sticky="ne")

        ml_button = tk.Button(root, text="ML", command=self.start_ml_app, width=10, height=3, font=("Helvetica", 16))
        ml_button.grid(row=1, column=5, padx=10, pady=5, sticky="ne")

        close_button = tk.Button(root, text="Quit", command=root.destroy, width=10, height=3, font=("Helvetica", 16))
        close_button.grid(row=2, column=5, padx=10, pady=5, sticky="ne")

    def start_scanning_app(self):
        # Closes main window, starts scanning window and restarts main app when done
        self.root.destroy()
        self.master = tk.Tk()
        rel1 = "resources"
        rel2 = "outs"
        try:
            scanapp = ScanningApp(self.master, rel1, rel2, self.w_size)
        except:
            print("Couldn't load Scanning app. It is Linux only as it needs sane")
        self.master.mainloop()
        self.__init__(tk.Tk())

    def start_ml_app(self):
        # Closes main window, starts scanning window and restarts main app when done
        self.root.destroy()
        rel1 = "resources"
        rel2 = "outs"
        model_path = "training"
        conf = 0.54
        ml_app = AppGUI(rel1, rel2, model_path, conf)
        ml_app.mainloop()
        self.__init__(tk.Tk())


if __name__ == "__main__":
    root = tk.Tk()
    app = MainApp(root)
    root.mainloop()
