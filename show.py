from os import walk

import watchdog
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

""" A class for the photo-frame project"""

class MyEventHandler(FileSystemEventHandler):   
   """Reacts to changes on the filesystem."""

   def __init__(self,show):
       self.show = show

   def on_any_event(self, event):
       if event.is_directory:
           return
       print "rescanning"
       # msg("Rescanning..")

       # print "Reloading path: %s" % theframe.activeshow.path
       self.show.load_path(self.show.path)

       # def on_moved(self, event):
       # def on_created(self, event):
       # def on_deleted(self, event):
       # def on_modified(self, event):

class show:
    """Encapsulates everything related to a collection of images to be shown in order."""
    def __init__(self):
        print "Creating a show"
        self.index = 0
        self.items = []
        self.path = ""
        
    def load_path(self,path):
        # TODO: make it content aware.  image files get simple processing.  
        #  contemplate special file processing for..
        #       1) a text file containing a url
        #       2) an apple webloc file (propery list)
        #       3) a medley API gallery result (really ambitious)
        print "Loading show from directory"
        self.items = []
        self.path = path
        for (dirpath, dirname, filenames) in walk(path):
            self.items.extend(filenames)
            break
        self.total = len(self.items)
        print "Built initial show: %s" % self.items

    def start_observer(self):
        print "Setting up observer for %s" % self.path
        self.event_handler = MyEventHandler(self)
        self.observer = Observer()
        self.observer.schedule(self.event_handler, self.path, recursive=True)
        self.observer.start()
    
    def current(self):
        if self.total == 0:
            return
        return self.items[self.index]
        
    def next(self):
        if self.total == 0:
            return
        self.index = (self.index + 1) % self.total

    def prev(self):
        if self.total == 0:
            return
        self.index = (self.index - 1) % self.total
    
