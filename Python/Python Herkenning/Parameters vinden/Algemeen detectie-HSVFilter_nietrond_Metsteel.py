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

def getpointpaprika(depth_frame,color_frame,hsvunder1,hsvunder2,hsvunder3,hsvupper1,hsvupper2,hsvupper3):
    coordinates=[]
    cx=0
    cy=0
    t=0
    j=0
    loc1=[]
    pointi=(10,10)
    distance=None
    mask,cnts=image_edits(color_frame,0,80,30,255,255,255)
    mask2,cnts2=image_edits(color_frame,hsvunder1,hsvunder2,hsvunder3,hsvupper1,hsvupper2,hsvupper3)#5,74,40,45,215,125
    for i in cnts2:
        area= cv2.contourArea(i)
        #print (area)
        if area>50:
            M = cv2.moments(i)
            # Calculate the moments
            if M['m00'] != 0:
                cx = int(M['m10']/M['m00'])
                cy = int(M['m01']/M['m00'])
                #cv2.circle(color_frame, (cx, cy), 7, (255, 0, 0), -1)
                epsilon = 0.005 * cv2.arcLength(i, True)
                approx = cv2.approxPolyDP(i, epsilon, True)
                cv2.drawContours(color_frame, [approx], -1, (255, 255, 0), 4)
                loc1.append([(cx),(cy)])

    number=2
    for c in cnts:
        area= cv2.contourArea(c)
        if area>1000:
            M = cv2.moments(c)
            #print ("Area=",area)
            # Calculate the moments
            if M['m00'] != 0:
                cx = int(M['m10']/M['m00'])
                cy = int(M['m01']/M['m00'])
                #print(loc1)
                for j in range(len(loc1)):
                    if (abs(cx-loc1[j][0])<=25 and abs(cy-loc1[j][1])<=25):   
                        cv2.circle(color_frame, (cx+number*(cx-loc1[j][0]), cy+number*(cy-loc1[j][1])), 7, (0, 0, 255), -1)
                        pointi=(cx+number*(cx-loc1[j][0]),cy+number*(cy-loc1[j][1]))
                        #bepalen van afstand en pixel coordinaat
                        distance = mean_distance(depth_frame,pointi)
                        coordinates.append([pointi,distance])
                        #tekenen van centrun en contour
                        cv2.putText(color_frame, "{}mm".format(distance), (pointi[0], pointi[1]- 40 ), cv2.FONT_HERSHEY_PLAIN, 2, (0, 0, 0), 2)
                        epsilon = 0.005 * cv2.arcLength(c, True)
                        approx = cv2.approxPolyDP(c, epsilon, True)
                        cv2.drawContours(color_frame, [approx], -1, (0, 255, 0), 4)
                    else:
                        cv2.circle(color_frame, (cx, cy), 7, (0, 0, 255), -1)
                        pointi=(cx,cy)
                        #bepalen van afstand en pixel coordinaat
                        distance = mean_distance(depth_frame,pointi)
                        coordinates.append([pointi,distance])
                        #tekenen van centrun en contour
                        cv2.putText(color_frame, "{}mm".format(distance), (pointi[0], pointi[1] - 40), cv2.FONT_HERSHEY_PLAIN, 2, (0, 0, 0), 2)
                        epsilon = 0.005 * cv2.arcLength(c, True)
                        approx = cv2.approxPolyDP(c, epsilon, True)
                        cv2.drawContours(color_frame, [approx], -1, (0, 255, 0), 4)
                    
                if (loc1==[]):
                    cv2.circle(color_frame, (cx, cy), 7, (0, 0, 255), -1)
                    pointi=(cx,cy)
                    #bepalen van afstand en pixel coordinaat
                    distance = mean_distance(depth_frame,pointi)
                    coordinates.append([pointi,distance])
                    #tekenen van centrun en contour
                    cv2.putText(color_frame, "{}mm".format(distance), (pointi[0], pointi[1] - 40), cv2.FONT_HERSHEY_PLAIN, 2, (0, 0, 0), 2)
                    epsilon = 0.005 * cv2.arcLength(c, True)
                    approx = cv2.approxPolyDP(c, epsilon, True)
                    cv2.drawContours(color_frame, [approx], -1, (0, 255, 0), 4)
    print(coordinates)

    return color_frame,coordinates,mask2
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



# Create windows
cv2.namedWindow("Made frame")
cv2.namedWindow("Color frame")
cv2.namedWindow("Trackbar")

cv2.createTrackbar('hsvunder1','Trackbar',5,255,nothing)#5,74,40,45,215,125
cv2.createTrackbar('hsvunder2','Trackbar',75,255,nothing)
cv2.createTrackbar('hsvunder3','Trackbar',40,255,nothing)
cv2.createTrackbar('hsvupper1','Trackbar',45,255,nothing)
cv2.createTrackbar('hsvupper2','Trackbar',215,255,nothing)
cv2.createTrackbar('hsvupper3','Trackbar',125,255,nothing)
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
#print(coor)
cv2.imshow("Made frame", madeframe)
cv2.imshow("Color frame", ed)

while True:
    hsvunder1 = cv2.getTrackbarPos('hsvunder1','Trackbar')
    hsvunder2 = cv2.getTrackbarPos('hsvunder2','Trackbar')
    hsvunder3 = cv2.getTrackbarPos('hsvunder3','Trackbar')
    hsvupper1 = cv2.getTrackbarPos('hsvupper1','Trackbar')
    hsvupper2 = cv2.getTrackbarPos('hsvupper2','Trackbar')
    hsvupper3 = cv2.getTrackbarPos('hsvupper3','Trackbar')
    
    depth,color=getframe()
    madeframe,coor,ed=getpointpaprika(depth,color,hsvunder1,hsvunder2,hsvunder3,hsvupper1,hsvupper2,hsvupper3)
    #print(coor)
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