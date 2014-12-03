#!/usr/bin/env python

# Tuesday; November 25, 2014 @ 11:04 PM
# Contemplating stripping ALL pygame code out so this is only a server
#  without any user interface.

# I will attempt to simply delete stuff first.. this started as a copy of
#  photoframe.py. As of 11:48 PM I have it basically working without pygame!
#

import sys
import time
import os
import json

DEBUG = -1
PORT = 8080
seconds_to_next_slide = 60

# Start import of dependancy libraries

# Twisted provides for cooperative multitasking between
#  frameworks and also scheduling of deferred calls
#  It is used for the primary event loop of this program.
#

# Used by autobahn for sure, others?
from twisted.python import log
from twisted.internet import reactor
from twisted.internet.defer import inlineCallbacks
from twisted.internet.endpoints import serverFromString

from twisted.application import internet, service
from twisted.internet.task import LoopingCall
from twisted.internet import defer

from twisted.python import threadpool

from twisted.web import server, resource, wsgi, static
from twisted.web.server import Site
from twisted.web.static import File

# Autobahn is the library used to implement our client API for HPF
#
from autobahn.wamp import types
from autobahn.twisted import wamp, websocket
# from autobahn.twisted.util import sleep


# Watchdog is a library that pays attention to change on the filesystem
#
import watchdog
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# Django is used inside this program to provide web framework
#  without having to run a standalone webserver and all that goes
#  into configuring one.  Keeps deployment simple and keeps HPF
#  self sufficient.
import twresource
from django.core.handlers.wsgi import WSGIHandler


# End import of dependancy libraries


# Print this before print statements get captured to the log.
print "Darrell's toy photo frame"

# Print statements will go to log file starting here.
log.startLogging(open('log.txt','w'))

# Libraries I wrote to encapsulate my data model
from show import show
from frame import frame

class MyEventHandler(FileSystemEventHandler):
   """Reacts to changes on the filesystem."""

   def on_created(self, event):
       scan_for_shows()
       print "FSE CREATED so show %s" % event.src_path
       show_image_fullyqualified(event.src_path)

   def on_modified(self, event):
       scan_for_shows()
       print "FSE MODIFIED so show %s" % event.src_path
       show_image_fullyqualified(event.src_path)

   def on_any_event(self, event):
       scan_for_shows()
       print "FSE ANY Rescanning shows."
       print "Watchdog event: %s" % event


class HPFbackendComponent(wamp.ApplicationSession):
    """Defines the behavior of the WAMP web service, both the PubSub and RPC"""

    @inlineCallbacks

    def onJoin(self,details):

        def getcurrentshow():
            result = list_currentshow()
            return result

        try:
            yield self.register(getcurrentshow, 'com.hpf.getcurrentshow')
        except Exception as e:
            print("failed to register procedure: {}".format(e))
        else:
            print("procedure registered")


        def getcurrentimage():
            result = theframe.current_image_url
            return result

        try:
            yield self.register(getcurrentimage, 'com.hpf.getcurrentimage')
        except Exception as e:
            print("failed to register procedure: {}".format(e))
        else:
            print("procedure registered")


        def switch(show):
            switch_shows(show)
            result = "Network call to -> Switch to %s" % show
            print result
            return result

        try:
            yield self.register(switch, 'com.hpf.switch')
        except Exception as e:
            print("failed to register procedure: {}".format(e))
        else:
            print("procedure registered")


        def advance():
            result = "Network call to advance."
            print result
            advance_show()
            return result

        try:
            yield self.register(advance, 'com.hpf.advance')
        except Exception as e:
            print("failed to register procedure: {}".format(e))
        else:
            print("procedure registered")

        def rewind():
            result = "Network call to rewind."
            print result
            rewind_show()
            return result


        try:
            yield self.register(rewind, 'com.hpf.rewind')
        except Exception as e:
            print("failed to register procedure: {}".format(e))
        else:
            print("procedure registered")

        def start():
            start_show()
            result = "Network call to start show."
            print result
            return result

        try:
            yield self.register(start, 'com.hpf.start')
        except Exception as e:
            print("failed to register procedure: {}".format(e))
        else:
            print("procedure registered")

        def showlist():
            result = list_shows()
            print result
            return result

        try:
            yield self.register(showlist, 'com.hpf.showlist')
        except Exception as e:
            print("failed to register procedure: {}".format(e))
        else:
            print("showlist procedure registered")

        def stop():
            stop_show()
            result = "Network call to stop show."
            print result
            return result

        try:
            yield self.register(stop, 'com.hpf.stop')
        except Exception as e:
            print("failed to register procedure: {}".format(e))
        else:
            print("procedure registered")

    #
    # @exportRpc
    # def onSessionOpen(self):
    #     self.registerForRpc(self, "http://localhost/frame#")
    #


    #     ## register a single, fixed URI as PubSub topic
    #     self.registerForPubSub("http://localhost/image")
    #     print "Registered for PubSub on /image topic."
    #
    #     self.registerForPubSub("http://localhost/msg")
    #     print "Registered for PubSub on /msg topic."
    #
    #     self.registerForPubSub("http://localhost/currentshow")
    #     print "Registered for PubSub on /currentshow topic."
    #
    #     self.registerForPubSub("http://localhost/status")
    #     print "Registered for PubSub on /status topic."


def hide_msg():
    theframe.txtoverlay_isvisible = -1
    component_session.publish("com.hpf.msg","")

def msg(message, duration=3):
    """Display some text at bottom of the screen"""
    print "msg: %s" % message
    theframe.txtoverlay_isvisible = 1

    reactor.callLater(duration, hide_msg)

    component_session.publish("com.hpf.msg",message)
    return


router_factory = wamp.RouterFactory()
session_factory = wamp.RouterSessionFactory(router_factory)

component_config = types.ComponentConfig(realm = "hpf")
component_session = HPFbackendComponent(component_config)
session_factory.add(component_session)

transport_factory = websocket.WampWebSocketServerFactory(session_factory,
                                                            debug = False,
                                                            debug_wamp = False)

wsserver = serverFromString(reactor, "tcp:9000")
wsserver.listen(transport_factory)

def show_from_path(path):
    """Extracts the show string from a given path"""
    (dir,file) = os.path.split(path)
    (base,show) = os.path.split(dir)
    return show


def show_image(imagefile):
    filepath = "%s/%s" % (theshow.path,imagefile)
    theframe.current_image_filename = filepath
    theframe.current_image_url =  filepath[1:]  # Removing the "."

    print "Current image is: %s" % theframe.current_image_filename
    print "Current image URL is: %s" % theframe.current_image_url
    component_session.publish("com.hpf.image",theframe.current_image_url)

def start_show():
    msg("GOING",duration=0.5)
    try:
        show_tick.start(seconds_to_next_slide)
    except:
        print "Can't start.  Already started?"

def stop_show():
    try:
        show_tick.stop()
        msg("STOPPED")
    except:
        msg("Can't stop.  Already stopped?")

def list_shows():
    print "list_shows() called"
    return json.dumps(theframe.shows)

def list_currentshow():
    return json.dumps(os.path.basename(theshow.path))

def switch_prev_show():
    global theframe
    newindex = (theframe.activeshow_index) % len(theframe.shows)  # we won't have to decement because two structures are already 'off by one'
    switch_shows( newindex )

def switch_next_show():
    global theframe
    newindex = (theframe.activeshow_index + 1) % len(theframe.shows)
    newindex = newindex +1 # fix 'off by one' difference between the two structures
    switch_shows( newindex )

def switch_shows(newshow):
    newshow = newshow -1 # fix off by one
    global theshow
    global theframe
    msg("Switching to show %s" % theframe.shows[newshow])
    component_session.publish("com.hpf.currentshow",theframe.shows[newshow])

    theshow = shows[newshow]
    show_image(theshow.current())
    theframe.activeshow_index = newshow

def advance_show():
    theshow.next()
    show_image(theshow.current())


def rewind_show():
    print "calling show image with:%s" % theshow.current()
    theshow.prev()
    show_image(theshow.current())

def scan_for_shows():
    print "SCANNING FOR SHOWS"
    # We build the collection of shows from the files system
    global shows

    print "Numbers of shows is: %s" % len(shows)
    shows = []
    theframe.shows = []

    # This contains show objects
    # Cargo cult recipie that gives only directories, not subdirectories
    for show_dir in os.walk('./shows').next()[1]:
        show_dir = "./shows/" + show_dir
        print "Creating show for directory: %s" % show_dir
        s = show()
        s.load_path(show_dir)
        s.start_observer()
        shows.append(s)
        # This merely contains show names
        theframe.shows.append(os.path.basename(show_dir))
    print "Numbers of shows is NOW: %s" % len(shows)
    component_session.publish("com.hpf.status",'show-list-rebuilt')


## Main program starts here -- everything up until here was definition
## of functions and setup.

# An instance of the frame class, intended to be used as a signleton
theframe = frame()
shows = []

# Do the initial read of shows on the file system.
scan_for_shows()

# Here we setup the use of the Watchdog framework, one of our external
#  Dependancies to pickup future changes on the filesystem.
print "Setting up observer for SHOWS DIRECTORY"
showchange_event_handler = MyEventHandler()
showobserver = Observer()
showobserver.schedule(showchange_event_handler, "./shows", recursive=True)
showobserver.start()

print "Assigning show shortcut variables"
theframe.activeshow = shows[0]
theshow = shows[0]

print "Current active path after loading: %s" % theframe.activeshow.path

# Schedule call to advance the show at our desired update period
show_tick = LoopingCall(advance_show)
show_tick.start(seconds_to_next_slide)


## Start DJango setup for serving images and build-in web client application.
sys.path.append("webremote")
os.environ['DJANGO_SETTINGS_MODULE'] = 'webremote.settings'

def wsgi_resource():
    pool = threadpool.ThreadPool()
    pool.start()
    # Allow Ctrl-C to get you out cleanly:
    reactor.addSystemEventTrigger('after', 'shutdown', pool.stop)
    wsgi_resource = wsgi.WSGIResource(reactor, pool, WSGIHandler())
    return wsgi_resource

# Twisted Application Framework setup:
application = service.Application('twisted-django')

# WSGI container for Django, combine it with twisted.web.Resource:
# XXX this is the only 'ugly' part: see the 'getChild' method in twresource.Root
wsgi_root = wsgi_resource()
root = twresource.Root(wsgi_root)

# Servce Django media files off of /media:
showssrc = static.File(os.path.join(os.path.abspath("."), "./webroot/shows"))
root.putChild("shows", showssrc)

staticrsrc = static.File(os.path.join(os.path.abspath("."), "./static"))
root.putChild("static", staticrsrc)

# Serve it up:
main_site = server.Site(root,logPath=('django.log'))
reactor.listenTCP(PORT, main_site)
## Finish Django setup

## Turn on the main Twisted event loop and make things go.
reactor.run()

## That's it, shows over.
print "Reactor ran.  Then program terminated."
