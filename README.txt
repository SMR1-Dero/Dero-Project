The project is structured into four files(you can find this files in the HMI map and Static/Json map):

Vegetables_V4:
This file contains various functions that can be used to filter data and calculate real-world coordinates.
Examples of functions in this file are filters and real world coordinates calculations.
Filters are functions used to manipulate data, such as removing outliers or selecting specific values.
Real world coordinates calculations are functions used to convert measurements taken from the sensors into coordinates that can be used in a mapping system.

Main_startFile:
This file can be used to test the functions from Vegetables_V4.
Testing functions is a common practice in software development to ensure that each function works as expected before integrating them into the main application.

database:
This file acts as a database for the vegetables and fresh packages.
It contains data structures and functions that allow the app to store and retrieve information about the vegetables and their freshness.

app:
This file contains the main application and HMI (Human Machine Interface) code.
The main application is the code responsible for controlling the system and making decisions based on the data collected by the sensors.
The HMI code is the interface that allows the user to interact with the system.
The app file imports all the functions from Vegetables_V4 and the database file.
It uses the functions from Vegetables_V4 to filter the data and calculate real-world coordinates.
It also uses the functions from the database file to store and retrieve information about the vegetables and their freshness.
