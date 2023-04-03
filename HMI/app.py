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

# ---------------------------------------------------------------------

async def position(positionArray):
    async with techmanpy.connect_sct(robot_ip=ip) as conn:
        await conn.move_to_point_ptp(positionArray, 1, 1000)

async def setSuctionCup(positionArray, status):
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

# --------------------------------------------------------------------------
async def setSuctionCupTest(status):
    async with techmanpy.connect_svr(robot_ip=ip) as conn:
            await conn.set_value("Ctrl_DO1", status)

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
    calibrationCamera1 = [-636.0 , -663.0  , -200.0 , 180.0 , 0.0 , -90.0]

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
    calibrationCamera2 = [-705.0 , 192.0 , -200.0 , 180.0 , 0.0 , -90.0]

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
    HomeBase = [511.01 , -212.48 , 700.0 , 180.0 , 0.0 , 90.0]

    async with techmanpy.connect_sct(robot_ip=ip) as conn:
        await conn.move_to_point_ptp(HomeBase, 1, 1000)

@app.route('/GoToHomeBase')
def GoToHomeBase():
    asyncio.run(GoToHomeBase_Coordinates())

    return Response(status=204)

# -----------------------------------------------------------
# Reset Conveyer

async def ResetConveyer():

    ir_status = False

    async with techmanpy.connect_svr(robot_ip=ip) as conn:
        await conn.set_value("Ctrl_DO5", 1)

    while ir_status == False:
        async with techmanpy.connect_svr(robot_ip=ip) as conn:
            ir_status = bool(await conn.get_value("Ctrl_DI2"))

    if ir_status == True:
        async with techmanpy.connect_svr(robot_ip=ip) as conn:
            await conn.set_value("Ctrl_DO5", 0)
    
@app.route('/resetConveyer')
def resetConveyer():
    asyncio.run(ResetConveyer())

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


    asyncio.run(setSuctionCup(hoverCrate1, 0))

    
    return Response(status=204)

@app.route('/setOutput', methods=['POST'])
def setOutput():

    mode = request.form['mode']
    status = request.form['status']

    if mode == "1":
        asyncio.run(setSuctionCupTest(status))
        print("Toggle Suction 1")
    if mode == "2":
        asyncio.run(setSuctionCupTest(status))
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
def getHoverCoordinates(crateNumber, x, y, z, xOffset, yOffset, zOffset):

    hoverCrate1 = [0.0 , 0.0 , 400.0 , -180.0 , 0.0 , -90.0]
    hoverCrate2 = [0.0 , 0.0 , 400.0 , -180.0 , 0.0 , -90.0]
    hoverCrate3 = [0.0 , 0.0 , 400.0 , -180.0 , 0.0 , -90.0]
    hoverCrate4 = [0.0 , 0.0 , 400.0 , -180.0 , 0.0 , -90.0]

    if crateNumber == "1":
        hoverCrate1[0] = x + xOffset
        hoverCrate1[1] = y + yOffset
        hoverCrate1[2] = z + zOffset
        asyncio.run(position(hoverCrate1))
    elif crateNumber == "2":
        hoverCrate2[0] += xOffset
        hoverCrate2[1] += yOffset
        hoverCrate2[2] += zOffset
        asyncio.run(position(hoverCrate2))
    elif crateNumber == "3":
        hoverCrate3[0] += xOffset
        hoverCrate3[1] += yOffset
        hoverCrate3[2] += zOffset
        asyncio.run(position(hoverCrate3))
    elif crateNumber == "4":
        hoverCrate4[0] += xOffset
        hoverCrate4[1] += yOffset
        hoverCrate4[2] += zOffset
        asyncio.run(position(hoverCrate4))

@app.route('/nextPackage')
def nextPackage():
    asyncio.run(moveConveyerBelt())

    return Response(status=204)

async def moveConveyerBelt():

    ir_status = True

    # Turn On Motor
    async with techmanpy.connect_svr(robot_ip=ip) as conn:
        await conn.set_value("Ctrl_DO5", 1)

    while ir_status == True:
        async with techmanpy.connect_svr(robot_ip=ip) as conn:
            ir_status = bool(await conn.get_value("Ctrl_DI2"))
            
    if ir_status == False:

        while ir_status == False:
            async with techmanpy.connect_svr(robot_ip=ip) as conn:
                ir_status = bool(await conn.get_value("Ctrl_DI2"))

        if ir_status == True:
            async with techmanpy.connect_svr(robot_ip=ip) as conn:
                await conn.set_value("Ctrl_DO5", 0)

def crateOffset(crateNumber):

    if crateNumber == "1":
        x_offset1 = 30.0
        y_offset1 = 10.0
        z_offset1 = 465.0
        return [x_offset1, y_offset1, z_offset1]
    
    elif crateNumber == "2":
        x_offset2 = 85.0
        y_offset2 = -10.0
        z_offset2 = 480.0
        return [x_offset2, y_offset2, z_offset2]
    
    elif crateNumber == "3":
        x_offset3 = 70.0
        y_offset3 = 40.0
        z_offset3 = 505.0
        return [x_offset3, y_offset3, z_offset3]
    
    elif crateNumber == "4":
        x_offset4 = 50.0
        y_offset4 = 20.0
        z_offset4 = 495.0
        return [x_offset4, y_offset4, z_offset4]

        


@app.route('/Start', methods=['POST'])
def Start():

    suction = False

    hoverBox = [511.01 , -212.48 , 700.0 , 180.0 , 0.0 , 90.0]

    # Suction
    # ry (-27.99 or 0.0), because of the other suction cup
    # rz (90.0 or -90.0), because of the lamp of the camera
    Orientation = [0.0 , 0.0 , 400.0 , -180.0 , 0.0 ,  -90.0] # Top of the crate

    # Initializing Camera
    pipeline1,pipeline2=initizalize_rs()
    camera=1

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
                            print(location)
                            
                        got_frame += 1
                            
                        if got_frame == 100:
                            break

                    if got_frame == 100:

                        getHoverCoordinates(item["crateNumber"], location[0], location[1], 400.0, crateOffset(item["crateNumber"])[0], crateOffset(item["crateNumber"])[1] , 0.0)

                        Orientation[0] = location[0] + crateOffset(item["crateNumber"])[0]
                        Orientation[1] = location[1] + crateOffset(item["crateNumber"])[1]
                        Orientation[2] = location[2] + crateOffset(item["crateNumber"])[2]

                        asyncio.run(setSuctionCup(Orientation, 1))

                        getHoverCoordinates(item["crateNumber"], location[0], location[1], 400.0, crateOffset(item["crateNumber"])[0], crateOffset(item["crateNumber"])[1] , 0.0)
                                        
                        suction = True
                                
                        # Go Home Last Item
                        asyncio.run(setSuctionCup(hoverBox, 0))

                        # Reset
                        suction = False

    asyncio.run(moveConveyerBelt())

    return Response(status=204) 
    

if __name__ == '__main__':
    app.run(debug=True)




