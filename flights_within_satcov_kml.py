"""
Program description
-----------------------------------------------------------
Program to represent in KML (Google Earth) the aircraft that
land within a satellite footprint for a specific radius, 
location and time.

User manual:

python flights_within_satcov_kml.py <mandatory_arg> <optional_arg>

	Mandatory arguments:
	*   <geojson_file>:     File with FIR border information.
	*   <flights_file>:     File with aircraft position for
							different time intervals.
	*   <output_name>:      Output file name.
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

Example	:

python flights_within_satcov_kml.py file.csv -lat 15.092736
	   -lon -23.792856 -time 23:25:00 -rad 1000 -km

python flights_within_satcov_kml.py -h

Program authorship
-----------------------------------------------------------
Author:     Daniel Polo Álvarez (dpolo@indra.es)
Company:    Indra Sistemas S.A.
Version:    01.01
"""

# Package import
from geopy.distance import great_circle
import pandas as pd
import pygeoj
import sys
import os

# Global variables

help_manual = ("flights_within_satcov_kml.py <mandatory_arg> <optional_arg>\n\n" + 
			   "  Mandatory arguments:\n\n" + 
			   "  *  <geojson_file>:     GeoJSON file with FIR information\n" +
			   "  *  <flights_file>:     Flight positions file per time instant.\n" + 
			   "                         It must be in cvs extension.\n" + 
			   "  *  <output_name>:      Output file name" +
			   "  *  -lat <latitude>:    Satellite latitude\n" +
			   "  *  -lon <longitude>:   Satellite longitude\n" +
			   "  *  -time <sat_time>:   Time instant to filter by\n" + 
			   "  *  -rad <sat_radius>:  Satellite radius coverage\n\n" + 
			   "  Optional arguments:\n\n" + 
			   "  *  -nm:                Use nautic miles for satellite radius\n" + 
			   "                         (default_option)\n" +
			   "  *  -km:                Use kilometers for satellite radius\n\n" + 
			   "Example:\n\n" + 
			   "python flights_within_satcov_kml.py firs.geojson fired.csv output.kml " + 
			   "-lat 15.092736 -lon -23.792856 -time 23:25:00 -rad 1000 -km")

###########################################################

# Program secondary functions

def getFIRs(geojson):
	"""
	This function obtains the information gathered in a 
	GeoJSON file with a Google Earth format and returns 
	data interpretable by Python and this program
	
	Output parameters:
	- polygons: it contains information of the points 
				that defined the outer borders of FIRs.
	- names:    it contains information about FIRs such
				as name, area extension, etc.
	"""

	polygons = []
	names = []
	testfile = pygeoj.load(geojson)
	for feature in testfile:
		polygons.append(feature.geometry.coordinates[0])
		names.append(feature.properties)

	return polygons, names

def writeKML(kml_file, kml_text):
	"""
	It writes the text in a buffer into the final
	document and cleans the buffer.
	"""

	kml_file.write(kml_text)
	kml_text = ""
	
	return kml_file, kml_text

###########################################################

# 0. Initial checks

# 0.1. Command line arguments filtering 

show_manual = False
if len(sys.argv) < 12:
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

# 0.2.3. GeoJSON file check
if os.path.isfile(str(sys.argv[1])):
	flights_file = str(sys.argv[1])
	file_extension = os.path.splitext(flights_file)[1]
	if file_extension != ".geojson":
		print("\nERROR: Incorrect file extension")
		print("FIR information file must be in geojson format")
		sys.exit()
else:
	print("\nERROR: argument is not a file")
	print("Please, introduce a .geojson valid file")
	sys.exit()

# 0.2.4. Flights file check
if os.path.isfile(str(sys.argv[2])):
	flights_file = str(sys.argv[2])
	file_extension = os.path.splitext(flights_file)[1]
	if file_extension != ".csv":
		print("\nERROR: Incorrect file extension")
		print("File with flights information must be in csv format")
		sys.exit()
else:
	print("\nERROR: argument is not a file")
	print("Please, introduce a .csv valid file")
	sys.exit()

# 0.2.5. Output name check
if str(sys.argv[3]).startswith("-"):
	print("\nERROR: output name is not valid")
	print("Please, introduce a valid name")

# 0.2.6. Metric unit to be used check
radius_in_mn = True
if "-km" in sys.argv:
	radius_in_mn = False

# 1. File and variables initialization for process

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

# 1.2. GeoJSON file reading
print("\nLoading geojson file...")
polygons, names = getFIRs(sys.argv[1])

# 1.3. Flights file reading
print("\nLoading csv file...")
flights_df = pd.read_csv(flights_file)

# 2. KML file creation process

print("\nStarting KML file creation...")

# 2.1. KML file opening
kml_file = open("./" + str(sys.argv[3]), "w")

# 2.2. KML initial values introduction
kml_text = '<?xml version="1.0" encoding="UTF-8"?>\n'
kml_text = kml_text + '<kml xmlns="http://www.opengis.net/kml/2.2" '
kml_text = kml_text + 'xmlns:gx="http://www.google.com/kml/ext/2.2" '
kml_text = kml_text + 'xmlns:kml="http://www.opengis.net/kml/2.2" '
kml_text = kml_text + 'xmlns:atom="http://www.w3.org/2005/Atom">\n'
kml_text = kml_text + "<Document>\n"

kml_text = kml_text + "\t<name>" + str(sys.argv[3]) + "</name>\n"
kml_text = kml_text + "\t<open>1</open>\n"

kml_file, kml_text = writeKML(kml_file, kml_text)

# 2.3. Styles

# 2.3.1. Style for FIR
kml_text = kml_text + '\t<Style id="FIR">\n'

kml_text = kml_text + '\t\t<LineStyle>\n'
kml_text = kml_text + '\t\t\t<color>FFFF0000</color>\n'
kml_text = kml_text + '\t\t\t<width>1</width>\n'
kml_text = kml_text + '\t\t</LineStyle>\n'

kml_text = kml_text + '\t\t<PolyStyle>\n'
kml_text = kml_text + '\t\t\t<color>00FFFFFF</color>\n'
kml_text = kml_text + '\t\t</PolyStyle>\n'

kml_text = kml_text + '\t</Style>\n'

kml_file, kml_text = writeKML(kml_file, kml_text)

# 2.3.2. Style for icons
kml_text = kml_text + '\t<Style id="Flight">\n'

kml_text = kml_text + '\t\t<IconStyle>\n'
kml_text = kml_text + '\t\t\t<color>FFFFD600</color>\n'
kml_text = kml_text + '\t\t\t<scale>1.3</scale>\n'
kml_text = kml_text + '\t\t\t<Icon>\n'
kml_text = kml_text + '\t\t\t\t<href>http://maps.google.com/mapfiles/kml/shapes/shaded_dot.png</href>\n'
kml_text = kml_text + '\t\t\t</Icon>\n'
kml_text = kml_text + '\t\t</IconStyle>\n'

kml_text = kml_text + '\t</Style>\n'

kml_file, kml_text = writeKML(kml_file, kml_text)

# 2.4. FIR data
for n_fir in range(len(polygons)):

	# 2.4.1. Introduction
	kml_text = kml_text + '\t<Placemark>\n'
	kml_text = kml_text + '\t\t<name>' + names[n_fir]["FIRname"] + '</name>\n'
	
	# 2.4.2. Style
	kml_text = kml_text + '\t\t<styleUrl>#FIR</styleUrl>\n'
	
	# 2.4.3. Extended data
	kml_text = kml_text + '\t\t<ExtendedData>\n'
	for data in names[n_fir]:
		kml_text = kml_text + '\t\t\t<Data name="' + str(data) + '">\n'
		kml_text = kml_text + '\t\t\t\t<value>' + str(names[n_fir][data]) + '</value>\n'
		kml_text = kml_text + '\t\t\t</Data>\n'
		
	kml_text = kml_text + '\t\t</ExtendedData>\n'
	
	# 2.4.4. Border points coordinates
	kml_text = kml_text + '\t\t<Polygon>\n'
	kml_text = kml_text + '\t\t\t<outerBoundaryIs>\n'
	kml_text = kml_text + '\t\t\t\t<LinearRing>\n'
	kml_text = kml_text + '\t\t\t\t\t<coordinates>\n'
	kml_text = kml_text + '\t\t\t\t\t\t'
	
	for polygon in polygons[n_fir]:
		kml_text = kml_text + str(polygon[0]) + "," + str(polygon[1]) + ",0 "
	
	kml_text = kml_text + '\n\t\t\t\t\t</coordinates>\n'
	kml_text = kml_text + '\t\t\t\t</LinearRing>\n'
	kml_text = kml_text + '\t\t\t</outerBoundaryIs>\n'
	kml_text = kml_text + '\t\t</Polygon>\n'
	
	# 2.4.5. FIR closing and file writing
	kml_text = kml_text + '\t</Placemark>\n'
	
	kml_file, kml_text = writeKML(kml_file, kml_text)
	
# 2.5. Flight data

# 2.5.1. Latitude & longitude obtention of flights per time instant

filtered_df = flights_df[flights_df.iloc[:,0] == sat_time]
flights_lat = filtered_df.iloc[:,1].to_list()
flights_lon = filtered_df.iloc[:,2].to_list()

# 2.5.2. Flight within satellite coverage check.
#		 If affirmative, it is included in KML file.

for index in range(len(flights_lat)):
	flight_accepted = False
	sat_pos = [sat_lat, sat_lon]
	flight_pos = [flights_lat[index], flights_lon[index]]
	if radius_in_mn and great_circle(sat_pos, flight_pos).nm < sat_radius:
		flight_accepted = True
	elif great_circle(sat_pos, flight_pos).km < sat_radius:
		flight_accepted = True

	if flight_accepted:
		kml_text = kml_text + '\t<Placemark>\n'
		kml_text = kml_text + '\t\t<styleUrl>#Flight</styleUrl>\n'
		kml_text = kml_text + '\t\t<Point>\n'
		kml_text = (kml_text + '\t\t\t<coordinates>' + 
					str(flight_pos[1]) + ',' + 
					str(flight_pos[0]) + ',0</coordinates>s\n')
		kml_text = kml_text + '\t\t</Point>\n'
		kml_text = kml_text + '\t</Placemark>\n'
		
		kml_file, kml_text = writeKML(kml_file, kml_text)

# 2.6. KML file closing
kml_text = kml_text + "</Document>\n"
kml_text = kml_text + "</kml>\n"
kml_file, kml_text = writeKML(kml_file, kml_text)
kml_file.close()
