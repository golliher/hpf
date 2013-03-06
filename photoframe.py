#!/usr/bin/env python 
import pygame
import sys
import time
import os

import json

DEBUG = -1

from pygame.locals import *
from show import show

from twisted.internet import reactor
from twisted.internet.task import LoopingCall
from twisted.python import log

from twisted.web.server import Site
from twisted.web.static import File

from frame import frame
 
from autobahn.websocket import WebSocketServerFactory, \
                               WebSocketServerProtocol, \
                               listenWS 

from autobahn.wamp import WampServerFactory, WampServerProtocol, exportRpc

import watchdog
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

sys.path.append("webremote")
os.environ['DJANGO_SETTINGS_MODULE'] = 'webremote.settings'
from django.core.handlers.wsgi import WSGIHandler

from twisted.application import internet, service
from twisted.web import server, resource, wsgi, static
from twisted.python import threadpool
from twisted.internet import reactor
from twisted.internet import defer

import twresource

PORT = 8080

def show_from_path(path):
    """Extracts the show string from a given path"""
    (dir,file) = os.path.split(path)
    (base,show) = os.path.split(dir)
    return show

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

seconds_to_next_slide = 300

black = 0,0,0
white = 250,250,250
yellow = 255,242,0
grey = 70, 70, 70

textcolor = white
bgcolor = black


class RpcServerProtocol(WampServerProtocol):

    @exportRpc
    def getcurrentshow(self):
        result = list_currentshow()
        return result

    @exportRpc
    def getcurrentimage(self):
        result = theframe.current_image_url
        return result

        
    @exportRpc
    def switch(self, show):
        switch_shows(show)
        result = "Newwork call to -> Switch to %s" % show
        print result
        return result

    @exportRpc
    def advance(self):
        result = "Newwork call to advance."
        print result
        advance_show()
        return result 

    @exportRpc
    def rewind(self):
        result = "Newwork call to rewind."
        print result
        rewind_show()
        return result 
      
    @exportRpc
    def stop(self):
        stop_show()
        result = "Newwork call to stop show."
        print result
        return result

    @exportRpc
    def start(self):
        start_show()
        result = "Newwork call to start show."
        print result
        return result
        
    @exportRpc
    def showlist(self):
        result = list_shows()
        print result
        # print dict(result)
        return result

    def onSessionOpen(self):
        self.registerForRpc(self, "http://localhost/frame#")
        
        ## register a single, fixed URI as PubSub topic
        self.registerForPubSub("http://localhost/image")
        print "Registered for PubSub on /image topic."
        
        self.registerForPubSub("http://localhost/msg")
        print "Registered for PubSub on /msg topic."

        self.registerForPubSub("http://localhost/currentshow")
        print "Registered for PubSub on /currentshow topic."
        
        self.registerForPubSub("http://localhost/status")
        print "Registered for PubSub on /status topic."
        

def hide_msg():
    theframe.txtoverlay_isvisible = -1
    factory.dispatch("http://localhost/msg","")

def dmsg(message, duration=3, bgcolor=grey, textcolor=white, alpha=200):
    global DEBUG
    if DEBUG > 0:
        msg(message, duration, bgcolor, textcolor, alpha)
    
    
def msg(message, duration=3, bgcolor=grey, textcolor=white,alpha=200):
    """Display some text at bottom of the screen"""
    print "msg: %s" % message
    theframe.txtoverlay_isvisible = 1

    font = pygame.font.Font(None, 36)
    text = font.render(message, 1, textcolor)

    textpos = text.get_rect()
    textpos.centerx = background.get_rect().centerx
    textpos.centery = h - text.get_height() 

    textbg.fill(bgcolor) 
    textbg.blit(text, ( bgwidth/2-(text.get_width()/2),(text.get_height()/2) ))
    textbg.set_alpha(alpha)

    reactor.callLater(duration, hide_msg)

    draw_screen()
    factory.dispatch("http://localhost/msg",message)

    
    return
            
def aspect_scale(img,(bx,by)):
    """ Scales 'img' to fit into box bx/by.
     This method will retain the original image's aspect ratio """
    ix,iy = img.get_size()
    if ix > iy:
        # fit to width
        scale_factor = bx/float(ix)
        sy = scale_factor * iy
        if sy > by:
            scale_factor = by/float(iy)
            sx = scale_factor * ix
            sy = by
        else:
            sx = bx
    else:
        # fit to height
        scale_factor = by/float(iy)
        sx = scale_factor * ix
        if sx > bx:
            scale_factor = bx/float(ix)
            sx = bx
            sy = scale_factor * iy
        else:
            sy = by

    return pygame.transform.smoothscale(img, (int(sx),int(sy)))

# log.startLogging(sys.stdout)
log.startLogging(open('log.txt','w'))
print "Darrell's toy photo frame"

#  Setup RPC
factory = WampServerFactory("ws://localhost:9000")
factory.protocol = RpcServerProtocol
listenWS(factory)

# Initial pygame and the screen 
pygame.init()
w = pygame.display.Info().current_w
h= pygame.display.Info().current_h
print "w: ", w, "h: ", h
size = (pygame.display.Info().current_w, pygame.display.Info().current_h)
pygame.mouse.set_visible(0)
screen = pygame.display.set_mode(size,pygame.FULLSCREEN)

# Create and Fill background
background = pygame.Surface(screen.get_size())
background = background.convert()  # This is cargo cult.. I don't know why it's here.
background.fill(bgcolor)

# Create the text overlay areas
bgwidth = int(w * 0.5)
textbg = pygame.Surface(  (bgwidth,50)   )

global show_frame 
show_frame = -1

# Event loop
def game_tick():
    
    global show_frame
    global DEBUG
    for event in pygame.event.get():
        if event.type == QUIT:
            return
        elif event.type == KEYDOWN:
            if event.key == K_ESCAPE:
                # observer.stop()
                reactor.stop()
                return
            elif event.key == K_d: 
                DEBUG = DEBUG * -1
                if DEBUG > 0: 
                    msg("Debug ON")
                else:
                    msg("Debug OFF")
            elif event.key == K_c: theframe.txtoverlay_isvisible = theframe.txtoverlay_isvisible * -1  # "Toggling message visibility"
            elif event.key == K_a: about_screen()
            elif event.key == K_1: switch_shows(1)
            elif event.key == K_2: switch_shows(2)
            elif event.key == K_3: switch_shows(3)
            elif event.key == K_f: show_frame = show_frame * -1
            elif event.key == K_n: advance_show()
            elif event.key == K_RIGHT: advance_show()
            elif event.key == K_p: rewind_show()
            elif event.key == K_LEFT: rewind_show()
            elif event.key == K_UP: switch_prev_show()
            elif event.key == K_DOWN: switch_next_show()
            elif event.key == K_s: stop_show()
            elif event.key == K_g: start_show()
    draw_screen()

def draw_screen():
    screen.blit(background, (0,0))
    if theframe.txtoverlay_isvisible > 0:
        screen.blit(textbg, ( (w/2)-(bgwidth/2) ,h-100))
    pygame.display.flip()


def show_image_fullyqualified(imagefile):
    """Given the path to a file, paints it onto the background"""
    global show_frame
    filepath = imagefile
    
    try:
        img = pygame.image.load(filepath)
    except:
        msg("Failed to load image")
        return
    img = aspect_scale(img,(int(w),int(h)))
    imgrect = img.get_rect()
    background.fill(bgcolor)
    ix,iy = img.get_size()	
    xshift = (w - ix) / 2
    background.blit(img, (xshift,0))

    try:
        frame = pygame.image.load("./frame.png")
        frame = pygame.transform.smoothscale(frame, (int(w),int(h)))
    except:
        msg("Failed to load frame overlay.")

    if show_frame > 0:
        background.blit(frame,(0,0))
        
    draw_screen()

def show_image(imagefile):
    filepath = "%s/%s" % (theshow.path,imagefile)
    theframe.current_image_filename = filepath
    # theframe.current_image_url = "http://192.168.4.77:8080" + filepath[1:]  # Removing the "."
    theframe.current_image_url =  filepath[1:]  # Removing the "."
    
    
    print "Current image is: %s" % theframe.current_image_filename
    print "Current image URL is: %s" % theframe.current_image_url
    factory.dispatch("http://localhost/image",theframe.current_image_url)
    
    
    show_image_fullyqualified(filepath)

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
    
def about_screen():
    show_image_fullyqualified("./about.png")

def list_shows():
    return json.dumps(theframe.shows)
    
def list_currentshow():
    return json.dumps(os.path.basename(theshow.path))

def switch_prev_show():
    global theframe
    newindex = (theframe.activeshow_index - 1) % len(theframe.shows)
    newindex = newindex -2 # fix off by two?  How maddening..
    switch_shows( newindex )

def switch_next_show():
    global theframe
    newindex = (theframe.activeshow_index + 1) % len(theframe.shows)
    newindex = newindex -1 # fix off by one
    switch_shows( newindex )

def switch_shows(newshow):
    newshow = newshow -1 # fix off by one
    global theshow
    global theframe
    msg("Switching to show %s" % theframe.shows[newshow])
    factory.dispatch("http://localhost/currentshow",theframe.shows[newshow])
    
    theshow = shows[newshow]
    show_image(theshow.current())
    theframe.activeshow_index = newshow
    
def advance_show():
    dmsg("Advancing...")
    theshow.next()
    dmsg("Displaying image...")
    show_image(theshow.current())   
    dmsg("Done.")

def rewind_show():
    print "calling show image with:%s" % theshow.current()
    theshow.prev()
    show_image(theshow.current())

def scan_for_shows():
    print "SCANNING FOR SHOWS"
    # We build the collection of shows
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
    dmsg("List of shows was rebuilt")
    factory.dispatch("http://localhost/status",'show-list-rebuilt')
    
    

# An instance of the frame class, intended to be used as a signleton
theframe = frame()

shows = []
scan_for_shows()

print "Setting up observer for SHOWS DIRECTORY"
showchange_event_handler = MyEventHandler()
showobserver = Observer()
showobserver.schedule(showchange_event_handler, "./shows", recursive=True)
showobserver.start()

print "assigning show shortcuts"

theframe.activeshow = shows[0]
theshow = shows[0]
print "Current active path after loading: %s" % theframe.activeshow.path

# Scheduled call to advance the show
show_tick = LoopingCall(advance_show)
show_tick.start(seconds_to_next_slide)

# Scheduled call to process the pygame events.  Essentially this put the pygame event loop in the control of autobahn and twisted
DESIRED_FPS = 30 
tick = LoopingCall(game_tick)
tick.start(1.0 / DESIRED_FPS)

msg("Hackers Photo Frame.",duration=2,bgcolor=grey,textcolor=white,alpha=255)

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
main_site = server.Site(root)
# internet.TCPServer(PORT, main_site).setServiceParent(application)
reactor.listenTCP(PORT, main_site)
reactor.run()

