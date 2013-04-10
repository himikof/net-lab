'''
Created on 10.11.2012

@author: Nikita Ofitserov
'''

import logging
import time
import uuid

from nfw.expire import AbstractExpiringDict
from nfw.event import Event

from sessions.server.session import Session, SessionKey
from sessions.server.common import DatabaseException
from sessions.server.replication.merger import Merger

import sessions.server.ServerReplication_pb2 as pb2

from twisted.internet.defer import inlineCallbacks

_log = logging.getLogger(__name__)

class SessionList(AbstractExpiringDict):
    # @inlineCallbacks
    def expire(self, sessionKey):
        _log.info('Trying to expire')
        s = self[sessionKey]
        now = time.time()
        if s.validUntil > now:
            # Reschedule
            return s
        return None

    def ttl(self, sessionKey):
        _log.debug("TTL: %s, %s, %s", self[sessionKey].validUntil, time.time(),
         self[sessionKey].validUntil - time.time())
        return max(self[sessionKey].validUntil - time.time(), 0)

class SessionDB(object):
    def __init__(self, serverId, sessionDuration):
        self.serverId = serverId
        self.sessionDuration = sessionDuration
        self.sessions = SessionList()
        self.updated = Event()

    def requestSession(self, source, destination):
        key = SessionKey(server=self.serverId, uuid=uuid.uuid4())
        now = time.time()
        validUntil = now + self.sessionDuration
        s = Session(key, now, source, destination.key, validUntil)
        _log.debug("Created session {}".format(key))
        self.sessions[key] = s
        self.updated.fire([key])
        return s

    def validateSession(self, sessionKey, destination):
        try:
            s = self.sessions[sessionKey]
        except KeyError:
            raise DatabaseException("Session {0} not found".format(sessionKey))
        if s.destination != destination.key:
            raise DatabaseException("Requested destination "
                                    "{0} does not match session "
                                    "{1}".format(destination, s))
        return True

    def merger(self):
        return SessionDBMerger(self)


class SessionDBMerger(Merger):
    def __init__(self, db):
        super(SessionDBMerger, self).__init__()
        self.db = db
        self.db.updated.subscribe(self.update)

    def update(self, keys):
        self.updated.fire([self.dumpValue(key) for key in keys])

    @property
    def mapping(self):
        return self.db.sessions

    def readKey(self, keyPb):
        return SessionKey(server=keyPb.serverId,
                          uuid=uuid.UUID(keyPb.sessionId))

    def dumpValue(self, key):
        value = self.mapping[key]
        message = pb2.Session()
        message.key.serverId = key.server
        message.key.sessionId = str(key.uuid)
        message.timestamp = long(value.timestamp * 1000)
        message.sessionSource = value.source.key
        message.sessionDest = value.destination
        message.validUntil = long(value.validUntil * 1000)
        return message

    def merge(self, key, dataPb):
        timestamp = dataPb.timestamp / 1000.0
        validUntil = dataPb.validUntil / 1000.0
        if key not in self.mapping:
            session = Session(key, timestamp,
                              dataPb.sessionSource, dataPb.sessionDest,
                              validUntil)
            _log.debug("Importing session: %s", session)
            self.mapping[key] = session
        else:
            if dataPb.HasField('validUntil'):
                _log.debug("Prolonging session: %s, %s", key, validUntil)
                self.mapping[key].prolong(timestamp, validUntil)

db = None

def setup(serverId):
    global db
    DEFAULT_SESSION_DURATION = 10.0
    db = SessionDB(serverId, DEFAULT_SESSION_DURATION)
