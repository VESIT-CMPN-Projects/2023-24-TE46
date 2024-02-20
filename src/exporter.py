## MODULES ##
import cv2
import os
import glob
from PIL import Image
import pandas as pd
import numpy as np
import json

## Custom Encoder for JSON objects ##
class CustomEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, list):
            return obj
        elif isinstance(obj, np.ndarray):
            return list(obj)
        return json.JSONEncoder.default(self, obj)

## Exporter Class ##
class Exporter:

    def __init__(self, outs, paths):
        self.outs = outs
        self.paths = paths
        self.fontScales = [0.5, 0.6, 0, 0.7, 0.7, 0, 0, 0.8]
        self.thicks = [1, 2, 0, 2, 2, 0, 0, 3]
    

    def annotate_holes(self, image, holes, DPI, /, color1=(255, 255, 255), color2=(255, 255, 0), thickness1=3, radius=4, thickness2=-1, fontFace=cv2.FONT_HERSHEY_DUPLEX, fontScale=1, filename="All_Names.jpg"):

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


    def write(self, img, text, factor, x_mul):
        cv2.putText(img, f"{text}", (x_mul * factor, img.shape[0] - 10 * factor), fontFace=cv2.FONT_HERSHEY_SIMPLEX, fontScale=self.fontScales[factor - 1], color=(0, 0, 0), thickness=self.thicks[factor - 1])


    def save_csv(self, data, filename):

        """Function to convert dictionary into equivalent CSV"""

        try:
            data_frame = pd.DataFrame(data)
            data_frame.to_csv(os.path.join(self.outs, filename if filename.endswith(".csv") else filename + ".csv"))
            return True
        except:
            return False
        
    
    def save_json(self, data, filename):

        """Function to convert dictionary and write JSON object to JSONFile"""

        try:
            jsonObject = json.dumps(data, cls=CustomEncoder)
            with open(os.path.join(self.outs, filename if filename.endswith(".json") else filename + ".json"), mode="w+") as out_file:
                chars_count = out_file.write(jsonObject)
            return chars_count
        except:
            return False
        

    def export_offsets(self, data_offset, holes, DPI):

        """Function to export data related to offset in the between the outer_circle and the inner_circle"""

        # CSV structure
        csv_data = {
            'image': [], 
            'actual_x (in px)': [], 
            'actual_y (in px)': [], 
            'local_outer_centre_x (in px)': [], 
            'local_outer_centre_y (in px)': [],
            'local_inner_centre_x (in px)': [],
            'local_inner_centre_y (in px)': [],
            'global_outer_centre_x (in px)': [],
            'global_outer_centre_y (in px)': [],
            'global_inner_centre_x (in px)': [],
            'global_inner_centre_y (in px)': [],
            'outer_centre_x (in mm)': [],
            'outer_centre_y (in mm)': [],
            'inner_centre_x (in mm)': [],
            'inner_centre_y (in mm)': [],
            'offset (in px)': [],
            'offset_microns': []
        }

        # getting a reference point
        data = data_offset['S042_014_999_999']
        ref_point = holes[np.where(holes[:, 2] == 'S042_014_999_999')][0]
        ref_point[0] = np.int64(int(ref_point[0]) - (70 * DPI // 600) + data['outer_centre'][0])
        ref_point[1] = np.int64(int(ref_point[1]) - (70 * DPI // 600) + data['outer_centre'][1])

        # Filling the CSV with data
        for hole in holes:
            data = data_offset[hole[2]]
            
            csv_data['image'].append(hole[2])
            csv_data['actual_x (in px)'].append(hole[0])
            csv_data['actual_y (in px)'].append(hole[1])
            csv_data['local_outer_centre_x (in px)'].append(np.int64(data['outer_centre'][0]))
            csv_data['local_outer_centre_y (in px)'].append(np.int64(data['outer_centre'][1]))
            csv_data['local_inner_centre_x (in px)'].append(np.int64(data['inner_centre'][0]))
            csv_data['local_inner_centre_y (in px)'].append(np.int64(data['inner_centre'][1]))
            csv_data['global_outer_centre_x (in px)'].append(np.int64(int(hole[0]) - (70 * DPI // 600) + data['outer_centre'][0]))
            csv_data['global_outer_centre_y (in px)'].append(np.int64(int(hole[1]) - (70 * DPI // 600) + data['outer_centre'][1]))
            csv_data['global_inner_centre_x (in px)'].append(np.int64(int(hole[0]) - (70 * DPI // 600) + data['inner_centre'][0]))
            csv_data['global_inner_centre_y (in px)'].append(np.int64(int(hole[1]) - (70 * DPI // 600) + data['inner_centre'][1]))
            csv_data['outer_centre_x (in mm)'].append(np.int64(csv_data['global_outer_centre_x (in px)'][-1] - int(ref_point[0])) * 25.4 // DPI)
            csv_data['outer_centre_y (in mm)'].append(np.int64(csv_data['global_outer_centre_y (in px)'][-1] - int(ref_point[1])) * 25.4 // DPI)
            csv_data['inner_centre_x (in mm)'].append(np.int64(csv_data['global_inner_centre_x (in px)'][-1] - int(ref_point[0])) * 25.4 // DPI)
            csv_data['inner_centre_y (in mm)'].append(np.int64(csv_data['global_inner_centre_y (in px)'][-1] - int(ref_point[1])) * 25.4 // DPI)
            csv_data['offset (in px)'].append(data['offset'])
            csv_data['offset_microns'].append(data['offset_microns'])

        return self.save_csv(csv_data, "offsets.csv")
