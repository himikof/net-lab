'''
Created on 26.03.2013

@author: Nikita Ofitserov
'''

import logging
import abc

from nfw.event import Event

_log = logging.getLogger(__name__)

class Merger(object):
    __metaclass__ = abc.ABCMeta

    def __init__(self):
        self.updated = Event()

    @abc.abstractmethod
    def readKey(self, keyPb):
        pass

    @abc.abstractmethod
    def dumpValue(self, key):
        pass

    @abc.abstractmethod
    def merge(self, key, dataPb):
        pass

    @abc.abstractproperty
    def mapping(self):
        pass

    def list(self, keysPb):
        keys = map(self.readKey, keysPb)
        return (self.dumpValue(k) for k in keys)

    def process(self, updates):
        _log.debug("Merging %s updates", len(updates))
        merged = []
        for update in updates:
            key = self.readKey(update.key)
            timestamp = update.timestamp
            remove = update.remove
            if key in self.mapping:
                local_timestamp = self.mapping[key].timestamp
                if local_timestamp >= timestamp:
                    continue
                if remove:
                    _log.debug("Removing object: " + str(key))
                    del self.mapping[key]
            else:
                self.merge(key, update)
            merged.append(update)
        return merged


