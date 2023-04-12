
import cv2
import numpy as np
from scipy import ndimage as ndi
import pyrealsense2
from realsense_depth import *

# --- main ---
font = cv2.FONT_HERSHEY_SIMPLEX
# Initialize Camera Intel Realsense
dc = DepthCamera()

point = (400, 300)

def show_distance(event, x, y, args, params):
    global point
    point = (x, y)
    
def nothing(x):
    pass


#---Afstel bars
cv2.namedWindow('image')
#cv2.namedWindow('Blur')
# cv2.createTrackbar('mindist','image',40,100,nothing)
# cv2.createTrackbar('minRadius','image',20,100,nothing)
# cv2.createTrackbar('maxRadius','image',50,100,nothing)

def getdepth():
    distance=0
    ret, depth_frame, color_frame = dc.get_frame()
    #---Afstel bars
    # mindist = cv2.getTrackbarPos('mindist','image')
    # minRadius = cv2.getTrackbarPos('minRadius','image')
    # maxRadius = cv2.getTrackbarPos('maxRadius','image')
    #--- coordinaten
    cordinates=[]
    #---beeldbewerking
    
    gray = cv2.cvtColor(color_frame,cv2.COLOR_BGR2GRAY)
    imgblur=cv2.medianBlur(gray,7)#Blur filter over de bais afbeelding
    frame = color_frame.copy()
    circles = cv2.HoughCircles(imgblur,cv2.HOUGH_GRADIENT,1,minDist=40,param1=50,param2=30,minRadius=20,maxRadius=50)
    if circles is not None:
        circles = np.uint16(np.around(circles))
        for i in circles[0,:]:
            # draw the outer circle
            cv2.circle(frame,(i[0],i[1]),i[2],(0,255,0),2)
        # draw the center of the circle
            cv2.circle(frame,(i[0],i[1]),2,(0,0,255),3)
            pointi=(i[0],i[1])
            distance = depth_frame[pointi[1], pointi[0]]
            cordinates.append([pointi,distance])
            cv2.putText(frame, "{}mm".format(distance), (pointi[0], pointi[1] - 20), cv2.FONT_HERSHEY_PLAIN, 2, (0, 0, 0), 2)       
    return frame,cordinates

madeframe,loc=getdepth()
print(loc)
cv2.imshow('image', madeframe)
# cv2.imshow('edges', edges)
#cv2.imshow('Blur', imgblur) 
cv2.waitKey(10)
#frame = color_frame.copy()

key = cv2.waitKey(0)

        
cv2.destroyAllWindows()