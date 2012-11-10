'''
Created on 08.11.2012

@author: Nikita Ofitserov
'''

import struct

from twisted.internet import defer
from twisted.internet.defer import inlineCallbacks

class ReaderMixin(object):
    def readBytes(self, count):
        return self.buffer.pop(count)
    
    @inlineCallbacks
    def readUnpacked(self, format_):
        length = struct.calcsize(format_)
        data = yield self.readBytes(length)
        defer.returnValue(struct.unpack(format_, buffer(data)))

    def readSingleUnpacked(self, format_):
        return self.readUnpacked(format_).addCallback(lambda (x,): x)

    def readInt32(self):
        return self.readSingleUnpacked('!I')

    def readBoolean(self):
        return self.readSingleUnpacked('!B').addCallback(lambda x: x == 0)

    @inlineCallbacks
    def readBinary(self):
        size = yield self.readInt32()
        data = yield self.readBytes(size)
        defer.returnValue(data)
    
    @inlineCallbacks
    def readString(self, encoding='utf8'):
        data = yield self.readBinary()
        defer.returnValue(data.decode(encoding))


class WriterMixin(object):
    def writePacked(self, format_, *args):
        self.writeBytes(struct.pack(format_, *args))

    def writeInt32(self, number):
        self.writePacked('!I', number)
        
    def writeBinary(self, data):
        self.writeInt32(len(data))
        self.writeBytes(data)
        
    def writeBoolean(self, boolean):
        value = 0 if boolean else 1
        self.writePacked('!B', value)

    def writeString(self, string, encoding='utf8'):
        self.writeBinary(string.encode(encoding))
