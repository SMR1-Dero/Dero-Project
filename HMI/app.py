from flask import Flask, render_template, request, jsonify, json
import cv2
import numpy as np
from flask import Flask, Response
import asyncio
import techmanpy
from techmanpy import TechmanException
import pyrealsense2 as rs
import time
import copy
from realsense_depth import *


app = Flask(__name__, template_folder=r'C:\Users\Jarik\OneDrive\Bureaublad\CobotConnection\templates')
app.static_folder = 'static'

# -----------------------------------------------------------
# PLC

ip = '192.168.0.202'

async def position(positionArray, tag):
    async with techmanpy.connect_sct(robot_ip=ip) as conn:
        await conn.move_to_point_ptp(positionArray, 1, 1000)

        await conn.set_queue_tag(tag_id = tag)
        await conn.wait_for_queue_tag(tag_id = tag)

async def setSuctionCup1(status):
    async with techmanpy.connect_sta(robot_ip=ip) as conn:
        tag_status = await conn.get_queue_tag_status(1)

    async with techmanpy.connect_svr(robot_ip=ip) as conn:
        if tag_status == True:
            await conn.set_value("Ctrl_DO1", status)
            tag_status = False

async def setSuctionCup2(status):
    async with techmanpy.connect_sta(robot_ip=ip) as conn:
        tag_status = await conn.get_queue_tag_status(1)

    async with techmanpy.connect_svr(robot_ip=ip) as conn:
        if tag_status == True:
            await conn.set_value("Ctrl_DO2", status)
            tag_status = False

async def setSuctionCup1Test(status):
    async with techmanpy.connect_svr(robot_ip=ip) as conn:
            await conn.set_value("Ctrl_DO1", status)

async def setSuctionCup2Test(status):
    async with techmanpy.connect_svr(robot_ip=ip) as conn:
            await conn.set_value("Ctrl_DO2", status)

# -----------------------------------------------------------
# Code Jochem

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
    crop=[[(75),(425),(140),(365)],[(75),(425),(385),(615)],[(0),(780),(0),(1280)]]

    shape = vegetable["product_shape"]
    min_size = vegetable["product_minSize"]
    max_size = vegetable["product_maxSize"]
    hsv_range = vegetable["product_HSVRange"]
    crate_number = int(vegetable["crateNumber"])

    depth_cut,color_cut,orginal_color_frame=getframe(pipeline,crop[1])

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
    cam1=[584.87,603.59,927]
    cam2=[-633,439.93,960.87]
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
    #point=[-(point[1]*1000)+cam2[0],-(-point[0]*1000)+cam2[1],(point[2]*1000)-cam2[2]]
    return point
def read_cal():
    with open('Calibration_one.txt', 'r') as f:
        mtx = np.loadtxt(f, max_rows=3,delimiter=',')
        dist = np.loadtxt(f, max_rows=1,delimiter=',')
    return mtx,dist



# -----------------------------------------------------------

# -----------------------------------------------------------

@app.route('/')
def routeView():
        return render_template('View.html')

@app.route('/manualPicker')
def routeManualPicker():
    return render_template('manualView.html')

@app.route('/routeSettingsView', methods=['GET', 'POST'])
def routeSettingsView():

    # Get Title
    title = request.form['title']
    package = request.form['package']
    link = request.form['link']

    # Load JSON data from file
    with open(link, 'r') as f:
        data = json.load(f)

    return render_template('detailSettings.html', title=title, link=link, package=package, items=data['items'])

@app.route('/detailView', methods=['GET', 'POST'])
def routeDetailView():

    # Get Title
    title = request.form['title']
    package = request.form['package']
    link = request.form['link']

    # Load JSON data from file
    with open(link, 'r') as f:
        data = json.load(f)

    return render_template('detailView.html', title=title, link=link, package=package, items=data['items'])


# Move Robot
@app.route('/move_robot', methods=['POST'])
def move_robot():
    x = float(request.form['x'])
    y = float(request.form['y'])
    z = float(request.form['z'])
    rx = float(request.form['rx'])
    ry = float(request.form['ry'])
    rz = float(request.form['rz'])
    
    positionArray = [x,y,z,rx,ry,rz]
    asyncio.run(position(positionArray))
    return Response(status=204)

@app.route('/testPosition', methods=['GET', 'POST'])
def move_robottest():

    value = request.form['value']
    x = 0.0
    y = 0.0
    z = 0.0
    topPlane = 400.0
    rx = 180.0
    ry = 0.0
    rz_crateSide = -90.0
    rz_boxSide = 90.0

    hoverCrate1 = [-536.42 , -799.43 , topPlane , rx , ry , rz_crateSide]
    hoverCrate2 = [-633.77 , -356.43 , topPlane , rx , ry , rz_crateSide]
    hoverCrate3 = [-647.11 , 139.67 , topPlane , rx , ry , rz_crateSide]
    hoverCrate4 = [-660.57 , 593.36 , topPlane , rx , ry , rz_crateSide]

    getVegetable = [-699.18 , -844.69 , 100.0 , rx , ry , rz_crateSide]

    if value == "hoverGet":
        asyncio.run(position(hoverCrate1))
    if value == "get":
        asyncio.run(position(getVegetable))
    if value == "hoverDrop":
        asyncio.run(position([511.01 , -212.48 , topPlane , 180.0 , 0.0 , 90.0]))
    if value == "drop":
        asyncio.run(position([511.01 , -212.48 , 315.41 , 180.0 , 0.0 , 90.0]))

    if value == "suction1drop":
        asyncio.run(position([555.95 , -212.34 , 269.28 , 180.0 , 31.19 , 90.0]))
    if value == "suction2drop":
        asyncio.run(position([562.27 , -403.77 , 294.42 , 180.0 , -27.99 , 90.0]))

    if value == "suction1get":
        asyncio.run(position([-619.47 , 186.75 , topPlane , 180.0 , 31.19 , -90.0]))
    if value == "suction2get":
        asyncio.run(position([-619.47 , 186.75 , topPlane , 180.0 , -27.99 , -90.0]))
    
    return Response(status=204)

@app.route('/setOutput', methods=['POST'])
def setOutput():

    mode = request.form['mode']
    status = request.form['status']

    if mode == "1":
        asyncio.run(setSuctionCup1Test(status))
        print("Toggle Suction 1")
    if mode == "2":
        asyncio.run(setSuctionCup2Test(status))
        print("Toggle Suction 2")

    return Response(status=204)

@app.route('/getLiveInformation')
def getLiveInformation():
    async def getCoordinates():
        async with techmanpy.connect_svr(robot_ip=ip) as conn:
            coordinates = await conn.get_value("Coord_Robot_Flange")
            speed = await conn.get_value("Project_Speed")
            status_suctionCup1 = bool(await conn.get_value("Ctrl_DO1"))
            status_suctionCup2 = bool(await conn.get_value("Ctrl_DO2"))
            luchtdruk = await conn.get_value("Ctrl_AI0")
            print(luchtdruk)
        return coordinates, speed, status_suctionCup1, status_suctionCup2
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    coordinates, speed, status_suctionCup1, status_suctionCup2 = loop.run_until_complete(getCoordinates())
    
    return jsonify({"coordinates": coordinates, "speed": speed, "status_suctionCup1": status_suctionCup1, "status_suctionCup2": status_suctionCup2})

@app.route('/updateJsonData', methods=['POST'])
def updateJsonData():

    # Load JSON data from file
    with open('static/json/database.json', 'r') as f:
        data = json.load(f)

    # Get the new values from the form
    id = request.form['id']
    product_name = request.form['product_name']
    product_image = request.form['product_image']
    product_package = request.form['product_package']
    crate_number = request.form['crateNumber']
    is_active = request.form.get('isActive', False)
    product_shape = request.form.get('product_shape', '')
    product_HSVRange = request.form.get('product_HSVRange', '')
    product_minSize = request.form.get('product_minSize', '')
    product_maxSize = request.form.get('product_maxSize', '')

    # Find the item in the JSON data
    for item in data['items']:
        if item['id'] == id:
            # Update the values
            item['product_name'] = product_name
            item['product_image'] = product_image
            item['product_package'] = product_package
            item['crateNumber'] = crate_number
            item['isActive'] = is_active
            item['product_shape'] = product_shape
            item['product_HSVRange'] = product_HSVRange
            item['product_minSize'] = product_minSize
            item['product_maxSize'] = product_maxSize
            break

    # Save the updated JSON data back to the file
    with open('static/json/database.json', 'w') as f:
        json.dump(data, f, indent=2)

    # Redirect back to the items grid
    return Response(status=204)


@app.route('/StartStream')
def StartStream():
    # Initialize Camera Intel Realsense
    pipeline=initizalize_rs()
    mtx,dist=calibrate_camera(pipeline)

# Test Variables -------------------------
x = 0.0
y = 0.0
z = 0.0
topPlane = 400.0
rx = 180.0
ry = 0.0
rz_crateSide = -90.0
rz_boxSide = 90.0

hoverCrate1 = [-536.42 , -799.43 , topPlane , rx , ry , rz_crateSide]
hoverCrate2 = [-633.77 , -356.43 , topPlane , rx , ry , rz_crateSide]
hoverCrate3 = [-647.11 , 139.67 , topPlane , rx , ry , rz_crateSide]
hoverCrate4 = [-660.57 , 593.36 , topPlane , rx , ry , rz_crateSide]

hoverBox = [511.01 , -212.48 , topPlane , rx , ry , rz_boxSide]

@app.route('/Start', methods=['POST'])
def Start():

    # Open Pipline
    pipeline=initizalize_rs()

    # Open JSON
    with open('static/json/database.json', 'r') as f:
        data = json.load(f)

    # Get Package Name
    package = request.form['package']
    #getVegetable = [0.0 , 0.0 , 0.0 , 0.0 , 0.0 , 0.0]

    for product in data["items"]:
        if product["package"] == package:
            for item in product["products"]:
                if item["isActive"] == "on":

                    # Code For CameraShit
                    got_frame = 0
                    # Initialize Camera Intel Realsense
        
                    #create trackbar and images
                    #calibrate_camera(pipeline)
                    mtx,dist=read_cal()
                    makeframe()
                    while True:
                        #read info from trackbars
                        hsvunder1,hsvunder2,hsvunder3,hsvupper1,hsvupper2,hsvupper3=readtrackbar()
                        #Use filters and circle detection to get center coordinate
                        image_with_points,pickup_coordinates,gray_image,crop,original_color_frame=getpoint(pipeline,item)
                        if pickup_coordinates != []:
                            getVegetable=make_3D_point(pickup_coordinates[0][0][0]+crop[2], pickup_coordinates[0][0][1]+crop[0],pipeline,mtx,dist)
                            print("3D Point in robot arm coordinates:", getVegetable)
                            #print(coor[0][0][0])
                            #show edited and original frame with contours and center
                            original_with_points=draw_original(original_color_frame, pickup_coordinates,crop[2],crop[0])
                            got_frame=1
                            cv2.imshow("Origineel frame", original_with_points)
                            cv2.imshow("bewerkt frame", image_with_points)
                            cv2.imshow("Grijs frame",gray_image)
                            cv2.waitKey(100)
                            key = cv2.waitKey(1)
                        if got_frame==1:
                            got_frame = 0
                            break

                    # Get Coordinate Crate Hover
                    if item["crateNumber"] == "1":
                        asyncio.run(position(hoverCrate1, 0))
                    if item["crateNumber"] == "2":
                        asyncio.run(position(hoverCrate2, 0))
                    # Get Coordinate Pick Up
                    getVegetable = [getVegetable[0] , getVegetable[1] , getVegetable[2] , rx , -27.99 , rz_crateSide]
                    asyncio.run(position(getVegetable, 1))
                    # Turn On Suction
                    asyncio.run(setSuctionCup1(1))
                    # Get Coordinate Crate Hover
                    asyncio.run(position(hoverCrate1, 0))
                    # Get Coordinate Box Hover
                    asyncio.run(position(hoverBox, 1))
                    # Get Coordinate Box Place

                    # Turn Off Suction
                    asyncio.run(setSuctionCup1(0))
                    # Get Coordinate Box Hover
                    asyncio.run(position(hoverBox, 0))
        
                 


    return Response(status=204)

if __name__ == '__main__':
    app.run(debug=True)




