## MODULES ##
import glob
import json
import os
import cv2
import numpy as np
import pandas as pd
from PIL import Image
import copy


## Custom Encoder for JSON objects ##
class CustomEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, list):
            return obj
        elif isinstance(obj, np.ndarray):
            return list(obj)
        elif isinstance(obj, np.int64):
            return str(obj)
        elif isinstance(obj, np.float64):
            return str(obj)
        return json.JSONEncoder.default(self, obj)


## Exporter Class ##
class Exporter:

    def __init__(self, outs, paths):
        self.outs = outs
        self.paths = paths
        self.fontScales = [0.3, 0.3, 0, 0.7, 0.7, 0, 0, 0.8]
        self.thicks = [1, 1, 0, 2, 2, 0, 0, 3]
        self.offsets_object_structure = {
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


    def annotate_holes(self, image, holes, DPI, /, color1=(255, 255, 255), color2=(255, 255, 0), thickness1=3, radius=4,
                       thickness2=-1, fontFace=cv2.FONT_HERSHEY_DUPLEX, fontScale=1, filename="All_Names.jpg"):
        """Function to annotate holes"""

        if not filename.endswith('.png') and not filename.endswith('.jpg') and not filename.endswith('.jpeg'):
            return

        result_img = image.copy()

        for hole in holes:
            cv2.putText(result_img, str(hole[2].split('_')[0]), (int(hole[0]), int(hole[1])), fontFace,
                        fontScale * (DPI // 600), color1, thickness1 * (DPI // 600))
            cv2.circle(result_img, (int(hole[0]), int(hole[1])), radius * (DPI // 600), color2,
                       thickness2 * (DPI // 600))

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
        out = cv2.VideoWriter(os.path.join(self.outs, filename), fourcc, 0.5, (images[0].shape[1], images[0].shape[0]),
                              True)

        for img in images:
            out.write(img)
        out.release()


    def mark_circles(self, img, factor, circles, /, center_radius=1, thickness=1, color=(255, 0, 255)):
        """Function to annotate circles with center to the image with no return"""

        for circle in circles[0]:
            cv2.circle(img, (int(circle[0]), int(circle[1])), int(center_radius * factor), thickness=-1, color=color)
            cv2.circle(img, (int(circle[0]), int(circle[1])), int(circle[2]), thickness=thickness * factor, color=color)


    def mark_signal_pads(self, img, boxes, image_path, DPI, /, thickness=1):
        """Function to annotate the boxes for signal pads from detection"""

        for box in boxes:
            cv2.rectangle(img, (box[0] - box[2] // 2, box[1] - box[3] // 2),
                          (box[0] + box[2] // 2, box[1] + box[3] // 2), color=(0, 0, 255), thickness=thickness * (DPI // 600))

        rgb_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        pil_img = Image.fromarray(rgb_img)
        pil_img.save(os.path.join(self.outs, self.paths[1], os.path.basename(image_path)), dpi=(DPI, DPI))


    def write(self, img, text, factor, x_mul):
        """Function to write the hole details on bottom white strip """
        
        cv2.putText(img, f"{text}", (x_mul * factor, img.shape[0] - 10 * factor), fontFace=cv2.FONT_HERSHEY_SIMPLEX,
                    fontScale=self.fontScales[factor - 1], color=(0, 0, 0), thickness=self.thicks[factor - 1])


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
            with open(os.path.join(self.outs, filename if filename.endswith(".json") else filename + ".json"),
                      mode="w+") as out_file:
                chars_count = out_file.write(jsonObject)
            return chars_count
        except Exception as err:
            print(err)
            return False
        
    
    def save_excel(self, data, filename, /, sheetname="Offsets"):
        """Function to convert dictionary and write JSON object to JSONFile"""

        try:
            dataframe = pd.DataFrame(data)
            with pd.ExcelWriter(os.path.join(self.outs, filename if filename.endswith(".xlsx") else filename + ".xlsx")) as writer:
                dataframe.to_excel(writer, sheet_name=sheetname)  
            return True
        except Exception as err:
            print(err)
            return False
    

    def json_to_excel(self, /, filename="strips.xlsx", sheetname="Offsets"):
        """Function to convert the strips json to excel file"""

        with open(os.path.join(self.outs, "strips.json"), mode='r') as file:
            data = json.load(file)

        strip_dataframe = pd.DataFrame()
        for strip_dict in data:
            strip_dataframe.combine(pd.DataFrame(strip_dict), pd.concat)
            strip_dataframe.combine(pd.DataFrame([" " for _ in range(len(data[0].keys()))]), pd.concat)

        with pd.ExcelWriter(os.path.join(self.outs, filename if filename.endswith(".xlsx") else filename + ".xlsx"), engine="xlsxwriter") as writer:
            strip_dataframe.to_excel(writer, sheet_name=sheetname)


    def export_offsets(self, data_offset, holes, DPI):
        """Function to export data related to offset in the between the outer_circle and the inner_circle"""

        # CSV structure
        csv_data = self.get_offsets_struct()

        # Getting a reference point
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
            csv_data['global_outer_centre_x (in px)'].append(
                np.int64(int(hole[0]) - (70 * DPI // 600) + data['outer_centre'][0]))
            csv_data['global_outer_centre_y (in px)'].append(
                np.int64(int(hole[1]) - (70 * DPI // 600) + data['outer_centre'][1]))
            csv_data['global_inner_centre_x (in px)'].append(
                np.int64(int(hole[0]) - (70 * DPI // 600) + data['inner_centre'][0]))
            csv_data['global_inner_centre_y (in px)'].append(
                np.int64(int(hole[1]) - (70 * DPI // 600) + data['inner_centre'][1]))
            csv_data['outer_centre_x (in mm)'].append(
                np.int64(csv_data['global_outer_centre_x (in px)'][-1] - int(ref_point[0])) * 25.4 // DPI)
            csv_data['outer_centre_y (in mm)'].append(
                np.int64(csv_data['global_outer_centre_y (in px)'][-1] - int(ref_point[1])) * 25.4 // DPI)
            csv_data['inner_centre_x (in mm)'].append(
                np.int64(csv_data['global_inner_centre_x (in px)'][-1] - int(ref_point[0])) * 25.4 // DPI)
            csv_data['inner_centre_y (in mm)'].append(
                np.int64(csv_data['global_inner_centre_y (in px)'][-1] - int(ref_point[1])) * 25.4 // DPI)
            csv_data['offset (in px)'].append(data['offset'])
            csv_data['offset_microns'].append(data['offset_microns'])

        return csv_data, self.save_csv(csv_data, "offsets.csv")


    def get_strips_config(self, img, DPI, holes, /, width=200):
        """Function to get strip of holes from the PCB"""

        # Setting the width for the strips
        width = width * int(DPI // 600)

        # Creating a list to store the hole names in strips
        strips_config = {
            "width": width,
            "configuration": []
        }

        # Looping over holes
        for index in range(0, img.shape[1], width):

            # If a hole falls in the range of current index + width, we add it to the current strip
            temp_strip = holes[np.where((np.int64(holes[:, 0]) >= index) & (np.int64(holes[:, 0]) < index + width))]

            # If temp_strip contains a hole, we append the strip
            if len(temp_strip) != 0:
                strips_config["configuration"].append(temp_strip[:, 2])

        # Saving the strips config for the given width
        return self.save_json(strips_config, "strips_config.json")


    def export_strip_offsets(self, img, DPI, holes, offsets, /, width=200):
        """Function to export data related to offset in the between the outer_circle and the inner_circle"""

        # Fetching the strips_config
        strips_config_path = os.path.join(self.outs, "strips_config.json")
        strips_config_exists = os.path.exists(strips_config_path)
        if strips_config_exists:
            with open(strips_config_path) as json_file:
                strips_config = json.load(json_file)

        # Generating a new strips_config file if it doesn't exists or the desired width is different
        if not strips_config_exists or width != strips_config["width"]:
            self.get_strips_config(img, DPI, holes, width)
        
        # Getting the headers for the offsets struct
        offsets_headers = list(offsets.keys())
        offsets_dataframe = pd.DataFrame(offsets)

        # Generating the strips
        strips = []
        for row in range(len(strips_config)):
            strips.append(self.get_offsets_struct())

            for col in range(len(strips_config[row])):
                offsets_row = np.where(offsets_dataframe["image"] == strips_config[row][col])[0][0]
                for offsets_col in range(len(offsets_headers)):
                    strips[-1][offsets_headers[offsets_col]].append(offsets_dataframe.iloc[offsets_row, offsets_col])

        return strips, self.save_json(strips, "strips.json"), self.save_excel(strips, "strips1.xlsx")
    

    def get_offsets_struct(self):
        """Function to get a copy of offsets_structure"""

        return copy.deepcopy(self.offsets_object_structure)