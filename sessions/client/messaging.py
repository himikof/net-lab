'''
Created on 10.04.2013

'''

import logging
import random

from twisted.internet import defer
from twisted.internet.defer import inlineCallbacks

from nfw.expire import AbstractExpiringDict

from sessions.client import broadcaster, sessionclient, clientchat

_log = logging.getLogger(__name__)

SESSION_LIFE = 4.

class SessionList(AbstractExpiringDict):
    def expire(self, key):
        _log.info('Session %s expired', key)
        pass
    
    def ttl(self, key):
        return SESSION_LIFE

@inlineCallbacks
def sendMessage(server, target, data):
    if server is None:
        peer = randomServer()
    else:
        peer = findPeer(server, True)
        if not peer:
            raise RuntimeError("No server '{}' found".format(server))
    target_peer = findPeer(target, False, defaultPort=9000)
    if not target_peer:
        raise RuntimeError("No client '{}' found".format(target))
    p = yield sessionclient.connect(peer.endpoint())
    sid = yield p.requestSession(target_peer.key().host)
    if not sid:
        _log.info("Server {} was not able to get us a"
                  " session".format(peer.key()))
        defer.returnValue(False)
    p.disconnect()
    pc = yield clientchat.connect(target_peer.endpoint())
    pc.sendMessage(sid, data)
    pc.disconnect()
    defer.returnValue(True)


def findPeer(server_str, isServer, defaultPort=9999):
    try:
        if ':' in server_str:
            host, port = server_str.split(':')
            port = int(port)
        else:
            host = server_str
            port = defaultPort
        key = broadcaster.PeerKey(host=host, port=port)
        peer = broadcaster.peerlist[key]
        if peer.isServer != isServer:
            return None
        return peer
    except Exception:
        return None

def randomServer():
    servers = [p for p in broadcaster.peerlist.itervalues() if p.isServer]
    return random.choice(servers)

@inlineCallbacks
def incomingMessage((sid, data)):
    _log.debug("Verifying session...")
    server = randomServer()
    p = yield sessionclient.connect(server.endpoint())
    sessionOk = yield p.verifySession(sid)
    p.disconnect()
    if not sessionOk:
        _log.warn("Incoming message with untrusted session: {}".format(sid))
    else:
        _log.info("Session {} was verified".format(sid))
        print str(data)

def setup():
    clientchat.incoming.subscribe(incomingMessage)
