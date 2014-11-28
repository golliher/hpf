#!/usr/bin/env python
import pygame
import sys
import time
import os

import json

DEBUG = -1

from pygame.locals import *

from twisted.internet import reactor
from twisted.internet.task import LoopingCall
from twisted.python import log
from twisted.application import internet, service
from twisted.python import threadpool
from twisted.internet import defer

log.startLogging(open('log.txt','w'))
print "HPF Client"

from show import show
from frame import frame

global show_frame # Should we draw a graphical photo frame for an image border?
show_frame = -1

black = 0,0,0
white = 250,250,250
grey = 70, 70, 70

textcolor = white
bgcolor = black

def hide_msg():
    theframe.txtoverlay_isvisible = -1

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

def about_screen():
    show_image_fullyqualified("./about.png")

def toggle_frame():
    global show_frame
    show_frame = show_frame * -1

def toggle_debug():
    global DEBUG
    DEBUG = DEBUG * -1
    if DEBUG > 0:
        msg("Debug ON")
    else:
        msg("Debug OFF")


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

    global frame_img
    print "Frame_img: %s" % frame_img
    if show_frame > 0:
        background.blit(frame_img,(0,0))

    draw_screen()


# Event loop
def game_tick():

    for event in pygame.event.get():
        if event.type == QUIT:
            return
        elif event.type == KEYDOWN:
            if event.key == K_ESCAPE:
                reactor.stop()
                return
            elif event.key == K_d: toggle_debug()
            elif event.key == K_c: theframe.txtoverlay_isvisible = theframe.txtoverlay_isvisible * -1  # "Toggling message visibility"
            elif event.key == K_a: about_screen()
            elif event.key == K_f: toggle_frame()
    draw_screen()

# Initial pygame and the screen
pygame.init()
w = pygame.display.Info().current_w
h= pygame.display.Info().current_h
print "Screen size apears to be"
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

try:
    frame_img = pygame.image.load("./frame.png")
    frame_img = pygame.transform.smoothscale(frame_img, (int(w),int(h)))
except:
    msg("Failed to load frame overlay.")

# An instance of the frame class, intended to be used as a signleton
theframe = frame()

# Scheduled call to process the pygame events.  Essentially this put the pygame event loop in the control twisted
DESIRED_FPS = 30
tick = LoopingCall(game_tick)
tick.start(1.0 / DESIRED_FPS)

# Twisted Application Framework setup:
application = service.Application('HPF Client')

reactor.run()

print "Program has exited."
