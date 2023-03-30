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

async def positionWithoutTag(positionWithoutTag):
    async with techmanpy.connect_sct(robot_ip=ip) as conn:
        await conn.move_to_point_ptp(positionWithoutTag, 1, 1000)

async def setSuctionCup1(status):
    async with techmanpy.connect_sta(robot_ip=ip) as conn:
        tag_status = await conn.get_queue_tag_status(1)

    async with techmanpy.connect_svr(robot_ip=ip) as conn:
        if tag_status == True:
            await conn.set_value("Ctrl_DO1", status)
            tag_status = False

async def setSuctionCup2(status):
    async with techmanpy.connect_sta(robot_ip=ip) as conn:
        tag_status = await conn.get_queue_tag_status(4)

    async with techmanpy.connect_svr(robot_ip=ip) as conn:
        if tag_status == True:
            await conn.set_value("Ctrl_DO4", status)
            tag_status = False

# ---------------------------------------------------------------------
async def setSuctionCup1Try(positionArray, status):
    async with techmanpy.connect_sct(robot_ip=ip) as conn:
        await conn.move_to_point_ptp(positionArray, 1, 1000)

        await conn.set_queue_tag(tag_id = 1)
        await conn.wait_for_queue_tag(tag_id = 1)

    async with techmanpy.connect_sta(robot_ip=ip) as conn:
        tag_status = await conn.get_queue_tag_status(1)

    async with techmanpy.connect_svr(robot_ip=ip) as conn:
        if tag_status == True:
            await conn.set_value("Ctrl_DO1", status)
            tag_status = False


async def setSuctionCup2Try(positionArray, status):
    async with techmanpy.connect_sct(robot_ip=ip) as conn:
        await conn.move_to_point_ptp(positionArray, 1, 1000)

        await conn.set_queue_tag(tag_id = 4)
        await conn.wait_for_queue_tag(tag_id = 4)

    async with techmanpy.connect_sta(robot_ip=ip) as conn:
        tag_status = False
        tag_status = await conn.get_queue_tag_status(4)

    async with techmanpy.connect_svr(robot_ip=ip) as conn:
        if tag_status == True:
            await conn.set_value("Ctrl_DO4", status)
             
# --------------------------------------------------------------------------
async def setSuctionCup1Test(status):
    async with techmanpy.connect_svr(robot_ip=ip) as conn:
            await conn.set_value("Ctrl_DO1", status)

async def setSuctionCup2Test(status):
    async with techmanpy.connect_svr(robot_ip=ip) as conn:
            await conn.set_value("Ctrl_DO4", status)

# -----------------------------------------------------------
# Pause an ongoing project

async def pauseProject():
    async with techmanpy.connect_sct(robot_ip=ip) as conn:
            await conn.pause_project()

@app.route('/PauseProject')
def PauseProject():
    asyncio.run(pauseProject())

    return Response(status=204)

# -----------------------------------------------------------
# Resume an paused project

async def resumeProject():
    async with techmanpy.connect_sct(robot_ip=ip) as conn:
            await conn.resume_project()

@app.route('/ResumeProject')
def ResumeProject():
    asyncio.run(resumeProject())

    return Response(status=204)

# -----------------------------------------------------------
# Calibrate Camera 1

async def calibrateCamera1_Position():
    calibrationCamera1 = [-636.0 , -663.0  , 300.0 , 180.0 , 0.0 , -90.0]

    async with techmanpy.connect_sct(robot_ip=ip) as conn:
        await conn.move_to_point_ptp(calibrationCamera1, 1, 1000)

async def calibrateCamera1_GetCoordinates():
    async with techmanpy.connect_svr(robot_ip=ip) as conn:
        coordinates = await conn.get_value("Coord_Robot_Flange")
    return coordinates

@app.route('/CalibrateCamera1')
def CalibrateCamera1():
    pipeline1,pipeline2=initizalize_rs()
    asyncio.run(calibrateCamera1_Position())

    asyncio.sleep(13)

    coordinates = asyncio.run(calibrateCamera1_GetCoordinates())
    coordinates = coordinates[:-3]

    calibrateXY(pipeline1, coordinates, 1)

    pipeline1.stop()
    pipeline2.stop()

    return Response(status=204)

# -----------------------------------------------------------
# Calibrate Camera 2

async def calibrateCamera2_Position():
    calibrationCamera2 = [-705.0 , 192.0 , 300.0 , 180.0 , 0.0 , -90.0]

    async with techmanpy.connect_sct(robot_ip=ip) as conn:
        await conn.move_to_point_ptp(calibrationCamera2, 1, 1000)

async def calibrateCamera2_GetCoordinates():
    async with techmanpy.connect_svr(robot_ip=ip) as conn:
        coordinates = await conn.get_value("Coord_Robot_Flange")
    return coordinates

@app.route('/CalibrateCamera2')
def CalibrateCamera2():
    pipeline1,pipeline2=initizalize_rs()
    asyncio.run(calibrateCamera2_Position())

    asyncio.sleep(13)

    coordinates = asyncio.run(calibrateCamera2_GetCoordinates())
    coordinates = coordinates[:-3]

    calibrateXY(pipeline2, coordinates, 2)

    pipeline1.stop()
    pipeline2.stop()

    return Response(status=204)

# -----------------------------------------------------------
# Home Base Coordinates

async def GoToHomeBase_Coordinates():
    HomeBase = [511.01 , -212.48 , 600.0 , 180.0 , 0.0 , 90.0]

    async with techmanpy.connect_sct(robot_ip=ip) as conn:
        await conn.move_to_point_ptp(HomeBase, 1, 1000)

@app.route('/GoToHomeBase')
def GoToHomeBase():
    asyncio.run(GoToHomeBase_Coordinates())

    return Response(status=204)

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


    asyncio.run(position(hoverCrate1, 0))

    
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



# -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def getHoverCoordinates(crateNumber, hoverCrate1, hoverCrate2, hoverCrate3, hoverCrate4):

    if crateNumber == "1":
        asyncio.run(positionWithoutTag(hoverCrate1))
        #return print("Hover over crate 1")
    elif crateNumber == "2":
        asyncio.run(positionWithoutTag(hoverCrate2))
        #return print("Hover over crate 2")
    elif crateNumber == "3":
        asyncio.run(positionWithoutTag(hoverCrate3))
        #return print("Hover over crate 3")
    elif crateNumber == "4":
        asyncio.run(positionWithoutTag(hoverCrate4))
        #return print("Hover over crate 4")

@app.route('/Start', methods=['POST'])
def Start():

    # Variables
    teller = 0 # Counts when it needs to return home
    place = "" # Camera Gives String that describes the place of the vegetable

    suctioncupRedLeft = False
    suctioncupRedRight = False

    topPlane = 400.0
    rx = 180.0
    ry = 0.0
    rz_crateSide = -90.0
    rz_boxSide = 90.0

    redSuctionQueue = 1
    blueSuctionQueue = 4

    hoverIdle = [-675.0 , -250.0 , 400.0 , rx , ry , rz_crateSide]
    hoverIdleUp = [-675.0 , -250.0 , 700.0 , rx , ry , rz_crateSide]

    hoverCrate1 = [-536.42 , -799.43 , topPlane , rx , ry , rz_crateSide]
    hoverCrate2 = [-633.77 , -356.43 , topPlane , rx , ry , rz_crateSide]
    hoverCrate3 = [-647.11 , 139.67 , topPlane , rx , ry , rz_crateSide]
    hoverCrate4 = [-660.57 , 593.36 , topPlane , rx , ry , rz_crateSide]

    hoverBox = [511.01 , -212.48 , 600.0 , rx , ry , rz_boxSide]

    # Suction
    # ry (-27.99 or 0.0), because of the other suction cup
    # rz (90.0 or -90.0), because of the lamp of the camera
    OrientationTop1 = [0.0 , 0.0 , 0.0 , 180.0 , 31.19 ,  0.0] # Top of the crate
    OrientationBottom1 = [0.0 , 0.0 , 0.0 , 180.0 , 31.19 , 180.0] # Bottom of the crate
    OrientationTop2 = [0.0 , 0.0 , 0.0 , -180.0 , -31.19 ,  -180.0] # Top of the crate
    OrientationBottom2 = [0.0 , 0.0 , 0.0 , -180.0 , -31.19 , 0.0] # Bottom of the crate


    # Initializing Camera
    pipeline1,pipeline2=initizalize_rs()
    camera=2

    # Open JSON
    with open('HMI\static\json\database.json', 'r') as f:
        data = json.load(f)

    # Get Package Name
    package = request.form['package']

    for product in data["items"]:
        if product["package"] == package:
            for index, item in enumerate(product["products"]):
                if item["isActive"] == "true":
                # Make Picture and Calculate Coordinates
                    got_frame = 0
                    while True:
                        #Use filters and circle detection to get center coordinate
                        image_with_points,pickup_coordinates,gray_image,crop,original_color_frame,camera,pipeline,place=getpoint(pipeline1,pipeline2,item)
                            
                        if pickup_coordinates != []:
                            location=make_3D_point(pickup_coordinates[0][0][0]+crop[2], pickup_coordinates[0][0][1]+crop[0],pipeline,camera)
                            original_with_points=draw_original(original_color_frame, pickup_coordinates,crop[0],crop[2])
        
                            got_frame = 1
                            
                        if got_frame == 1:
                            break

                    if got_frame == 1:

                            # Get Coordinate Crate Hover
                            getHoverCoordinates(item["crateNumber"], hoverCrate1, hoverCrate2, hoverCrate3, hoverCrate4)

                            if (item["suctioncup"] == "Rood"):
                                if ((place == "LeftUp") or (place == "LeftDown")): 
                                    if (suctioncupRedLeft == False and suctioncupRedRight == False):

                                        OrientationTop1[0] = location[0]
                                        OrientationTop1[1] = location[1]
                                        OrientationTop1[2] = 300.0

                                        # Pickup Red as preference
                                        asyncio.run(setSuctionCup1Try(OrientationTop1, 1))
                                 
                                        asyncio.run(positionWithoutTag(hoverIdle))
                                        suctioncupRedLeft = True
                                    elif (suctioncupRedLeft == True and suctioncupRedRight == False):

                                        OrientationTop2[0] = location[0]
                                        OrientationTop2[1] = location[1]
                                        OrientationTop2[2] = 300.0

                                        # Pickup with Blue is necessary
                                        asyncio.run(setSuctionCup2Try(OrientationTop2, 1))
                                        
                                        suctioncupRedRight = True

                                if ((place == "RightUp") or (place == "RightDown")):
                                    if (suctioncupRedLeft == False and suctioncupRedRight == False):

                                        OrientationBottom1[0] = location[0]
                                        OrientationBottom1[1] = location[1]
                                        OrientationBottom1[2] = 300.0

                                        # Pickup Red as preference
                                        asyncio.run(setSuctionCup1Try(OrientationBottom1, 1))
                                        
                                        asyncio.run(positionWithoutTag(hoverIdle))
                                        suctioncupRedLeft = True
                                    elif (suctioncupRedLeft == True and suctioncupRedRight == False):

                                        OrientationBottom2[0] = location[0]
                                        OrientationBottom2[1] = location[1]
                                        OrientationBottom2[2] = 300.0

                                        # Pickup with Blue is necessary
                                        asyncio.run(setSuctionCup2Try(OrientationBottom2, 1))
                                        
                                        suctioncupRedRight = True

                            #elif (item["suctioncup"] == "Blauw"):

                        # ---------------------------------------------------------------

                    if (suctioncupRedLeft == True and suctioncupRedRight == True):
                        # Go Home 
                        asyncio.run(setSuctionCup1Try(hoverBox, 0))
                        asyncio.run(setSuctionCup2Try(hoverBox, 0))

                        # Reset
                        suctioncupRedRight = False
                        suctioncupRedLeft = False

    # Go Home Last Item
    asyncio.run(setSuctionCup1Try(hoverBox, 0))
    asyncio.run(setSuctionCup2Try(hoverBox, 0))

    # Reset
    suctioncupRedLeft = False
    suctioncupRedRight = False

    return Response(status=204) 

if __name__ == '__main__':
    app.run(debug=True)




