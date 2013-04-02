'''
Created on 10.11.2012

@author: Nikita Ofitserov
'''

import logging
import time

from sessions.server.host import Host
from sessions.server.common import DatabaseException
from sessions.server.replication.merger import Merger

_log = logging.getLogger(__name__)

class HostDB(object):
    def __init__(self):
        self.hosts = {}

    def validateHost(self, address, cname):
        if address not in self.hosts:
            # Remember invalid hosts anyway, to ease administration
            self.hosts[address] = Host(address, time.time(), cname, False)
            raise DatabaseException("Unknown host {0}, "
                                    "remembering".format(address))
        h = self.hosts[address]
        if not h.isAllowed:
            raise DatabaseException("Forbidden host {0}".format(h))
        if h.name != cname:
            raise DatabaseException("Bad computer name {0} "
                                    "for host {1}".format(cname, h))
        return h
    
    def queryHost(self, address):
        if address not in self.hosts:
            raise DatabaseException("Unknown host {0}".format(address))
        h = self.hosts[address]
        if not h.isAllowed:
            raise DatabaseException("Forbidden host {0}".format(h))
        return h
    
    def merger(self):
        return Merger(self.hosts)

db = None

def setup():
    global db
    db = HostDB()
