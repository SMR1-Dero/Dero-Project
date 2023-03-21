# -*- coding: utf-8 -*-
"""
Created on Thu Mar 16 19:44:20 2023

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
    #create
    cv2.createTrackbar('hsvunder1','Grijs frame',0,255,nothing)
    cv2.createTrackbar('hsvunder2','Grijs frame',115,255,nothing)
    cv2.createTrackbar('hsvunder3','Grijs frame',85,255,nothing)
    cv2.createTrackbar('hsvupper1','Grijs frame',225,255,nothing)
    cv2.createTrackbar('hsvupper2','Grijs frame',255,255,nothing)
    cv2.createTrackbar('hsvupper3','Grijs frame',255,255,nothing)    
def readtrackbar():
    hsvunder1 = cv2.getTrackbarPos('hsvunder1','Grijs frame')
    hsvunder2 = cv2.getTrackbarPos('hsvunder2','Grijs frame')
    hsvunder3 = cv2.getTrackbarPos('hsvunder3','Grijs frame')
    hsvupper1 = cv2.getTrackbarPos('hsvupper1','Grijs frame')
    hsvupper2 = cv2.getTrackbarPos('hsvupper2','Grijs frame')
    hsvupper3 = cv2.getTrackbarPos('hsvupper3','Grijs frame')
    return hsvunder1,hsvunder2,hsvunder3,hsvupper1,hsvupper2,hsvupper3
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
def getpoint_round(depth_frame,color_frame,hsvunder1,hsvunder2,hsvunder3,hsvupper1,hsvupper2,hsvupper3):
    coordinates=[]
    pointi=None
    distance=None
    gray,cnts=image_edits(color_frame,hsvunder1,hsvunder2,hsvunder3,hsvupper1,hsvupper2,hsvupper3)#0,80,80,255,255,255
    circles = cv2.HoughCircles(gray,cv2.HOUGH_GRADIENT,2,minDist=15,param1=50,param2=30,minRadius=15,maxRadius=25)#hier aanpassingen aan maken voor filtering
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
def getpoint_notround_withstem(depth_frame,color_frame,hsvunder1,hsvunder2,hsvunder3,hsvupper1,hsvupper2,hsvupper3):
    coordinates=[]
    cx=0
    cy=0
    j=0
    loc1=[]
    pointi=(10,10)
    distance=None
    mask,cnts=image_edits(color_frame,0,80,30,255,255,255)#0,80,30,255,255,255
    mask2,cnts2=image_edits(color_frame,10,60,0,35,200,255)#10,60,0,35,200,255
    for i in cnts2:
        area= cv2.contourArea(i)
        #print (area)
        if area>150:
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
                        pointi=((cx+number*(cx-loc1[j][0])),(cy+number*(cy-loc1[j][1])))
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
                        pointi=(cx),(cy)
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
                    pointi=(cx),(cy)
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

def getpoint_notround(depth_frame,color_frame,hsvunder1,hsvunder2,hsvunder3,hsvupper1,hsvupper2,hsvupper3):
    coordinates=[]
    cx=0
    cy=0
    pointi=(10,10)
    distance=None
    mask,cnts=image_edits(color_frame,hsvunder1,hsvunder2,hsvunder3,hsvupper1,hsvupper2,hsvupper3)
    for c in cnts:
        area= cv2.contourArea(c)
        if area>1000:
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
    return color_frame,coordinates,mask


def draw_original(original,coordinates,xcorrect,ycorrect):
    cv2.circle(original,(coordinates[0][0][0]+xcorrect,coordinates[0][0][1]+ycorrect),1,(0,255,0),2)
    return original
def initizalize_rs():
    pipeline = rs.pipeline()
    config = rs.config()
    config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 30)
    config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)

    # Start streaming
    pipeline.start(config)
    return pipeline 
def read_cal():
    with open('Calibration_one.txt', 'r') as f:
        mtx = np.loadtxt(f, max_rows=3,delimiter=',')
        dist = np.loadtxt(f, max_rows=1,delimiter=',')
    return mtx,dist
def calibrate_camera(pipeline, chessboard_size=(17, 12), square_size=20):
    objp = np.zeros((chessboard_size[0] * chessboard_size[1], 3), np.float32)
    objp[:, :2] = np.mgrid[0:chessboard_size[0], 0:chessboard_size[1]].T.reshape(-1, 2) * square_size

    objpoints = []
    imgpoints = []

    while True:
        frames = pipeline.wait_for_frames()
        color_frame = frames.get_color_frame()

        if not color_frame:
            continue

        color_image = np.asanyarray(color_frame.get_data())
        gray_image = cv2.cvtColor(color_image, cv2.COLOR_BGR2GRAY)

        ret, corners = cv2.findChessboardCorners(gray_image, chessboard_size, None)

        if ret:
            objpoints.append(objp)
            imgpoints.append(corners)

            cv2.drawChessboardCorners(color_image, chessboard_size, corners, ret)
            cv2.imshow('Chessboard', color_image)
            cv2.waitKey(500)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

            if len(objpoints) >= 10:
                ret, mtx, dist, rvecs, tvecs = cv2.calibrateCamera(objpoints, imgpoints, gray_image.shape[::-1], None, None)
                f=open('Calibration_one.txt','a')
                f.truncate(0)
                np.savetxt(f, mtx,delimiter=',')
                f.write("\n")
                np.savetxt(f, dist,delimiter=',')
                f.write("\n")
                f.close()
                cv2.destroyAllWindows()
                break

def make_3D_point(x, y, pipeline, mtx, dist):
    cam1=[584.87,603.59,927]#y,x,z
    # Get the depth frame
    depth_frame = pipeline.wait_for_frames().get_depth_frame()
    # Get the intrinsics of the depth frame
    depth_intrin = depth_frame.profile.as_video_stream_profile().intrinsics
    # Convert the pixel coordinates to the undistorted coordinates
    pts = np.array([[x, y]], dtype=np.float32)
    pts_undistorted = cv2.undistortPoints(pts, mtx, dist,P=mtx)
    # Get the depth value at the pixel coordinates
    depth = depth_frame.get_distance(int(pts_undistorted[0][0][0]), int(pts_undistorted[0][0][1]))
    # Convert the pixel coordinates to the camera coordinate system
    point = rs.rs2_deproject_pixel_to_point(depth_intrin, [(pts_undistorted[0][0][0]), (pts_undistorted[0][0][1])], depth)#x,y,z
    print(point)
    point=[(-point[1]*1000)-cam1[0],(-point[0]*1000)-cam1[1],(point[2]*1000)-cam1[2]]
    return point

def main():
    # Initialize Camera Intel Realsense
    pipeline=initizalize_rs()
    #create trackbar and images
    #calibrate_camera(pipeline)
    mtx,dist=read_cal()
    crop=[[(75),(425),(140),(365)],[(75),(425),(385),(615)],[(0),(780),(0),(1280)]]
    makeframe()
    while True:
        #read info from trackbars
        hsvunder1,hsvunder2,hsvunder3,hsvupper1,hsvupper2,hsvupper3=readtrackbar()
        #get depth and color frame
        depth_cut,color_cut,org=getframe(pipeline,crop[2])
        #Use filters and circle detection to get center coordinate
        madeframe,coor,gray=getpoint_round(depth_cut,color_cut,hsvunder1,hsvunder2,hsvunder3,hsvupper1,hsvupper2,hsvupper3)
        if coor != []:
            point=make_3D_point(coor[0][0][0]+crop[2][2], coor[0][0][1]+crop[2][0],pipeline,mtx,dist)
            print("3D Point in robot arm coordinates:", point)
            #print(coor[0][0][0])
            #show edited and original frame with contours and center
            org_draw=draw_original(org, coor,crop[1][2],crop[1][0])
            org_draw=draw_original(org, coor,320,240)
            cv2.imshow("Origineel frame", org_draw)
        cv2.imshow("bewerkt frame", madeframe)
        cv2.imshow("Grijs frame",gray)
        cv2.waitKey(100)
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