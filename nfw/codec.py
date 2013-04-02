'''
Created on 08.11.2012

@author: Nikita Ofitserov
'''

import struct

from twisted.internet import defer
from twisted.internet.defer import inlineCallbacks

class ReaderMixin(object):
    @inlineCallbacks
    def readUnpacked(self, format_):
        length = struct.calcsize(format_)
        data = yield self.readBytes(length)
        defer.returnValue(struct.unpack(format_, buffer(data)))

    def readSingleUnpacked(self, format_):
        return self.readUnpacked(format_).addCallback(lambda (x,): x)

    def readUInt32(self):
        return self.readSingleUnpacked('!I')

    def readUInt16(self):
        return self.readSingleUnpacked('!H')

    def readUInt8(self):
        return self.readSingleUnpacked('!B')

    def readBoolean(self):
        return self.readUInt8().addCallback(lambda x: x == 0)

    @inlineCallbacks
    def readBinary(self, sizeReader):
        size = yield sizeReader()
        data = yield self.readBytes(size)
        defer.returnValue(data)
    
    @inlineCallbacks
    def readString(self, sizeReader, encoding='utf8'):
        data = yield self.readBinary(sizeReader)
        defer.returnValue(data.decode(encoding))

    def readBinary8(self):
        return self.readBinary(self.readUInt8)

    def readBinary16(self):
        return self.readBinary(self.readUInt16)
    
    def readString8(self, encoding='utf8'):
        return self.readString(self.readUInt8, encoding)
    
    def readString16(self, encoding='utf8'):
        return self.readString(self.readUInt16, encoding)


class WriterMixin(object):
    def writePacked(self, format_, *args):
        self.writeBytes(struct.pack(format_, *args))

    def writeUInt8(self, number):
        self.writePacked('!B', number)

    def writeUInt16(self, number):
        self.writePacked('!H', number)
    
    def writeUInt32(self, number):
        self.writePacked('!I', number)
        
    def writeBinary(self, sizeWriter, data):
        sizeWriter(len(data))
        self.writeBytes(data)
        
    def writeBoolean(self, boolean):
        value = 0 if boolean else 1
        self.writePacked('!B', value)

    def writeString(self, sizeWriter, string, encoding='utf8'):
        self.writeBinary(sizeWriter, string.encode(encoding))
        
    def writeBinary8(self, data):
        self.writeBinary(self.writeUInt8, data)

    def writeBinary16(self, data):
        self.writeBinary(self.writeUInt8, data)

    def writeString8(self, string, encoding='utf8'):
        self.writeString(self.writeUInt8, string, encoding)
    
    def writeString16(self, string, encoding='utf8'):
        self.writeString(self.writeUInt16, string, encoding)
