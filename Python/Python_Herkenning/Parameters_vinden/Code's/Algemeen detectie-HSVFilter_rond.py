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


def show_distance(event, x, y, args, params):
    global point
    point = (x, y)

def nothing(x):
    pass

def getframe():
    ret, depth_frame, color_frame = dc.get_frame()   
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

def image_edits(color_frame,hsvunder1,hsvunder2,hsvunder3,hsvupper1,hsvupper2,hsvupper3):
    hsv = cv2.cvtColor(color_frame, cv2.COLOR_BGR2HSV)
    #set the lower and upper bounds for the HSV
    lower_red = np.array([hsvunder1,hsvunder2,hsvunder3])
    upper_red = np.array([hsvupper1,hsvupper2,hsvupper3])
    # lower_red = np.array([0,80,90])
    # upper_red = np.array([255,255,255])
    #create a mask for the colour using inRange function
    mask = cv2.inRange(hsv, lower_red, upper_red)
    res = cv2.bitwise_and(color_frame, color_frame, mask=mask)
    #make image gray 
    gray = cv2.cvtColor(res,cv2.COLOR_BGR2GRAY)
    #find the contours
    (cnts, _) = cv2.findContours(gray.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    return gray,cnts

def getpoint(depth_frame,color_frame,hsvunder1,hsvunder2,hsvunder3,hsvupper1,hsvupper2,hsvupper3):
    coordinates=[]
    pointi=None
    distance=None
    gray,cnts=image_edits(color_frame,hsvunder1,hsvunder2,hsvunder3,hsvupper1,hsvupper2,hsvupper3)
    circles = cv2.HoughCircles(gray,cv2.HOUGH_GRADIENT,2,minDist=15,param1=50,param2=30,minRadius=15,maxRadius=20)#hier aanpassingen aan maken voor filtering
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
    
    return color_frame,coordinates,gray
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
    if (deler==0):
        return 0
    else :
        return (int(mean_height/deler))
# while True:

def makeframe():
    # Create windows
    cv2.namedWindow("Made frame")
    cv2.namedWindow("Color frame")
    cv2.namedWindow("Trackbar")
    #create
    cv2.createTrackbar('hsvunder1','Trackbar',0,255,nothing)
    cv2.createTrackbar('hsvunder2','Trackbar',80,255,nothing)
    cv2.createTrackbar('hsvunder3','Trackbar',80,255,nothing)
    cv2.createTrackbar('hsvupper1','Trackbar',10,255,nothing)
    cv2.createTrackbar('hsvupper2','Trackbar',255,255,nothing)
    cv2.createTrackbar('hsvupper3','Trackbar',255,255,nothing)
    
def readtrackbar():
    hsvunder1 = cv2.getTrackbarPos('hsvunder1','Trackbar')
    hsvunder2 = cv2.getTrackbarPos('hsvunder2','Trackbar')
    hsvunder3 = cv2.getTrackbarPos('hsvunder3','Trackbar')
    hsvupper1 = cv2.getTrackbarPos('hsvupper1','Trackbar')
    hsvupper2 = cv2.getTrackbarPos('hsvupper2','Trackbar')
    hsvupper3 = cv2.getTrackbarPos('hsvupper3','Trackbar')
    return hsvunder1,hsvunder2,hsvunder3,hsvupper1,hsvupper2,hsvupper3


# Initialize Camera Intel Realsense
dc = DepthCamera()
depth,color=getframe()
#create trackbar
makeframe()

while True:
    #read info from trackbars
    hsvunder1,hsvunder2,hsvunder3,hsvupper1,hsvupper2,hsvupper3=readtrackbar()
    #get depth and color frame
    depth,color=getframe()
    #Use filters and circle detection to get center coordinate
    madeframe,coor,ed=getpoint(depth,color,hsvunder1,hsvunder2,hsvunder3,hsvupper1,hsvupper2,hsvupper3)
    print(coor)
    #show edited and original frame with contours and center
    cv2.imshow("Made frame", madeframe)
    cv2.imshow("Color frame", ed)
    cv2.imshow("Trackbar",ed)
    cv2.waitKey(100)
    key = cv2.waitKey(1)
    if key == 27:  # ESC
        break
#maxheight,pos=find_high_points(depth)
key = cv2.waitKey(0)
#if key == 27:
#        break
cv2.destroyAllWindows()