from twisted.internet import reactor, task
from twisted.internet.defer import inlineCallbacks
from twisted.internet.endpoints import TCP4ClientEndpoint

import logging
import socket
import time
from collections import namedtuple

from nfw.protocol import StatefulDatagramProtocol, ProtocolException
from nfw.expire import AbstractExpiringDict
from nfw.event import Event

_log = logging.getLogger(__name__)

TIMEOUT = 6.0

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

    def __init__(self, host, port):
        super(Broadcaster, self).__init__()
        self.host = host
        self.port = port

    def startProtocol(self):
        super(Broadcaster, self).startProtocol()
        # FIXME: How to tell Twisted to set it?
        self.transport.socket.setsockopt(socket.SOL_SOCKET,
                                         socket.SO_BROADCAST, 1)

    def sendDatagram(self):
        "Send DISCOVER_REQ"
        self.writeUInt8(0x00)
        self.send(('<broadcast>', 9999))

    @inlineCallbacks
    def stateMachine(self):
        yield self.receiveDatagram()
        timestamp = long(time.time())
        command = yield self.readUInt8()
        if command == 0x00:
            self.writeUInt8(0x01)
            self.writeString8(self.host)
            self.writeUInt16(self.port)
            self.send(('<broadcast>', 9999))
        elif command == 0x01:
            host = yield self.readString8()
            port = yield self.readUInt16()
            if host == self.host and port == self.port:
                return
            #_log.debug('Saw server %s', (host, port, timestamp))
            peer = Peer(host, port, timestamp)
            peerSeen.fire(peer)
        else:
            raise ProtocolException("Unknown broadcast type: %u" % command)

peerlist = None

'''
Fires on peer discovery
@param peer: the seen peer
'''
peerSeen = Event()

def setup(sessionPort):
    global peerlist
    peerlist = PeerList()
    host = socket.gethostbyname(socket.gethostname())
    br = Broadcaster(host, sessionPort)
    #reactor.listenUDP(9999, br) #@UndefinedVariable
    reactor.listenMulticast(9999, br, listenMultiple=True) #@UndefinedVariable
    l = task.LoopingCall(br.sendDatagram)
    l.start(2.0)
    #l1 = task.LoopingCall(peerlist.output)
    #l1.start(2.0)


