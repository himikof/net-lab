'''
Created on 26.03.2013

@author: Nikita Ofitserov
'''

import logging

_log = logging.getLogger(__name__)

class Host(object):
    def __init__(self, address, timestamp, cname, allowed):
        self._address = address
        self._timestamp = timestamp
        self._cname = cname
        self._allowed = allowed
        
    @property
    def key(self):
        """Get the unique host key (address)."""
        return self._address
    
    @property
    def timestamp(self):
        """Get the time of the last host update."""
        return self._timestamp
    
    @property
    def name(self):
        """Get the host computer name."""
        return self._cname

    @property
    def isAllowed(self):
        """Get whether the host is allowed to participate."""
        return self._allowed

    def setAllowed(self, timestamp, isAllowed):
        if timestamp < self.timestamp:
            raise ValueError("Time stamp can only be incremented")
        self._timestamp = timestamp
        self._allowed = isAllowed

    def setName(self, timestamp, newName):
        if timestamp < self.timestamp:
            raise ValueError("Time stamp can only be incremented")
        self._timestamp = timestamp
        self._cname = newName

    def __repr__(self):
        return str(self.__dict__)
