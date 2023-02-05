"""
Program description
-----------------------------------------------------------
Program to filter aircraft within satellite coverage for a
specific radius, location and time.

User manual:

python flights_one_sat_filter.py <mandatory_arg> <optional_arg>

	Mandatory arguments:
	*   <flights_file>:     File with aircraft position for
							different time intervals.
	*   -lat <latitude>:    Satellite latitude.
	*   -lon <longitude>:   Satellite longitude.
	*   -time <sat_time>:   Time instant.
	*   -rad <sat_radius>:  Satellite coverage radius.

	Optional arguments:
	*   -h:                 It shows the user manual.
	*   -nm:                It uses nautic miles as unit for the
							coverage radius (default option).
	*   -km:                It uses kilometers as unit for the
							coverage radius.

Example:

python flights_one_sat_filter.py file.csv -lat 15.092736 
	   -lon -23.792856 -time 23:25:00 -rad 1000 -km
python flights_one_sat_filter.py -h

Program authorship
-----------------------------------------------------------
Author:     Daniel Polo Álvarez
Company:    Indra Sistemas S.A.
Version:    01.01
"""

# Package import
from geopy.distance import great_circle
import pandas as pd
import sys
import os

# Global variables

help_manual = ("flights_one_sat_filter.py <mandatory_arg> <optional_arg>\n\n" + 
			   "  Mandatory arguments:\n\n" + 
			   "  *  <flights_file>:     Flight positions file per time instant.\n" +
			   "                         It must be in cvs extension.\n" + 
			   "  *  -lat <latitude>:    Satellite latitude\n" +
			   "  *  -lon <longitude>:   Satellite longitude\n" +
			   "  *  -time <sat_time>:   Time instant\n" + 
			   "  *  -rad <sat_radius>:  Satellite coverage radius\n\n" + 
			   "  Optional arguments:\n\n" + 
			   "  *  -nm:                Use nautic miles for satellite radius\n" + 
			   "                         (default_option)\n" +
			   "  *  -km:                Use kilometers for satellite radius\n\n" + 
			   "Example:\n\n" + 
			   "python flights_one_sat_filter.py file.csv -lat 15.092736 " + 
			   "-lon -23.792856 -time 23:25:00 -rad 1000 -km")

###########################################################

# 0. Initial checks

# 0.1. Command line arguments filtering

show_manual = False
if len(sys.argv) < 10:
	if len(sys.argv) == 2 and sys.argv[1] == "-h":
		print("\nHELP MANUAL\n")
	else:
		print("\nERROR: Incorrect arguments\n")

	print(help_manual)                    
	sys.exit()
else:
	man_arg_list = ["-lat", "-lon", "-time", "-rad"]
	for argument in man_arg_list:
		if argument not in sys.argv:
			print("ERROR: " + str(argument) + " argument not found\n")
			print(help_manual)                    
			sys.exit()       

# 0.2. Input data check 

# 0.2.1. Numerical values
try:
	sat_lat = float(sys.argv[int(sys.argv.index("-lat")) + 1])
	sat_lon = float(sys.argv[int(sys.argv.index("-lon")) + 1])
	sat_radius = int(sys.argv[int(sys.argv.index("-rad")) + 1])
except ValueError:
	print("\nERROR: Incorrect argument values\n")
	print(help_manual)                    
	sys.exit()

# 0.2.2. Time values
sat_time = str(sys.argv[int(sys.argv.index("-time")) + 1])
sat_time_split = sat_time.split(":")

if len(sat_time_split) != 3 or (not (0 <= int(sat_time_split[0]) < 24 and
	0 <= int(sat_time_split[1]) < 60 and 0 <= int(sat_time_split[1]) < 60)):

	print("\nERROR: Incorrect time format\n")
	print(help_manual)                    
	sys.exit()

# 0.2.3. Flights file check 

if os.path.isfile(str(sys.argv[1])):
	flights_file = str(sys.argv[1])
	file_extension = os.path.splitext(flights_file)[1]
	if file_extension != ".csv":
		print("\nERROR: Incorrect file extension")
		print("File with flights information must be in csv format")
		sys.exit()
else:
	print("\nERROR: argument is not a file")
	print("Please, introduce a .csv valid file")
	sys.exit()

# 0.2.4. Metric unit to be used check
radius_in_mn = True
if "-km" in sys.argv:
	radius_in_mn = False

# 1. Process initialization

# 1.1. User information

if radius_in_mn:
	radius_unit = "NM"
else:
	radius_unit = "km"

print("\nUser input values:")
print("  Satellite time:      " + str(sat_time))
print("  Satellite radius:    " + str(sat_radius) + " " + radius_unit)
print("  Satellite latitude:  " + str(sat_lat))
print("  Satellite longitude: " + str(sat_lon))

# 1.2. Flight file reading

print("\nLoading file...")
flights_df = pd.read_csv(flights_file)

# 1.3. Latitude & longitude obtention of flights per time instant

filtered_df = flights_df[flights_df.iloc[:,0] == sat_time]

flights_lat = filtered_df.iloc[:,1].to_list()
flights_lon = filtered_df.iloc[:,2].to_list()

# 1.4. Aircraft count process

count = 0
for i in range(len(flights_lat)):
	flight_accepted = False
	sat_pos = [sat_lat, sat_lon]
	flight_pos = [flights_lat[i], flights_lon[i]]
	if radius_in_mn and great_circle(sat_pos, flight_pos).nm < sat_radius:
		flight_accepted = True
	elif great_circle(sat_pos, flight_pos).km < sat_radius:
		flight_accepted = True

	if flight_accepted:
		count = count + 1

# 2. Outcome printing

print("\nFlights within satellite coverage: " + str(count))