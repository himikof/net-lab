'''
Created on 10.11.2012

@author: Nikita Ofitserov
'''

from functools import partial
from twisted.internet.defer import inlineCallbacks, Deferred

class Event(object):
    def __init__(self):
        self.subscribers = set()
        
    def subscribe(self, callback, *args, **kwargs):
        subscription = partial(callback, *args, **kwargs)
        self.subscribers.add(subscription)
        return subscription

    def unsubscibe(self, handle):
        self.subscribers.remove(handle)
    
    def fire(self, *args, **kwargs):
        subscribers = list(self.subscribers)
        for callback in subscribers:
            callback(*args, **kwargs)
    
    @inlineCallbacks
    def waitFor0(self):
        d = Deferred()
        s = self.subscribe(d.callback, None)
        yield d
        self.unsubscibe(s)

    @inlineCallbacks
    def waitFor1(self):
        d = Deferred()
        s = self.subscribe(d.callback)
        yield d
        self.unsubscibe(s)
