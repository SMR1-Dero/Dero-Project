import cv2
import numpy as np
import copy

# Read in the camera footage
original_image_unsized = cv2.imread("Python/Python Herkenning/Parameters vinden/Testing_mart/courgettes.jpeg")

original_image = cv2.resize(original_image_unsized, (480,640))