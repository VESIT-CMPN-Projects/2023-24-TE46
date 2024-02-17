## MODULES ##
import cv2
import os
import glob
from PIL import Image
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

    
    def focus_board(self, image, DPI, /, threshold=50, chips=[100, 100], filename='Cropped.jpg'):
        if not filename.endswith('.png') and not filename.endswith('.jpg') and not filename.endswith('.jpeg'):
            return
        
        factor = int(DPI // 600)
        resized_img = resized_img = cv2.resize(image, (int(image.shape[1] // factor), int(image.shape[0] // factor)), interpolation=cv2.INTER_AREA)
        result_img = image.copy()
        
        zeroes = np.zeros((resized_img.shape[0], resized_img.shape[1], 3), dtype=np.uint8)
        ones = np.zeros((resized_img.shape[0], resized_img.shape[1], 3), dtype=np.uint8) + 255

        p_zeroes = np.zeros((resized_img.shape[0], resized_img.shape[1]), dtype=np.uint8)
        p_ones = np.zeros((resized_img.shape[0], resized_img.shape[1]), dtype=np.uint8) + 255

        mask = np.where(resized_img[:, :, :] < 80, ones, zeroes)
        mask = cv2.bilateralFilter(mask, d=9, sigmaColor=80, sigmaSpace=125)
        mask = np.where((mask[:, :, 0] == 255) & (mask[:, :, 1] <= 5) & (mask[:, :, 2] == 255), p_ones, p_zeroes)

        rows = np.where(np.count_nonzero(mask, 1) >= threshold)[0]
        cols = np.where(np.count_nonzero(mask, 0) >= threshold)[0]

        result_img = result_img[rows[0] * factor + chips[0] : rows[-1] * factor - chips[0], 
                                cols[0] * factor + chips[0] : cols[-1] * factor - chips[0]]

        cv2.imwrite(os.path.join(self.exporter.outs, filename), result_img)

        return result_img


    def rotate_image(self, image, DPI):
        factor = int(DPI // 600)
        resized_img = cv2.resize(image, (int(image.shape[1] // factor), int(image.shape[0] // factor)), interpolation=cv2.INTER_AREA)

        # We know image is 600DPI after resizing, thus getting the window in a static way
        window = cv2.cvtColor(resized_img[resized_img.shape[0] - 700 : resized_img.shape[0] - 300, :], cv2.COLOR_BGR2GRAY)

        circles = cv2.HoughCircles(window, cv2.HOUGH_GRADIENT, 0.8, minDist=100, param1=10, param2=34, minRadius=22, maxRadius=29)

        holes = np.int64(circles)
        holes = np.flip(holes[0, np.argsort(holes[:, :, 1])[0]], axis=0)

        # for hole in holes:
        #     cv2.circle(window, (hole[0], hole[1]), 22, (255, 255, 255), -1)
        # plt.imshow(window)

        if (holes[0][0] < holes[1][0]):
            y2_minus_y1 = holes[0][1] - holes[1][1]
            x2_minus_x1 = holes[0][0] - holes[1][0]
        else:
            y2_minus_y1 = holes[1][1] - holes[0][1]
            x2_minus_x1 = holes[1][0] - holes[0][0]

        if (x2_minus_x1 == 0): return image

        angle = np.round(np.degrees(np.arctan(np.abs(y2_minus_y1 / x2_minus_x1))), 2)
        # print(angle)

        # Rotating the image in opposite direction
        rotated_img = image.copy()
        rotation_matrix = cv2.getRotationMatrix2D((0, 0), -angle, 1)
        rotated_img = cv2.warpAffine(rotated_img, rotation_matrix, (rotated_img.shape[1], rotated_img.shape[0]))

        return rotated_img


    def get_holes(self, image, DPI):

        """Function to get the holes from the image"""

        factor = int(DPI // 600)
        resized_img = cv2.resize(image, (int(image.shape[1] // factor), int(image.shape[0] // factor)), interpolation=cv2.INTER_AREA)

        # getting the window for rotation-angle measurement
        window = cv2.cvtColor(resized_img[ : , 300 : 500], cv2.COLOR_BGR2GRAY)

        circles = cv2.HoughCircles(window, cv2.HOUGH_GRADIENT, 0.8, minDist=100, param1=11, param2=44, minRadius=22, maxRadius=31)

        holes = np.int64(circles)
        holes = holes[0, np.argsort(holes[:, :, 0])[0]]
        # for hole in holes:
        #     cv2.circle(window, (hole[0], hole[1]), 22, (255, 255, 255), -1)
        # plt.imshow(window)
        # cv2.imwrite('temp.jpg', window)

        ref_point = [(holes[0][0] + 300) * factor, holes[0][1] * factor]

        # shifting the real coords for considering hole1 as reference point or (0, 0)
        shifted_x = real_x - real_x[0]
        shifted_y = real_y - real_y[0]

        # getting pixel-based coords from real coords
        real_coords = np.array((shifted_x, shifted_y)).T
        real_converted = np.int64(real_coords * DPI // 25.4)

        # applying translations
        real_pix_y = real_converted[:, 1] + ref_point[1]
        real_pix_x = np.abs(ref_point[0] + real_converted[:, 0])
        coords_real_pix = np.array((real_pix_x, real_pix_y, names)).T

        return coords_real_pix


    def get_holes_fv(self, image, DPI):

        """Function to get the holes from the image"""

        factor = int(DPI // 600)
        resized_img = cv2.resize(image, (int(image.shape[1] // factor), int(image.shape[0] // factor)), interpolation=cv2.INTER_AREA)

        # getting the window for rotation-angle measurement
        window = cv2.cvtColor(resized_img[resized_img.shape[0] - 700 : resized_img.shape[0] - 470, :], cv2.COLOR_BGR2GRAY)
        circles = cv2.HoughCircles(window, cv2.HOUGH_GRADIENT, 0.8, minDist=100, param1=11, param2=34, minRadius=22, maxRadius=29)

        holes = np.int64(circles)
        holes = np.flip(holes[0, np.argsort(holes[:, :, 1])[0]], axis=0)

        ref_point = [holes[0][0] * factor, (holes[0][1] + resized_img.shape[0] - 700) * factor]

        # shifting the real coords for considering hole1 as reference point or (0, 0)
        shifted_x = real_y - real_y[0]
        shifted_y = real_x - real_x[0]

        # getting pixel-based coords from real coords
        real_coords = np.array((shifted_x, shifted_y)).T
        real_converted = np.int64(real_coords * DPI // 25.4)

        # applying translations
        real_pix_x = real_converted[:, 0] + ref_point[0]
        real_pix_y = np.abs(ref_point[1] - real_converted[:, 1])
        coords_real_pix = np.array((real_pix_x, real_pix_y, names)).T

        return coords_real_pix


    def detect_signal_pads(self, DPI):

        """Function to detect the signal pads from the stepped holes"""

        my_model = YOLO(os.path.join(self.model_path, 'best.pt'))

        detection_results = []
        data_offset = {}

        for index, image_path in enumerate(glob.glob(os.path.join(self.exporter.outs, self.exporter.paths[0], '*.jpg'))):
            results = list(my_model(image_path, conf=self.conf))
            result = results[0]

            # Reading the image at image_path for annotation of signal pads and putting text
            markings_vis = cv2.imread(image_path)

            outer_centre, inner_centre, offset, offset_microns = self.get_concentrics(markings_vis, DPI)

            # Updating the dictionary for storing offsets between the holes
            data_offset.update({os.path.basename(image_path).split('.')[0]: {'outer_centre': outer_centre, 'inner_centre': inner_centre, 'offset': offset, 'offset_microns': offset_microns}})

            bxs = np.int64(result.boxes.xywh.cpu().numpy())
            test_list = result.boxes.cls.cpu().numpy().tolist()

            self.exporter.mark_signal_pads(markings_vis, bxs, image_path, DPI)

            detection_results.append({ 'result': result, 'bxs': bxs, 'test_list': test_list })

        return detection_results, data_offset


    def get_concentrics(self, img, DPI, /, color1=(255, 255, 0), color2=(255, 0, 255)):

        """Function to detect concentric circles from the stepped holes"""
        
        blur_img = cv2.GaussianBlur(img, ksize=(3, 3), sigmaX=1.1)
        gray_img = cv2.cvtColor(blur_img, cv2.COLOR_BGR2GRAY)

        factor = DPI // 600
        outer_circles = np.array(cv2.HoughCircles(gray_img, cv2.HOUGH_GRADIENT, 0.8, minDist=600, param1=8, param2=29, minRadius=int(46.875 * factor), maxRadius=int(56.25 * factor)))
        inner_circles = np.array(cv2.HoughCircles(gray_img, cv2.HOUGH_GRADIENT, 0.8, minDist=600, param1=20, param2=29, minRadius=int(18.75 * factor), maxRadius=int(28.125 * factor)))

        self.exporter.mark_circles(img, outer_circles, center_radius=3, thickness=3, color=color1)
        self.exporter.mark_circles(img, inner_circles, center_radius=3, thickness=3, color=color2)
        self.exporter.write(img, f"Offset = {np.round(np.sqrt(np.power((outer_circles[0][0][0] - inner_circles[0][0][0]), 2) + np.power((outer_circles[0][0][1] - inner_circles[0][0][1]), 2)) * 25400 / DPI, 3)}um", DPI // 600, x_mul=75)

        return (outer_circles[0][0], inner_circles[0][0], np.sqrt(np.power((outer_circles[0][0][0] - inner_circles[0][0][0]), 2) + np.power((outer_circles[0][0][1] - inner_circles[0][0][1]), 2)), np.sqrt(np.power((outer_circles[0][0][0] - inner_circles[0][0][0]), 2) + np.power((outer_circles[0][0][1] - inner_circles[0][0][1]), 2)) * 25400 / DPI)
