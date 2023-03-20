# -*- coding: utf-8 -*-
"""
Created on Thu Mar  9 15:22:36 2023

@author: joche
"""

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

def nothing(x):
    pass

# Create windows
cv2.namedWindow("Made frame")
cv2.namedWindow("Color frame")

# cv2.createTrackbar('Edgdemin','Made frame',0,400,nothing)
# cv2.createTrackbar('Edgdemax','Made frame',150,500,nothing)
# cv2.createTrackbar('Radmin','Made frame',15,100,nothing)
# cv2.createTrackbar('Radmax','Made frame',30,200,nothing)

def getpointtomaat(depth_frame,color_frame):
    coordinates=[]
    font = cv2.FONT_HERSHEY_SIMPLEX
    pointi=None
    distance=None
    # Show distance for a specific point
    hsv = cv2.cvtColor(color_frame, cv2.COLOR_BGR2HSV)
    #set the lower and upper bounds for the green hue
    lower_red = np.array([0,80,80])
    upper_red = np.array([70,255,255])
    #create a mask for green colour using inRange function
    mask = cv2.inRange(hsv, lower_red, upper_red)
    res = cv2.bitwise_and(color_frame, color_frame, mask=mask)
    #beeldbewerking
    gray = cv2.cvtColor(res,cv2.COLOR_BGR2GRAY)
    imgblur=cv2.medianBlur(gray,1)#Blur filter over de bais afbeelding
   # edges = cv2.Canny(imgblur,200,100)
    circles = cv2.HoughCircles(imgblur,cv2.HOUGH_GRADIENT,2,minDist=15,param1=50,param2=30,minRadius=14,maxRadius=25)#hier aanpassingen aan maken voor filtering
    #print(circles)
    if circles is not None:
        circles = np.uint16(np.around(circles))
        for i in circles[0,:]:
            # draw the outer circle
            cv2.circle(color_frame,(i[0],i[1]),i[2],(0,255,0),2)
            # draw the center of the circle
            cv2.circle(color_frame,(i[0],i[1]),2,(0,0,255),3)
            pointi=(i[0],i[1])
            distance = mean_distance(depth_frame,pointi)
            coordinates.append([pointi,distance])
            cv2.putText(color_frame, "{}mm".format(distance), (pointi[0], pointi[1] - 20), cv2.FONT_HERSHEY_PLAIN, 2, (0, 0, 0), 2)
    
    return color_frame,coordinates,imgblur
def mean_distance(depth_frame,point):
    deler=0
    height=0
    mean_height=0
    for i in range(-1,1):
        for j in range(-1,1):
            height=depth_frame[point[1]+j, point[0]+i]
            if (height != 0):
                mean_height+=height
                deler+=1
            j+=1
        i+=1
    return (int(mean_height/deler))
# while True:
# Edgdemin = cv2.getTrackbarPos('Edgdemin','Made frame')
# Edgdemax = cv2.getTrackbarPos('Edgdemax','Made frame')
# Radmin = cv2.getTrackbarPos('Radmin','Made frame')
# Radmax = cv2.getTrackbarPos('Radmax','Made frame')
def getframe():
    ret, depth_frame, color_frame = dc.get_frame()
    depth_frame = depth_frame[50:500, 220:500]
    color_frame = color_frame[50:500, 220:500]   
    #cv2.imwrite("test_foto_tomaten.jpg",color_frame)
    return (depth_frame,color_frame)
def find_high_points(depth_frame):
    height=0
    save_height=0
    pos=(0,0)
    for i in 450:
        for j in 215:
            height=depth_frame[j, i]
            if height>save_height:
                save_height=height
                pos=(i,j)
    return save_height,pos
    
depth,color=getframe()
madeframe,coor,ed=getpointtomaat(depth,color)
while coor==[]:
    depth,color=getframe()
    madeframe,coor,ed=getpointtomaat(depth,color)
    cv2.imshow("Made frame", madeframe)
    cv2.imshow("Color frame", ed)
    cv2.waitKey(500)
    key = cv2.waitKey(10)
    if key == 27:  # ESC
        break
#maxheight,pos=find_high_points(depth)
print(coor)
cv2.imshow("Made frame", madeframe)
cv2.imshow("Color frame", ed)
key = cv2.waitKey(0)
#if key == 27:
#        break
cv2.destroyAllWindows()