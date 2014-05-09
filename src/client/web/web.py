#!/usr/bin/env python
"""Web server based on Flask"""

__author__ = "Artur Balanuta"
__version__ = "1.0.2"
__email__ = "artur.balanuta [at] tecnico.ulisboa.pt"


from flask import Flask, request, render_template, flash, redirect, send_from_directory
from multiprocessing import Process
from threading import Thread
from time import sleep


app = Flask(__name__)

#######################################################################################
#    Flusk Routes
#######################################################################################		
@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
def index():

	if request.method == 'POST':
		process_index_post()


	#Ambient values
	actual_temperature = "--"
	actual_humidity = "--"
	last_update = "--"
	actual_luminosity = "--"
	actual_current = "--"
	ac_speed = "--"

	#Users
	u = [
		{ 'author': "Artur", 'body': 'Test post #1' },
		{ 'author': "Joao", 'body': 'Test post #2' }
	]
	
	if app.config["HUB"]:
		hub = app.config["HUB"]

		if "TEMPERATURE" in hub.keys():
			actual_temperature = hub["TEMPERATURE"].getTemperature()
			actual_humidity = hub["TEMPERATURE"].getHumidity()
			last_update = hub["TEMPERATURE"].getLastUpdate()

		if "CURRENT" in hub.keys():
			actual_current = hub["CURRENT"].getValue()
			
		if "LUMINOSITY" in hub.keys():
			actual_luminosity = hub["LUMINOSITY"].getValue()			

		if "RELAY" in hub.keys():	
			ac_speed = hub["RELAY"].get_ac_speed()
		


	return render_template("index.html",
							title = 'Home',
							temp = actual_temperature,
							humid = actual_humidity,
							last_update = last_update,
							lux = actual_luminosity,
							current = actual_current,
							speed = ac_speed
							)

@app.route('/settings')
def settings():
	return render_template("settings.html")
	
@app.route('/gateway')
def gateway():
	return render_template("gateway.html")

@app.route('/graph')
def graph():

	data = {}

	if app.config["HUB"]:
		hub = app.config["HUB"]

		if "STORAGE HANDLER" in hub.keys():
			data = hub["STORAGE HANDLER"].getGraphData()

	return render_template("graphs.html", data=data)

def process_index_post():
	
	#print str(request.form.keys())
	
	if "HUB" in app.config.keys() and app.config["HUB"]:

		if "RELAY" in app.config["HUB"].keys():
			
			relay = app.config["HUB"]["RELAY"]
			if "AC_OFF" in request.form.keys():
				relay.set_ac_speed(0)
			elif "AC_1" in request.form.keys():
				relay.set_ac_speed(1)
			elif "AC_2" in request.form.keys():
				relay.set_ac_speed(2)
			elif "AC_3" in request.form.keys():
				relay.set_ac_speed(3)


class WebHandler(Thread):
	
	def __init__(self, hub):
		Thread.__init__(self)
		app.config["HUB"] = hub
		app.config.update(
			CSRF_ENABLED = True,
			SECRET_KEY = '2c1de198f4d30fa5d342ab60c31eeb308sb6de0f063e20efb9322940e3888d51c'
			)
		self.server = Process(target=app.run(debug = True, 
											host='0.0.0.0',
											use_reloader=False))

	def run(self):
		self.server.start()
		print "-------------------------------"

	def stop(self):
	 	self.server.join()

if __name__ == "__main__":
	
	wh = WebHandler(None)
	wh.start()
	sleep(10)
	wh.stop()
