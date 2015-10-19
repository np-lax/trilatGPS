#!/usr/bin/env python
import re
import sys

class AccessPoint:
	"""
	hold access point data and gps coords
	"""

	def __init__(self, bssid):
		#capture ID and starting info
		self.bssid = bssid
		
		#create arrays to hold lat/long/sig strength
		self.lat_a = []
		self.lon_a = []
		self.strength = []

		#arrays to hold ECEF coords
		self.xCoords = []
		self.yCoords = []
		self.zCoords = []

	def get_bssid(self):
		"""return bssid of access point"""
		if self.bssid:
			return self.bssid
		else:
			return -1

	def update(self, lat_u, lon_u, dbm_u):
		"""update access point's lat/long/signal strength
			:param lat_u: latitude update
			:param lon_u: longitude update
			:param dbm_u: signal strength update
		"""

		#check for empty arrays, if yes, commit initial data
		if (not self.lat_a and not self.lon_a):
			self.lat_a.append(lat_u)
			self.lon_a.append(lon_u)
			self.strength.append(dbm_u)
		#ensure arrays are the same length
		elif (len(self.lat_a) == len(self.lon_a) and len(self.lat_a) == len(self.strength) and len(self.lon_a) == len(self.strength)):
			#run through list, ensure lat/long combos are all unique
			for index in range(0, len(self.lon_a)):
				if (lat_u != self.lat_a[index] and lon_u != self.lon_a[index]):
					self.lat_a.append(lat_u)
					self.lon_a.append(lon_u)
					self.strength.append(dbm_u)


	def get_current_lat(self):
		""":returns: last recorded latitude of access point"""
		if self.lat_a[-1]:
			return self.lat_a[-1]
		else:
			return -1

	def get_current_lon(self):
		""":returns: last recorded longitude of access point"""
		if self.lon_a[-1]:
			return self.lon_a[-1]
		else:
			return -1

	def get_current_strength(self):
		""":returns: last recorded signal strength of access point"""
		if self.strength[-1]:
			return self.strength[-1]
		else:
			return -1

	def get_lats(self):
		if self.lat_a[-1]:
			return self.lat_a
		else:
			return -1
	def get_lons(self):
		if self.lon_a[-1]:
			return self.lon_a
		else:
			return -1
	def get_strs(self):
		if self.strength[-1]:
			return self.strength
		else:
			return -1



def ap_exists(bssid, ap_list):
	"""check if ap object is in master list of AccessPoints
		:param bssid: access point BSSID from .gpsxml FILE
		:param ap_list: master list of APs to check against
		:returns: boolean value - False if AP is not in list/True if Ap is in list
	"""
	size = len(ap_list)

	if size > 0:
		for x in range(size):
			if bssid == ap_list[x].get_bssid():
				return True
	else:
 		return False

	return False

#seperate from obj.update() because prgm only has bssid when updating, not the object. So rather than doing a lookup and then updating, just combined them into single method
def update_ap(bssid, ap_list, lat, lon, sig):
	"""pull ap from master list and update it with newest coords/strength
	        :param bssid: access point BSSID from .gpsxml FILE
		:param lat: new latitude
		:param lon: new longitude
		:param sig: new signal strength
	        :param ap_list: master list of APs to check against
                :returns: null
	"""
	size = len(ap_list)

	if size > 0:
		for x in range(size):
			if bssid == ap_list[x].get_bssid():
				ap_list[x].update(lat, lon, sig) 

def gather_ap_info(line):
	"""pull data from gpsxml file and add to new AccessPoint object
		:param ap: AccessPoint object
		:param line: next line in gpsxml file to pull data from
		:returns: AccessPoint object with initial location/signal data
	"""
	lat = re.search(lat_re,line)
	lat = lat.group(0)[5:-1]

	lon = re.search(lon_re, line)
	lon= lon.group(0)[5:-1]

	sig = re.search(sig_re, line)
	sig = sig.group(0)[12:-1]

	return (lat, lon, sig)


#MAIN PROGRAM#

#build out regular expressions for each piece of data in the gpsxml file
bssid_re = '(bssid="([0-9A-F]{2}[:]){5}([0-9A-F]{2})")'
lat_re = '(lat="([0-9]{2})[.]([0-9]{6})")'
lon_re = '(lon="[-?]([0-9]{2}[0-9]?)[.]([0-9]{6})")'
sig_re = '(signal_dbm="[-]([0-9]{2})")'



#open gpsxml file (how to do this dynamically?) - could just run through periodically

if len(sys.argv) != 2:
	print("Usage: python trilatGPS.py [filename]")
else:
	fname = sys.argv[1]


try:
	f = open(fname, 'r')
except IOError:
	print("DEBUG: ERROR - COULD NOT READ FILE")
	sys.exit()

#initalize global list of access point objects
ap_list = []

for line in f:
	bssid = re.search(bssid_re, line)
	if bssid:
		xml_bssid = bssid.group(0)[7:-1]
		#filter out probe packets
		if not xml_bssid == '00:00:00:00:00:00':
			#pull coords & sig strength from gpsxml file
			newAPInfo = gather_ap_info(line)
			xml_lat = newAPInfo[0]
			xml_lon = newAPInfo[1]
			xml_sig = newAPInfo[2]
			
			#check if the access point is already in the master AP list	
			if not ap_exists(xml_bssid, ap_list):
				#create new access point
				newestAP = AccessPoint(xml_bssid)
				#commit inital data to new AP
				newestAP.update(xml_lat, xml_lon, xml_sig)
				#add to global AccessPoint object list
				ap_list.append(newestAP)
			else:			
				update_ap(xml_bssid, ap_list, xml_lat, xml_lon, xml_sig)

print("AP Scan complete - " + str(len(ap_list)) + " unique APs added to list")

#initalize list of APs with at least 3 data points each
pruned_ap_list = []

#check for at least 3 data points per AP, if so, add to prunded list
for x in range(len(ap_list)):
	if (len(ap_list[x].get_lats()) >= 3):
		pruned_ap_list.append(ap_list[x])
		#print("GOOD AP: " + str(ap_list[x].get_bssid()) + "" + str(ap_list[x].get_lats()))i

print("Pruning complete - " + str(len(pruned_ap_list)) + " APs suitable for analysis (3 unique data points)")
#TO DO
#
