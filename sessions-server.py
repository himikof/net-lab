#-------------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      ofitserov
#
# Created:     13.10.2012
# Copyright:   (c) ofitserov 2012
# License:     <your license>
#-------------------------------------------------------------------------------
#!/usr/bin/env python

from twisted.internet import reactor
from twisted.python import log as txlog
import logging
import tempfile

from sessions.server import broadcaster, sessionserver
from sessions.server import hostdb, sessiondb
from sessions.server.replication import replicator

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    observer = txlog.PythonLoggingObserver()
    txlog.startLoggingWithObserver(observer.emit, setStdout=0)
    serverId = "ofitserov"
    sessionPort = 9000
    broadcaster.setup(sessionPort)
    hostdb.setup()
    sessiondb.setup(serverId)
    sessionserver.setup(sessionPort)
    replicator.setup()
    #web.setup(8080)
    reactor.run() #@UndefinedVariable
