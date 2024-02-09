## MODULES ##
import cv2
import os
import glob
from PIL import Image
import json
import pandas as pd

## Exporter Class ##
class Exporter:

    def __init__(self, outs, paths):
        self.outs = outs
        self.paths = paths


    def annotate_circles(self, image, holes, DPI, /, color1=(255, 255, 255), color2=(255, 255, 0), thickness1=3, radius=4, thickness2=-1, fontFace=cv2.FONT_HERSHEY_DUPLEX, fontScale=1, filename="All_Names.png"):

        """Function to annotate circles"""

        if not filename.endswith('.png') and not filename.endswith('.jpg') and not filename.endswith('.jpeg'):
            return

        result_img = image.copy()
        
        for hole in holes:
            cv2.putText(result_img, str(hole[2].split('_')[0]), (int(hole[0]), int(hole[1])), fontFace, fontScale * (DPI // 600), color1, thickness1 * (DPI // 600))
            cv2.circle(result_img, (int(hole[0]), int(hole[1])), radius * (DPI // 600), color2, thickness2 * (DPI // 600))

        cv2.imwrite(os.path.join(self.outs, filename), result_img)
        return result_img
    

    def annotate_holes(self, image, holes, DPI, /, color1=(255, 255, 255), color2=(255, 255, 0), thickness1=3, radius=4, thickness2=-1, fontFace=cv2.FONT_HERSHEY_DUPLEX, fontScale=1, filename="All_Names.png"):

        """Function to annotate holes"""

        if not filename.endswith('.png') and not filename.endswith('.jpg') and not filename.endswith('.jpeg'):
            return

        result_img = image.copy()
        
        for hole in holes:
            cv2.putText(result_img, str(hole[2].split('_')[0]), (int(hole[0]), int(hole[1])), fontFace, fontScale * (DPI // 600), color1, thickness1 * (DPI // 600))
            cv2.circle(result_img, (int(hole[0]), int(hole[1])), radius * (DPI // 600), color2, thickness2 * (DPI // 600))

        cv2.imwrite(os.path.join(self.outs, filename), result_img)
        return result_img
    
    
    def get_vid(self, dir, filename):

        """Function to extract holes from the img"""

        paths = glob.glob(os.path.join(self.outs, dir, '*.jpg'))

        if paths is None: return

        images = []
        for im_path in paths:
            img = cv2.imread(im_path)
            images.append(img)

        fourcc = cv2.VideoWriter_fourcc(*'DIVX')
        out = cv2.VideoWriter(os.path.join(self.outs, filename), fourcc, 0.5, (images[0].shape[1], images[0].shape[0]), True)

        for img in images:
            out.write(img)
        out.release()


    def mark_circles(self, img, circles, /, center_radius=10, thickness=3, color=(255, 0, 255)):

        """Function to annotate circles with center to the image with no return"""

        for circle in circles[0]:
            cv2.circle(img, (int(circle[0]), int(circle[1])), center_radius, thickness=-1, color=color)
            cv2.circle(img, (int(circle[0]), int(circle[1])), int(circle[2]), thickness=thickness, color=color)


    def mark_signal_pads(self, img, boxes, image_path, DPI):

        """Function to annotate the boxes for signal pads from detection"""

        for box in boxes:
            cv2.rectangle(img, (box[0] - box[2] // 2, box[1] - box[3] // 2), (box[0] + box[2] // 2, box[1] + box[3] // 2), (0, 0, 255), 3)

        rgb_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        pil_img = Image.fromarray(rgb_img)
        pil_img.save(os.path.join(self.outs, self.paths[1], os.path.basename(image_path)), dpi=(DPI, DPI))


    def save_json(self, detection_results):

        """Function to convert and write JSON object to file"""

        try:
            with open(os.path.join(self.outs, "detection_results.json"), "w") as outfile: 
                json.dump(detection_results, outfile, sort_keys=True, indent=4)
            return True
        except:
            return False


    def save_csv(self, data):

        """Function to convert dictionary and write JSON object to CSV"""

        try:
            data_frame = pd.DataFrame(data)
            data_frame.to_csv(os.path.join(self.outs, "area.csv"))
            return True
        except:
            return False