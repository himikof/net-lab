'''
Created on 26.03.2013

@author: Nikita Ofitserov
'''

import logging
import time
from collections import namedtuple

from nfw.expire import AbstractExpiringDict
from nfw.event import Event
from nfw.reconnect import PersistentClientService

from sessions.server import broadcaster
from sessions.server import sessiondb, hostdb
from sessions.server.replication.factory import ClientFactory
from sessions.server.ServerReplication_pb2 import List

from twisted.internet import reactor
from twisted.internet.endpoints import TCP4ClientEndpoint
from twisted.internet.defer import Deferred, inlineCallbacks

_log = logging.getLogger(__name__)

PeerKey = namedtuple('PeerKey', ['host', 'port'])

class Peer(object):
    def __init__(self, host, port, timestamp, serverId=None):
        self.host = host
        self.port = port
        self.timestamp = timestamp
        self.serverId = serverId

    def key(self):
        return PeerKey(self.host, self.port)

    def data(self):
        d = self.__dict__.copy()
        d['timestamp'] = time.asctime(time.localtime(self.timestamp))
        return d

    def endpoint(self):
        return TCP4ClientEndpoint(reactor, self.host, self.port)

    def __str__(self):
        return str(self.data())


PEER_FORGET_DELAY = 15.0

class OutPeerList(dict, object):
    def __init__(self, connectionMadeCallback=None):
        self.connectionMadeCallback = connectionMadeCallback
        self.expirations = {}

    def addPeer(self, peer):
        key = peer.key()
        factory = ClientFactory()
        def _onConnectionLost(reason):
            self.peerConnectionLost(peer)
        def _onConnectionMade():
            self.expirations.pop(key).cancel()
            if self.connectionMadeCallback:
                self.connectionMadeCallback()
        service = PersistentClientService(
             peer.endpoint(), factory, reactor,
             connectionLostCallback=_onConnectionLost)
        self[key] = service
        service.startService()
        return service.connectedProtocol()

    def _peerScheduleExpiration(self, peer):
        key = peer.key()
        def _expirePeer():
            service = self.pop(key)
            service.stopService()
            del self.expirations[key]
        dc = reactor.callLater(PEER_FORGET_DELAY, #@UndefinedVariable
                               _expirePeer)
        self.expirations[key] = dc

    def peerConnectionLost(self, peer):
        self._peerScheduleExpiration(peer)

    def peerProtocol(self, peer):
        return self[peer.key()].connectedProtocol()


class Replicator(object):
    def __init__(self):
        self.outPeers = OutPeerList()
        self.inPeers = {}
        self.peers = {}
        self.sessionMerger = sessiondb.db.merger()
        self.hostMerger = hostdb.db.merger()
        #for peer in broadcaster.peerlist.values():
        #    self.updatePeer(peer)
        broadcaster.peerSeen.subscribe(self.connectToPeer)

    @inlineCallbacks
    def registerProtocol(self, protocol):
        serverId = yield protocol.remoteServerId()
        if serverId not in self.peers:
            self.peers[serverId] = set()
        self.peers[serverId].add(protocol)
        def onDisconnect(reason):
            self.peers[serverId].remove(protocol)
            if not self.peers[serverId]:
                del self.peers[serverId]
        protocol.disconnectEvent.subscribe(onDisconnect)
        protocol.onUpdate.subscribe(self.processUpdates)
        protocol.onListRequest.subscribe(self.processList)
        self.refresh(protocol)

    def addIncomingPeer(self, peer, protocol):
        serverId = peer.serverId
        if serverId is None:
            raise ValueError("Unknown serverId on incoming peer")
        def onDisconnect(reason):
            del self.inPeers[protocol]
        protocol.disconnectEvent.subscribe(onDisconnect)
        self.inPeers[protocol] = peer
        self.registerProtocol(protocol)

    @inlineCallbacks
    def refresh(self, protocol):
        _log.info("Sending refresh request now...")
        #return
        yield protocol.list()

    def sendUpdates(self, updates):
        for ps in self.peers.itervalues():
            chosen_one = next(iter(ps))
            chosen_one.sendUpdates(updates)

    def processUpdates(self, updates):
        _log.debug("Processing updates...")
        (sessionUpdates, hostUpdates) = updates
        sessionUpdates = self.sessionMerger.process(sessionUpdates)
        hostUpdates = self.hostMerger.process(hostUpdates)
        self.sendUpdates((sessionUpdates, hostUpdates))

    def processList(self, protocol, keys):
        _log.debug("Processing list request...")
        (sessionKeys, hostKeys) = keys
        sessionUpdates = self.sessionMerger.list(sessionKeys)
        hostUpdates = self.hostMerger.list(hostKeys)
        protocol.sendUpdates((sessionUpdates, hostUpdates))

    @inlineCallbacks
    def connectToPeer(self, peer):
        if peer.key() in self.outPeers:
            return
        _log.info('Connecting to peer %s', peer.key())
        protocol = yield self.outPeers.addPeer(peer)
        self.registerProtocol(protocol)
        _log.info('Outgoing peer %s ready', peer.key())

replicator = None

def setup():
    global replicator
    replicator = Replicator()