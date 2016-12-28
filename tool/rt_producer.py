import math
import argparse
import requests
from datetime import datetime
from time import sleep

HMTOOL = "http://localhost:8080/rtconsumer"

def pushSineFunctionData(method, station):
	i = 0
	while True:
		if method == "sin":
			y = math.sin( (i/10.0) * math.pi )
		elif method == "cos":
			y = math.cos( (i/10.0) * math.pi )
		else:
			raise Exception("Error. Wrong argument: " + method)

		i = i+1
		now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

		print now, y

		r = requests.post(HMTOOL, data = {'station':station, 'date':now, 'value':y})		
		
		sleep(10) # Wait

def main():
	parser = argparse.ArgumentParser(description='Generate synthetic real-time data for the HMTOOL web application')
	parser.add_argument('--station', dest='station', default="test", 
		help='The name of the station which is generating the data. Default: test')
	parser.add_argument('--method', dest='method', default="sin", 
		help='The method for creating the data (sin, cos)')

	args = parser.parse_args()
	#print args.method

	pushSineFunctionData(args.method, args.station)


if __name__ == "__main__":
    main()