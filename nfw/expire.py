'''
Created on 10.11.2012

@author: Nikita Ofitserov
'''

from collections import MutableMapping
from abc import abstractmethod, ABCMeta
from twisted.internet.defer import inlineCallbacks
from twisted.internet import defer

import logging

_log = logging.getLogger(__name__)

class AbstractExpiringDict(MutableMapping, object):
    __metaclass__ = ABCMeta
    
    def __init__(self, _dict=None, _reactor=None, **kwargs):
        if _reactor is None:
            from twisted.internet import reactor as _reactor
        self.reactor = _reactor
        super(AbstractExpiringDict, self).__init__()
        self.data = {}
        if _dict is not None:
            self.update(_dict)
        if len(kwargs):
            self.update(kwargs)
    
    @abstractmethod
    def expire(self, key):
        '''
        Is called when an entry expires.
        @param key: the key of the expired entry
        @return: None if entry should be deleted, or the new value for this key (could be Deferred)
        '''
        pass

    @abstractmethod
    def ttl(self, key):
        '''
        Returns entry's TTL (time to live). This entry should be present in the
        dictionary.
        @param key: the key to get TTL for
        @return: entry TTL in seconds
        '''
        pass
    
    @inlineCallbacks
    def _do_expire(self, key):
        _log.info("_do_expire")
        result = yield defer.maybeDeferred(self.expire, key)
        if result is None:
            del self.data[key]
        else:
            self[key] = result
    
    def __contains__(self, key):
        return key in self.data
    
    def __len__(self):
        return len(self.data)
    
    def __iter__(self):
        return iter(self.data)
    
    def __getitem__(self, key):
        return self.data[key][0]
    
    def __setitem__(self, key, value):
        if key in self:
            del self[key]
        ttl = self.ttl(key)
        expireD = self.reactor.callLater(ttl, self._do_expire, key)
        self.data[key] = (value, expireD)
        
    def __delitem__(self, key):
        _, expireD = self.data[key]
        expireD.cancel()
        del self.data[key]
        
    def __repr__(self):
        return '<{0}: {1}>'.format(type(self), dict(self))
