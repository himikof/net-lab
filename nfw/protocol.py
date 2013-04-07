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

from nfw.buffer import Buffer, ConstBuffer, BufferClearedException
from nfw.codec import ReaderMixin, WriterMixin
from nfw.event import Event

_log = logging.getLogger(__name__)

class ProtocolException(Exception):
    pass

class StateMixin(object):
    def __init__(self):
        super(StateMixin, self).__init__()
        self.deferred = None
        self.stateMachineStopped = False

    def _startSM(self):
        if self.stateMachineStopped:
            return
        self.deferred = self.stateMachine()
        if self.deferred is None:
            self.deferred = defer.Deferred()
        self.deferred.addCallbacks(lambda v: self._startSM(), self.protocolError)

    def _stopSM(self):
        self.stateMachineStopped = True


class BufferMixin(object):
    def __init__(self):
        self.buffer = Buffer()

    def clearBuffer(self):
        self.buffer.clear()

    def flushBuffer(self):
        return self.buffer.flush()


class SwitchingMixin(BufferMixin):
    def __init__(self):
        super(SwitchingMixin, self).__init__()
        self.nestedProtocol = None

    def _switchProtocol(self, nestedProtocolFactory):
        self.nestedProtocol = nestedProtocolFactory.\
            buildProtocol(self.transport.getPeer())
        _log.info('Switching protocol to %s', self.nestedProtocol)
        newData = self.flushBuffer()
        self.nestedProtocol.makeConnection(self.transport)
        if len(newData):
            self.nestedProtocol.dataReceived(newData)


class SignalingMixin(object):
    def __init__(self, *args, **kwargs):
        super(SignalingMixin, self).__init__(*args, **kwargs)
        self.dataEvent = Event()
        self.disconnectEvent = Event()
        self.connectEvent = Event()

    def dataReceived(self, data):
        self.dataEvent.fire(data)
        super(SignalingMixin, self).dataReceived(data)

    def connectionLost(self, reason):
        self.disconnectEvent.fire(reason)
        super(SignalingMixin, self).connectionLost(reason)

    def connectionMade(self):
        self.connectEvent.fire()
        super(SignalingMixin, self).connectionMade()


class BufferedProtocol(BufferMixin, WriterMixin, ReaderMixin, object, Protocol):
    def __init__(self):
        super(BufferedProtocol, self).__init__()

    def dataReceived(self, data):
        self.buffer.extend(data)

    def connectionLost(self, reason):
        self.clearBuffer()

    def readBytes(self, count):
        return self.buffer.pop(count)

    def writeBytes(self, data):
        self.transport.write(data)


class StatefulProtocol(StateMixin, BufferedProtocol):
    __metaclass__ = ABCMeta

    @abstractmethod
    def stateMachine(self):
        return defer.Deferred()

    def protocolError(self, failure):
        _log.info('protocolError:' + str(failure))
        if not failure.check('twisted.python.failure.DefaultException'):
            #import pdb; pdb.set_trace()
            txlog.err(failure)
        self.disconnect()

    def disconnect(self):
        self.transport.loseConnection()
        self._stopSM()

    def connectionLost(self, reason):
        self._stopSM()
        super(StatefulProtocol, self).connectionLost(reason)

    def connectionMade(self):
        super(StatefulProtocol, self).connectionMade()
        self._startSM()

    def dataReceived(self, data):
        super(StatefulProtocol, self).dataReceived(data)
        if self.deferred is None:
            self._startSM()


class StatefulSwitchingProtocol(SwitchingMixin, StatefulProtocol):
    def connectionMade(self):
        if self.nestedProtocol is not None:
            return self.nestedProtocol.connectionMade()
        super(StatefulSwitchingProtocol, self).connectionMade()
        #self._startSM()

    def connectionLost(self, reason):
        if self.nestedProtocol is not None:
            return self.nestedProtocol.connectionLost(reason)
        super(StatefulSwitchingProtocol, self).connectionLost(reason)

    def dataReceived(self, data):
        if self.nestedProtocol is not None:
            return self.nestedProtocol.dataReceived(data)
        super(StatefulSwitchingProtocol, self).dataReceived(data)
        if self.deferred is None:
            self._startSM()

    def switchProtocol(self, nestedProtocolFactory):
        self._stopSM()
        self._switchProtocol(nestedProtocolFactory)


class StatefulDatagramProtocol(WriterMixin, ReaderMixin, StateMixin,
                               object, DatagramProtocol):
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

    def readBytes(self, count):
        return self.buffer.pop(count)

    def writeBytes(self, data):
        self.writeBuffer.extend(data)

    def writePacked(self, format_, *args):
        offset = len(self.writeBuffer)
        self.writeBuffer.extend(itertools.repeat(0, struct.calcsize(format_)))
        struct.pack_into(format_, self.writeBuffer, offset, *args)

    def send(self, addr=None):
        #if _log.isEnabledFor(logging.DEBUG):
        #    s = str(self.writeBuffer).encode('string_escape')
        #    _log.debug('Sending %s', s)
        if addr is None:
            self.transport.write(self.writeBuffer)
        else:
            self.transport.write(self.writeBuffer, addr=addr)
        self.writeBuffer = bytearray()
