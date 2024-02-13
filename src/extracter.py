## MODULES ##
# import json
import os
import cv2
import numpy as np
from PIL import Image

## Extracter class ##
class Extracter:

    def __init__(self, exporter):
        self.exporter = exporter
        self.data = []


    def extract(self, image, holes, image_DPI, /, path="Conventionally_named_holes", offset=(70, 70)):

        """Function to extract holes from the img"""

        if type(offset) != type(()):
            print("Offset must be specified as a tuple")
            return
        
        factor = image_DPI // 600
        x_offset, y_offset = np.array(offset) * factor

        try:
            strip = (np.ones((25 * factor, 2 * x_offset, 3)) * 255).astype('uint8')

            for hole in holes:
                cropped_hole = image[int(hole[1]) - x_offset : int(hole[1]) + x_offset, int(hole[0]) - y_offset : int(hole[0]) + y_offset]
                final_img = np.vstack((cropped_hole, strip))
                self.exporter.write(final_img, f"{hole[2]}.jpg", factor, x_mul=5)
                Image.fromarray(cv2.cvtColor(final_img, cv2.COLOR_BGR2RGB)).save(f"{os.path.join(self.exporter.outs, path, hole[2])}.jpg", dpi=(image_DPI, image_DPI))

            return True

        except Exception as err:
            print(err)
            return False
    

    def get_analytics(self, detection_results, DPI):

        """Function to analytics csv from the detected signal pads"""

        Area11 = [0] * 92
        Area1 = [0] * 92
        Area2 = [0] * 92
        Area3 = [0] * 92
        Area4 = [0] * 92
        Area5 = [0] * 92
        Area6 = [0] * 92
        Area7 = [0] * 92
        Area8 = [0] * 92
        Area9 = [0] * 92
        Area10 = [0] * 92
        Area12 = [0] * 92

        # detection_results = json.load(open(os.path.join(self.exporter.outs, "detection_results.json"), "r"))

        for idx, detection in enumerate(detection_results):
            
            classes = detection['test_list']

            if detection['result'].masks is not None:
                maskList = [(detection['result'].masks.data[int(a)].cpu().numpy() * 255).astype("uint8") for a in range(len(detection['result'].masks.data))]

                for mask in enumerate(maskList):
                    edged = cv2.Canny(mask[1], threshold1=30, threshold2=200)
                    contours, _ = cv2.findContours(edged,cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

                    for j in range(0, len(contours)):
                        if classes[j] != 13:
                            area = cv2.contourArea(contours[j])
                            if classes[j] == 0:
                                Area1[idx] = area * 25400 / DPI
                            elif classes[j] == 1:
                                Area2[idx] = area * 25400 / DPI
                            elif classes[j] == 2:
                                Area3[idx] = area * 25400 / DPI
                            elif classes[j] == 3:
                                Area4[idx] = area * 25400 / DPI
                            elif classes[j] == 4:
                                Area5[idx] = area * 25400 / DPI
                            elif classes[j] == 5:
                                Area6[idx] = area * 25400 / DPI
                            elif classes[j] == 6:
                                Area7[idx] = area * 25400 / DPI
                            elif classes[j] == 7:
                                Area8[idx] = area * 25400 / DPI
                            elif classes[j] == 8:
                                Area9[idx] = area * 25400 / DPI
                            elif classes[j] == 9:
                                Area10[idx] = area * 25400 / DPI
                            elif classes[j] == 10:
                                Area11[idx] = area * 25400 / DPI
                            elif classes[j] == 11:
                                Area12[idx] = area * 25400 / DPI

        data = {
            'Area1': Area1,
            'Area2': Area2,
            'Area3': Area3,
            'Area4': Area4,
            'Area5': Area5,
            'Area6': Area6,
            'Area7': Area1,
            'Area8': Area8,
            'Area9': Area9,
            'Area10': Area10,
            'Area11': Area11,
            'Area12': Area12
        }

        return self.exporter.save_csv(data, "area.csv")
