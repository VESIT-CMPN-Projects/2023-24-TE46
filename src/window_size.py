#
#   Templates used for defining the general window sizes based on screen size the application runs on
#   They are of 3 kinds roughly corresponding to 1440p and above, around 1080p and around 720p screens
#
class WinSize:
    def __init__(self, stype):
        if stype == "medium":   # >800p <1200p screens(1920x1080, 1920x1200, 1600x900, 1600x1000, 2560x1080p)
            # Main Window sizes
            self.main_window = [900, 900]
            self.main_app_logo = [710, 700]
            self.main_logos = [150, 150]

            # Scan Window sizes
            self.scan_window = [1070, 900]
            self.scan_preview = [674, 950]

            # ML Window sizes
            self.ml_window = []
            self.ml_image = []
            self.ml_thumb = []
        elif stype == "large":  # >1200p screens(2560x1440, 2160, 3840x2160, 3440x1440)
            # Main Window sizes
            self.main_window = [1275, 1220]
            self.main_app_logo = [940, 940]
            self.main_logos = [248, 248]

            # Scan Window sizes
            self.scan_window = [1310, 1100]
            self.scan_preview = [824, 1060]

            # ML Window sizes
            self.ml_window = []
            self.ml_image = []
            self.ml_thumb = []
        else:                       #<800p screens (1366x768, 1280x720(why do you hate yourself?))
            # Main Window sizes
            self.main_window = [710, 670]
            self.main_app_logo = [500, 500]
            self.main_logos = [100, 100]

            # Scan Window sizes
            self.scan_window = [810, 680]
            self.scan_preview = [470, 680]

            # ML Window sizes
            self.ml_window = []
            self.ml_image = []
            self.ml_thumb = []