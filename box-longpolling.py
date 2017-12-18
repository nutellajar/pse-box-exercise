#!/usr/bin/env python

"""
This is a simple web "crawler" that long polls the BOX events REST API

This python script uses the python libraries from

http://eventlet.net/  Eventlet is a concurrent networking library for Python that allows you to change how you run your code
http://docs.python-requests.org/en/master/ Requests is the only Non-GMO HTTP library for Python, safe for human consumption.

"""
import eventlet
import requests
import json
# greening an application is to import networking-related libraries from the eventlet.green package. 
# It contains libraries that have the same interfaces as common standard ones, but they are modified to behave well with green threads.
from eventlet.green import urllib2

# This function monkeypatches the key system modules by replacing their key elements with green equivalents. 
eventlet.monkey_patch()


# In order to run you need to generate a developer token from your developer.box.com account
# found in the configuration section of an App.
# you can hardcode it here in the ACCESS_TOKEN or store it in an environment variable
ACCESS_TOKEN = "xxxx"
AUTH_BEARER = "Bearer " + ACCESS_TOKEN
HEADERS = {'Authorization' : AUTH_BEARER }

currentstreamURL = "https://api.box.com/2.0/events?stream_position=now"
eventstreamURL = "https://api.box.com/2.0/events"


"""
fetchCurrentPosition retrieves the next stream position from the BOX events API
Returns : next stream position
"""
def fetchCurrentPosition():
    print("opening URL ", currentstreamURL)
    #body = urllib2.urlopen(url).read()
    r = requests.get(currentstreamURL, headers=HEADERS)
    rjsondata = r.json()
    print json.dumps(rjsondata, indent=4, sort_keys=False)
   
    return rjsondata["next_stream_position"]
 
"""
callEventsOptions retrieves the server url that will be used for a long poll
Returns : server url
""" 
def callEventsOptions():
    print("opening URL ", eventstreamURL)
    r = requests.options(eventstreamURL, headers=HEADERS)
    rjsondata = r.json()
    print json.dumps(rjsondata, indent=4, sort_keys=False)
    return rjsondata["entries"][0]['url']

"""
fetchSubscribeUrl long polls a specific server
and retrieves the message if there is new activity on the account
Input : server url, current stream position
Returns : message from long poll

"""
def fetchSubscribeUrl(sURL,currposition):
	pollingURL = "{}{}{}".format(sURL,'&stream_position=',currposition)
	print "opening long polling URL : ", pollingURL
	print "long polling ..... "
	req = urllib2.Request(pollingURL, None, headers=HEADERS)
	response = urllib2.urlopen(req)
	html=response.read()
	json_obj=json.loads(html)

	print json_obj["message"]
	return json_obj["message"]

"""
fetchEventDetails retrieves the events at a given stream position
and returns the next stream position

Input: stream position
Returns : next stream position

"""
def fetchEventDetails(currposition):
	newEventStreamURL = "{}{}{}".format(eventstreamURL, '?stream_position=',currposition)
	print "Fetching events details"
	print("opening URL : ", newEventStreamURL)
	r = requests.get(newEventStreamURL, headers=HEADERS)
	rjsondata = r.json()
	next_stream_position = rjsondata["next_stream_position"]
	event_id = rjsondata["entries"][0]['event_id']
	event_type = rjsondata["entries"][0]['event_type']
	print "next_stream_position :: ", next_stream_position
	print "event ID  :: ", event_id
	print "event TYPE :: ", event_type
	return next_stream_position
   

try:

	currentPosition  = fetchCurrentPosition()
	print "{} and {}".format("Next Stream ID is ", currentPosition )
	subscribeURL = callEventsOptions()

	while True:
		message = fetchSubscribeUrl(subscribeURL,currentPosition)
		if message == 'new_change':
			next_id = fetchEventDetails(currentPosition)
			currentPosition = next_id
		elif message == 'reconnect':
			currentPosition  = fetchCurrentPosition()
			subscribeURL = callEventsOptions()
except (KeyboardInterrupt, SystemExit):
    print("long polling exiting.")


