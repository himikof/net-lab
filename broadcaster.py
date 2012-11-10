from twisted.internet import reactor, task
from twisted.internet.defer import inlineCallbacks
from twisted.internet.endpoints import TCP4ClientEndpoint

import logging
import socket
import time
import binascii

from nfw.protocol import StatefulDatagramProtocol
from nfw.expire import AbstractExpiringDict
from nfw.event import Event
from collections import namedtuple

_log = logging.getLogger(__name__)

TIMEOUT = 6.0

PeerKey = namedtuple('PeerKey', ['ip', 'cname'])

class Peer(object):
    def __init__(self, ip, cname, timestamp, cid):
        self.ip = ip
        self.cname = cname
        self.timestamp = timestamp
        self.cid = cid

    def key(self):
        return PeerKey(self.ip, self.cname)

    def data(self):
        d = self.__dict__.copy()
        d['timestamp'] = time.asctime(time.localtime(self.timestamp))
        d['cid'] = binascii.hexlify(d['cid'])
        return d

    def endpoint(self):
        return TCP4ClientEndpoint(reactor, self.ip, 9999)

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
    
    def __init__(self, peerlist, content):
        super(Broadcaster, self).__init__()
        self.peerlist = peerlist
        self.content = content
        self.ip = socket.gethostbyname(socket.gethostname())

    def startProtocol(self):
        super(Broadcaster, self).startProtocol()
        self.transport.socket.setsockopt(socket.SOL_SOCKET,
                                         socket.SO_BROADCAST, 1)
    
    def sendDatagram(self):
        cname = socket.gethostname().encode('utf8')
        ip = self.ip
        cid = self.content.getContentId()
        self.writeString(ip)
        self.writeString(cname)
        self.writeBinary(cid)
        self.send(('<broadcast>', 9999))

    @inlineCallbacks
    def stateMachine(self):
        yield self.receiveDatagram()
        timestamp = long(time.time())
        ip = yield self.readString()
        cname = yield self.readString()
        cid = yield self.readBinary()
        #send_time = time.asctime(time.localtime(timestamp))
        _log.debug('Saw %s', (ip, cname, timestamp, cid))
        peer = Peer(ip, cname, timestamp, cid)
        key = peer.key()
        if key not in self.peerlist or self.peerlist[key].cid != peer.cid:
            peerUpdated.fire(peer)
        self.peerlist[peer.key()] = peer

peerlist = None

'''
Fires on ContentID change
@param peer: the changed peer
'''
peerUpdated = Event()

def setup(content):
    global peerlist
    peerlist = PeerList()
    _log.info('cname = %s', socket.gethostname())
    br = Broadcaster(peerlist, content)
    reactor.listenUDP(9999, br) #@UndefinedVariable
    l = task.LoopingCall(br.sendDatagram)
    l.start(2.0)
    #l1 = task.LoopingCall(peerlist.output)
    #l1.start(2.0)


