'''
Created on 10.11.2012

@author: Nikita Ofitserov
'''

import logging

from nfw.expire import AbstractExpiringDict
from nfw.m2m import ManyToMany

import broadcaster
import storageclient
from twisted.internet.defer import inlineCallbacks
from twisted.internet import defer
from nfw.util import HexBytes

_log = logging.getLogger(__name__)

class FileList(AbstractExpiringDict):
    @inlineCallbacks
    def expire(self, peerKey):
        _log.info('Trying to expire')
        try:
            peer = broadcaster.peerlist[peerKey]
            result = db.updatePeer(peer)
        except Exception:
            _log.info('Cannot refresh %s, expiring list', peerKey)
            return
        defer.returnValue(result)
    
    def ttl(self, key):
        return 10.0

# db :: peer_key -> [binaryHash :: HexBytes]
# db.flip() :: binaryHash -> [peer_key]
class NetDB(ManyToMany):
    #_first = FileList
    
    def __init__(self):
        super(NetDB, self).__init__()
        for peer in broadcaster.peerlist.values():
            self.updatePeer(peer)
        broadcaster.peerUpdated.subscribe(self.updatePeer)
    
    @inlineCallbacks
    def updatePeer(self, peer):
        _log.info('Updating peer %s', peer.key())
        client = yield storageclient.connect(peer.endpoint())
        items = yield client.list()
        self[peer.key()] = map(HexBytes, items)
        _log.info('Updated peer %s: %d files', peer.key(), len(items))
        defer.returnValue(self[peer.key()])
        
    def locateHash(self, binaryHash):
        return list(self.flip()[binaryHash])

    def jsonData(self):
        # FIXME: o_0
        def niceItem((k, v)):
            return (str(k), list(map(repr, v))) 
        return dict(map(niceItem, self.items()))

db = None

def setup():
    global db
    db = NetDB()
