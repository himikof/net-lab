from twisted.internet import reactor, task
from twisted.internet.defer import inlineCallbacks
from twisted.internet.endpoints import TCP4ClientEndpoint

import logging
import socket
import time

from nfw.protocol import StatefulDatagramProtocol, ProtocolException
from nfw.expire import AbstractExpiringDict
from collections import namedtuple

_log = logging.getLogger(__name__)

TIMEOUT = 6.0

PeerKey = namedtuple('PeerKey', ['host', 'port'])

class Peer(object):
    def __init__(self, host, port, isServer, timestamp):
        self.host = host
        self.port = port
        self.isServer = isServer
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


class PeerList(AbstractExpiringDict):
    def expire(self, key):
        _log.info('Expiring %s', key)
        pass
    
    def ttl(self, key):
        return TIMEOUT
    
    def output(self):
        print '====================='
        for p in self.values():
            print p
            
    def jsonData(self):
        return [p.data() for p in self.values()]


class Broadcaster(StatefulDatagramProtocol):
    
    def __init__(self, peerlist, port):
        super(Broadcaster, self).__init__()
        self.peerlist = peerlist
        self.port = port

    def startProtocol(self):
        super(Broadcaster, self).startProtocol()
        self.transport.socket.setsockopt(socket.SOL_SOCKET,
                                         socket.SO_BROADCAST, 1)
    
    def sendDatagram(self):
        "Send DISCOVER_REQ"
        self.writeUInt8(0x00)
        self.send(('<broadcast>', 9999))

    @inlineCallbacks
    def stateMachine(self):
        source_host, _ = yield self.receiveDatagram()
        timestamp = long(time.time())
        command = yield self.readUInt8()
        if command == 0x00:
            # Maybe it is a client? Unsound, actually...
            peer = Peer(source_host, self.port, False, timestamp)
            key = peer.key()
            if key in self.peerlist:
                old_peer = self.peerlist[key]
                if old_peer.isServer:
                    return
            self.peerlist[key] = peer
        elif command == 0x01:
            host = yield self.readString8()
            port = yield self.readUInt16()
            #_log.debug('Saw server %s', (host, port, timestamp))
            peer = Peer(host, port, True, timestamp)
            self.peerlist[peer.key()] = peer
        else:
            raise ProtocolException("Unknown broadcast type: %u" % command)

peerlist = None


def setup(clientPort):
    global peerlist
    peerlist = PeerList()
    _log.info('client_ip = %s', socket.gethostbyname(socket.gethostname()))
    br = Broadcaster(peerlist, clientPort)
    reactor.listenMulticast(9999, br, listenMultiple=True) #@UndefinedVariable
    l = task.LoopingCall(br.sendDatagram)
    l.start(3.0)
    #l1 = task.LoopingCall(peerlist.output)
    #l1.start(10.0)


