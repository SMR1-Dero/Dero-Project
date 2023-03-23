# -*- coding: utf-8 -*-
"""
Created on Tue Mar 14 14:07:45 2023

@author: joche
"""

# -*- coding: utf-8 -*-
"""
Created on Mon Mar  6 10:08:10 2023

@author: joche
"""

import cv2
import pyrealsense2 as rs
import numpy as np
import time
import copy
from realsense_depth import *


def show_distance(event, x, y, args, params):
    global point
    point = (x, y)
def nothing(x):
    pass
def getframe(pipeline,crop):
    # Wait for a new set of frames from the pipeline
    frames = pipeline.wait_for_frames()
    
    # Retrieve the depth and color frames
    depth_frame_full = frames.get_depth_frame()
    color_frame_full = frames.get_color_frame()
    
    # Convert the frames to numpy arrays
    depth_frame_np = copy.deepcopy(np.asanyarray(depth_frame_full.get_data()))
    color_frame_np = copy.deepcopy(np.asanyarray(color_frame_full.get_data()))

    # Crop the frames
    depth_frame_cut = depth_frame_np[crop[0]:crop[1],crop[2]:crop[3]]
    color_frame_cut = color_frame_np[crop[0]:crop[1],crop[2]:crop[3]]

    # Return the cropped depth and color frames, as well as the full color frame
    return depth_frame_cut, color_frame_cut, np.asanyarray(color_frame_full.get_data())
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
def makeframe():
    # Create windows
    cv2.namedWindow("bewerkt frame")
    cv2.namedWindow("Origineel frame")
    cv2.namedWindow("Grijs frame")
    cv2.namedWindow("gray frame")
    #create
    cv2.createTrackbar('hsvunder1','Grijs frame',0,255,nothing)
    cv2.createTrackbar('hsvunder2','Grijs frame',80,255,nothing)
    cv2.createTrackbar('hsvunder3','Grijs frame',80,255,nothing)
    cv2.createTrackbar('hsvupper1','Grijs frame',10,255,nothing)
    cv2.createTrackbar('hsvupper2','Grijs frame',255,255,nothing)
    cv2.createTrackbar('hsvupper3','Grijs frame',255,255,nothing) 
    cv2.createTrackbar('minsize','Grijs frame',10,100,nothing)
    cv2.createTrackbar('maxsize','Grijs frame',50,100,nothing)  
def readtrackbar():
    hsvunder1 = cv2.getTrackbarPos('hsvunder1','Grijs frame')
    hsvunder2 = cv2.getTrackbarPos('hsvunder2','Grijs frame')
    hsvunder3 = cv2.getTrackbarPos('hsvunder3','Grijs frame')
    hsvupper1 = cv2.getTrackbarPos('hsvupper1','Grijs frame')
    hsvupper2 = cv2.getTrackbarPos('hsvupper2','Grijs frame')
    hsvupper3 = cv2.getTrackbarPos('hsvupper3','Grijs frame')
    minsize = cv2.getTrackbarPos('minsize','Grijs frame')
    maxsize = cv2.getTrackbarPos('maxsize','Grijs frame')
    return hsvunder1,hsvunder2,hsvunder3,hsvupper1,hsvupper2,hsvupper3,minsize,maxsize
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
def getpoint_tomato(depth_frame,color_frame,hsvunder1,hsvunder2,hsvunder3,hsvupper1,hsvupper2,hsvupper3,minsize,maxsize):
    coordinates=[]
    pointi=None
    distance=None
    gray,cnts=image_edits(color_frame,hsvunder1,hsvunder2,hsvunder3,hsvupper1,hsvupper2,hsvupper3)
    circles = cv2.HoughCircles(gray,cv2.HOUGH_GRADIENT,2,minDist=40,param1=50,param2=30,minRadius=minsize,maxRadius=maxsize)#hier aanpassingen aan maken voor filtering
    #print(circles)
    if circles is not None:
        circles = np.uint16(np.around(circles))
        for i in circles[0,:]:
            # draw the outer circle
            cv2.circle(color_frame,(i[0],i[1]),i[2],(0,255,0),2)
            # draw the center of the circle
            cv2.circle(color_frame,(i[0],i[1]),2,(0,0,255),3)
            pointi=[(i[0]),(i[1])]
            distance = mean_distance(depth_frame,pointi)
            coordinates.append([(pointi),(distance)])
            cv2.putText(color_frame, "{}mm".format(distance), (pointi[0], pointi[1] - 20), cv2.FONT_HERSHEY_PLAIN, 2, (0, 0, 0), 2)
    
    return color_frame,coordinates,gray
def getpoint_notround(depth_frame,color_frame,hsvunder1,hsvunder2,hsvunder3,hsvupper1,hsvupper2,hsvupper3,minxsize,maxsize):
    coordinates=[]
    cx=0
    cy=0
    pointi=(10,10)
    distance=None
    mask,cnts=image_edits(color_frame,hsvunder1,hsvunder2,hsvunder3,hsvupper1,hsvupper2,hsvupper3)
    for c in cnts:
        area= cv2.contourArea(c)
        if area>100:
            M = cv2.moments(c)
            #print ("Area=",area)
            # Calculate the moments
            if M['m00'] != 0:
                cx = int(M['m10']/M['m00'])
                cy = int(M['m01']/M['m00'])
                cv2.circle(color_frame, (cx, cy), 7, (0, 0, 255), -1)
                pointi=(cx,cy)
                #bepalen van afstand en pixel coordinaat
                distance = mean_distance(depth_frame,pointi)
                coordinates.append([pointi,distance])
                #tekenen van centrun en contour
                cv2.putText(color_frame, "{}mm".format(distance), (pointi[0], pointi[1] - 20), cv2.FONT_HERSHEY_PLAIN, 2, (0, 0, 0), 2)
                epsilon = 0.005 * cv2.arcLength(c, True)
                approx = cv2.approxPolyDP(c, epsilon, True)
                cv2.drawContours(color_frame, [approx], -1, (0, 255, 0), 4)
    print(coordinates)

    return color_frame,coordinates,mask
def getpoint_paprika(depth_frame,color_frame,hsvunder1,hsvunder2,hsvunder3,hsvupper1,hsvupper2,hsvupper3,minxsize,maxsize):
    coordinates=[]
    cx=0
    cy=0
    j=0
    loc1=[]
    pointi=(10,10)
    distance=None
    mask,cnts=image_edits(color_frame,hsvunder1,hsvunder2,hsvunder3,hsvupper1,hsvupper2,hsvupper3)#0,80,30,255,255,255
    mask2,cnts2=image_edits(color_frame,10,60,0,35,200,255)#10,60,0,35,200,255
    for i in cnts2:
        area= cv2.contourArea(i)
        #print (area)
        if area>250:
            M = cv2.moments(i)
            # Calculate the moments
            if M['m00'] != 0:
                cx = int(M['m10']/M['m00'])
                cy = int(M['m01']/M['m00'])
                #cv2.circle(color_frame, (cx, cy), 7, (255, 0, 0), -1)
                epsilon = 0.001 * cv2.arcLength(i, True)
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
                        pointi=((cx+number*(cx-loc1[j][0])),(cy+number*(cy-loc1[j][1])))
                        #bepalen van afstand en pixel coordinaat
                        distance = mean_distance(depth_frame,pointi)
                        coordinates.append([pointi,distance])
                        #tekenen van centrun en contour
                        cv2.putText(color_frame, "{}mm".format(distance), (pointi[0], pointi[1]- 40 ), cv2.FONT_HERSHEY_PLAIN, 2, (0, 0, 0), 2)
                        epsilon = 0.001 * cv2.arcLength(c, True)
                        approx = cv2.approxPolyDP(c, epsilon, True)
                        cv2.drawContours(color_frame, [approx], -1, (0, 255, 0), 4)
                    else:
                        cv2.circle(color_frame, (cx, cy), 7, (0, 0, 255), -1)
                        pointi=(cx),(cy)
                        #bepalen van afstand en pixel coordinaat
                        distance = mean_distance(depth_frame,pointi)
                        coordinates.append([pointi,distance])
                        #tekenen van centrun en contour
                        cv2.putText(color_frame, "{}mm".format(distance), (pointi[0], pointi[1] - 40), cv2.FONT_HERSHEY_PLAIN, 2, (0, 0, 0), 2)
                        epsilon = 0.001 * cv2.arcLength(c, True)
                        approx = cv2.approxPolyDP(c, epsilon, True)
                        cv2.drawContours(color_frame, [approx], -1, (0, 255, 0), 4)
                    
                if (loc1==[]):
                    cv2.circle(color_frame, (cx, cy), 7, (0, 0, 255), -1)
                    pointi=(cx),(cy)
                    #bepalen van afstand en pixel coordinaat
                    distance = mean_distance(depth_frame,pointi)
                    coordinates.append([pointi,distance])
                    #tekenen van centrun en contour
                    cv2.putText(color_frame, "{}mm".format(distance), (pointi[0], pointi[1] - 40), cv2.FONT_HERSHEY_PLAIN, 2, (0, 0, 0), 2)
                    epsilon = 0.001 * cv2.arcLength(c, True)
                    approx = cv2.approxPolyDP(c, epsilon, True)
                    cv2.drawContours(color_frame, [approx], -1, (0, 255, 0), 4)
    print(coordinates)

    return color_frame,coordinates,mask2
def draw_original(original,coordinates,xcorrect,ycorrect):
    cv2.circle(original,(coordinates[0][0][0]+xcorrect,coordinates[0][0][1]+ycorrect),1,(0,255,0),2)
    return original
def initizalize_rs():
    pipeline = rs.pipeline()
    config = rs.config()
    config.enable_stream(rs.stream.depth, 1280, 720, rs.format.z16, 30)
    config.enable_stream(rs.stream.color, 1280, 720, rs.format.bgr8, 30)

    # Start streaming
    pipeline.start(config)
    return pipeline    

def make_3D_point(x, y, pipeline):
    # Get the frames from the pipeline
    frames = pipeline.wait_for_frames()
    
    # Get the color frame and intrinsics
    color_frame = frames.get_color_frame()
    color_intrin = color_frame.profile.as_video_stream_profile().intrinsics

    # Get the distortion coefficients and convert to numpy array
    dist_coeffs = np.array(color_intrin.coeffs)

    # Convert the color intrinsics to numpy array and reshape
    color_intrin_arr = np.array([[color_intrin.fx, 0, color_intrin.ppx],
                                 [0, color_intrin.fy, color_intrin.ppy],
                                 [0, 0, 1]], dtype=np.float32)

    # Undistort the point
    undist_color_point = cv2.undistortPoints(np.array([[x, y]], dtype=np.float32),
                                             color_intrin_arr,
                                             dist_coeffs,
                                             P=color_intrin_arr)[0]

    # Get the depth value and convert to meters
    depth_frame = frames.get_depth_frame()
    depth_value = depth_frame.get_distance(x, y)
    depth_meters = depth_value*0.001

    # Calculate the 3D point in camera coordinates
    x_c = (depth_meters * undist_color_point[0][0] / color_intrin.fx)*100
    y_c = (depth_meters * undist_color_point[0][1] / color_intrin.fy)*100
    z_c = depth_meters*1000

    # Return the 3D point
    return x_c, y_c, z_c

# ((depth_point[1]-771.17),(depth_point[1]-916.68),-(depth_point[2]-783.46))
def main():
    # Initialize Camera Intel Realsense
    pipeline=initizalize_rs()
    #create trackbar and images
    crop=[[(20),(700),(600),(1075)],[(20),(680),(150),(600)],[(0),(680),(630),(1100)],[(0),(680),(170),(630)],[(0),(720),(0),(1280)]]
    makeframe()
    while True:
        #read info from trackbars
        hsvunder1,hsvunder2,hsvunder3,hsvupper1,hsvupper2,hsvupper3,minsize,maxsize=readtrackbar()
        #get depth and color frame
        #org=[]
        depth_cut,color_cut,org=getframe(pipeline,crop[3])
        #Use filters and circle detection to get center coordinate
        madeframe,coor,gray=getpoint_tomato(depth_cut,color_cut,hsvunder1,hsvunder2,hsvunder3,hsvupper1,hsvupper2,hsvupper3,minsize,maxsize)
        if coor != []:
            point=make_3D_point(coor[0][0][0]+crop[3][2], coor[0][0][1]+crop[3][0],pipeline)
            print("3D Point in robot arm coordinates:", point)
            #print(coor[0][0][0])
            #show edited and original frame with contours and center
            org_draw=draw_original(org, coor,crop[1][2],crop[1][0])
            cv2.imshow("Origineel frame", org_draw)
        cv2.imshow("bewerkt frame", madeframe)
        cv2.imshow("Grijs frame",gray)
        cv2.imshow("gray frame",gray)
        cv2.waitKey(10)
        key = cv2.waitKey(1)
        if key == 27:  # ESC
            break
        #maxheight,pos=find_high_points(depth)
    key = cv2.waitKey(0)
        #if key == 27:
            #        break
    cv2.destroyAllWindows()
    # Stop streaming
    pipeline.stop()
main()