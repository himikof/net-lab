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
from twisted.python import log as txlog
import logging
import tempfile

from storage import broadcaster
from storage import storageserver
from storage import netdb
from storage import content
from storage import web

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    observer = txlog.PythonLoggingObserver()
    txlog.startLoggingWithObserver(observer.emit, setStdout=0)
    rootDir = tempfile.mkdtemp('', 'netlab_')
    #rootDir = 'C:\\'
    c = content.Content(rootDir)
    broadcaster.setup(c)
    storageserver.setup(c)
    netdb.setup()
    web.setup(8080)
    reactor.run() #@UndefinedVariable
