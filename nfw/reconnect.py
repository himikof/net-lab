'''
Created on 27.03.2013

@author: Nikita Ofitserov
'''

import logging

from twisted.application import service
from twisted.internet import defer
from twisted.protocols.policies import ProtocolWrapper, WrappingFactory

from nfw.protocol import SignalingMixin

_log = logging.getLogger(__name__)

class SignalingProtocol(SignalingMixin, object, ProtocolWrapper):
    def __init__(self, factory, wrappedProtocol):
        super(SignalingProtocol, self).__init__()
        ProtocolWrapper.__init__(self, factory, wrappedProtocol)
        
    def __getattr__(self, name):
        return getattr(self.wrappedProtocol, name)
        
#    def connectionMade(self):
#        ProtocolWrapper.connectionMade(self)
#        if self.factory.onConnectionMade:
#            self.factory.onConnectionMade()
#
#    def connectionLost(self, reason):
#        ProtocolWrapper.connectionLost(self, reason)
#        if self.factory.onConnectionLost:
#            self.factory.onConnectionLost(reason)


class SignalingFactory(WrappingFactory):
#        def __init__(self, wrappedFactory, onConnectionMade,
#                     onConnectionLost):
#            WrappingFactory.__init__(self, wrappedFactory)
#            self.onConnectionMade = onConnectionMade
#            self.onConnectionLost = onConnectionLost
    
    protocol = SignalingProtocol
        
    def buildProtocol(self, addr):
        p = WrappingFactory.buildProtocol(self, addr)
        _log.debug("Built SignalingProtocol: %s", p)
        return p


class PersistentClientService(service.Service):
    """
    A L{PersistentClientService} is an L{service.IService} which keeps a
    connection to a L{IStreamClientEndpoint}, restarting the client when the
    connection is lost.

    @ivar factory: A L{protocol.Factory} which will be used to create clients
        for the endpoint.

    @ivar endpoint: An L{IStreamClientEndpoint
        <twisted.internet.interfaces.IStreamClientEndpoint>} provider
        which will be used to connect when the service starts.
    """
    
    DEFAULT_DELAY = 1.0

    def __init__(self, endpoint, factory, reactor, 
                 nextDelay=DEFAULT_DELAY, connectionLostCallback=None):
        self.endpoint = endpoint
        self.factory = SignalingFactory(factory)
        self._reactor = reactor
        self._nextDelay = nextDelay
        self._dConnectingProtocol = None
        self._currentProtocol = None
        self._subscribers = []
        self._connectionLostCallback = connectionLostCallback

    def startService(self):
        service.Service.startService(self)
        self._startConnection()
        
    def stopService(self):
        if self._currentProtocol:
            self._currentProtocol.loseConnection()
        service.Service.stopService(self)

    def _startConnection(self):
        if not self.running:
            return
        assert not self._dConnectingProtocol, self._dConnectingProtocol
        #import pdb; pdb.set_trace()
        self._dConnectingProtocol = self.endpoint.connect(self.factory)
        (self._dConnectingProtocol
            .addCallback(self._onConnect))

    def _onConnectionLost(self, reason):
        self._currentProtocol = None
        if self._connectionLostCallback:
            self._connectionLostCallback(reason)
        self._reactor.callLater(self._nextDelay, self._startConnection)
        #self._startConnection()

    def _onConnect(self, protocol):
        protocol.disconnectEvent.subscribe(self._onConnectionLost)
        self._dConnectingProtocol = None
        self._currentProtocol = protocol
        subscribers = self._subscribers
        self._subscribers = []
        for sub in subscribers:
            sub.callback(protocol)

    def connectedProtocol(self):
        if self._currentProtocol:
            return defer.succeed(self._currentProtocol)
        else:
            d = defer.Deferred()
            self._subscribers.append(d)
            return d


