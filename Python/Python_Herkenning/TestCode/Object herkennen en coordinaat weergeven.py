# -*- coding: utf-8 -*-
"""
Created on Mon Mar  6 10:08:10 2023

@author: joche
"""

import cv2
import pyrealsense2
import numpy as np
import time
from realsense_depth import *

point = (400, 300)

def show_distance(event, x, y, args, params):
    global point
    point = (x, y)

# Initialize Camera Intel Realsense
dc = DepthCamera()

# Create mouse event
cv2.namedWindow("Color frame")
pointi=(0,0)

while True:
    ret, depth_frame, color_frame = dc.get_frame()
    
    # Show distance for a specific point
    distance = depth_frame[pointi[1], pointi[0]]
    #beeldbewerking
    frame=cv2.medianBlur(color_frame,3)#Blur filter over de bais afbeelding
    edges=edges = cv2.Canny(frame,200,300)#randen detecteren van de afbeelding
    circles = cv2.HoughCircles(edges,cv2.HOUGH_GRADIENT,1,20,param1=50,param2=30,minRadius=1,maxRadius=200)
    if circles is not None:
        circles = np.uint16(np.around(circles))
        for i in circles[0,:]:
            # draw the outer circle
            cv2.circle(color_frame,(i[0],i[1]),i[2],(0,255,0),2)
            # draw the center of the circle
            cv2.circle(color_frame,(i[0],i[1]),2,(0,0,255),3)
            font = cv2.FONT_HERSHEY_SIMPLEX
            pointi=(i[0],i[1])
            print(pointi)
    
    cv2.putText(color_frame, "{}mm".format(distance), (pointi[0], pointi[1] - 20), cv2.FONT_HERSHEY_PLAIN, 2, (0, 0, 0), 2)

    cv2.imshow("Color frame", color_frame)
    key = cv2.waitKey(1)
    if key == 27:
        break
cv2.destroyAllWindows()