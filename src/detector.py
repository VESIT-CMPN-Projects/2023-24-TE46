## MODULES ##
import glob
import os
import cv2
import numpy as np
from ultralytics import YOLO

## DATA ##
from data import real_y, real_x, names


## Detector class ##
class Detector:

    def __init__(self, exporter, model_path, conf):
        self.model_path = model_path
        self.exporter = exporter
        self.conf = conf
        

    def get_holes(self, image, DPI):
        """Function to get the holes from the image"""

        # Resizing the image
        factor = int(DPI // 600)
        resized_img = cv2.resize(image, (int(image.shape[1] // factor), int(image.shape[0] // factor)),
                                 interpolation=cv2.INTER_AREA)

        # Getting the window for detecting the bottommost hole and applying CHT to get the circles
        window = cv2.cvtColor(resized_img[:, 300: 500], cv2.COLOR_BGR2GRAY)
        circles = cv2.HoughCircles(window, cv2.HOUGH_GRADIENT, 0.8, minDist=100, param1=11, param2=44, minRadius=22,
                                   maxRadius=31)

        # Sorting the holes based on their Y-coordinates to get the bottommost hole as the first hole
        holes = np.int64(circles)
        holes = holes[0, np.argsort(holes[:, :, 0])[0]]
        # for hole in holes:
        #     cv2.circle(window, (hole[0], hole[1]), 22, (255, 255, 255), -1)
        # cv2.imwrite('temp.jpg', window)

        # Setting bottommost hole as the reference point
        # Using the window's start row to obtain the Y-coordinate of hole in entire image
        ref_point = [(holes[0][0] + 300) * factor, holes[0][1] * factor]

        # Shifting the real coords for considering hole1 as reference point or (0, 0)
        shifted_x = real_x - real_x[0]
        shifted_y = real_y - real_y[0]

        # Getting pixel-based coords from real coords
        real_coords = np.array((shifted_x, shifted_y)).T
        real_converted = np.int64(real_coords * DPI // 25.4)

        # Applying translations
        real_pix_y = real_converted[:, 1] + ref_point[1]
        real_pix_x = np.abs(ref_point[0] + real_converted[:, 0])
        coords_real_pix = np.array((real_pix_x, real_pix_y, names)).T

        return coords_real_pix


    def get_holes_fv(self, image, DPI):
        """Function to get the holes from the image"""

        # Resizing the image
        factor = int(DPI // 600)
        resized_img = cv2.resize(image, (int(image.shape[1] // factor), int(image.shape[0] // factor)),
                                 interpolation=cv2.INTER_AREA)

        # Getting the window for detecting the bottommost hole and applying CHT to get the circles
        window = cv2.cvtColor(resized_img[resized_img.shape[0] - 1000: resized_img.shape[0] - 500, :],
                              cv2.COLOR_BGR2GRAY)
        circles = cv2.HoughCircles(window, cv2.HOUGH_GRADIENT, 0.8, minDist=100, param1=11, param2=32, minRadius=22,
                                   maxRadius=30)

        # Sorting the holes based on their Y-coordinates to get the bottommost hole as the first hole
        holes = np.int64(circles)
        holes = np.flip(holes[0, np.argsort(holes[:, :, 1])[0]], axis=0)
        # for hole in holes:
        #     cv2.circle(window, (hole[0], hole[1]), 22, (255, 255, 255), -1)
        # cv2.imwrite('temp.jpg', window)

        # Setting bottommost hole as the reference point
        # Using the window's start row to obtain the Y-coordinate of hole in entire image
        ref_point = [holes[0][0] * factor, (holes[0][1] + resized_img.shape[0] - 1000) * factor]

        # Shifting the real coords for considering hole1 as reference point or (0, 0)
        shifted_x = real_y - real_y[0]
        shifted_y = real_x - real_x[0]

        # Getting pixel-based coords from real coords
        real_coords = np.array((shifted_x, shifted_y)).T
        real_converted = np.int64(real_coords * DPI // 25.4)

        # Applying translations
        real_pix_x = real_converted[:, 0] + ref_point[0]
        real_pix_y = np.abs(ref_point[1] - real_converted[:, 1])
        coords_real_pix = np.array((real_pix_x, real_pix_y, names)).T

        return coords_real_pix


    def start_detections(self, DPI):
        """Function to detect the signal pads from the stepped holes"""

        # Calling the YOLO-Model
        my_model = YOLO(os.path.join(self.model_path, 'best.pt'))

        # VARIABLES #
        detection_results = []
        data_offset = {}

        # Looping over the cropped images
        for image_path in glob.glob(os.path.join(self.exporter.outs, self.exporter.paths[0], '*.jpg')):
            results = list(my_model(image_path, conf=self.conf))
            result = results[0]

            # Reading the image at image_path for annotation of signal pads and putting text
            markings_vis = cv2.imread(image_path)

            outer_centre, inner_centre, offset, offset_microns = self.get_concentrics(markings_vis, DPI)

            # Updating the dictionary for storing offsets between the holes
            data_offset.update({os.path.basename(image_path).split('.')[0]: {'outer_centre': outer_centre,
                                                                             'inner_centre': inner_centre,
                                                                             'offset': offset,
                                                                             'offset_microns': offset_microns}})

            # Getting the boxes for signal pads
            test_list = result.boxes.cls.cpu().numpy()
            indices = np.where(test_list != 12)[0]
            test_list = test_list[indices]
            bxs = np.int64(result.boxes.xywh.cpu().numpy())[indices]

            # Drawing the boxes to mark the signal pads on the image
            self.exporter.mark_signal_pads(markings_vis, bxs, image_path, DPI)

            # Updating the detection_results list to store the detection results for future use
            detection_results.append({'result': result, 'bxs': bxs, 'test_list': test_list})

        return detection_results, data_offset


    def get_concentrics(self, img, DPI, /, color1=(255, 255, 0), color2=(255, 0, 255)):
        """Function to detect concentric circles from the stepped holes"""

        # Applying gaussian blur and converting the image to gray image
        blur_img = cv2.GaussianBlur(img, ksize=(3, 3), sigmaX=1.2)
        gray_img = cv2.cvtColor(blur_img, cv2.COLOR_BGR2GRAY)

        # Getting the inner and outer circles
        factor = DPI // 600
        outer_circles = np.array(cv2.HoughCircles(gray_img, cv2.HOUGH_GRADIENT, 0.1, minDist=600, param1=60, param2=43,
                                                  minRadius=int(46.875 * factor), maxRadius=int(62 * factor)))
        inner_circles = np.array(cv2.HoughCircles(gray_img, cv2.HOUGH_GRADIENT, 0.3, minDist=600, param1=35, param2=37,
                                                  minRadius=int(18.75 * factor), maxRadius=int(30 * factor)))

        if outer_circles.ndim != 0 and inner_circles.ndim != 0:
            # Drawing the inner and outer circles
            self.exporter.mark_circles(img, factor, outer_circles, center_radius=1, thickness=1, color=color1)
            self.exporter.mark_circles(img, factor, inner_circles, center_radius=1, thickness=1, color=color2)

            # Writing the offset to the bottom white strip of images
            self.exporter.write(img,
                                f"Offset = {np.round(np.sqrt(np.power((outer_circles[0][0][0] - inner_circles[0][0][0]), 2) + np.power((outer_circles[0][0][1] - inner_circles[0][0][1]), 2)) * 25400 / DPI, 3)}um",
                                factor, x_mul=75)

            # Returning the offset value in pixels and micrometers
            return (outer_circles[0][0], inner_circles[0][0], np.sqrt(
                np.power((outer_circles[0][0][0] - inner_circles[0][0][0]), 2) + np.power(
                    (outer_circles[0][0][1] - inner_circles[0][0][1]), 2)), np.sqrt(
                np.power((outer_circles[0][0][0] - inner_circles[0][0][0]), 2) + np.power(
                    (outer_circles[0][0][1] - inner_circles[0][0][1]), 2)) * 25400 / DPI)

        return [np.nan] * 4
