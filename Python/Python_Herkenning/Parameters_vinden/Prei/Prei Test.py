# -*- coding: utf-8 -*-
"""
Created on Wed Mar  8 12:48:15 2023

@author: joche
"""

import cv2
import numpy as np

# Load the image
img = cv2.imread('Prei.jpg')
scale_percent = 20 # percent of original size
width = int(img.shape[1] * scale_percent / 100)
height = int(img.shape[0] * scale_percent / 100)
dim = (width, height)
# resize image
resized = cv2.resize(img, dim, interpolation = cv2.INTER_AREA)
cropped_image = resized[100:500, 0:600]
# Convert to grayscale
gray = cv2.cvtColor(cropped_image, cv2.COLOR_BGR2GRAY)

# Apply a Gaussian blur to reduce noise
blur = cv2.GaussianBlur(gray, (11, 7), 0)

# Apply adaptive thresholding to obtain a binary image
thresh = cv2.adaptiveThreshold(blur, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY_INV, 11, 2)

# Find contours in the binary image
contours, hierarchy = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
print(contours)
# Draw contours on the original image
cv2.drawContours(cropped_image, contours, -1, (0, 0, 255), 2)

# Display the result
cv2.imshow('leak detection', cropped_image)
key = cv2.waitKey(0)
cv2.destroyAllWindows()
    