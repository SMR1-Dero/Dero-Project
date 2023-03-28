import cv2
import pyrealsense2 as rs
import numpy as np
import copy

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
    gray,cnts=image_edits(color_frame,hsvunder1,hsvunder2,hsvunder3,hsvupper1,hsvupper2,hsvupper3)#0,80,80,255,255,255
    circles = cv2.HoughCircles(gray,cv2.HOUGH_GRADIENT,2,minDist=50,param1=50,param2=30,minRadius=24,maxRadius=30)#hier aanpassingen aan maken voor filtering
    #print(circles)
    if circles is not None:
        circles = np.uint16(np.around(circles))
        for i in circles[0,:]:
            # draw the outer circle
            cv2.circle(color_frame,(i[0],i[1]),i[2],(0,255,0),2)
            # draw the center of the circle
            cv2.circle(color_frame,(i[0],i[1]),2,(0,0,255),3)
            pointi=[(i[0]),(i[1])]
            coordinates.append([(pointi)])

    return color_frame,coordinates,gray
def getpoint_notround_withstem(depth_frame,color_frame,hsvunder1,hsvunder2,hsvunder3,hsvupper1,hsvupper2,hsvupper3):
    coordinates=[]
    cx=0
    cy=0
    j=0
    loc1=[]
    pointi=(10,10)
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
                        coordinates.append([pointi])
                        epsilon = 0.005 * cv2.arcLength(c, True)
                        approx = cv2.approxPolyDP(c, epsilon, True)
                        cv2.drawContours(color_frame, [approx], -1, (0, 255, 0), 4)
                    else:
                        cv2.circle(color_frame, (cx, cy), 7, (0, 0, 255), -1)
                        pointi=(cx),(cy)
                        #bepalen van afstand en pixel coordinaat
                        coordinates.append([pointi])
                        epsilon = 0.005 * cv2.arcLength(c, True)
                        approx = cv2.approxPolyDP(c, epsilon, True)
                        cv2.drawContours(color_frame, [approx], -1, (0, 255, 0), 4)

                if (loc1==[]):
                    cv2.circle(color_frame, (cx, cy), 7, (0, 0, 255), -1)
                    pointi=(cx),(cy)
                    #bepalen van afstand en pixel coordinaat
                    coordinates.append([pointi])
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
                coordinates.append([pointi])
                epsilon = 0.005 * cv2.arcLength(c, True)
                approx = cv2.approxPolyDP(c, epsilon, True)
                cv2.drawContours(color_frame, [approx], -1, (0, 255, 0), 4)
    return color_frame,coordinates,mask

def getpoint(pipeline1,pipeline2, vegetable):
    crop=[[(20),(700),(600),(1075)],[(20),(680),(150),(600)],[(0),(680),(630),(1100)],[(0),(680),(170),(630)],[(0),(720),(0),(1280)]]


    shape = vegetable["product_shape"]
    min_size = vegetable["product_minSize"]
    max_size = vegetable["product_maxSize"]
    hsv_range = vegetable["product_HSVRange"]
    crate_number = int(vegetable["crateNumber"])
    if (crate_number==1) or (crate_number==2):
        pipeline=pipeline1
        camera=1
    if (crate_number==3) or (crate_number==4):
        pipeline=pipeline2
        camera=2
    depth_cut,color_cut,orginal_color_frame=getframe(pipeline,crop[crate_number-1])
    print((crop[crate_number-1][3]-crop[crate_number-1][2])/2)
    
    if (shape == "Round"):
        image_with_points,pickup_coordinates,gray_image=getpoint_round(depth_cut,color_cut,hsv_range[0],hsv_range[1],hsv_range[2],hsv_range[3],hsv_range[4],hsv_range[5])
    elif (shape == "Not round"):
        image_with_points,pickup_coordinates,gray_image=getpoint_notround(depth_cut,color_cut,hsv_range[0],hsv_range[1],hsv_range[2],hsv_range[3],hsv_range[4],hsv_range[5])
    elif (shape == "Not round with stem"):
        image_with_points,pickup_coordinates,gray_image=getpoint_notround_withstem(depth_cut,color_cut,hsv_range[0],hsv_range[1],hsv_range[2],hsv_range[3],hsv_range[4],hsv_range[5])
    #determine place in crate
    if (pickup_coordinates != []):
        if (pickup_coordinates[0][0][0]<(crop[crate_number-1][3]-crop[crate_number-1][2])/2 and pickup_coordinates[0][0][1]<(crop[crate_number-1][1]-crop[crate_number-1][0])/2):
            place="LeftUp"
        elif(pickup_coordinates[0][0][0]<(crop[crate_number-1][3]-crop[crate_number-1][2])/2 and pickup_coordinates[0][0][1]>=(crop[crate_number-1][1]-crop[crate_number-1][0])/2):
            place="LeftDown"
        elif(pickup_coordinates[0][0][0]>=(crop[crate_number-1][3]-crop[crate_number-1][2])/2 and pickup_coordinates[0][0][1]<(crop[crate_number-1][1]-crop[crate_number-1][0])/2):
            place="RightUp"
        elif (pickup_coordinates[0][0][0]>=(crop[crate_number-1][3]-crop[crate_number-1][2])/2 and pickup_coordinates[0][0][1]>=(crop[crate_number-1][1]-crop[crate_number-1][0])/2):
            place="RightDown"
    elif(pickup_coordinates == []):
        place=None
    
    return image_with_points,pickup_coordinates,gray_image,crop[crate_number-1],orginal_color_frame,camera,pipeline,place

def draw_original(original,coordinates,xcorrect=0,ycorrect=0):
    cv2.circle(original,(coordinates[0][0][0]+xcorrect,coordinates[0][0][1]+ycorrect),1,(0,255,0),2)
    return original
def initizalize_rs():
    # use the serial number of the camera to determine which camera is where
    # Configure the first pipeline to stream depth frames with the serial number filter
    pipeline1 = rs.pipeline()
    config1 = rs.config()
    config1.enable_stream(rs.stream.depth, 1280, 720, rs.format.z16, 30)
    config1.enable_stream(rs.stream.color, 1280, 720, rs.format.bgr8, 30)
    serial_number1 = "839512061465" # Replace this with the serial number of your camera
    config1.enable_device(serial_number1)
    pipeline1.start(config1)
    
    # Configure the second pipeline to stream depth frames with the serial number filter
    pipeline2 = rs.pipeline()
    config2 = rs.config()
    config2.enable_stream(rs.stream.depth,1280, 720, rs.format.z16, 30)
    config2.enable_stream(rs.stream.color,1280, 720, rs.format.bgr8, 30)
    serial_number2 = "211122062283" # Replace this with the serial number of your camera
    config2.enable_device(serial_number2)
    pipeline2.start(config2)
    #Start streaming
    cv2.waitKey(1000)
    return pipeline1,pipeline2

def make_3D_point(x, y, pipeline,camera):
    # Wait for a coherent pair of frames: depth and color
    frames = pipeline.wait_for_frames()
    depth_frame = frames.get_depth_frame()
    color_frame = frames.get_color_frame()

    # Get the depth value at the point of interest
    depth_value = depth_frame.get_distance(x, y)

    # Convert depth pixel coordinates to world coordinates
    depth_intrinsics = depth_frame.profile.as_video_stream_profile().intrinsics
    depth_to_color_extrinsics = depth_frame.profile.get_extrinsics_to(color_frame.profile)
    world_coords = rs.rs2_deproject_pixel_to_point(depth_intrinsics, [x, y], depth_value)
    rotation = np.array(depth_to_color_extrinsics.rotation).reshape(3, 3)
    translation = np.array(depth_to_color_extrinsics.translation).reshape(3, 1)
    depth_to_color_extrinsics = np.concatenate((rotation, translation), axis=1)
    world_coords = np.append(world_coords, [1])
    world_coords = np.dot(depth_to_color_extrinsics, world_coords)
    world_coords = world_coords[:3]
    #return world_coords
    if (camera==1):
        cam1=[-594.37,-645,936.8]
        point=[-(world_coords[1]*1000)+cam1[0],-(world_coords[0]*1000)+cam1[1],(-world_coords[2]*1000)+cam1[2]]
    elif(camera==2):
        cam2=[-670,215,936.8]
        point=[-(world_coords[1]*1000)+cam2[0],-(world_coords[0]*1000)+cam2[1],(-world_coords[2]*1000+cam2[2])]
    


    return(point)