# -*- coding: utf-8 -*-
"""
Created on Wed Mar  8 12:16:09 2023

@author: joche
"""
import cv2
import numpy as np
img = cv2.imread('Uien.jpg')
scale_percent = 20 # percent of original size
width = int(img.shape[1] * scale_percent / 100)
height = int(img.shape[0] * scale_percent / 100)
dim = (width, height)
# resize image
resized = cv2.resize(img, dim, interpolation = cv2.INTER_AREA)

cropped_image = resized[100:730, 100:900]
cv2.imshow("cropped", cropped_image)
cv2.waitKey(0)
cv2.destroyAllWindows()