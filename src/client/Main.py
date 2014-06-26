#!/usr/bin/env python
"""Application Main Class

Starts the different modules composing the Application
"""
__author__ = "Artur Balanuta"
__version__ = "1.0.2"
__email__ = "artur.balanuta [at] tecnico.ulisboa.pt"

import time, signal, sys
from time import sleep
from datetime import datetime
from sensors.HTU21D.HTU21D import TempHumid #Temp/Humid
from sensors.OPENWEATHERMAPAPI.OpenWeatherMapAPI import OpenWeatherMapAPI #Exterior Temp/Humid
from sensors.TSL2561.TSL2561 import TSL2561	#Lux
from sensors.ADS1115.ADS1115 import ADS1115	#Current
from detection.WifiLocation import WifiDetector
from detection.BTDetector import BTDetector
#from interaction.lcd.LCDmenu import LCD
#from interaction.pitft.tft_interface import TFT
from interaction.Relay import Relay
from communication.Pub_Sub import MQTTC
from web.web import *
from Scheduler_Manager import ScheduleManager
from Storage_Handler import StorageHandler
from Logic_Engine import Logic_Engine




##Executed if only is the main app
if __name__ == '__main__':	
	

	DEBUG		= True		# Debug Mode
	CLI_INTERFACE	= False		# 
	WEB_INTERFACE	= True		# 
	
	def signal_handler(signal, frame):
		
		print 'You pressed Ctrl+C!'
		for key, value in hub.items():
			
			if "STORAGE HANDLER" is not key:
				if DEBUG:
					print "Stopping", key

				if value.stop:
					value.stop()
				print "\t\t\t\tDone"

		sys.exit(0)
	
	if DEBUG:
		print "-> Starting Client <-"
	
	try:
		
		#Main object used for sharing
		hub = dict()
		signal.signal(signal.SIGINT, signal_handler)
		#print 'Press Ctrl+C to exit'

		#Starts the Storage Handler
		sh = StorageHandler(hub)
		hub["STORAGE HANDLER"] = sh
		if DEBUG:
			print "Storage is ON"

		#Start Temperature/Humidity Sensor
		th = TempHumid(hub)
		th.start()
		hub["TEMPERATURE"] = th
		hub["HUMIDITY"] = th
		if DEBUG:
			print "T/H sensor is ON"

		#Start Extenal Temperature/Humidity Sensor
		ext_th = OpenWeatherMapAPI(hub)
		hub["EXTERNAL TEMPERATURE"] = ext_th
		hub["EXTERNAL HUMIDITY"] = ext_th
		if DEBUG:
			print "External T/H sensor is ON"

		
		#Start Luminosity Sensor
		lux = TSL2561(hub)
		lux.start()
		hub["LUMINOSITY"] = lux
		if DEBUG:
			print "LUX sensor is ON"
		
		#Start Current Sensor
		watt = ADS1115(hub)
		watt.start()
		hub["CURRENT"] = watt
		if DEBUG:
			print "CURRENT sensor is ON"

		#Starts Wifi Detector
		wifi = WifiDetector(hub)
		wifi.start()
		hub["WIFI"] = wifi
		wifi.track_device('40:B0:FA:C7:A1:EB')
		wifi.track_device('CC:C3:EA:0E:23:8F')
		if DEBUG:
			print "WIFI sensor is ON"
		
		#Starts BT Detector
		bt = BTDetector(hub)
		bt.start()
		bt.track_device('40:B0:FA:3D:5F:08')
		hub["BLUETOOTH"] = bt
		if DEBUG:
			print "BT sensor is ON"

		#Starts Relay
		r = Relay(hub)
		hub["RELAY"] = r
		if DEBUG:
			print "Relays are ON"
		
		#Starts TFT
		#tft = TFT(hub)
		#tft.start()
		#hub["TFT"] = tft
		#if DEBUG:
		#	print "TFT screen is ON"

		#Starts LCD
		#lcd = LCD(hub)
		#lcd.start()
		#hub["LCD"] = lcd
		#if DEBUG:
		#	print "LCD screen is ON"

		#Starts The MQTT Listener
		#mqtt = MQTTC(hub)
		#mqtt.start()
		#hub["PUBLISHER"] = mqtt
		#if DEBUG:
		#	print "MQTT Publisher is ON"
		
		#Starts the Scheduler Manager
		sm = ScheduleManager(hub)
		sm.start()
		hub["SCHEDULE MANAGER"] = sm
		if DEBUG:
			print "Scheduler Manager started automation"

		#Starts the Logic Engine
		le = Logic_Engine(hub)
		le.start()
		hub["LOGIC ENGINE"] = le
		if DEBUG:
			print "Logic Engine started automation"
		
		#Starts Web Server
		#Must be last (Blocking)
		if WEB_INTERFACE:

			if DEBUG:
				print "Starting Web interface"

			wh = WebHandler(hub)
			wh.start()
			hub["WEB"] = wh
			
			
	except Exception as inst:
		print "Exception"
		print type(inst)     # the exception instance
		print inst.args      # arguments stored in .args
		raise
	
	print "The End"
