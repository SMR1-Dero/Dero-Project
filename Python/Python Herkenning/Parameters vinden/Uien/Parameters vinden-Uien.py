# -*- coding: utf-8 -*-
"""
Created on Wed Mar  8 11:12:14 2023

@author: joche
"""

import cv2
import numpy as np
from scipy import ndimage as ndi
# --- functions ---

def change_sensitivity(value):
    global sensitivity  # inform function to assign value to global variable instead of local variable
    
    sensitivity = value
    #print('sensitivity:', sensitivity)
    
# --- main ---

sensitivity = 30   # global variable

baseimg = cv2.imread(r'Uien.jpg')
scale_percent = 20 # percent of original size
width = int(baseimg.shape[1] * scale_percent / 100)
height = int(baseimg.shape[0] * scale_percent / 100)
dim = (width, height)
# resize image
resized = cv2.resize(baseimg, dim, interpolation = cv2.INTER_AREA)
cropped_image = resized[100:730, 100:800]
gray = cv2.cvtColor(cropped_image,cv2.COLOR_BGR2GRAY)
imgblur=cv2.medianBlur(gray,3)#Blur filter over de bais afbeelding




def nothing(x):
    pass

cv2.namedWindow('image')
cv2.namedWindow('Blur')
cv2.createTrackbar('mindist','image',65,100,nothing)
cv2.createTrackbar('minRadius','image',31,100,nothing)
cv2.createTrackbar('maxRadius','image',46,100,nothing)


while True:
    mindist = cv2.getTrackbarPos('mindist','image')
    minRadius = cv2.getTrackbarPos('minRadius','image')
    maxRadius = cv2.getTrackbarPos('maxRadius','image')
    # para1 = cv2.getTrackbarPos('para1','image')
    # para2 = cv2.getTrackbarPos('para2','image')
    # edges = cv2.Canny(imgblur,para1,para2)#randen detecteren van de afbeelding
    frame = cropped_image.copy()
    # #if frame is not None:
    # low_green = (60 - sensitivity, 100, 50)  
    # high_green= (60 + sensitivity, 255, 255)
        
    # hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # mask = cv2.inRange(hsv, low_green, high_green)
    # mask = cv2.bitwise_not(mask)
        
    # frame = cv2.bitwise_and(frame, frame, mask=mask)

    circles = cv2.HoughCircles(imgblur,cv2.HOUGH_GRADIENT,1.2,minDist=mindist,param1=50,param2=30,minRadius=minRadius,maxRadius=maxRadius)
    if circles is not None:
        circles = np.uint16(np.around(circles))
        for i in circles[0,:]:
            # draw the outer circle
            cv2.circle(frame,(i[0],i[1]),i[2],(0,255,0),2)
        # draw the center of the circle
            cv2.circle(frame,(i[0],i[1]),2,(0,0,255),3)
            print(circles)
    
    cv2.imshow('image', frame)
    # cv2.imshow('edges', edges)
    cv2.imshow('Blur', imgblur) 
    cv2.waitKey(100)
    frame = cropped_image.copy()

    key = cv2.waitKey(1)
    if key == 27:  # ESC
        break
        
cv2.destroyAllWindows()