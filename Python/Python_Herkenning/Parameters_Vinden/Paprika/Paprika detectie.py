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

def getpointpaprika(depth_frame,color_frame,hsvunder1,hsvunder2,hsvunder3,hsvupper1,hsvupper2,hsvupper3):
    coordinates=[]
    font = cv2.FONT_HERSHEY_SIMPLEX
    pointi=None
    distance=None
    # Show distance for a specific point
    hsv = cv2.cvtColor(color_frame, cv2.COLOR_BGR2HSV)
    #set the lower and upper bounds for the green hue
    lower_red = np.array([hsvunder1,hsvunder2,hsvunder3])
    upper_red = np.array([hsvupper1,hsvupper2,hsvupper3])
    # lower_red = np.array([0,80,80])
    # upper_red = np.array([1,255,220])
    #create a mask for green colour using inRange function
    mask = cv2.inRange(hsv, lower_red, upper_red)
    res = cv2.bitwise_and(color_frame, color_frame, mask=mask)
    #beeldbewerking
    gray = cv2.cvtColor(res,cv2.COLOR_BGR2GRAY)
    imgblur=cv2.medianBlur(gray,1)#Blur filter over de bais afbeelding
   # edges = cv2.Canny(imgblur,200,100)
    #circles = cv2.HoughCircles(imgblur,cv2.HOUGH_GRADIENT,2,minDist=15,param1=50,param2=30,minRadius=14,maxRadius=25)#hier aanpassingen aan maken voor filtering
    #print(circles)
    ret,thresh1 = cv2.threshold(gray,70,75,cv2.THRESH_BINARY)
        
    (ret, thresh) = cv2.threshold(gray, 10, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
    edge = cv2.Canny(thresh1, 100, 200)
    (cnts, _) = cv2.findContours(gray.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        
    total = 0
    for c in cnts:
        epsilon = 0.005 * cv2.arcLength(c, True)
        approx = cv2.approxPolyDP(c, epsilon, True)

        cv2.drawContours(color_frame, [approx], -1, (0, 255, 0), 4)
        total += 1

            #distance = mean_distance(depth_frame,pointi)
            #coordinates.append([pointi,distance])
        #cv2.putText(color_frame, "{}mm".format(distance), (pointi[0], pointi[1] - 20), cv2.FONT_HERSHEY_PLAIN, 2, (0, 0, 0), 2)
    
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



# Create windows
cv2.namedWindow("Made frame")
cv2.namedWindow("Color frame")
cv2.namedWindow("Trackbar")

cv2.createTrackbar('hsvunder1','Trackbar',0,255,nothing)
cv2.createTrackbar('hsvunder2','Trackbar',150,255,nothing)
cv2.createTrackbar('hsvunder3','Trackbar',150,255,nothing)
cv2.createTrackbar('hsvupper1','Trackbar',15,255,nothing)
cv2.createTrackbar('hsvupper2','Trackbar',30,255,nothing)
cv2.createTrackbar('hsvupper3','Trackbar',30,255,nothing)
point = (400, 300)
# Initialize Camera Intel Realsense
dc = DepthCamera()
    
depth,color=getframe()
hsvunder1 = cv2.getTrackbarPos('hsvunder1','Trackbar')
hsvunder2 = cv2.getTrackbarPos('hsvunder2','Trackbar')
hsvunder3 = cv2.getTrackbarPos('hsvunder3','Trackbar')
hsvupper1 = cv2.getTrackbarPos('hsvupper1','Trackbar')
hsvupper2 = cv2.getTrackbarPos('hsvupper2','Trackbar')
hsvupper3 = cv2.getTrackbarPos('hsvupper3','Trackbar')

madeframe,coor,ed=getpointpaprika(depth,color,hsvunder1,hsvunder2,hsvunder3,hsvupper1,hsvupper2,hsvupper3)
print(coor)
cv2.imshow("Made frame", madeframe)
cv2.imshow("Color frame", ed)

while coor==[]:
    hsvunder1 = cv2.getTrackbarPos('hsvunder1','Trackbar')
    hsvunder2 = cv2.getTrackbarPos('hsvunder2','Trackbar')
    hsvunder3 = cv2.getTrackbarPos('hsvunder3','Trackbar')
    hsvupper1 = cv2.getTrackbarPos('hsvupper1','Trackbar')
    hsvupper2 = cv2.getTrackbarPos('hsvupper2','Trackbar')
    hsvupper3 = cv2.getTrackbarPos('hsvupper3','Trackbar')
    
    depth,color=getframe()
    madeframe,coor,ed=getpointpaprika(depth,color,hsvunder1,hsvunder2,hsvunder3,hsvupper1,hsvupper2,hsvupper3)
    cv2.imshow("Made frame", madeframe)
    cv2.imshow("Color frame", ed)
    cv2.imshow("Trackbar",ed)
    cv2.waitKey(10)
    key = cv2.waitKey(1)
    if key == 27:  # ESC
        break
#maxheight,pos=find_high_points(depth)
key = cv2.waitKey(0)
#if key == 27:
#        break
cv2.destroyAllWindows()