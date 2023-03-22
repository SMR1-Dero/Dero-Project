"""
Created on Thu Mar 16 19:44:20 2023
@author: joche
"""
import cv2
import pyrealsense2 as rs
import numpy as np
import copy
from realsense_depth import *
vegetabledict = {
    "id": "1_8",
    "product_name": "Tomaat",
    "product_image": "https://github.com/ItsJarik/CobotHMI/blob/main/Tomaten.png?raw=true",
    "product_package": "Curry Madras",
    "crateNumber": "1",
    "isActive": "on",
    "product_shape": "Round",
    "product_HSVRange": [0,80,80,255,255,255],
    "product_minSize": "",
    "product_maxSize": ""
}

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
    circles = cv2.HoughCircles(gray,cv2.HOUGH_GRADIENT,2,minDist=15,param1=50,param2=30,minRadius=22,maxRadius=27)#hier aanpassingen aan maken voor filtering
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
    mask,cnts=image_edits(color_frame,hsvunder1,hsvunder2,hsvunder3,hsvupper1,hsvupper2,hsvupper3)#0,80,30,255,255,255
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

def getpoint(pipeline, vegetable):
    crop=[[(20),(700),(600),(1075)],[(20),(680),(150),(600)],[(0),(680),(630),(1100)],[(0),(680),(170),(630)],[(0),(720),(0),(1280)]]


    shape = vegetable["product_shape"]
    min_size = vegetable["product_minSize"]
    max_size = vegetable["product_maxSize"]
    hsv_range = vegetable["product_HSVRange"]
    crate_number = int(vegetable["crateNumber"])

    depth_cut,color_cut,orginal_color_frame=getframe(pipeline,crop[crate_number-1])

    if (shape == "Round"):
        image_with_points,pickup_coordinates,gray_image=getpoint_round(depth_cut,color_cut,hsv_range[0],hsv_range[1],hsv_range[2],hsv_range[3],hsv_range[4],hsv_range[5])
    elif (shape == "Not round"):
        image_with_points,pickup_coordinates,gray_image=getpoint_notround(depth_cut,color_cut,hsv_range[0],hsv_range[1],hsv_range[2],hsv_range[3],hsv_range[4],hsv_range[5])
    elif (shape == "Not round with stem"):
        image_with_points,pickup_coordinates,gray_image=getpoint_notround_withstem(depth_cut,color_cut,hsv_range[0],hsv_range[1],hsv_range[2],hsv_range[3],hsv_range[4],hsv_range[5])
    
    return image_with_points,pickup_coordinates,gray_image,crop[crate_number-1],orginal_color_frame

def draw_original(original,coordinates,xcorrect,ycorrect):
    cv2.circle(original,(coordinates[0][0][0]+xcorrect,coordinates[0][0][1]+ycorrect),1,(0,255,0),2)
    return original
def initizalize_rs(pl):
    # pipeline = rs.pipeline()
    # config = rs.config()
    # config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 30)
    # config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)
    
    # # Start streaming
    # pipeline.start(config)
    # return pipeline

    # use the serial number of the camera to determine which camera is where
    # Configure the first pipeline to stream depth frames with the serial number filter
    if (pl==1):
        pipeline = rs.pipeline()
        config1 = rs.config()
        config1.enable_stream(rs.stream.depth, 1280, 720, rs.format.z16, 30)
        config1.enable_stream(rs.stream.color, 1280, 720, rs.format.bgr8, 30)
        serial_number1 = "839512061465" # Replace this with the serial number of your camera
        config1.enable_device(serial_number1)
        pipeline.start(config1)
    
    # Configure the second pipeline to stream depth frames with the serial number filter
    elif (pl==2):
        pipeline = rs.pipeline()
        config2 = rs.config()
        config2.enable_stream(rs.stream.depth,1280, 720, rs.format.z16, 30)
        config2.enable_stream(rs.stream.color,1280, 720, rs.format.bgr8, 30)
        serial_number2 = "211122062283" # Replace this with the serial number of your camera
        config2.enable_device(serial_number2)
        pipeline.start(config2)
    #Start streaming
    return pipeline
def read_cal(pl):
    if pl==1:
        with open('Calibration_one.txt', 'r') as f:
            mtx = np.loadtxt(f, max_rows=3,delimiter=',')
            dist = np.loadtxt(f, max_rows=1,delimiter=',')
    if pl==2:
        with open('Calibration_two.txt', 'r') as f:#'Python\Python_Herkenning\Parameters_Vinden\Calibration_two.txt'
            mtx = np.loadtxt(f, max_rows=3,delimiter=',')
            dist = np.loadtxt(f, max_rows=1,delimiter=',')
    return mtx,dist
def calibrate_camera(pipeline,pl ,chessboard_size=(17, 12), square_size=20):
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
                if pl ==1:
                    f=open('Calibration_one.txt','a')
                    f.truncate(0)
                    np.savetxt(f, mtx,delimiter=',')
                    f.write("\n")
                    np.savetxt(f, dist,delimiter=',')
                    f.write("\n")
                    f.close()
                    cv2.destroyAllWindows()
                if pl==2:
                    f=open('Calibration_two.txt','a')
                    f.truncate(0)
                    np.savetxt(f, mtx,delimiter=',')
                    f.write("\n")
                    np.savetxt(f, dist,delimiter=',')
                    f.write("\n")
                    f.close()
                    cv2.destroyAllWindows()
                break

def make_3D_point(x, y, pipeline, mtx, dist):
    cam1=[-642.56,277.4,976.87]
    cam2=[-642.56,277.4,976.87]
    # Get the depth frame
    depth_frame = pipeline.wait_for_frames().get_depth_frame()
    # Get the intrinsics of the depth frame
    depth_intrin = depth_frame.profile.as_video_stream_profile().intrinsics
    # Convert the pixel coordinates to the undistorted coordinates
    pts = np.array([[x, y]], dtype=np.float32)
    pts_undistorted = cv2.undistortPoints(pts, mtx, dist,P=mtx)
    # Get the depth value at the pixel coordinates
    # deler=0
    # height=0
    # mean_height=0
    # for i in range(-1,1):
    #     for j in range(-1,1):
    #         height=depth_frame.get_distance(int(pts_undistorted[0][0][0]+j), int(pts_undistorted[0][0][1])+i)
    #         if (height != 0):
    #             mean_height+=height
    #             deler+=1
    #         j+=1
    #     i+=1
    # if(deler!=0):
    #     depth=mean_height/deler
    # else:
    #     depth = depth_frame.get_distance(int(pts_undistorted[0][0][0]), int(pts_undistorted[0][0][1]))
        
    depth = depth_frame.get_distance(int(pts_undistorted[0][0][0]), int(pts_undistorted[0][0][1]))
    # Convert the pixel coordinates to the camera coordinate system
    point = rs.rs2_deproject_pixel_to_point(depth_intrin, [(pts_undistorted[0][0][0]), (pts_undistorted[0][0][1])], depth)#x,y,z
    print(point)
    #point=[(-point[1]*1000)-cam1[0],(-point[0]*1000)+cam1[1],(point[2]*1000)-cam1[2]]
    point=[-(point[1]*1000)+cam2[0],(-point[0]*1000)+cam2[1],(point[2]*1000)-cam2[2]]
    return point

def main(debug=False):
    # Initialize Camera Intel Realsense
    pipeline1=initizalize_rs(1)
    pipeline2=initizalize_rs(2)
    #create trackbar and images
    #calibrate_camera(pipeline2,pl)
    makeframe()
    while True:
        pl=1
        if (pl==1):
            pipeline=pipeline1
        elif(pl==2):
            pipeline=pipeline2
        mtx,dist=read_cal(pl)
        #read info from trackbars
        hsvunder1,hsvunder2,hsvunder3,hsvupper1,hsvupper2,hsvupper3=readtrackbar()
        #Use filters and circle detection to get center coordinate
        image_with_points,pickup_coordinates,gray_image,crop,original_color_frame=getpoint(pipeline,vegetabledict)
        if pickup_coordinates != []:
            point=make_3D_point(pickup_coordinates[0][0][0]+crop[2], pickup_coordinates[0][0][1]+crop[0],pipeline,mtx,dist)
            print("3D Point in robot arm coordinates:", point)
            #print(coor[0][0][0])
            #show edited and original frame with contours and center
            original_with_points=draw_original(original_color_frame, pickup_coordinates,crop[0],crop[2])
            if debug:
                cv2.imshow("Origineel frame", original_with_points)
        if debug:
            cv2.imshow("bewerkt frame", image_with_points)
            cv2.imshow("Grijs frame",gray_image)
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
    pipeline1.stop()
    pipeline2.stop()
main(debug=True)
