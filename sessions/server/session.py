'''
Created on 26.03.2013

@author: Nikita Ofitserov
'''

import logging
import uuid

from collections import namedtuple

_log = logging.getLogger(__name__)

SessionKey = namedtuple('SessionKey', ['uuid', 'server'])

def parseKey(stringKey):
    v = stringKey.split("$")
    if len(v) != 2:
        raise ValueError("Invalid key format")
    return SessionKey(server=v[0], uuid=uuid.UUID(bytes=v[1]))

class Session(object):
    def __init__(self, key, timestamp, source, destination, validUntil):
        self._key = key
        self._timestamp = timestamp
        self._source = source
        self._destination = destination
        self._validUntil = validUntil
        
    @property
    def key(self):
        """Get the unique session key."""
        return self._key
    
    def binaryKey(self):
        # TODO: check specification
        return "{0}${1}".format(self._key.server, self._key.uuid.bytes)

    @property
    def timestamp(self):
        """Get the time of the last session update."""
        return self._timestamp
    
    @property
    def source(self):
        """Get the session source address."""
        return self._source

    @property
    def destination(self):
        """Get the session destination address."""
        return self._destination

    @property
    def validUntil(self):
        """Get the session expiration time."""
        return self._validUntil
    
    def prolong(self, timestamp, newValidUntil):
        if timestamp <= self.timestamp:
            raise ValueError("Time stamp can only be incremented")
        if newValidUntil < self._validUntil:
            raise ValueError("Expiration time can only be incremented")
        self._timestamp = timestamp
        self._validUntil = newValidUntil
