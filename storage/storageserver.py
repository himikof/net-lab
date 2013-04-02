#-------------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      ofitserov
#
# Created:     13.10.2012
# Copyright:   (c) ofitserov 2012
# Licence:     <your licence>
#-------------------------------------------------------------------------------
#!/usr/bin/env python

from twisted.internet import reactor
from twisted.internet.defer import inlineCallbacks
from twisted.internet.protocol import Factory
from twisted.internet.endpoints import TCP4ServerEndpoint

import struct
import logging

from nfw.protocol import StatefulProtocol
from nfw.util import HexBytes

_log = logging.getLogger(__name__)

class Unpacker(object):
    def __init__(self, dataCallback):
        self.dataCallback = dataCallback
        self.offset = 0

    def tryUnpack(self, fmt):
        data = self.dataCallback()
        nextOffset = self.offset + struct.calcsize(fmt)
        if nextOffset > len(data):
            print "Need %d, got %d" % (nextOffset, len(data))
            return None
        result = struct.unpack_from(fmt, data, self.offset)
        self.offset += struct.calcsize(fmt)
        return result

class StorageProtocol(StatefulProtocol):
    
    def __init__(self, content):
        super(StorageProtocol, self).__init__()
        self.content = content
        
    @inlineCallbacks
    def stateMachine(self):
        command = yield self.readInt32()
        if command == 0:
            _log.info("got LIST")
            files = self.content.files
            self.writeInt32(len(files))
            for binaryHash in files:
                self.writeBinary(binaryHash)
        elif command == 1:
            binaryHash = yield self.readBinary()
            binaryHash = HexBytes(binaryHash)
            _log.info("Got item: %r", binaryHash)
            data = self.content.get(binaryHash)
            if data is None:
                _log.info("Reply FALSE")
                self.writeBoolean(False)
            else:
                _log.info("Reply length: %s", len(data))
                self.writeBoolean(True)
                self.writeBinary(data)
        elif command == 2:
            fileData = yield self.readBinary()
            _log.info("Got item with size %d", len(fileData))
            result = self.content.put(fileData)
            self.writeBoolean(result)
        else:
            raise RuntimeError('Bad command')


class StorageFactory(Factory):
    def __init__(self, content):
        self.content = content

    def buildProtocol(self, addr):
        _log.info("server: accepted from %s", str(addr))
        return StorageProtocol(self.content)

def setup(content):
    factory = StorageFactory(content)
    endpoint = TCP4ServerEndpoint(reactor, 9999)
    endpoint.listen(factory)

if __name__ == '__main__':
    pass
