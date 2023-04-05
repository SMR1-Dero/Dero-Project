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
import math
#sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))
from Vegetables_V4 import *

# ---------------------------------------------------------------------
# Settings Flask App
app = Flask(__name__, template_folder=r'C:\Users\Jarik\OneDrive\Documenten\GitHub\Dero-Project\HMI\templates')
app.static_folder = 'static'

# ---------------------------------------------------------------------
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
    HomeBase = [505.24 , -317.63 , 700.0 , 180.0 , 0.0 , 90.0]

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
    # Returns HTML Page (Home.html)
    return render_template('Home.html')

# -----------------------------------------------------------

@app.route('/AutomaticControl', methods=['GET', 'POST'])
def AutomaticControl():

    # Get Title
    package = request.form['package']
    link = request.form['link']

    # Load JSON data from file
    with open(link, 'r') as f:
        data = json.load(f)

    return render_template('AutomaticControl.html', link=link, package=package, items=data['items'])

# -----------------------------------------------------------

@app.route('/AutomaticControlSettings', methods=['GET', 'POST'])
def AutomaticControlSettings():

    # Get the Package name and the product image link from the HTML file (AutomaticControl.html)
    package = request.form['package']
    link = request.form['link']

    # Load JSON data from file (database.json)
    with open(link, 'r') as f:
        data = json.load(f)

    # Returns HTML Page (AutomaticControlSettings.html)
    return render_template('AutomaticControlSettings.html', link=link, package=package, items=data['items'])

# -----------------------------------------------------------

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

@app.route('/setOutput', methods=['POST'])
def setOutput():

    status = request.form['status']

    asyncio.run(setSuctionCupTest(status))


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

@app.route('/updateAmount', methods=['POST'])
def updateAmount():
     # Load JSON data from file
    with open('HMI/static/json/database.json', 'r') as f:
        data = json.load(f)

    # Get the new values from the form
    product_package = request.form['package']
    amount = request.form['amount']

    # Loop through each package and product
    for item in data['items']:
        if item['package'] == product_package:
            item['amount'] = int(amount)

    # Save the updated JSON data back to the file
    with open('HMI/static/json/database.json', 'w') as f:
        json.dump(data, f, indent=2)

    # Redirect back to the items grid
    return Response(status=204)



# -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def getHoverCoordinates(crateNumber, x, y, xOffset, yOffset):

    hoverCrate = [0.0 , 0.0 , 400.0 , -180.0 , 0.0 , -90.0]

    if crateNumber == "1":
        hoverCrate[0] = x + xOffset
        hoverCrate[1] = y + yOffset
        print("Hover Crate 1:", hoverCrate)
        asyncio.run(setSuctionCup(hoverCrate, 1))
    elif crateNumber == "2":
        hoverCrate[0] += x + xOffset
        hoverCrate[1] += y + yOffset
        print("Hover Crate 2:", hoverCrate)
        asyncio.run(setSuctionCup(hoverCrate, 1))
    elif crateNumber == "3":
        hoverCrate[0] += x + xOffset
        hoverCrate[1] += y + yOffset
        asyncio.run(setSuctionCup(hoverCrate, 1))
    elif crateNumber == "4":
        hoverCrate[0] += x + xOffset
        hoverCrate[1] += y + yOffset
        asyncio.run(setSuctionCup(hoverCrate, 1))


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

def crateOffset(crateNumber, suctionCupColor):

    if crateNumber == "1":
        x_offset1 = 15.0
        y_offset1 = 5.0

        if suctionCupColor == "Rood":
            z_offset1 = 440.0
        elif suctionCupColor == "Blauw":
            z_offset1 = 440.0

        return [x_offset1, y_offset1, z_offset1]
    
    elif crateNumber == "2":
        x_offset2 = 5.0
        y_offset2 = -15.0

        if suctionCupColor == "Rood":
            z_offset2 = 420.0
        elif suctionCupColor == "Blauw":
            z_offset2 = 400.0

        return [x_offset2, y_offset2, z_offset2]
    
    elif crateNumber == "3":
        x_offset3 = -20.0
        y_offset3 = 25.0

        if suctionCupColor == "Rood":
            z_offset3 = 450.0
        elif suctionCupColor == "Blauw":
            z_offset3 = 405.0

        return [x_offset3, y_offset3, z_offset3]
    
    elif crateNumber == "4":
        x_offset4 = -45.0
        y_offset4 = 25.0

        if suctionCupColor == "Rood":
            z_offset4 = 405.0
        elif suctionCupColor == "Blauw":
            z_offset4 = 415.0

        return [x_offset4, y_offset4, z_offset4]

async def isSucking():
    
    suction = False

    async with techmanpy.connect_svr(robot_ip=ip) as conn:
        suction = bool(await conn.get_value("Ctrl_DI1"))

    return suction


@app.route('/Start', methods=['POST'])
def Start():

    hoverBox = [505.24 , -317.63 , 700.0 , 180.0 , 0.0 , 90.0]

    # Will count how many packages need to packed
    amount = 0

    # Suction
    # ry (-27.99 or 0.0), because of the other suction cup
    # rz (90.0 or -90.0), because of the lamp of the camera
    Orientation = [0.0 , 0.0 , 400.0 , -180.0 , 0.0 ,  -90.0] # Top of the crate
    location = [0.0 , 0.0 , 0.0]

    # Initializing Camera
    pipeline1,pipeline2=initizalize_rs()

    # Open JSON
    with open('HMI\static\json\database.json', 'r') as f:
        data = json.load(f)

    # Get Package Name
    package = request.form['package']

    for product in data["items"]:
        if product["package"] == package:
            while amount < product["amount"]:
                for index, item in enumerate(product["products"]):
                    if item["isActive"] == "true":

                        # Maximum number of attempts
                        max_attempts = 3
                        attempt_count = 0
                        # Suction
                        suction = False
                        get_newPhoto = True

                        while suction == False and attempt_count != max_attempts:

                            # Reset got_Frame and coordinates array
                            pickup_coordinates = []
                            got_frame = 0

                            # Choosing Camera
                            if ((item['crateNumber'] == "1") or (item['crateNumber'] == "2")):
                                camera = 1
                            elif ((item['crateNumber'] == "3") or (item['crateNumber'] == "4")):
                                camera = 2

                            # Make Picture and Calculate Coordinates                    
                            while get_newPhoto == True:
                                
                                #Use filters and circle detection to get center coordinate
                                image_with_points,pickup_coordinates,gray_image,crop,original_color_frame,camera,pipeline,place=getpoint(pipeline1,pipeline2,item)

                                cv2.imshow("Origineel frame", image_with_points)
                                cv2.waitKey(100)

                                if pickup_coordinates != []:
                                    location=make_3D_point(pickup_coordinates[0][0][0]+crop[2], pickup_coordinates[0][0][1]+crop[0],pipeline,camera)
                                    original_with_points=draw_original(original_color_frame, pickup_coordinates,crop[0],crop[2])
                                    got_frame = 1
                                
                                if got_frame == 1:
                                    get_newPhoto = False
                                    break

                            if got_frame == 1:
                                getHoverCoordinates(item["crateNumber"], location[0], location[1], crateOffset(item["crateNumber"], item["suctioncup"])[0], crateOffset(item["crateNumber"], item["suctioncup"])[1])

                                Orientation[0] = location[0] + crateOffset(item["crateNumber"], item["suctioncup"])[0]
                                Orientation[1] = location[1] + crateOffset(item["crateNumber"], item["suctioncup"])[1]
                                Orientation[2] = location[2] + crateOffset(item["crateNumber"], item["suctioncup"])[2]
                                
                                # Jochem Gives Orientation
                                #Orientation[5] = corner

                                asyncio.run(position(Orientation))

                                getHoverCoordinates(item["crateNumber"], location[0], location[1], crateOffset(item["crateNumber"], item["suctioncup"])[0], crateOffset(item["crateNumber"], item["suctioncup"])[1])
                                
                                suction = asyncio.run(isSucking())

                                attempt_count += 1

                                if suction == False:
                                    asyncio.run(setSuctionCup(hoverBox, 0))
                                    #suction = asyncio.run(isSucking())

                                    get_newPhoto = True

                                elif suction == True:
                                    break

                        if suction == False:      
                            # Go Home Last Item
                            asyncio.run(position(hoverBox))

                        if suction == True:
                            # Go Home Last Item
                            asyncio.run(position(hoverBox))
                            asyncio.run(setSuctionCup(item["dropdown_coordinate"], 0))
                            asyncio.run(position(hoverBox))

                        # Reset
                        suction = False

                asyncio.run(moveConveyerBelt())
                amount += 1

    return Response(status=204) 
    

if __name__ == '__main__':
    app.run(debug=True)




