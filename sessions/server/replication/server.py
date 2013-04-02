'''
Created on 26.03.2013

@author: Nikita Ofitserov
'''

from twisted.internet.defer import inlineCallbacks
from twisted.internet.protocol import Factory

import logging

from nfw.protocol import StatefulProtocol
from nfw.util import HexBytes

_log = logging.getLogger(__name__)

class ServerProtocol(StatefulProtocol):
    
    def __init__(self, content):
        super(ServerProtocol, self).__init__()
        self.content = content
        
    @inlineCallbacks
    def stateMachine(self):
        command = yield self.readInt32()
        if command == 0x00:
            _log.info("got LIST_REQUEST")
            # TODO: implement
        elif command == 0x01:
            _log.info("got LIST_UPDATES")
            # TODO: implement
        else:
            raise RuntimeError('Bad command')


class ServerProtocolFactory(Factory):
    def __init__(self, content):
        self.content = content

    def buildProtocol(self, addr):
        _log.info("server: accepted from %s", str(addr))
        return ServerProtocol(self.content)

serverFactory = None

def setup(content):
    global serverFactory
    serverFactory = ServerProtocolFactory(content)

