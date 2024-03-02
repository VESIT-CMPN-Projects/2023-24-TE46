## MODULES ##
import os

import cv2
import numpy as np


## Image PreProcessing Class ##
class Preprocessor:

    def __init__(self, outs):
        self.outs = outs


    def focus_board(self, image, DPI, /, threshold=50, chips=[100, 100], filename='Cropped.jpg'):
        if not filename.endswith('.png') and not filename.endswith('.jpg') and not filename.endswith('.jpeg'):
            return

        factor = int(DPI // 600)
        resized_img = resized_img = cv2.resize(image, (int(image.shape[1] // factor), int(image.shape[0] // factor)),
                                               interpolation=cv2.INTER_AREA)
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

        result_img = result_img[rows[0] * factor + chips[0]: rows[-1] * factor - chips[0],
                     cols[0] * factor + chips[0]: cols[-1] * factor - chips[0]]

        cv2.imwrite(os.path.join(self.outs, filename), result_img)

        return result_img


    def rotate_image(self, image, DPI, /, filename='Rotated.jpg'):
        if not filename.endswith('.png') and not filename.endswith('.jpg') and not filename.endswith('.jpeg'):
            return

        factor = int(DPI // 600)
        print(DPI)
        resized_img = cv2.resize(image, (int(image.shape[1] // factor), int(image.shape[0] // factor)),
                                 interpolation=cv2.INTER_AREA)

        # We know image is 600DPI after resizing, thus getting the window in a static way
        window = cv2.cvtColor(resized_img[resized_img.shape[0] - 700: resized_img.shape[0] - 300, :],
                              cv2.COLOR_BGR2GRAY)

        circles = cv2.HoughCircles(window, cv2.HOUGH_GRADIENT, 0.8, minDist=100, param1=10, param2=34, minRadius=22,
                                   maxRadius=29)

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

        cv2.imwrite(os.path.join(self.outs, filename), rotated_img)

        return rotated_img
