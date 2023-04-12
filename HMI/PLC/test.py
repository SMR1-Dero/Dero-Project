# ----------------------------------------------------------------------------------------------------
# PLC

ip = '192.168.0.202'

base_pick_hoverA = [55.20 , -566.73 , 489.33 , -179.72 , 0.51 , 6.84]
base_pick_grapA = [55.20 , -566.73 , 289.33 , -179.72 , 0.51 , 6.84]
base_place_hoverA = [438.70 , 229.69 , 489.33 , 178.73 , 1.33 , 128.15]
base_place_dropA = [438.70 , 229.69 , 446.54 , 178.73 , 1.33 , 128.15]

async def status1():
    async with techmanpy.connect_sta(robot_ip=ip) as conn:
        tag_status1 = await conn.get_queue_tag_status(1)

    async with techmanpy.connect_svr(robot_ip=ip) as conn:
        if tag_status1 == True:
            print("Turn Suction On:", tag_status1)
            await conn.set_value("Ctrl_DO1", 1)

async def status2():
    async with techmanpy.connect_sta(robot_ip=ip) as conn:
        tag_status2 = await conn.get_queue_tag_status(2)

    async with techmanpy.connect_svr(robot_ip=ip) as conn:
        if tag_status2 == True:
            print("Turn Suction Off:", tag_status2)
            await conn.set_value("Ctrl_DO1", 0)

async def position(positionArray):
    async with techmanpy.connect_sct(robot_ip=ip) as conn:
        await conn.move_to_point_ptp(positionArray, 1, 1000)

async def handleVar(positionArray, tag): 

    async with techmanpy.connect_sct(robot_ip=ip) as conn:
        await conn.move_to_point_ptp(positionArray, 1, 1000)

        await conn.set_queue_tag(tag_id = tag)
        await conn.wait_for_queue_tag(tag_id = tag)

async def Main():

    await position(positionArray=base_pick_hoverA)
    await handleVar(positionArray=base_pick_grapA, tag=1)
    await status1()
    await position(positionArray=base_pick_hoverA)
    await position(positionArray=base_place_hoverA)
    await handleVar(positionArray=base_place_dropA, tag=2)
    await status2()
    await position(positionArray=base_place_hoverA)

# ----------------------------------------------------------------------------------------------------

{
    "items": [
      {
        "package": "CurryMadras",
        "products": [
          {
            "id": "1_1",
            "product_name": "Curry Madras Saus",
            "product_image": "https://github.com/SMR1-Dero/Dero-Project/blob/main/CurryMadrasSaus.jpg?raw=true",
            "product_package": "Curry Madras",
            "crateNumber": "2",
            "isActive": "on",
            "product_shape": "Not round",
            "product_HSVRange": "",
            "product_minSize": "",
            "product_maxSize": ""
          },
          {
            "id": "1_2",
            "product_name": "Kokosmelk",
            "product_image": "https://github.com/SMR1-Dero/Dero-Project/blob/main/Kokosmelk.jpg?raw=true",
            "product_package": "Curry Madras",
            "crateNumber": "2",
            "isActive": "on",
            "product_shape": "Not round",
            "product_HSVRange": "",
            "product_minSize": "",
            "product_maxSize": ""
          },
          {
            "id": "1_3",
            "product_name": "Peper",
            "product_image": "https://github.com/ItsJarik/CobotHMI/blob/main/Peper.png?raw=true",
            "product_package": "Curry Madras",
            "crateNumber": "2",
            "isActive": "on",
            "product_shape": "Not round",
            "product_HSVRange": "",
            "product_minSize": "",
            "product_maxSize": ""
          },
          {
            "id": "1_4",
            "product_name": "Ui",
            "product_image": "https://github.com/ItsJarik/CobotHMI/blob/main/Uien.jpg?raw=true",
            "product_package": "Curry Madras",
            "crateNumber": "2",
            "isActive": "on",
            "product_shape": "Not round",
            "product_HSVRange": "",
            "product_minSize": "",
            "product_maxSize": ""
          },
          {
            "id": "1_5",
            "product_name": "Limoen",
            "product_image": "https://github.com/ItsJarik/CobotHMI/blob/main/Limoen.png?raw=true",
            "product_package": "Curry Madras",
            "crateNumber": "2",
            "isActive": "on",
            "product_shape": "Not round",
            "product_HSVRange": "",
            "product_minSize": "",
            "product_maxSize": ""
          },
          {
            "id": "1_6",
            "product_name": "Bloemkool",
            "product_image": "https://github.com/SMR1-Dero/Dero-Project/blob/main/bloemkool.png?raw=true",
            "product_package": "Curry Madras",
            "crateNumber": "2",
            "isActive": "on",
            "product_shape": "Not round",
            "product_HSVRange": "",
            "product_minSize": "",
            "product_maxSize": ""
          },
          {
            "id": "1_7",
            "product_name": "Tomaat",
            "product_image": "https://github.com/ItsJarik/CobotHMI/blob/main/Tomaten.png?raw=true",
            "product_package": "Curry Madras",
            "crateNumber": "2",
            "isActive": "on",
            "product_shape": "Not round",
            "product_HSVRange": "",
            "product_minSize": "",
            "product_maxSize": ""
          },
          {
            "id": "1_8",
            "product_name": "Tomaat",
            "product_image": "https://github.com/ItsJarik/CobotHMI/blob/main/Tomaten.png?raw=true",
            "product_package": "Curry Madras",
            "crateNumber": "2",
            "isActive": "on",
            "product_shape": "Not round",
            "product_HSVRange": "",
            "product_minSize": "",
            "product_maxSize": ""
          },
          {
            "id": "1_9",
            "product_name": "Paprika",
            "product_image": "https://github.com/ItsJarik/CobotHMI/blob/main/Paprika.png?raw=true",
            "product_package": "Curry Madras",
            "crateNumber": "2",
            "isActive": "on",
            "product_shape": "Not round",
            "product_HSVRange": "",
            "product_minSize": "",
            "product_maxSize": ""
          }
        ]
      },
      {
        "package": "TomatenSoep",
        "products": [
          {
            "id": "89379832",
            "product_name": "Tomaat",
            "product_image": "https://github.com/ItsJarik/CobotHMI/blob/main/Tomaten.png?raw=true",
            "product_package": "Tomaten Soep",
            "crateNumber": "2",
            "isActive": "on",
            "product_shape": "Round",
            "product_HSVRange": "",
            "product_minSize": "",
            "product_maxSize": ""
          }
        ]
      }
    ]
  }
  

# Getting Connected
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
                    await conn.get_value('Robot_Model')
                    status['SVR'] = 'Connected'
            except TechmanException: pass

            # Check SCT connection (only active when inside listen node)
            try:
                async with techmanpy.connect_sct(robot_ip=ip, conn_timeout=1) as conn:
                    status['SCT'] = 'Online'
                    await conn.resume_project()
                    status['SCT'] = 'Connected'
            except TechmanException: pass

            # Check STA connection (only active when running project)
            try:
                async with techmanpy.connect_sta(robot_ip=ip, conn_timeout=1) as conn:
                    status['STA'] = 'Online'
                    await conn.is_listen_node_active()
                    status['STA'] = 'Connected'
            except TechmanException: pass

            # Print status
            def colored(status):
                if status == 'Online': return f'{status}'
                if status == 'Connected': return f'{status}'
                if status == 'Offline': return f'{status}'
            #print(f'SVR: {colored(status["SVR"])}, SCT: {colored(status["SCT"])}, STA: {colored(status["STA"])}')

            SVR_status = colored(status["SVR"])
            SCT_status = colored(status["SCT"])
            STA_status = colored(status["STA"])
            break
        return SVR_status, SCT_status, STA_status



                        indexZ = 400.0
                        print(getVegetable[2])
                        while True:
                            if indexZ <= getVegetable[2]:
                                print("test")
                                break
                            if indexZ != getVegetable[2]:
                                print("Lower")
                                asyncio.run(position([getVegetable[0], getVegetable[1], indexZ, rx, 31.19, rz_crateSide], 1))
                                indexZ -= 50.0