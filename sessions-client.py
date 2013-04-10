#!/usr/bin/env python

from twisted.internet import reactor
from twisted.python import log as txlog
import logging
import tempfile
import socket
import sys
import os.path

from sessions.client import broadcaster, cli, clientchat, sessionclient, messaging

if __name__ == '__main__':
    directory = os.path.dirname(sys.argv[0])
    fileHandler = logging.FileHandler(os.path.join(directory, "run.log"))
    logging.basicConfig(level=logging.DEBUG)
    logging.root.addHandler(fileHandler)
    observer = txlog.PythonLoggingObserver()
    txlog.startLoggingWithObserver(observer.emit, setStdout=0)
    clientPort = 9000
    cname = socket.gethostname()
    clientchat.setup(clientPort)
    sessionclient.setup(cname)
    messaging.setup()
    broadcaster.setup(clientPort)
    cli.setup()
    reactor.run() #@UndefinedVariable
