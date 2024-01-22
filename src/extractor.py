from data import real_y, real_x, names
import os
import cv2
import glob
import numpy as np
import pandas as pd
from PIL import Image
from ultralytics import YOLO
import matplotlib.pyplot as plt


class Extractor:
    def __init__(self, img, outs, paths, model_path):
        self.outs = os.path.abspath(os.path.relpath(outs))
        self.paths = paths
        self.model_path = os.path.relpath(model_path)

        DPI = img.info['dpi'][0]
        img = np.array(img)

        # converting rgb to bgr
        img = np.flip(img, axis=-1)

        if img.shape[0] < img.shape[1]:
            img = self.get_vertical_board(img, DPI)

        cropped_img = self.focus_board(img, DPI)
        rotated_img = self.rotate_image(cropped_img, DPI)

        holes = self.get_holes(rotated_img, DPI)
        _ = self.annotate_holes(rotated_img, holes, DPI)

        self.extract(rotated_img, holes, DPI, path=self.paths[0])
        self.get_vid(self.paths[0], "video.avi")
        
        self.get_area()

        self.get_vid(self.paths[1], "video--s.avi")


    def get_vertical_board(self, img, DPI):
        resize_img = cv2.resize(img, (int(img.shape[1] // DPI * 600), int(img.shape[0] // DPI * 600)), interpolation=cv2.INTER_AREA)

        left_strip = cv2.cvtColor(resize_img[:, : 600].copy(), cv2.COLOR_BGR2GRAY)
        
        circles_left = cv2.HoughCircles(left_strip, cv2.HOUGH_GRADIENT, 0.8, minDist=100, param1=11, param2=34, minRadius=22, maxRadius=29)
        circles_left = np.int32(circles_left[0])

        left_strip_res = left_strip.copy()
        for cir in circles_left:
            cv2.circle(left_strip_res, (cir[0], cir[1]), cir[2], (255, 255, 255), 10)

        left_count = len(circles_left[np.where((circles_left[:, 1] < 600) | (circles_left[:, 1] > resize_img.shape[0] - 600))])

        if left_count == 1:
            img = np.transpose(img, (1, 0, 2))[:, ::-1, :]
        else:
            img = np.transpose(img, (1, 0, 2))[::-1, ::-1, :]
        return img

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
        mask = np.where((mask[:, :, 0] == 255) & (mask[:, :, 1] == 255) & (mask[:, :, 2] == 255), p_ones, p_zeroes)

        rows = np.where(np.count_nonzero(mask, 1) >= threshold)[0]
        cols = np.where(np.count_nonzero(mask, 0) >= threshold)[0]

        result_img = result_img[rows[0] * factor + chips[0] : rows[-1] * factor - chips[0], 
                                cols[0] * factor + chips[0] : cols[-1] * factor - chips[0]]

        cv2.imwrite(os.path.join(self.outs, filename), result_img)

        return result_img


    def rotate_image(self, image, DPI):
        factor = int(DPI // 600)
        resized_img = cv2.resize(image, (int(image.shape[1] // factor), int(image.shape[0] // factor)), interpolation=cv2.INTER_AREA)

        # We know image is 600DPI after resizing, thus getting the window in a static way
        window = cv2.cvtColor(resized_img[resized_img.shape[0] - 700 : , :], cv2.COLOR_BGR2GRAY)

        circles = cv2.HoughCircles(window, cv2.HOUGH_GRADIENT, 0.8, minDist=100, param1=11, param2=34, minRadius=22, maxRadius=31)

        holes = np.int64(circles)
        holes = np.flip(holes[0, np.argsort(holes[:, :, 1])[0]], axis=0)

        for hole in holes:
            cv2.circle(window, (hole[0], hole[1]), 22, (255, 255, 255), -1)
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
        factor = int(DPI // 600)
        resized_img = cv2.resize(image, (int(image.shape[1] // factor), int(image.shape[0] // factor)), interpolation=cv2.INTER_AREA)

        # getting the window for rotation-angle measurement
        window = cv2.cvtColor(resized_img[resized_img.shape[0] - 700 : resized_img.shape[0] - 400, :], cv2.COLOR_BGR2GRAY)

        circles = cv2.HoughCircles(window, cv2.HOUGH_GRADIENT, 0.8, minDist=100, param1=11, param2=34, minRadius=22, maxRadius=31)

        holes = np.int64(circles)
        holes = np.flip(holes[0, np.argsort(holes[:, :, 1])[0]], axis=0)
        for hole in holes:
            cv2.circle(window, (hole[0], hole[1]), 22, (255, 255, 255), -1)
        # plt.imshow(window)

        ref_point = [holes[0][0] * factor, (holes[0][1] + resized_img.shape[0] - 700) * factor]

        # shifting the real coords for considering hole1 as reference point or (0, 0)
        shifted_x = real_x - real_x[0]
        shifted_y = real_y - real_y[0]

        # getting pixel-based coords from real coords
        real_coords = np.array((shifted_x, shifted_y)).T
        real_converted = np.int64(real_coords * DPI // 25.4)

        # applying translations
        real_pix_x = real_converted[:, 0] + ref_point[0]
        real_pix_y = np.abs(ref_point[1] - real_converted[:, 1])
        coords_real_pix = np.array((real_pix_x, real_pix_y, names)).T

        return coords_real_pix


    def annotate_holes(self, image, holes, DPI, /, color1=(255, 255, 255), color2=(255, 255, 0), thickness1=3, radius=4, thickness2=-1, fontFace=cv2.FONT_HERSHEY_DUPLEX, fontScale=1, filename="All_Names.png"):
        if not filename.endswith('.png') and not filename.endswith('.jpg') and not filename.endswith('.jpeg'):
            return

        result_img = image.copy()
        
        for hole in holes:
            cv2.putText(result_img, str(hole[2].split('_')[0]), (int(hole[0]), int(hole[1])), fontFace, fontScale * (DPI // 600), color1, thickness1 * (DPI // 600))
            cv2.circle(result_img, (int(hole[0]), int(hole[1])), radius * (DPI // 600), color2, thickness2 * (DPI // 600))

        cv2.imwrite(os.path.join(self.outs, filename), result_img)
        return result_img


    def extract(self, image, holes, image_DPI, /, path="Conventionally_named_holes", offset=(100, 100)):
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

                Image.fromarray(cv2.cvtColor(final_img, cv2.COLOR_BGR2RGB)).save(f"{os.path.join(self.outs, path, hole[2])}.jpg", dpi=(image_DPI, image_DPI))
        except Exception as err:
            print(err)
            return False
        return True


    def get_vid(self, dir, filename):
        paths = glob.glob(os.path.join(self.outs, dir, '*.jpg'))
        # print(os.path.join(self.outs, dir), len(paths), paths)

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


    def get_area(self):
        my_model = YOLO(os.path.join(self.model_path, 'bestv8.pt'))
        DPI = None

        classes = []
        Area11 = [0] * 92
        Area1 = [0] * 92
        Area3 = [0] * 92
        Area5 = [0] * 92
        Area7 = [0] * 92
        Area9 = [0] * 92

        for idx, image_path in enumerate(glob.glob(os.path.join(self.outs, self.paths[0], '*.jpg'))):
            results = list(my_model(image_path, conf=0.5))
            result = results[0]
            box_vis = cv2.imread(image_path)

            if DPI is None:
                DPI = Image.open(image_path).info["dpi"][0]

            bxs = np.int64(result.boxes.xywh.cpu().numpy())
            test_list = result.boxes.cls.cpu().numpy().tolist()

            for box in bxs:
                cv2.rectangle(box_vis, (box[0] - box[2] // 2, box[1] - box[3] // 2), (box[0] + box[2] // 2, box[1] + box[3] // 2), (0, 0, 255), 3)

            rgb_img = cv2.cvtColor(box_vis, cv2.COLOR_BGR2RGB)
            pil_img = Image.fromarray(rgb_img)
            pil_img.save(os.path.join(self.outs, self.paths[1], os.path.basename(image_path)), dpi=(DPI, DPI))

            [classes.append(x) for x in test_list if x not in classes]

            if result.masks is not None:
                no = -1 if not (6 in classes) else classes.index(6)
                maskList = []
                [maskList.append((result.masks.data[int(a)].cpu().numpy() * 255).astype("uint8")) for a in range(len(result.masks.data)) if a != no]

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
        data_frame = pd.DataFrame(data)
        data_frame.to_csv(os.path.join(self.outs, "area.csv"))
        return data_frame