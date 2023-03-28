# Get Coordinate Crate Hover
                    getHoverCoordinates(item["crateNumber"], hoverCrate1, hoverCrate2, hoverCrate3, hoverCrate4)

                    # Get Coordinates and closer hover
                    getVegetable = [location[0] , location[1] , 100.0 , 180.0 , 0.0 , -90.0]
                    asyncio.run(position(getVegetable, 0))
                    print(place)
                    if place == "LeftUp":
                        redSuctionTop[0] = location[0]
                        redSuctionTop[1] = location[1]
                        redSuctionTop[2] = location[2]
                        asyncio.run(position(redSuctionTop, 0))
                    elif place == "RightUp":
                        blueSuctionTop[0] = location[0]
                        blueSuctionTop[1] = location[1]
                        blueSuctionTop[2] = location[2]
                        asyncio.run(position(blueSuctionTop, 0))

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