'''
Created on 10.04.2013

'''

import os

from twisted.internet import defer, stdio
from twisted.protocols import basic

from nfw.protocol import StateMixin

from sessions.client import broadcaster, messaging

class CliProtocol(StateMixin, object, basic.LineReceiver):
    delimiter = os.linesep

    def __init__(self):
        self.lines = defer.DeferredQueue()
        self.commands = ["servers", "send", "help"]
        super(CliProtocol, self).__init__()

    def connectionMade(self):
        self._startSM()

    def lineReceived(self, line):
        self.lines.put(line)

    def protocolError(self, failure):
        if self.stateMachineStopped:
            # This is a normal connectionLost process
            return
        self.transport.write(str(failure))
        self._startSM()

    @defer.inlineCallbacks
    def stateMachine(self):
        self.transport.write('#> ')
        raw_command_line = yield self.lines.get()
        if not raw_command_line:
            return
        command_line = raw_command_line.split(" ")
        command = command_line[0]
        if command == "help":
            self.sendLine("Available commands:")
            for c in self.commands:
                self.sendLine("  " + c)
        if command == "servers":
            for peer in broadcaster.peerlist.itervalues():
                if peer.isServer:
                    self.sendLine(str(peer))
        if command == "clients":
            for peer in broadcaster.peerlist.itervalues():
                if not peer.isServer:
                    self.sendLine(str(peer))
        elif command == "send":
            if len(command_line) < 3:
                self.sendLine("usage: send [@server] target data")
                return
            target = command_line[1]
            server = None
            k = 2
            if target.startswith("@"):
                server = target[1:]
                target = command_line[2]
                k += 1
            data_idx = 0
            for _ in xrange(k):
                data_idx = raw_command_line.index(' ', data_idx + 1)
            data = raw_command_line[data_idx + 1:]
            server_str = server if server is not None else "random server"
            self.sendLine("Sending '{}' to '{}' "
                          "via {}".format(data, target, server_str))
            result = yield messaging.sendMessage(server, target, data)
            if not result:
                self.sendLine("Failed to send the message")
            else:
                self.sendLine("Message sent ok")
        else:
            self.sendLine("Unrecognized command")

def setup():
    stdio.StandardIO(CliProtocol())
