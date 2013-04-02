'''
Created on 26.03.2013

@author: Nikita Ofitserov
'''

import logging

_log = logging.getLogger(__name__)

class Merger(object):
    def __init__(self, mapping, readKey, merge):
        self.mapping = mapping
        self.readKey = readKey
        self.merge = merge

    def process(self, updates):
        #_log.debug("Merging %s", updates)
        for update in updates:
            key = self.readKey(update.key)
            timestamp = update.timestamp
            remove = update.remove
            if remove:
                if key in self.mapping:
                    del self.mapping[key]
            else:
                self.merge(key, update)


