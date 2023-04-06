import cv2
import pyrealsense2 as rs
import numpy as np
import copy
def nothing(x):
    pass
def getframe(pipeline,crop=((0),(720),(0),(1280))):
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
def getpoint_round(depth_frame,color_frame,hsvunder1,hsvunder2,hsvunder3,hsvupper1,hsvupper2,hsvupper3,min_size,max_size):
    coordinates=[]
    pointi=None
    gray,cnts=image_edits(color_frame,hsvunder1,hsvunder2,hsvunder3,hsvupper1,hsvupper2,hsvupper3)#0,80,80,255,255,255
    circles = cv2.HoughCircles(gray,cv2.HOUGH_GRADIENT,2,minDist=50,param1=50,param2=30,minRadius=min_size,maxRadius=max_size)#hier aanpassingen aan maken voor filtering
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
def getpoint_notround_withstem(depth_frame,color_frame,hsvunder1,hsvunder2,hsvunder3,hsvupper1,hsvupper2,hsvupper3,min_size,max_size):
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
        #print ("Area",area)
        if area>20:
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
    return color_frame,coordinates,mask2
def getpoint_notround(depth_frame,color_frame,hsvunder1,hsvunder2,hsvunder3,hsvupper1,hsvupper2,hsvupper3,min_size,max_size):
    coordinates=[]
    cx=0
    cy=0
    pointi=(10,10)
    mask,cnts=image_edits(color_frame,hsvunder1,hsvunder2,hsvunder3,hsvupper1,hsvupper2,hsvupper3)
    for c in cnts:
        area= cv2.contourArea(c)
        if area>500:
            M = cv2.moments(c)
            #print ("Area=",area)
            # Calculate the moments
            if M['m00'] != 0:
                # Calculate the x and y pixelcoordinates of the moment
                cx = int(M['m10']/M['m00'])
                cy = int(M['m01']/M['m00'])

                # Draw point on each moment
                cv2.circle(color_frame, (cx, cy), 7, (0, 0, 255), -1)
                pointi=(cx,cy)
                coordinates.append([pointi])

                # Determine and draw the contours
                epsilon = 0.005 * cv2.arcLength(c, True)
                approx = cv2.approxPolyDP(c, epsilon, True)
                cv2.drawContours(color_frame, [approx], -1, (0, 255, 0), 4)

                # cv2.putText(color_frame, f'{length}', (x,y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,255,255), 1)
                # Calculate the orientation of the contour
                angle = 0.5 * np.arctan2(2*M['mu11'], M['mu20']-M['mu02'])

                # Calculate the length of the axis
                length = int(M['m00'] ** 0.5)

                # Compute the end points of the line
                x1 = int(cx - length*np.cos(angle))
                y1 = int(cy - length*np.sin(angle))
                x2 = int(cx + length*np.cos(angle))
                y2 = int(cy + length*np.sin(angle))

                # Draw the line
                cv2.line(color_frame, (x1, y1), (x2, y2), (255, 0, 255), 2)
                cv2.putText(color_frame, f'{np.rad2deg(angle)}', (x1,y1-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,255,255), 1)
    return color_frame,coordinates,mask
def getpoint(pipeline1,pipeline2, vegetable):
    '''
    Description
    ----------
    Function which finds de pickup points for vegetables.
    Parameters
    ----------
    pipeline1 : pyrealsense.pipeline
        Camera pipeline object of camera 1
    pipeline2 : pyrealsense.pipeline
        Camera pipeline object of camera 2
    vegetable : dictionary
        Dictionary containing all necessary information about a vegetable eg. Shape, Color, Crate number and more
    Returns
    -------
    image_with_points : numpy array
        The cropped image with the pickup points drawn on the image
    pickup_coordinates : array of float
        An array containing all the (x, y) coordinates of the detected pickup points
    gray_image : numpy array
        The cropped image but in greyscale
    crop : array of int
        A small array of integers containing the four vertices used to crop the original image
    orginal_color_frame : numpy array
        The original input image
    camera : int
        This is an integer representing the camera that is used to look for the vegetable
    pipeline : realsense.pipeline
        Pipeline object of the realsense camera
    place : string
        Used to identify in which quadrant of the crate the vegetable is located
    '''
    crop=[[(0),(600),(625),(1000)],[(50),(600),(250),(600)],[(50),(620),(640),(1000)],[(50),(630),(250),(600)],[(0),(1280),(0),(720)]]
    shape = vegetable["product_shape"]
    min_size = vegetable["product_minSize"]
    max_size = vegetable["product_maxSize"]
    hsv_range = vegetable["product_HSVRange"]
    crate_number = int(vegetable["crateNumber"])
    highest_coordinate=[]
    CurrentHeighest=2000
    if (crate_number==1) or (crate_number==2):
        pipeline=pipeline1
        camera=1
    if (crate_number==3) or (crate_number==4):
        pipeline=pipeline2
        camera=2
    depth_cut,color_cut,orginal_color_frame=getframe(pipeline,crop[crate_number-1])

    if (shape == "Round"):
        image_with_points,pickup_coordinates,gray_image=getpoint_round(depth_cut,color_cut,hsv_range[0],hsv_range[1],hsv_range[2],hsv_range[3],hsv_range[4],hsv_range[5],min_size,max_size)
    elif (shape == "Not round"):
        image_with_points,pickup_coordinates,gray_image=getpoint_notround(depth_cut,color_cut,hsv_range[0],hsv_range[1],hsv_range[2],hsv_range[3],hsv_range[4],hsv_range[5],min_size,max_size)
    elif (shape == "Not round with stem"):
        image_with_points,pickup_coordinates,gray_image=getpoint_notround_withstem(depth_cut,color_cut,hsv_range[0],hsv_range[1],hsv_range[2],hsv_range[3],hsv_range[4],hsv_range[5],min_size,max_size)
    #determine place in crate
    for i in range(len(pickup_coordinates)):
            depth_value = depth_cut[pickup_coordinates[i][0][1],pickup_coordinates[i][0][0]]
            if depth_value>CurrentHeighest:
                highest_coordinate=pickup_coordinates[i][0]
                CurrentHeighest=depth_value
    if highest_coordinate!=[]:
        cv2.circle(image_with_points,(highest_coordinate[0],highest_coordinate[1]),10,(255,0,0),4)
    #determine place in crate
    if (pickup_coordinates != []):
        if (pickup_coordinates[0][0][1]<(crop[crate_number-1][1]-crop[crate_number-1][0])/2):
            place="Up"
        elif(pickup_coordinates[0][0][1]>=(crop[crate_number-1][1]-crop[crate_number-1][0])/2):
            place="Down"
    elif(pickup_coordinates == []):
        place=None

    return image_with_points,highest_coordinate,gray_image,crop[crate_number-1],orginal_color_frame,camera,pipeline,place
def draw_original(original,coordinates,xcorrect=0,ycorrect=0):
    cv2.circle(original,(coordinates[0]+xcorrect,coordinates[1]+ycorrect),1,(0,255,0),2)
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
def make_3D_point(x, y, pipeline, camera):
    '''
    Description
    ----------
    Function to calculate the coordinates of a point in the 3D space.
    Parameters
    ----------
    x : float
        X coordinate of the point
    y : float
        Y coordinate of the point
    pipeline : pyrealsense.pipeline
        Camera pipeline object
    camera : int
        Integer value to specify in which camera frame the point needs to be calculated
    Returns
    -------
    point : array of float
        An array containing the X, Y and Z coordinates of the point
    '''
    xmean, ymean, zmean = 0, 0, 0
    number = 50
    count=1
    depthmean=0
    k=-1
    for i in range(number):
        # Wait for a coherent pair of frames: depth and color
        frames = pipeline.wait_for_frames()
        depth_frame = frames.get_depth_frame()
        color_frame = frames.get_color_frame()
        #Get the depth value at the point of interest
        # for k in range(-2,2):
        #     for j in range(-2,2):
        #         depthmean+=depth_frame.get_distance(x+k, y+j)
        #         count+=1
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
        world_coords = world_coords[:3]*1000
        
        xmean += world_coords[0]
        ymean += world_coords[1]
        zmean += world_coords[2]
    world_coords = np.array([xmean, ymean, zmean]) / number
    if camera == 1:
        cam1 = np.loadtxt('HMI\Cam_Off_1.txt')  # difference from the camera to the robot coordinates  HMI
        point = [-(world_coords[1]) + cam1[0], -(world_coords[0] ) + cam1[1],
                 (-world_coords[2] ) + cam1[2]]
    elif camera == 2:
        cam2 = np.loadtxt('HMI\Cam_Off_2.txt')  # difference from the camera to the robot coordinates
        point = [-(world_coords[1]) + cam2[0], -(world_coords[0] ) + cam2[1],
                 (-world_coords[2] + cam2[2])]
    return point
def calibrateXY(pipeline, robot_coordinates,camera):
    '''
    Description
    ----------
    Function to calculate the offset between the robot coordinates and camera coordinates.
    Parameters
    ----------
    pipeline : pyrealsense.pipeline
        Camera pipeline object
    robot_coordinates : array of float
        Array containing the coordinates of the robot position
    Returns
    -------
    x_offset : float
        The offset/difference between the camera and robot x coordinates
    y_offset : float
        The offset/difference between the camera and robot y coordinates
    '''
    frames = pipeline.wait_for_frames()
    depth_frame = frames.get_depth_frame()
    color_frame = frames.get_color_frame()
    depth_arr = np.asanyarray(depth_frame.get_data())
    color_arr = np.asanyarray(color_frame.get_data())
    Test_frame, camera_coordinates, _ = getpoint_round(depth_arr, color_arr,103,94,143,116,255,255,35,45)
    #print(camera_coordinates)
    while (camera_coordinates==[]):
        frames = pipeline.wait_for_frames()
        depth_frame = frames.get_depth_frame()
        color_frame = frames.get_color_frame()
        depth_arr = np.asanyarray(depth_frame.get_data())
        color_arr = np.asanyarray(color_frame.get_data())
        Test_frame, camera_coordinates, _ = getpoint_round(depth_arr, color_arr,103,94,143,116,255,255,35,45)

    # Get the depth value at the point of interest
    depth_value = depth_frame.get_distance(camera_coordinates[0][0][0], camera_coordinates[0][0][1])
    # Convert depth pixel coordinates to world coordinates
    depth_intrinsics = depth_frame.profile.as_video_stream_profile().intrinsics
    depth_to_color_extrinsics = depth_frame.profile.get_extrinsics_to(color_frame.profile)
    world_coords = rs.rs2_deproject_pixel_to_point(depth_intrinsics, [camera_coordinates[0][0][0], camera_coordinates[0][0][1]], depth_value)
    rotation = np.array(depth_to_color_extrinsics.rotation).reshape(3, 3)
    translation = np.array(depth_to_color_extrinsics.translation).reshape(3, 1)
    depth_to_color_extrinsics = np.concatenate((rotation, translation), axis=1)
    world_coords = np.append(world_coords, [1])
    world_coords = np.dot(depth_to_color_extrinsics, world_coords)
    world_coords = world_coords[:3]*1000
    if (camera == 1):
        x_offset = robot_coordinates[0] + (world_coords[1] )
        y_offset = robot_coordinates[1] + (world_coords[0] )
        z_offset = robot_coordinates[2] + (world_coords[2] )
        cam1=[x_offset, y_offset,z_offset]
        with open ('HMI\Cam_Off_1.txt','w') as f:
            np.savetxt(f, cam1)
        point=[-(world_coords[1])+cam1[0],-(world_coords[0])+cam1[1],(-world_coords[2])+cam1[2]]
    if (camera == 2):
        x_offset = robot_coordinates[0] + (world_coords[1] )
        y_offset = robot_coordinates[1] + (world_coords[0] )
        z_offset = robot_coordinates[2] + (world_coords[2] )
        cam2=[x_offset, y_offset,z_offset]
        with open ('HMI\Cam_Off_2.txt','w') as f:
            np.savetxt(f, cam2)
        point=[-(world_coords[1])+cam2[0],-(world_coords[0])+cam2[1],(-world_coords[2]+cam2[2])]
    #print (point)
    return Test_frame
