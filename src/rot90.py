import cv2
import numpy as np
import os

img = cv2.imread(os.path.join(os.path.abspath(os.path.relpath('resources')), 'FED_008.jpeg'), cv2.IMREAD_COLOR)
img = np.rot90(img, axes=(0, 1))
cv2.imwrite(os.path.join(os.path.abspath(os.path.relpath('resources')), 'FED_008_vertical.jpeg'), img)