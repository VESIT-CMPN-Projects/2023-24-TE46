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


    def extract(self, image, holes, image_DPI, /, path="Conventionally_named_holes", offset=(70, 70)):

        """Function to extract holes from the img"""

        if type(offset) != type(()):
            print("Offset must be specified as a tuple")
            return
        
        factor = image_DPI // 600
        x_offset, y_offset = np.array(offset) * factor

        fontScales = [0.5, 0.6, 0, 0.7, 0.7, 0, 0, 0.8]
        thicks = [1, 2, 0, 2, 2, 0, 0, 3]

        try:
            strip = (np.ones((25 * factor, 2 * x_offset, 3)) * 255).astype('uint8')
            for hole in holes:
                cropped_hole = image[int(hole[1]) - x_offset : int(hole[1]) + x_offset, int(hole[0]) - y_offset : int(hole[0]) + y_offset]

                final_img = np.vstack((cropped_hole, strip))

                cv2.putText(final_img, f"{hole[2]}.jpg", (5 * factor, final_img.shape[0] - 10 * factor), fontFace=cv2.FONT_HERSHEY_SIMPLEX, fontScale=fontScales[factor - 1], color=(0, 0, 0), thickness=thicks[factor - 1])

                Image.fromarray(cv2.cvtColor(final_img, cv2.COLOR_BGR2RGB)).save(f"{os.path.join(self.exporter.outs, path, hole[2])}.jpg", dpi=(image_DPI, image_DPI))
        except Exception as err:
            print(err)
            return False
        return True
    

    def get_analytics(self, detection_results):

        """Function to analytics csv from the detected signal pads"""

        classes = []
        Area11 = [0] * 92
        Area1 = [0] * 92
        Area3 = [0] * 92
        Area5 = [0] * 92
        Area7 = [0] * 92
        Area9 = [0] * 92

        # detection_results = json.load(open(os.path.join(self.exporter.outs, "detection_results.json"), "r"))

        for idx, detection in enumerate(detection_results):
            
            [classes.append(x) for x in detection['test_list'] if x not in classes]

            if detection['result'].masks is not None:
                no = -1 if not (6 in classes) else classes.index(6)
                maskList = []
                [maskList.append((detection['result'].masks.data[int(a)].cpu().numpy() * 255).astype("uint8")) for a in range(len(detection['result'].masks.data)) if a != no]

                for _class, mask in enumerate(maskList):
                    edged = cv2.Canny(mask, 30, 200)
                    contours, _ = cv2.findContours(edged,cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

                    for j in range(0, len(contours)):
                        if classes[_class] != 6 or _class > 3:
                            area = cv2.contourArea(contours[j])
                            if classes[_class] == 0:
                                Area11[idx] = area
                            elif classes[_class] == 1:
                                Area1[idx] = area
                            elif classes[_class] == 2:
                                Area3[idx] = area
                            elif classes[_class] == 3:
                                Area5[idx] = area
                            elif classes[_class] == 4:
                                Area7[idx] = area
                            elif classes[_class] == 5:
                                Area9[idx] = area

        data={'Area11': Area11, 'Area1': Area1, 'Area3': Area3, 'Area5': Area5, 'Area7': Area7, 'Area9': Area9}

        return self.exporter.save_csv(data, "area.csv")
