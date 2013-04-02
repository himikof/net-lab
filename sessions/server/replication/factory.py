'''
Created on 26.03.2013

@author: Nikita Ofitserov
'''

from twisted.internet import defer
from twisted.internet.protocol import Factory
from twisted.internet.defer import Deferred, inlineCallbacks

import binascii
import logging
from functools import partial

from nfw.timeout import timeout
from nfw.protocol import BufferedProtocol

from sessions.server.replication.protocol import ReplicationProtocol

_log = logging.getLogger(__name__)

class ClientFactory(Factory):

    def __init__(self):
        self.connected = Deferred()
        self.protocol = partial(ReplicationProtocol,
                                localServerId, None)
    
    def buildProtocol(self, addr):
        p = Factory.buildProtocol(self, addr)
        _log.debug("Built ReplicationProtocol: %s", p)
        return p

class ServerFactory(Factory):
    def __init__(self, remoteServerId):
        self.content = content
        self.protocol = partial(ReplicationProtocol,
                                localServerId, remoteServerId)


def setup(serverId):
    global localServerId
    localServerId = serverId
