'''
Created on 10.11.2012

@author: Nikita Ofitserov
'''

import logging
import time

from nfw.event import Event

from sessions.server.host import Host
from sessions.server.common import DatabaseException
from sessions.server.replication.merger import Merger

import sessions.server.ServerReplication_pb2 as pb2

_log = logging.getLogger(__name__)

class HostDB(object):
    def __init__(self):
        self.hosts = {}
        self.updated = Event()

    def validateHost(self, address, cname):
        if address not in self.hosts:
            # Remember invalid hosts anyway, to ease administration
            self.hosts[address] = Host(address, time.time(), cname, True)
            self.updated.fire([address])
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
        return HostDBMerger(self)


class HostDBMerger(Merger):
    def __init__(self, db):
        super(HostDBMerger, self).__init__()
        self.db = db
        self.db.updated.subscribe(self.update)

    def update(self, keys):
        self.updated.fire([self.dumpValue(key) for key in keys])

    @property
    def mapping(self):
        return self.db.hosts

    def readKey(self, keyPb):
        return keyPb.address

    def dumpValue(self, key):
        value = self.mapping[key]
        message = pb2.Host()
        message.key.address = key
        message.timestamp = long(value.timestamp * 1000)
        message.name = value.name
        message.valid = value.isAllowed
        return message

    def merge(self, key, dataPb):
        timestamp = dataPb.timestamp / 1000.0
        if key not in self.mapping:
            self.mapping[key] = Host(key, timestamp, dataPb.name, dataPb.valid)
            _log.debug("Importing host: %s", self.mapping[key])
        else:
            #if dataPb.HasField('name'):
            #    _log.debug("Setting host %s ts=%s name=%s", key, timestamp,
            #               dataPb.name)
            #    self.mapping[key].setName(timestamp, dataPb.name)
            if dataPb.HasField('valid'):
                _log.debug("Setting host %s ts=%s isAllowed=%s", key, 
                           timestamp, dataPb.valid)
                self.mapping[key].setAllowed(timestamp, dataPb.valid)


db = None

def setup():
    global db
    db = HostDB()
