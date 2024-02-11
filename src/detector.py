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


    def detect_signal_pads(self):

        """Function to detect the signal pads from the stepped holes"""

        my_model = YOLO(os.path.join(self.model_path, 'best.pt'))
        DPI = None

        detection_results = []
        offsets = {'image': [], 'offset': []}

        for image_path in glob.glob(os.path.join(self.exporter.outs, self.exporter.paths[0], '*.jpg')):
            results = list(my_model(image_path, conf=self.conf))
            result = results[0]
            markings_vis = cv2.imread(image_path)

            offsets['image'].append(os.path.basename(image_path))
            offsets['offset'].append(self.get_concentrics(markings_vis))

            if DPI is None:
                DPI = Image.open(image_path).info["dpi"][0]

            bxs = np.int64(result.boxes.xywh.cpu().numpy())
            test_list = result.boxes.cls.cpu().numpy().tolist()

            self.exporter.mark_signal_pads(markings_vis, bxs, image_path, DPI)

            detection_results.append({ 'result': result, 'bxs': bxs, 'test_list': test_list })

        return detection_results, self.exporter.save_json(detection_results), self.exporter.save_csv(offsets, "offsets.csv")


    def get_concentrics(self, img, /, color1=(255, 255, 0), color2=(255, 0, 255)):

        """Function to detect concentric circles from the stepped holes"""
        
        blur_img = cv2.GaussianBlur(img, ksize=(5, 5), sigmaX=1.2)
        gray_img = cv2.cvtColor(blur_img, cv2.COLOR_BGR2GRAY)

        big_circles = np.array(cv2.HoughCircles(gray_img, cv2.HOUGH_GRADIENT, 0.8, minDist=600, param1=8, param2=29, minRadius=250, maxRadius=300))
        small_circles = np.array(cv2.HoughCircles(gray_img, cv2.HOUGH_GRADIENT, 0.8, minDist=600, param1=20, param2=29, minRadius=100, maxRadius=150))

        self.exporter.mark_circles(img, big_circles, center_radius=3, thickness=3, color=color1)
        self.exporter.mark_circles(img, small_circles, center_radius=3, thickness=3, color=color2)

        print(big_circles[0][0][0], small_circles[0][0][0])
        print(np.sqrt(np.power((big_circles[0][0][0] - small_circles[0][0][0]), 2) - np.power((big_circles[0][0][1] - small_circles[0][0][1]), 2)))
        return np.sqrt(np.power((big_circles[0][0][0] - small_circles[0][0][0]), 2) - np.power((big_circles[0][0][1] - small_circles[0][0][1]), 2))
