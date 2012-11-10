'''
Created on 10.11.2012

@author: Nikita Ofitserov
'''

from collections import MutableMapping, MutableSet
import logging

_log = logging.getLogger(__name__)

class _ManyHolder(MutableSet, object):
    def __init__(self, key, parent):
        self.key = key
        self.parent = parent
        self.storage = set()

    def __contains__(self, key):
        return key in self.storage
    
    def __len__(self):
        return len(self.storage)
    
    def __iter__(self):
        return iter(self.storage)

    def __repr__(self):
        return repr(self.storage)
            
    def add(self, value):
        if self.key not in self.parent.forward:
            self.parent.forward[self.key] = self
        twin = self.parent.flip()[value]
        if value not in self.parent.backward:
            self.parent.backward[value] = twin
        self.storage.add(value)
        twin.storage.add(self.key)
    
    def discard(self, value):
        self.storage.discard(value)
        if not self.storage:
            del self.parent.forward[self.key]
        twin = self.parent.flip()[value]
        twin.storage.discard(self.key)
        if not twin.storage:
            del self.parent.backward[value]


class ManyToMany(MutableMapping, object):
    _first = dict
    _second = dict
     
    def __init__(self, _dict=None, **kwargs):
        super(ManyToMany, self).__init__()
        if '_flipped' in kwargs:
            self.flipped = kwargs['_flipped']
            self.forward = self.flipped.backward
            self.backward = self.flipped.forward
            return
        else:
            _log.info('Forward type: %s', self._first)
            _log.info('Backward type: %s', self._second)
            self.forward = self._first()
            self.backward = self._second()
            self.flipped = ManyToMany(_flipped=self)
        if _dict is not None:
            self.update(_dict)
        if len(kwargs):
            self.update(kwargs)
            
    def flip(self):
        return self.flipped
        
    def __contains__(self, key):
        return key in self.forward
    
    def __len__(self):
        return len(self.forward)
    
    def __iter__(self):
        return iter(self.forward)
    
    def __getitem__(self, key):
        try:
            return self.forward[key]
        except KeyError:
            return _ManyHolder(key, self)
    
    def __setitem__(self, key, value):
        child = self[key]
        child.clear()
        child |= value
    
    def __delitem__(self, key):
        self[key].clear()
    
    def __repr__(self):
        return '<{0}: {1}>'.format(type(self), dict(self))
