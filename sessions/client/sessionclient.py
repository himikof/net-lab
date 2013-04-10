'''
Created on 10.04.2013

'''

import logging

from twisted.internet import protocol, defer
from twisted.internet.defer import Deferred, inlineCallbacks

from nfw.timeout import timeout
from nfw.protocol import BufferedProtocol, ProtocolException

_log = logging.getLogger(__name__)

class SessionClient(BufferedProtocol):
    """Once connected, send a message."""
    
    def connectionMade(self):
        self.factory.connected.callback(self)
        
    @inlineCallbacks
    def requestSession(self, dest_addr):
        _log.debug("Requesting session to %s", dest_addr)
        self.writeUInt8(0x00)
        self.writeString8(cname)
        self.writeString8(dest_addr)
        result = yield self.readUInt8()
        if result == 0x00:
            _log.debug("Got SESSION_ACK")
            sid = yield self.readBinary8()
            dest_addr_r = yield self.readString8()
            if dest_addr_r != dest_addr:
                raise ProtocolException("Invalid reply ID")
            defer.returnValue(sid)
        elif result == 0x01:
            _log.debug("Got SESSION_REJ")
            dest_addr_r = yield self.readString8()
            if dest_addr_r != dest_addr:
                raise ProtocolException("Invalid reply ID")
            defer.returnValue(None)
        else:
            raise ProtocolException("Invalid reply")

    @inlineCallbacks
    def verifySession(self, sid):
        _log.debug("Verifying session %s", sid)
        self.writeUInt8(0x01)
        self.writeBinary8(sid)
        self.writeString8(cname)
        result = yield self.readUInt8()
        if result == 0x02:
            _log.debug("Got SESSION_VALID")
            sid_r = yield self.readBinary8()
            if sid_r != sid:
                raise ProtocolException("Invalid reply ID")
            defer.returnValue(True)
        elif result == 0x03:
            _log.debug("Got SESSION_FAIL")
            sid_r = yield self.readBinary8()
            if sid_r != sid:
                raise ProtocolException("Invalid reply ID")
            defer.returnValue(False)
        else:
            raise ProtocolException("Invalid reply")
                

    def disconnect(self):
        self.transport.loseConnection()


class SessionClientFactory(protocol.Factory):
    protocol = SessionClient
    
    def __init__(self):
        self.connected = Deferred()


@timeout(5)
def connect(endpoint):
    _log.info("Connecting to server %s:%s", endpoint._host, endpoint._port)
    factory = SessionClientFactory()
    attempt = endpoint.connect(factory) #@UnusedVariable
    return factory.connected

cname = None

def setup(computer_name):
    _log.info('cname = %s', computer_name)
    global cname
    cname = computer_name
