import time
import datetime
import sys
import json
import requests
import xively
import subprocess 
import spidev

global moisture_datastream
moisture_channel = 0

GPIO.setmode(GPIO.BCM)
TRIGGER_PIN = 18
threshold = 10

spi = spidev.SpiDev()
spi.open(0,0)

FEED_ID = "enter feed id"
API_KEY = "enter key"
api = xively.XivelyAPIClient(API_KEY)

def ReadChannel(channel):
   adc = spi.xfer2([1,(8+channel)<<4,0])
   data = ((adc[1]&3)<<8)+adc[2]
   return data

def readMoisture():
   level = ReadChannel(moisture_channel)
   return level
   
def runController():
   global moisture_datastream
   level = readMoisture()
   
   if (level<threshold):
     GPIO.output (TRIGGER_PIN, True)
   else :
     GPIO.output(TRIGGER_PIN, False)

   moisture_datastream.current_value = level
   moisture_datastream.at = datetime.datetime.utcnow()
   
   print "Updating Xively feed with moisture: %s" %moisture try:
     moisture_datastream.update()
   except requests.HTTPError as e:
     print "HTTPError({0}): {1}".format(e.errno, e.strerror)

def get_moisturedatastream(feed):
   try:
     datastream = feed.datastreams.get("moisture")
     return datastream
   except:
     datasream = feed.datastreams.create("moisture", tags="moisture")
     return datasream

def setupController():
    global moisture_datastream
    feed api.feeds.get(FEED_ID)

    feed.location.lat="latitude given"
	feed.location.lon="longitude given"
	feed.tags="Soil Moisture"
	feed.update()
	
	moisture_datastream = get_moisturedatastream(feed)
	moisture_datastream.max_value = None
	moisture_datastream.min_value = None
	
setupController()
while True:
    runController()
    time.sleep(10)	
      