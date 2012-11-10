'''
Created on 08.11.2012

@author: Nikita Ofitserov
'''

from abc import ABCMeta, abstractmethod
import struct
import itertools
import logging

from twisted.internet import defer
from twisted.internet.defer import Deferred
from twisted.internet.protocol import Protocol, DatagramProtocol
from twisted.python import log as txlog

from nfw.buffer import Buffer, ConstBuffer
from nfw.codec import ReaderMixin, WriterMixin

_log = logging.getLogger(__name__)

class StateMixin(object):
    def __init__(self):
        super(StateMixin, self).__init__()
        self.deferred = None
        
    def _startSM(self):
        self.deferred = self.stateMachine()
        if self.deferred is None:
            self.deferred = defer.Deferred()
        self.deferred.addCallbacks(lambda v: self._startSM(), self.protocolError)
    

class BufferedProtocol(WriterMixin, ReaderMixin, object, Protocol):
    def __init__(self):
        super(BufferedProtocol, self).__init__()
        self.buffer = Buffer()
        
    def clearBuffer(self):
        self.buffer.clear()

    def dataReceived(self, data):
        self.buffer.extend(data)
        
    def connectionLost(self, reason):
        self.buffer.clear()

    def writeBytes(self, data):
        self.transport.write(data)
    

class StatefulProtocol(StateMixin, BufferedProtocol):
    __metaclass__ = ABCMeta

    @abstractmethod
    def stateMachine(self):
        return defer.Deferred()

    def protocolError(self, failure):
        txlog.err(failure)
        self.transport.loseConnection()

    def connectionMade(self):
        super(StatefulProtocol, self).connectionMade()
        self._startSM()

    def dataReceived(self, data):
        super(StatefulProtocol, self).dataReceived(data)
        if self.deferred is None:
            self._startSM()
            

class StatefulDatagramProtocol(WriterMixin, ReaderMixin, StateMixin, 
                               DatagramProtocol):
    __metaclass__ = ABCMeta
    
    def __init__(self):
        super(StatefulDatagramProtocol, self).__init__()
        self.datagramDeferred = Deferred()
        self.writeBuffer = bytearray()

    @abstractmethod
    def stateMachine(self):
        return defer.Deferred()

    def protocolError(self, failure):
        txlog.err(failure)

    def datagramReceived(self, data, addr):
        self.buffer = ConstBuffer(data)
        if self.deferred is None:
            self._startSM()
        old_deferred = self.datagramDeferred
        self.datagramDeferred = Deferred()
        old_deferred.callback(addr)

    def receiveDatagram(self):
        return self.datagramDeferred

    def writeBytes(self, data):
        self.writeBuffer.extend(data)

    def writePacked(self, format_, *args):
        offset = len(self.writeBuffer)
        self.writeBuffer.extend(itertools.repeat(0, struct.calcsize(format_)))
        struct.pack_into(format_, self.writeBuffer, offset, *args)

    def send(self, addr=None):
        if _log.isEnabledFor(logging.DEBUG):
            s = str(self.writeBuffer).encode('string_escape')
            _log.debug('Sending %s', s)
        if addr is None:
            self.transport.write(self.writeBuffer)
        else:
            self.transport.write(self.writeBuffer, addr=addr)
        self.writeBuffer = bytearray()
