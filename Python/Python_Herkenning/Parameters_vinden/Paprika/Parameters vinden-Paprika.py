# -*- coding: utf-8 -*-
"""
Created on Wed Mar  8 11:12:14 2023

@author: joche
"""

import cv2
import numpy as np
from scipy import ndimage as ndi
import imutils
# --- functions ---

def change_sensitivity(value):
    global sensitivity  # inform function to assign value to global variable instead of local variable
    
    sensitivity = value
    #print('sensitivity:', sensitivity)
    
# --- main ---

sensitivity = 30   # global variable

baseimg = cv2.imread(r'Paprika.jpg')
scale_percent = 20 # percent of original size
width = int(baseimg.shape[1] * scale_percent / 100)
height = int(baseimg.shape[0] * scale_percent / 100)
dim = (width, height)
# resize image
resized = cv2.resize(baseimg, dim, interpolation = cv2.INTER_AREA)
cropped_image = resized[50:600, 100:600]
gray = cv2.cvtColor(cropped_image,cv2.COLOR_BGR2GRAY)
imgblur=cv2.medianBlur(gray,1)#Blur filter over de bais afbeelding
ret,thresh = cv2.threshold(imgblur,127,255,0)
im2,contours,hierarchy = cv2.findContours(thresh, 1, 2)
cnt = contours[0]
M = cv2.moments(cnt)
print( M )


def nothing(x):
    pass

cv2.namedWindow('img')
# cv2.namedWindow('edges')
cv2.namedWindow('contour')
cv2.createTrackbar('minThres','contour',255,255,nothing)
cv2.createTrackbar('maxThres','contour',0,255,nothing)
# cv2.createTrackbar('para1','image',50,500,nothing)
# cv2.createTrackbar('para2','image',100,500,nothing)

# # dp=2
# # param1= 
# # param2= 1

while True:
    minThres = cv2.getTrackbarPos('minThres','contour')
    maxThres = cv2.getTrackbarPos('maxThres','contour')
    # edges = cv2.Canny(imgblur,para1,para2)#randen detecteren van de afbeelding
    frame = resized.copy()
    thresh = cv2.adaptiveThreshold(imgblur, minThres, cv2.ADAPTIVE_THRESH_MEAN_C,cv2.THRESH_BINARY, 21, 1)


    key = cv2.waitKey(1)
    if key == 27:  # ESC
        break
        
