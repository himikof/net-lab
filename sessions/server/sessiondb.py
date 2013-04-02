'''
Created on 10.11.2012

@author: Nikita Ofitserov
'''

import logging
import time
import uuid

from nfw.expire import AbstractExpiringDict

from sessions.server.session import Session, SessionKey
from sessions.server.common import DatabaseException
from sessions.server.replication.merger import Merger

from twisted.internet.defer import inlineCallbacks

_log = logging.getLogger(__name__)

class SessionList(AbstractExpiringDict):
    @inlineCallbacks
    def expire(self, sessionKey):
        _log.info('Trying to expire')
        s = self[sessionKey]
        now = time.time()
        if s.validUntil > now:
            # Reschedule
            return s
        return None
    
    def ttl(self, sessionKey):
        return max(self[sessionKey].validUntil - time.time(), 0)

class SessionDB(object):
    def __init__(self, serverId, sessionDuration):
        self.serverId = serverId
        self.sessionDuration = sessionDuration
        self.sessions = SessionList()
    
    def requestSession(self, source, destination):
        key = SessionKey(server=self.serverId, uuid=uuid.uuid4())
        now = time.time()
        s = Session(key, now, source, destination, now + self.sessionDuration)
        self.sessions[key] = s
        return s
    
    def validateSession(self, sessionKey, destination):
        try:
            s = self.sessions[sessionKey]
        except KeyError:
            raise DatabaseException("Session {0} not found".format(sessionKey))
        if s.destination != destination:
            raise DatabaseException("Requested destination "
                                    "{0} does not match session "
                                    "{1}".format(destination, s))
        return True

    def merger(self):
        return Merger(self.sessions)


db = None

def setup(serverId):
    global db
    DEFAULT_SESSION_DURATION = 10.0
    db = SessionDB(serverId, DEFAULT_SESSION_DURATION)
