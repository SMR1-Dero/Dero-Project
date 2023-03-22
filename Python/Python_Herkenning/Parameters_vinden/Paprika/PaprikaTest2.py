# -*- coding: utf-8 -*-
"""
Created on Wed Mar  8 16:10:46 2023

@author: joche
"""

import cv2
import numpy as np
from matplotlib import pyplot as plt
import pyrealsense2
from realsense_depth import *
font = cv2.FONT_HERSHEY_SIMPLEX
# Initialize Camera Intel Realsense
#dc = DepthCamera()

point = (400, 300)

def show_distance(event, x, y, args, params):
    global point
    point = (x, y)
    
def nothing(x):
    pass


#---Afstel bars
distance=0
#ret, depth_frame, color_frame = dc.get_frame()

img = cv2.imread(r'Paprika.jpg')
scale_percent = 20 # percent of original size
width = int(img.shape[1] * scale_percent / 100)
height = int(img.shape[0] * scale_percent / 100)
dim = (width, height)
# # resize image
resized = cv2.resize(img, dim, interpolation = cv2.INTER_AREA)
gray = cv2.cvtColor(resized, cv2.COLOR_BGR2GRAY)
ret,thresh1 = cv2.threshold(gray,70,75,cv2.THRESH_BINARY)
    
(ret, thresh) = cv2.threshold(gray, 10, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
edge = cv2.Canny(thresh1, 100, 200)
(cnts, _) = cv2.findContours(edge.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    
total = 0
for c in cnts:
    epsilon = 0.005 * cv2.arcLength(c, True)
    approx = cv2.approxPolyDP(c, epsilon, True)

    cv2.drawContours(resized, [approx], -1, (0, 255, 0), 4)
    total += 1

print ("I found {0} RET in that image".format(total))
cv2.imshow("Output2", thresh1)
cv2.imshow("Output", resized)
cv2.waitKey(0)
cv2.destroyAllWindows()
