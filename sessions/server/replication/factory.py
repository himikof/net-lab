'''
Created on 26.03.2013

@author: Nikita Ofitserov
'''

from twisted.internet.protocol import Factory
from twisted.internet.defer import Deferred

import logging
from functools import partial

from sessions.server.replication.protocol import ReplicationProtocol

_log = logging.getLogger(__name__)

class ClientFactory(Factory):
    noisy = False

    def __init__(self):
        self.connected = Deferred()
        self.protocol = partial(ReplicationProtocol,
                                localServerId, None)


class ServerFactory(Factory):
    def __init__(self, remoteServerId):
        self.protocol = partial(ReplicationProtocol,
                                localServerId, remoteServerId)


def setup(serverId):
    global localServerId
    localServerId = serverId
