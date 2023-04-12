# -*- coding: utf-8 -*-
"""
Created on Mon Mar  6 11:39:41 2023

@author: joche
"""

import cv2
import numpy as np
from PIL import Image, ImageFilter
from scipy import ndimage as ndi
  
Baseimage = cv2.imread("Tomaten.jpg")#basis afbeelding
scale_percent = 20 # percent of original size
width = int(Baseimage.shape[1] * scale_percent / 100)
height = int(Baseimage.shape[0] * scale_percent / 100)
dim = (width, height)
# resize image
resized = cv2.resize(Baseimage, dim, interpolation = cv2.INTER_AREA)
gray = cv2.cvtColor(resized,cv2.COLOR_BGR2GRAY)
img=cv2.medianBlur(gray,7)#Blur filter over de bais afbeelding
assert Baseimage is not None, "file could not be read, check with os.path.exists()"
edges = cv2.Canny(img,50,100)#randen detecteren van de afbeelding
fill_holes = ndi.binary_fill_holes(edges)
#cv2.imshow('auto edges',fill_holes)
# def auto_canny_edge_detection(image, sigma=0.6):
#     md = np.median(image)
#     lower_value = int(max(0, (1.0-sigma) * md))
#     upper_value = int(min(255, (1.0+sigma) * md))
#     return cv2.Canny(image, lower_value, upper_value)

#auto_edge = auto_canny_edge_detection(edges)

circles = cv2.HoughCircles(edges,cv2.HOUGH_GRADIENT,1,20,param1=50,param2=30,minRadius=10,maxRadius=53)
if circles is not None:
    circles = np.uint16(np.around(circles))
    for i in circles[0,:]:
        # draw the outer circle
        cv2.circle(resized,(i[0],i[1]),i[2],(0,255,0),2)
        # draw the center of the circle
        cv2.circle(resized,(i[0],i[1]),2,(0,0,255),3)
        font = cv2.FONT_HERSHEY_SIMPLEX
        x=i[0]
        y=i[1]
        print(x,y)
        cv2.putText(Baseimage,'Volle Fles',(i[0]-70,i[1]-50), font, 1,(255,255,255),2,cv2.LINE_AA)
#cv2.imshow('auto edges',auto_edge)
cv2.imshow('image edges',edges)
cv2.imshow('image',resized)
cv2.imwrite('TomaatDetc.jpg',Baseimage)
k = cv2.waitKey(0)
if k == 27:         # wait for ESC key to exit
    cv2.destroyAllWindows()