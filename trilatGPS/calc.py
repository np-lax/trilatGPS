#/usr/bin/python

import numpy as np

#global vars
PI = 3.14159

#point setup (will be pulled from other file)
latA = 34.0522
lonA = -118.40806

def CoordToECEF(lat, lon, alt):
	"""Convert lat/long/alt (LLA) coords to Earth-centered-Earth-fixed (ECEF)
        	:param lat: latitude in degrees
	        :param lon: longitude in degrees
	        :param alt: altitude in meters
	        :returns: x,y,z coords in ECEF format
	"""

	#convert degrees to radians
	latInRads = lat * PI/180
	lonInRads = lon * PI/180	
	
	#format radius as a float
	earthRadius = np.float64(6378137.0)

	#calc flattening factor according to WGS84
	flatFactor = np.float64(1.0/298.257223563)
	
	#get cos/sin of latitude
	cosLat = np.cos(latInRads)
	sinLat = np.sin(latInRads)

	#calc geocentric latitude at MSL
	geoLat = (1.0-flatFactor)**2
	
	#questionable math from StackOverflow, probably simplified equations?
	C = 1/np.sqrt(cosLat**2 + geoLat * sinLat**2)
	S = C * geoLat

	#finally get actual ECEF coords
	x = (earthRadius * C + alt)*cosLat * np.cos(lonInRads)
	y = (earthRadius * C + alt)*cosLat * np.sin(lonInRads)
	z = (earthRadius * S + alt)*sinLat

	#return coords
	return(x, y, z)

def MapPoints(x, y, z, strength)
	"""draw circles on coord plane using ECEF coords and signal strength
		@prarm:x



point1_ECEF = CoordToECEF(lat, lon, 0)

P1 = np.array(point1_ECEF)

print(P1)
