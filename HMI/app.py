from flask import Flask, render_template, request, jsonify, json
import cv2
import numpy as np
from flask import Flask, Response
import asyncio
import techmanpy
from techmanpy import TechmanException
import pyrealsense2 as rs

from connectionPLC import *

import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))
from Vegetables_V4 import *


app = Flask(__name__, template_folder=r'C:\Users\Jarik\OneDrive\Documenten\GitHub\Dero-Project\HMI\templates')
app.static_folder = 'static'

# -----------------------------------------------------------
# PLC

ip = '192.168.0.204'

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
            await conn.set_value("Ctrl_DO4", status)
            tag_status = False

async def setSuctionCup1Test(status):
    async with techmanpy.connect_svr(robot_ip=ip) as conn:
            await conn.set_value("Ctrl_DO1", status)

async def setSuctionCup2Test(status):
    async with techmanpy.connect_svr(robot_ip=ip) as conn:
            await conn.set_value("Ctrl_DO4", status)

# -----------------------------------------------------------

@app.route('/')
def routeView():
        return render_template('Home.html')

@app.route('/ManualControl')
def ManualControl():
    return render_template('ManualControl.html')

@app.route('/AutomaticControlSettings', methods=['GET', 'POST'])
def AutomaticControlSettings():

    # Get Title
    package = request.form['package']
    link = request.form['link']

    # Load JSON data from file
    with open(link, 'r') as f:
        data = json.load(f)

    return render_template('AutomaticControlSettings.html', link=link, package=package, items=data['items'])

@app.route('/AutomaticControl', methods=['GET', 'POST'])
def AutomaticControl():

    # Get Title
    package = request.form['package']
    link = request.form['link']

    # Load JSON data from file
    with open(link, 'r') as f:
        data = json.load(f)

    return render_template('AutomaticControl.html', link=link, package=package, items=data['items'])


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
    asyncio.run(position(positionArray,0))
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
    hoverCrate4 = [-646.80 , 387.27 , topPlane , rx , 31.19 , rz_crateSide]

    getVegetable = [-699.18 , -844.69 , 100.0 , rx , ry , rz_crateSide]

    if value == "hoverGet":
        asyncio.run(position(hoverCrate4, 0))
    if value == "get":
        asyncio.run(position(getVegetable))
    if value == "hoverDrop":
        asyncio.run(position([511.01 , -212.48 , topPlane , 180.0 , 0.0 , 90.0], 0))
    if value == "drop":
        asyncio.run(position([511.01 , -212.48 , 315.41 , 180.0 , 0.0 , 90.0]))

    if value == "suction1drop":
        asyncio.run(position([555.95 , -212.34 , 269.28 , 180.0 , 31.19 , 90.0], 0))
    if value == "suction2drop":
        asyncio.run(position([562.27 , -403.77 , 294.42 , 180.0 , -27.99 , 90.0], 0))

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
        # Connect to the robot server
        async with techmanpy.connect_svr(robot_ip=ip) as conn:
            # Retrieve live information about the robot
            coordinates = await conn.get_value("Coord_Robot_Flange")
            speed = await conn.get_value("Project_Speed")
            status_suctionCup1 = bool(await conn.get_value("Ctrl_DO1"))
            status_suctionCup2 = bool(await conn.get_value("Ctrl_DO4"))
        return coordinates, speed, status_suctionCup1, status_suctionCup2
    
    # Check the connection status of the robot before retrieving live information
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    #SVR_status, SCT_status, STA_status = loop.run_until_complete(test_connection(ip))
    
    # Retrieve live information about the robot
    coordinates, speed, status_suctionCup1, status_suctionCup2 = loop.run_until_complete(getCoordinates())

    # Return the live information as a JSON object
    return jsonify({
        'coordinates': coordinates,
        'speed': speed,
        'status_suctionCup1': str(status_suctionCup1),
        'status_suctionCup2': str(status_suctionCup2),
        #'SVR_status': SVR_status,
        #'SCT_status': SCT_status,
        #'STA_status': STA_status,
    })


@app.route('/updateJsonData', methods=['POST'])
def updateJsonData():
     # Load JSON data from file
    with open('HMI/static/json/database.json', 'r') as f:
        data = json.load(f)

    # Get the new values from the form
    id = request.form['id']
    product_package = request.form['product_package']
    crateNumber = request.form['crateNumber']
    isActive = request.form.get('isActive')

    # Loop through each package and product
    for item in data['items']:
        if item['package'] == product_package:
            for product in item['products']:
                if product['id'] == id:
                    # Update the values for the matching product
                    product['crateNumber'] = crateNumber
                    product['isActive'] = isActive
                    break

    # Save the updated JSON data back to the file
    with open('HMI/static/json/database.json', 'w') as f:
        json.dump(data, f, indent=2)

    # Redirect back to the items grid
    return Response(status=204)

@app.route('/Stop', methods=['POST'])
def Stop():
    return Response(status=204)




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
hoverCrate4 = [-646.80 , 387.27 , topPlane , rx , ry , rz_crateSide]

hoverBox = [511.01 , -212.48 , topPlane , rx , ry , rz_boxSide]

@app.route('/Start', methods=['POST'])
def Start():
    got_frame = 0

    # Initialize Camera Intel Realsense
    pipeline1,pipeline2=initizalize_rs()
    #create trackbar and images
    camera=2
    #calibrate_camera(pipeline2,camera)

    # Open JSON
    with open('HMI\static\json\database.json', 'r') as f:
        data = json.load(f)

    # Get Package Name
    package = request.form['package']

    for product in data["items"]:
        if product["package"] == package:
            for item in product["products"]:
                if item["isActive"] == "true":
                    got_frame = 0

                    # Camera
                    while True:
                        if (camera==1):
                            pipeline=pipeline1
                        elif(camera==2):
                            pipeline=pipeline2
                        #read info from trackbars
                        #hsvunder1,hsvunder2,hsvunder3,hsvupper1,hsvupper2,hsvupper3=readtrackbar()
                        #Use filters and circle detection to get center coordinate
                        image_with_points,pickup_coordinates,gray_image,crop,original_color_frame,camera,pipeline=getpoint(pipeline1,pipeline2,item)

                        if pickup_coordinates != []:
                            getVegetable=make_3D_point(pickup_coordinates[0][0][0]+crop[2], pickup_coordinates[0][0][1]+crop[0],pipeline,camera)
                            print("3D Point in robot arm coordinates:", getVegetable)
                            original_with_points=draw_original(original_color_frame, pickup_coordinates,crop[0],crop[2])
                            got_frame=1
                        if got_frame==1:
                            break

                    if (got_frame == 1):
                         # Get Coordinate Crate Hover
                        if item["crateNumber"] == "1":
                            asyncio.run(position(hoverCrate1, 0))
                        if item["crateNumber"] == "2":
                            asyncio.run(position(hoverCrate2, 0))
                        if item["crateNumber"] == "3":
                            asyncio.run(position(hoverCrate3, 0))
                        if item["crateNumber"] == "4":
                            asyncio.run(position(hoverCrate4, 0))
                        
                        # Get Coordinate Pick Up
                        getVegetable = [getVegetable[0] , getVegetable[1] , getVegetable[2] , rx , 31.19 , rz_crateSide]
                        asyncio.run(position([getVegetable[0], getVegetable[1], 400.0, rx, 31.19, rz_crateSide], 1))
                        asyncio.run(position([getVegetable[0], getVegetable[1], getVegetable[2], rx, 31.19, rz_crateSide], 1))

                        # Turn On Suction
                        asyncio.run(setSuctionCup1(1))
                        
                        # Get Coordinate Crate Hover
                        if item["crateNumber"] == "1":
                            asyncio.run(position(hoverCrate1, 0))
                        if item["crateNumber"] == "2":
                            asyncio.run(position(hoverCrate2, 0))
                        if item["crateNumber"] == "3":
                            asyncio.run(position(hoverCrate3, 0))
                        if item["crateNumber"] == "4":
                            asyncio.run(position(hoverCrate4, 0))
                        # Get Coordinate Box Hover
                        
                        asyncio.run(position(hoverBox, 1)) 
                        # Get Coordinate Box Place

                        # Turn Off Suction
                        
                        asyncio.run(setSuctionCup1(0))
                        # Get Coordinate Box Hover
                        
                        asyncio.run(position(hoverBox, 0))

    pipeline1.stop()    

    return Response(status=204)

if __name__ == '__main__':
    app.run(debug=True)




