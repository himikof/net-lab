#-------------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      ofitserov
#
# Created:     27.10.2012
# Copyright:   (c) ofitserov 2012
# Licence:     <your licence>
#-------------------------------------------------------------------------------
#!/usr/bin/env python

import os
import hashlib
import binascii
import logging

_log = logging.getLogger(__name__)

MAX_FILES = 10

class Content(object):
    def __init__(self, path):
        self.path = path
        self.files = []
        
    def hashBytes(self, bytes):
        m = hashlib.md5() #@UndefinedVariable
        m.update(bytes)
        return m.hexdigest()

    def verifyFile(self, hexHash):
        try:
            with open(os.path.join(self.path, hexHash)) as f:
                contents = f.read()
                return self.hashBytes(contents) == hexHash
        except IOError:
            return False

    def getContentId(self):
        self.updateFiles()
        m = hashlib.md5() #@UndefinedVariable
        for f in self.files:
            m.update(f)
        return m.digest()

    def updateFiles(self):
        self.files = []
        for fname in os.listdir(self.path):
            fpath = os.path.join(self.path, fname)
            if not os.path.isfile(fpath):
                continue
            if not self.verifyFile(fname):
                continue
            self.files.append(binascii.unhexlify(fname))

    def get(self, binaryHash):
        hexHash = binascii.hexlify(binaryHash)
        if not self.verifyFile(hexHash):
            return None
        try:
            with open(os.path.join(self.path, hexHash)) as f:
                return f.read()
        except IOError:
            return None

    def put(self, content):
        if len(self.files) >= MAX_FILES:
            _log.info('File number limit reached')
            return False
        hexHash = self.hashBytes(content)
        try:
            with open(os.path.join(self.path, hexHash), 'w') as f:
                f.write(content)
            self.files.append(binascii.unhexlify(hexHash))
            return True
        except IOError:
            return False
