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
  


def main(debug=False):
    # Initialize Camera Intel Realsense
    pl=2
    #pipeline1=initizalize_rs(pl)
    pipeline2=initizalize_rs(pl)
    #create trackbar and images
    #calibrate_camera(pipeline2,pl)
    mtx,dist=read_cal(pl)
    makeframe()
    while True:
        #read info from trackbars
        hsvunder1,hsvunder2,hsvunder3,hsvupper1,hsvupper2,hsvupper3=readtrackbar()
        #Use filters and circle detection to get center coordinate
        image_with_points,pickup_coordinates,gray_image,crop,original_color_frame=getpoint(pipeline1,vegetabledict)
        if pickup_coordinates != []:
            point=make_3D_point(pickup_coordinates[0][0][0]+crop[2], pickup_coordinates[0][0][1]+crop[0],pipeline1,mtx,dist)
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
    #pipeline2.stop()
#main(debug=True)