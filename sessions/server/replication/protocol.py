'''
Created on 26.03.2013

@author: Nikita Ofitserov
'''

from twisted.internet.defer import Deferred, inlineCallbacks
from twisted.internet.protocol import Factory

import logging

from nfw.protocol import StatefulProtocol, ProtocolException, SignalingMixin
from nfw.util import HexBytes
from nfw.event import Event
from nfw.timeout import timeout

import sessions.server.ServerReplication_pb2 as pb2

_log = logging.getLogger(__name__)

class ReplicationProtocol(SignalingMixin, StatefulProtocol):

    def __init__(self, localServerId, remoteServerId):
        super(ReplicationProtocol, self).__init__()
        _log.debug("Constructed")
        self._localServerId = localServerId
        self._remoteServerId = remoteServerId
        self._remoteServerIdD = Deferred()
        self.onUpdate = Event()
        self.onListRequest = Event()
        if self._remoteServerId:
            self._remoteServerIdD.callback(self._remoteServerId)

    @timeout()
    @inlineCallbacks
    def announce(self):
        _log.info('Announcing serverId to %s', self.transport.getPeer())
        self.writeUInt8(0x02)
        self.writeString8(self._localServerId)
        reply = yield self.readUInt8()
        if reply != 0x04:
            raise ProtocolException("Invalid reply to SERVER_ID")
        self._remoteServerId = yield self.readString8()
        self._remoteServerIdD.callback(self._remoteServerId)

    @timeout()
    def list(self):
        self.writeUInt8(0xF0)
        keys = pb2.List()
        data = keys.SerializeToString()
        _log.debug('Requesting LIST: data=%s', data)
        self.writeBinary16(data)
        return self.onUpdate.waitFor1()

    def sendUpdates(self, (sessionUpdates, hostUpdates)):
        updatesList = pb2.List()
        updatesList.hosts.extend(hostUpdates)
        updatesList.sessions.extend(sessionUpdates)
        data = updatesList.SerializeToString()
        self.writeUInt8(0xF1)
        self.writeBinary16(data)

    def connectionLost(self, reason):
        if not self.stateMachineStopped:
            _log.info("Connection to %s lost", self.transport.getPeer())
        super(ReplicationProtocol, self).connectionLost(reason)

    def connectionMade(self):
        _log.info('Starting replication protocol on %s',
                  self.transport.getPeer())
        super(ReplicationProtocol, self).connectionMade()

    @inlineCallbacks
    def stateMachine(self):
        if not self._remoteServerId:
            yield self.announce()
        command = yield self.readUInt8()
        if command == 0xF0:
            _log.info("got LIST_REQUEST")
            data = yield self.readBinary16()
            updates = pb2.List()
            updates.ParseFromString(str(data))
            self.onListRequest.fire(self, (updates.sessions, updates.hosts))
            # TODO: implement
        elif command == 0xF1:
            #_log.info("got LIST_UPDATES")
            data = yield self.readBinary16()
            updates = pb2.List()
            updates.ParseFromString(str(data))
            self.onUpdate.fire((updates.sessions, updates.hosts))
        else:
            raise RuntimeError('Bad command')

    def remoteServerId(self):
        return self._remoteServerIdD
