'''
Created on 26.03.2013

@author: Nikita Ofitserov
'''

from twisted.internet import defer
from twisted.internet.protocol import Factory
from twisted.internet.defer import Deferred, inlineCallbacks

import binascii
import logging

from nfw.timeout import timeout
from nfw.protocol import BufferedProtocol

_log = logging.getLogger(__name__)

class RequestFailed(Exception):
    pass

class StorageClient(BufferedProtocol):

    def connectionMade(self):
        _log.info("Connection made")
        super(StorageClient, self).connectionMade()
        self.factory.connected.callback(self)

    @timeout()
    @inlineCallbacks
    def list(self):
        raise NotImplementedError()
        self.clearBuffer()
        self.writeInt32(0)
        count = yield self.readInt32()
        items = []
        for _ in range(count):
            item = yield self.readBinary()
            _log.info("Got list item: %s" % binascii.hexlify(item))
            items.append(bytes(item))
        defer.returnValue(items)

    @inlineCallbacks
    def sendList(self, updates):
        raise NotImplementedError()
        self.clearBuffer()
        self.writeInt32(1)
        self.writeBinary(updates)
        success = yield self.readBoolean()
        if success:
            data = yield self.readBinary()
            _log.info("Got item with size %d" % len(data))
            defer.returnValue(data)
        else:
            raise RequestFailed()


class StorageClientFactory(Factory):

    def __init__(self):
        self.connected = Deferred()

    def buildProtocol(self, addr):
        p = StorageClient()
        p.factory = self
        _log.info("Protocol built")
        return p

@timeout(5)
def connect(endpoint):
    _log.info("Connecting to %s:%s", endpoint._host, endpoint._port)
    factory = StorageClientFactory()
    attempt = endpoint.connect(factory) #@UnusedVariable
    #reactor.callLater(5, attempt.cancel)
    #attempt.addErrback(d.errback)
    return factory.connected

