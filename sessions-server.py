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
import sys
import os.path

from sessions.server import broadcaster, sessionserver
from sessions.server import hostdb, sessiondb
from sessions.server import replication

if __name__ == '__main__':
    directory = os.path.dirname(sys.argv[0])
    fileHandler = logging.FileHandler(os.path.join(directory, "run.log"))
    logging.basicConfig(level=logging.DEBUG)
    logging.root.addHandler(fileHandler)
    observer = txlog.PythonLoggingObserver()
    txlog.startLoggingWithObserver(observer.emit, setStdout=0)
    serverId = "ofitserov"
    sessionPort = 9950
    broadcaster.setup(sessionPort)
    hostdb.setup()
    sessiondb.setup(serverId)
    sessionserver.setup(sessionPort)
    replication.setup(serverId)
    #web.setup(8080)
    reactor.run() #@UndefinedVariable
