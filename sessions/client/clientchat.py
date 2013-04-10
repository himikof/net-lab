'''
Created on 10.04.2013

'''

import logging
import socket

from twisted.internet import protocol, reactor
from twisted.internet.defer import Deferred, inlineCallbacks
from twisted.internet.endpoints import TCP4ServerEndpoint

from nfw.event import Event
from nfw.timeout import timeout
from nfw.protocol import BufferedProtocol, StatefulProtocol

_log = logging.getLogger(__name__)

class MessagingClient(BufferedProtocol):
    """Once connected, send a message."""
    
    def connectionMade(self):
        self.factory.connected.callback(self)
        
    def sendMessage(self, sid, data):
        self.writeUInt8(0xFF)
        self.writeBinary8(sid)
        self.writeBinary16(data)

    def disconnect(self):
        self.transport.loseConnection()


class MessagingClientFactory(protocol.Factory):
    protocol = MessagingClient
    
    def __init__(self):
        self.connected = Deferred()


@timeout(5)
def connect(endpoint):
    _log.info("Connecting to %s:%s", endpoint._host, endpoint._port)
    factory = MessagingClientFactory()
    attempt = endpoint.connect(factory) #@UnusedVariable
    return factory.connected

class MessagingServer(StatefulProtocol):
    @inlineCallbacks
    def stateMachine(self):
        command = yield self.readUInt8()
        #import pdb; pdb.set_trace()
        if command == 0xFF:
            src_ip = self.transport.getPeer().host
            _log.info("MESSAGE: src_ip=%s", src_ip)
            sid = yield self.readBinary8()
            _log.info("MESSAGE: sid=%s", sid)
            data = yield self.readBinary16()
            _log.info("MESSAGE: len(data)=%s", len(data))
            incoming.fire((sid, data))
        else:
            raise RuntimeError('Bad command')

class MessagingServerFactory(protocol.Factory):
    protocol = MessagingServer
    def __init__(self):
        pass

incoming = None

def setup(clientPort):
    global incoming
    incoming = Event()
    factory = MessagingServerFactory()
    endpoint = TCP4ServerEndpoint(reactor, clientPort)
    endpoint.listen(factory)
