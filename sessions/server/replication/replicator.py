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

from sessions.server import broadcaster, replication
from sessions.server import sessiondb, hostdb

from twisted.internet import reactor
from twisted.internet.endpoints import TCP4ClientEndpoint
from twisted.internet.defer import Deferred, inlineCallbacks

_log = logging.getLogger(__name__)

PeerKey = namedtuple('PeerKey', ['host', 'port'])

class Peer(object):
    def __init__(self, host, port, timestamp):
        self.host = host
        self.port = port
        self.timestamp = timestamp

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

class PeerList(dict, object):
    def __init__(self, connectionMadeCallback=None):
        self.connectionMadeCallback = connectionMadeCallback
        self.expirations = {}
        
    def addPeer(self, peer):
        key = peer.key()
        factory = replication.client.StorageClientFactory()
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
        self.outPeers = PeerList()
        self.sessionMerger = sessiondb.db.merger()
        self.hostMerger = hostdb.db.merger()
        #for peer in broadcaster.peerlist.values():
        #    self.updatePeer(peer)
        broadcaster.peerSeen.subscribe(self.refreshPeer)

    @inlineCallbacks
    def refreshPeer(self, peer):
        if peer.key() in self.outPeers:
            return
        protocol = yield self.outPeers.addPeer(peer)
        (sessionUpdates, hostUpdates) = yield protocol.list()
        sessionUpdates = self.sessionMerger.process(sessionUpdates)
        hostUpdates = self.hostMerger.process(hostUpdates)
        protocol.sendList((sessionUpdates, hostUpdates))

    def addInPeer(self, peer, protocol):
        pass

    @inlineCallbacks
    def updatePeer(self, peer):
        _log.info('Updating peer %s', peer.key())
        client = yield replication.client.connect(peer.endpoint())
        (sessionUpdates, hostUpdates) = yield client.list()
        sessionUpdates = self.sessionMerger.process(sessionUpdates)
        hostUpdates = self.hostMerger.process(hostUpdates)
        client.sendList((sessionUpdates, hostUpdates))
        _log.info('Updated from peer %s', peer.key())

def setup():
    pass