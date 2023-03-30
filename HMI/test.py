if place == "LeftUp":
                        redSuctionTop[0] = location[0]
                        redSuctionTop[1] = location[1]
                        redSuctionTop[2] = location[2]
                        asyncio.run(position(redSuctionTop, 0))
                    elif place == "LeftDown":
                        redSuctionDown[0] = location[0]
                        redSuctionDown[1] = location[1]
                        redSuctionDown[2] = location[2]
                        asyncio.run(position(redSuctionDown, 0))
                    elif place == "RightUp":
                        blueSuctionTop[0] = location[0]
                        blueSuctionTop[1] = location[1]
                        blueSuctionTop[2] = location[2]
                        asyncio.run(position(blueSuctionTop, 0))
                    elif place == "RightDown":
                        blueSuctionDown[0] = location[0]
                        blueSuctionDown[1] = location[1]
                        blueSuctionDown[2] = location[2]
                        asyncio.run(position(blueSuctionDown, 0))

                    # Turn On Suction
                    asyncio.run(setSuctionCup1(1))

                    # Get Coordinate Crate Hover
                    getHoverCoordinates(item["crateNumber"], hoverCrate1, hoverCrate2, hoverCrate3, hoverCrate4)

                    # Rest Position to make photo



                    # Get Coordinate Box Hover
                    asyncio.run(position(hoverBox, 1))

                    # Get Coordinate Box Place
  
                    # Turn Off Suction
                    asyncio.run(setSuctionCup1(0))
                    # Get Coordinate Box Hover
                    asyncio.run(position(hoverBox, 0))



{
          "coordinates": [
            -429.97391462192377,
            -346.30422575318306,
            10.677678636451105
          ],
          "crateNumber": "2",
          "id": "1_4",
          "indexCoordinates": 0,
          "isActive": "true",
          "isPicked": false,
          "product_HSVRange": [
            10,
            81,
            20,
            35,
            255,
            255
          ],
          "product_image": "https://github.com/ItsJarik/CobotHMI/blob/main/Uien.jpg?raw=true",
          "product_location": "LeftUp",
          "product_maxSize": "",
          "product_minSize": "",
          "product_name": "Ui wit",
          "product_package": "Curry Madras",
          "product_shape": "Round",
          "suctioncup": "RoodBlauw"
        },

,
        {
          "coordinates": [
            -436.07090266212344,
            -341.7911364625357,
            9.746516170409109
          ],
          "crateNumber": "2",
          "id": "1_5",
          "indexCoordinates": 1,
          "isActive": "true",
          "isPicked": false,
          "product_HSVRange": [
            10,
            81,
            20,
            35,
            255,
            255
          ],
          "product_image": "https://github.com/ItsJarik/CobotHMI/blob/main/Uien.jpg?raw=true",
          "product_location": "LeftUp",
          "product_maxSize": "",
          "product_minSize": "",
          "product_name": "Ui wit",
          "product_package": "Curry Madras",
          "product_shape": "Round",
          "suctioncup": "RoodBlauw"
        }


@app.route('/Start', methods=['POST'])
def Start():

    # Variables
    teller = 0 # Counts when it needs to return home
    place = "" # Camera Gives String that describes the place of the vegetable
    topPlane = 400.0
    rx = 180.0
    ry = 0.0
    rz_crateSide = -90.0
    rz_boxSide = 90.0

    hoverCrate1 = [-536.42 , -799.43 , topPlane , rx , ry , rz_crateSide]
    hoverCrate2 = [-633.77 , -356.43 , topPlane , rx , ry , rz_crateSide]
    hoverCrate3 = [-647.11 , 139.67 , topPlane , rx , ry , rz_crateSide]
    hoverCrate4 = [-660.57 , 593.36 , topPlane , rx , ry , rz_crateSide]

    hoverBox = [511.01 , -212.48 , 600.0 , rx , ry , rz_boxSide]

    # Suction
    # ry (-27.99 or 0.0), because of the other suction cup
    # rz (90.0 or -90.0), because of the lamp of the camera
    redSuction = [0.0 , 0.0 , 0.0 , 180.0 , -31.19 , -90.0]
    blueSuction = [0.0 , 0.0 , 0.0 , 180.0 , 31.19 , -90.0]

    # Initializing Camera
    pipeline1,pipeline2=initizalize_rs()
    camera=2

    # Open JSON
    with open('HMI\static\json\database_test.json', 'r') as f:
        data = json.load(f)

    # Get Package Name
    package = request.form['package']

    for product in data["items"]:
        if product["package"] == package:
            for item in product["products"]:
                if item["isActive"] == "true":

                    # Make Picture and Calculate Coordinates
                    got_frame = 0
                    while True:
                        #Use filters and circle detection to get center coordinate
                        image_with_points,pickup_coordinates,gray_image,crop,original_color_frame,camera,pipeline,place=getpoint(pipeline1,pipeline2,item)
                        
                        if pickup_coordinates != []:
                            location=make_3D_point(pickup_coordinates[item['indexCoordinates']][0][0]+crop[2], pickup_coordinates[item['indexCoordinates']][0][1]+crop[0],pipeline,camera)
                            original_with_points=draw_original(original_color_frame, pickup_coordinates,crop[0],crop[2])
                            print(location)
                            item['coordinates'] = location # Coordinates
                            item['product_location'] = place # Placement in crate
                            print(item["indexCoordinates"])
                            if len(pickup_coordinates) >= 2:
                                got_frame = 1
                        
                        if got_frame == 1:
                            break

    # Save the updated JSON data back to the file
    with open('HMI/static/json/database_test.json', 'w') as f:
        json.dump(data, f, indent=2)

    for product in data["items"]:
        if product["package"] == package:
            for item in product["products"]:
                if item["isActive"] == "true":
                    # Get Coordinate Crate Hover
                    getHoverCoordinates(item["crateNumber"], hoverCrate1, hoverCrate2, hoverCrate3, hoverCrate4)

                    print(item["product_location"])

                    if ((item["product_location"] == "LeftUp") or (item["product_location"] == "LeftDown")):
                        redSuction[0] = item["coordinates"][0]
                        redSuction[1] = item["coordinates"][1]
                        redSuction[2] = 200.0
                        asyncio.run(position(redSuction, 0))
                        
                    elif ((item["product_location"] == "RightUp") or (item["product_location"] == "RightDown")):
                        blueSuction[0] = item["coordinates"][0]
                        blueSuction[1] = item["coordinates"][1]
                        blueSuction[2] = 200.0
                        asyncio.run(position(blueSuction, 0))
                        

                    # Get Coordinate Crate Hover
                    getHoverCoordinates(item["crateNumber"], hoverCrate1, hoverCrate2, hoverCrate3, hoverCrate4)
                    teller += 1
                    if teller == 2:
                        # Get Coordinate Box Hover
                        asyncio.run(position(hoverBox, 0))
                        teller = 0




    #pipeline1.stop()    
    #pipeline2.stop()

    return Response(status=204)


@app.route('/getLiveInformation')
def getLiveInformation():
    async def test_connection(ip):
        while True:
            status = {'SCT': 'Offline', 'SVR': 'Offline', 'STA': 'Offline'}

            SCT_status = ""
            SVR_status = ""
            STA_status = ""

            # Check SVR connection (should be always active)
            try:
                async with techmanpy.connect_svr(robot_ip=ip, conn_timeout=1) as conn:
                    status['SVR'] = 'Online'
                    #await conn.get_value('Robot_Model')
                    status['SVR'] = 'Connected'
            except TechmanException: pass

            # Check SCT connection (only active when inside listen node)
            try:
                async with techmanpy.connect_sct(robot_ip=ip, conn_timeout=1) as conn:
                    status['SCT'] = 'Online'
                    #await conn.resume_project()
                    status['SCT'] = 'Connected'
            except TechmanException: pass

            # Check STA connection (only active when running project)
            try:
                async with techmanpy.connect_sta(robot_ip=ip, conn_timeout=1) as conn:
                    status['STA'] = 'Online'
                    #await conn.is_listen_node_active()
                    status['STA'] = 'Connected'
            except TechmanException: pass

            # Print status
            def colored(status):
                if status == 'Online': return f'{status}'
                if status == 'Connected': return f'{status}'
                if status == 'Offline': return f'{status}'

            SVR_status = colored(status["SVR"])
            SCT_status = colored(status["SCT"])
            STA_status = colored(status["STA"])
            break
        return SVR_status, SCT_status, STA_status
        
    async def getCoordinates():
        # Connect to the robot server
        async with techmanpy.connect_svr(robot_ip=ip) as conn:
            # Retrieve live information about the robot
            coordinates = []#await conn.get_value("Coord_Robot_Flange")
            speed = 5#await conn.get_value("Project_Speed")
            status_suctionCup1 = False#bool(await conn.get_value("Ctrl_DO1"))
            status_suctionCup2 = False#bool(await conn.get_value("Ctrl_DO2"))
        return coordinates, speed, status_suctionCup1, status_suctionCup2
    
    # Check the connection status of the robot before retrieving live information
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    #SVR_status, SCT_status, STA_status = loop.run_until_complete(test_connection(ip))
    
    # Retrieve live information about the robot
    #coordinates, speed, status_suctionCup1, status_suctionCup2 = loop.run_until_complete(getCoordinates())

    # Return the live information as a JSON object
    return jsonify({
        'coordinates': [],
        #'speed': speed,
        #'status_suctionCup1': str(status_suctionCup1),
        #'status_suctionCup2': str(status_suctionCup2),
        #'SVR_status': SVR_status,
        #'SCT_status': SCT_status,
        #'STA_status': STA_status,
    })


# I think we are going to throw this out the window
@app.route('/Start', methods=['POST'])
def Start():

    # Variables
    teller = 0 # Counts when it needs to return home
    place = "" # Camera Gives String that describes the place of the vegetable
    zuigerRood = False
    zuigerBlauw = False
    topPlane = 400.0
    rx = 180.0
    ry = 0.0
    rz_crateSide = -90.0
    rz_boxSide = 90.0

    redSuctionQueue = 1
    blueSuctionQueue = 4

    calibrationCamera2 = [-705.0 , 192.0 , 300.0 , 180.0 , 0.0 , -90.0]

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
    redSuctionLeft = [0.0 , 0.0 , 0.0 , 180.0 , 31.19 ,  -90.0]
    redSuctionRight = [0.0 , 0.0 , 0.0 , 180.0 , -31.19 , -90.0]
    blueSuctionLeft = [0.0 , 0.0 , 0.0 , 180.0 , -31.19 , -90.0]
    blueSuctionRight = [0.0 , 0.0 , 0.0 , 180.0 , 31.19 , -90.0]

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
            for item in product["products"]:
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

                        if ((place == "LeftUp") or (place == "LeftDown")):
                            # Red can pickup Left
                            if (item["suctioncup"] == "Rood"):
                                # Pickup with Red
                                if (zuigerRood == False):
                                    # Possible to pickup with Red

                                    print("Pickup")

                            elif (item["suctioncup"] == "Blauw"):
                                # Pickup with Blue
                                if (zuigerBlauw == False):
                                    # Possible to pickup with Blue

                                    print("Pickup")

                            elif (item["suctioncup"] == "RoodBlauw"):
                                # Pickup with Red or Blue
                                if (zuigerRood == False and zuigerBlauw == False):
                                    # Possible to pickup with Red or Blue

                                    redSuctionLeft[0] = location[0]
                                    redSuctionLeft[1] = location[1]
                                    redSuctionLeft[2] = 300.0

                                    # Pickup Red as preference
                                    asyncio.run(setSuctionCup1Try(redSuctionLeft, 1))

                                    asyncio.run(positionWithoutTag(hoverIdle))
                                    zuigerRood = True
                                elif (zuigerRood == True and zuigerBlauw == False):
                                    # Pickup with Blue
                                    print("Pickup blue")
                                    
                                    blueSuctionLeft[0] = location[0]
                                    blueSuctionLeft[1] = location[1]
                                    blueSuctionLeft[2] = 300.0

                                    # Pickup with Blue is necessary
                                    asyncio.run(setSuctionCup2Try(blueSuctionLeft, 1))
                                    asyncio.run(positionWithoutTag(hoverIdle))
                                    zuigerBlauw = True

                        if ((place == "RightUp") or (place == "RightDown")):
                            # Red can pickup Left
                            if (item["suctioncup"] == "Rood"):
                                # Pickup with Red
                                if (zuigerRood == False):
                                    # Possible to pickup with Red

                                    print("Pickup")

                            elif (item["suctioncup"] == "Blauw"):
                                # Pickup with Blue
                                if (zuigerBlauw == False):
                                    # Possible to pickup with Blue

                                    print("Pickup")
                                    
                            elif (item["suctioncup"] == "RoodBlauw"):
                                # Pickup with Red or Blue
                                if (zuigerRood == False and zuigerBlauw == False):
                                    # Possible to pickup with Red or Blue

                                    print("Pickup")
                                elif (zuigerRood == True and zuigerBlauw == True):
                                    # Go Home

                                    print("Pickup")
                                elif (zuigerRood == True and zuigerBlauw == False):
                                    # Pickup with Blue

                                    print("Pickup")
                                elif (zuigerRood == False and zuigerBlauw == True):
                                    # Pickup with Red

                                    print("Pickup")

                    # ---------------------------------------------------------------

                    if (zuigerRood == True and zuigerBlauw == True):
                        # Go Home 
                        asyncio.run(setSuctionCup1Try(hoverBox, 0))
                        asyncio.run(setSuctionCup2Try(hoverBox, 0))

                        # Reset
                        zuigerRood = False
                        zuigerBlauw = False

    # Go Home Last Item
    asyncio.run(setSuctionCup1Try(hoverBox, 0))
    asyncio.run(setSuctionCup2Try(hoverBox, 0))

    # Reset
    zuigerRood = False
    zuigerBlauw = False

    return Response(status=204)   


# We are going to use this

@app.route('/Start', methods=['POST'])
def Start():

    # Variables
    teller = 0 # Counts when it needs to return home
    place = "" # Camera Gives String that describes the place of the vegetable
    zuigerRood = False
    zuigerBlauw = False
    topPlane = 400.0
    rx = 180.0
    ry = 0.0
    rz_crateSide = -90.0
    rz_boxSide = 90.0

    redSuctionQueue = 1
    blueSuctionQueue = 4

    calibrationCamera2 = [-705.0 , 192.0 , 300.0 , 180.0 , 0.0 , -90.0]

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
    redSuctionLeft = [0.0 , 0.0 , 0.0 , 180.0 , 31.19 ,  -90.0]
    redSuctionRight = [0.0 , 0.0 , 0.0 , 180.0 , -31.19 , -90.0]
    blueSuctionLeft = [0.0 , 0.0 , 0.0 , 180.0 , -31.19 , -90.0]
    blueSuctionRight = [0.0 , 0.0 , 0.0 , 180.0 , 31.19 , -90.0]

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
            for item in product["products"]:
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

                        getVegetable = [0.0 , 0.0 , 0.0 , 180 , 0.0 , -90.0]
                        getVegetable[0] = location[0]
                        getVegetable[1] = location[1]
                        getVegetable[2] = 300.0

                        # Pickup Red as preference
                        asyncio.run(setSuctionCup1Try(getVegetable, 1))

                        asyncio.run(setSuctionCup1Try(hoverBox, 0))

    return Response(status=204)