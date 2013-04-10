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
from sessions.server.replication import factory as rf
from sessions.server.replication import replicator
from sessions.server.common import DatabaseException

_log = logging.getLogger(__name__)

class ServerProtocol(StatefulSwitchingProtocol):

    def __init__(self, sessiondb, hostdb):
        super(ServerProtocol, self).__init__()
        self.sessiondb = sessiondb
        self.hostdb = hostdb

    @inlineCallbacks
    def stateMachine(self):
        _log.debug("ENTERING SM: %s", self.transport.getPeer())
        command = yield self.readUInt8()
        #import pdb; pdb.set_trace()
        if command == 0x00:
            _log.info("got SESSION_REQUEST: buffer=%s", self.buffer.data)
            src_ip = self.transport.getPeer().host
            _log.info("SESSION_REQUEST: src_ip=%s", src_ip)
            src_cname = yield self.readString8()
            dest_ip = yield self.readString8()
            _log.info("SESSION_REQUEST: dest_ip=%s, src_cname=%s", dest_ip, src_cname)
            try:
                source = self.hostdb.validateHost(src_ip, src_cname)
                destination = self.hostdb.queryHost(dest_ip)
                session = self.sessiondb.requestSession(source, destination)
            except Exception:
                _log.error("Error", exc_info=1)
                _log.info("sending SESSION_REJ")
                self.writeUInt8(0x01)
                self.writeString8(dest_ip)
            else:
                _log.info("sending SESSION_ACK")
                self.writeUInt8(0x00)
                self.writeBinary8(session.binaryKey())
                self.writeString8(dest_ip)
        elif command == 0x01:
            _log.info("got SESSION_CHECK")
            sid = yield self.readBinary8()
            dest_ip = self.transport.getPeer().host
            dest_cname = yield self.readString8()
            try:
                destination = self.hostdb.validateHost(dest_ip, dest_cname)
                sessionKey = parseKey(str(sid))
                try:
                    self.sessiondb.validateSession(sessionKey, destination)
                except DatabaseException:
                    if sessionKey.server == self.sessiondb.serverId:
                        raise
                    _log.info("Retrying with refresh...")
                    yield replicator.replicator.refreshServer(sessionKey.server)
                    self.sessiondb.validateSession(sessionKey, destination)
            except Exception:
                _log.error("Error", exc_info=1)
                _log.info("sending SESSION_FAIL")
                self.writeUInt8(0x03)
                self.writeBinary8(sid)
            else:
                _log.info("sending SESSION_VALID")
                self.writeUInt8(0x02)
                self.writeBinary8(sid)
        elif command == 0x02:
            _log.info("got SERVER_ID, upgrading to s2s")
            # TODO: implement
            serverId = yield self.readString8()
            self.switchProtocol(rf.ServerFactory(serverId))
            # Nothing should be done here, after the switch
        elif command == 0x03:
            _log.info("got SERVER_ADMIN_CS, disconnecting client")
            self.disconnect()
            #_log.info("buffer: %s", self.buffer.requests)
            #import pdb; pdb.set_trace()
        else:
            #import pdb; pdb.set_trace()
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

