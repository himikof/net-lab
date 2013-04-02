'''
Created on 26.03.2013

@author: Nikita Ofitserov
'''

from twisted.internet import reactor
from twisted.internet.defer import inlineCallbacks
from twisted.internet.protocol import Factory
from twisted.internet.endpoints import TCP4ServerEndpoint

import logging

from nfw.protocol import StatefulSwitchingProtocol

from sessions.server.session import parseKey
from sessions.server import hostdb, sessiondb
from sessions.server import replication

_log = logging.getLogger(__name__)

class ServerProtocol(StatefulSwitchingProtocol):
    
    def __init__(self, sessiondb, hostdb):
        super(ServerProtocol, self).__init__()
        self.sessiondb = sessiondb
        self.hostdb = hostdb
        
    @inlineCallbacks
    def stateMachine(self):
        command = yield self.readUInt8()
        if command == 0x00:
            try:
                _log.info("got SESSION_REQUEST")
                src_ip = self.transport.getPeer().host
                src_cname = yield self.readString8()
                dest_ip = yield self.readString8()
                source = self.hostdb.validateHost(src_ip, src_cname)
                destination = self.hostdb.validateHost(dest_ip)
                session = self.sessiondb.requestSession(source, destination)
            except Exception:
                _log.info("sending SESSION_REJ")
                self.writeUInt8(0x01)
                self.writeString8(dest_ip)
            else:
                _log.info("sending SESSION_ACK")
                self.writeUInt8(0x00)
                self.writeBinary8(session.binaryKey())
                self.writeString8(dest_ip)
        elif command == 0x01:
            try:
                _log.info("got SESSION_CHECK")
                sid = yield self.readBinary8()
                dest_ip = self.transport.getPeer().host
                dest_cname = yield self.readString8()
                destination = self.hostdb.validateHost(dest_ip, dest_cname)
                sessionKey = parseKey(sid)
                self.sessiondb.validateSession(sessionKey, destination)
            except Exception:
                _log.info("sending SESSION_FAIL")
                self.writeUInt8(0x03)
                self.writeBinary8(sid)
            else:
                _log.info("sending SESSION_VALID")
                self.writeUInt8(0x02)
                self.writeBinary8(sid)
        elif command == 0x2:
            _log.info("got SERVER_ID, upgrading to s2s")
            # TODO: implement
            serverId = yield self.readString8()
            self.switchProtocol(replication.server.serverFactory)
            # Nothing should be done here, after the switch
        else:
            raise RuntimeError('Bad command')


class ProtocolFactory(Factory):
    def __init__(self):
        pass

    def buildProtocol(self, addr):
        _log.info("server: accepted from %s", str(addr))
        return ServerProtocol(sessiondb.db, hostdb.db)

def setup(port):
    factory = ProtocolFactory()
    endpoint = TCP4ServerEndpoint(reactor, port)
    endpoint.listen(factory)

