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

from twisted.web import server, resource, http, xmlrpc
from twisted.internet import reactor, defer
from twisted.internet.endpoints import TCP4ServerEndpoint
from twisted.internet.defer import inlineCallbacks
from twisted.python import log as txlog

import json
from functools import wraps

import broadcaster
import storageclient
from abc import abstractmethod, ABCMeta
import binascii
from storageclient import RequestFailed
import netdb
import logging
from nfw.util import HexBytes

_log = logging.getLogger(__name__)

def xmlrpcCatch(func):
    def errback(failure):
        raise xmlrpc.Fault(2, failure.getBriefTraceback())
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return defer.maybeDeferred(func, *args, **kwargs)\
                .addErrback(errback)
        except:
            return defer.fail().addErrback(errback)
    return wrapper

class XmlRpcInterface(xmlrpc.XMLRPC):
    
    def __init__(self):
        xmlrpc.XMLRPC.__init__(self, allowNone=True)
    
    def xmlrpc_peers(self):
        return broadcaster.peerlist.jsonData()
    
    def client(self, cname):
        peer = None
        for p in broadcaster.peerlist.values():
            if p.cname == cname:
                peer = p
                break
        if peer is None:
            raise xmlrpc.Fault(1, 'No peer with cname = %s' % cname)
        return storageclient.connect(peer.endpoint())        
    
    @xmlrpcCatch
    @inlineCallbacks
    def xmlrpc_force_list(self, cname):
        client = yield self.client(cname)
        items = yield client.list()
        items = map(binascii.hexlify, items)
        _log.info(items)
        defer.returnValue(items)

    @xmlrpcCatch
    @inlineCallbacks
    def xmlrpc_get(self, cname, hexHash):
        client = yield self.client(cname)
        try:
            content = yield client.get(binascii.unhexlify(hexHash))
        except RequestFailed:
            return
        defer.returnValue(xmlrpc.Binary(content))

    @xmlrpcCatch
    def xmlrpc_list(self):
        return netdb.db.jsonData()

    @xmlrpcCatch
    @inlineCallbacks
    def xmlrpc_pull(self, hexHash):
        binaryHash = HexBytes(binascii.unhexlify(hexHash))
        candidates = netdb.db.locateHash(binaryHash)
        _log.info("Candidates for %s: %s", hexHash, candidates)
        if not candidates:
            raise xmlrpc.Fault(0, 'No such content found')
        peer = broadcaster.peerlist[candidates[0]]
        client = yield storageclient.connect(peer.endpoint())
        try:
            content = yield client.get(binaryHash)
        except RequestFailed:
            raise xmlrpc.Fault(1, 'Cannot get content')
        defer.returnValue(xmlrpc.Binary(content))

    @xmlrpcCatch
    @inlineCallbacks
    def xmlrpc_push(self, cname, data):
        client = yield self.client(cname)
        result = yield client.put(data)
        defer.returnValue(result)


class PeerLister(resource.Resource):
    isLeaf = True
    def render_GET(self, request):
        return json.dumps(broadcaster.peerlist.jsonData(), indent=4)

class BasePeerQuery(object, resource.Resource):
    __metaclass__ = ABCMeta
    
    isLeaf = True
    def render_GET(self, request):
        cname = request.args['cname'][0]
        peer = None
        for p in broadcaster.peerlist.values():
            if p.cname == cname:
                peer = p
                break
        if peer is None:
            request.setResponseCode(http.BAD_REQUEST)
            return 'No peer with cname = %s' % cname
        d = storageclient.connect(peer.endpoint())
        d.addCallback(self.callback, request)
        d.addErrback(self.errback, request)
        return server.NOT_DONE_YET

    def errback(self, failure, request):
        request.setResponseCode(http.INTERNAL_SERVER_ERROR)
        txlog.err(failure)
        request.write('Client failed:\n')
        request.write(failure.getTraceback())
        request.finish()

    @abstractmethod
    def callback(self, client, request):
        pass

class ListQuery(BasePeerQuery):
    @inlineCallbacks
    def callback(self, client, request):
        items = yield client.list()
        request.write(json.dumps(items, indent=4, encoding='utf8'))
        request.finish()

class GetQuery(BasePeerQuery):
    @inlineCallbacks
    def callback(self, client, request):
        binaryHash = binascii.unhexlify(request.args['hash'][0])
        try:
            content = yield client.get(binaryHash)
            request.write(content)
        except storageclient.RequestFailed:
            request.write('Request failed')
        request.finish()

'''class MassQuery(resource.Resource):
    isLeaf = True

    @inlineCallbacks
    def process(self, request):
        peers = peerlist.map.values()
        dl = DeferredList([stringclient.connect(peer.endpoint()) for
            peer in peers], consumeErrors=True)
        results = yield dl
        map = {}
        for (success, value), peer in zip(results, peers):
            if success:
                map[peer.cname] = {"name": peer.name, "data": value}
        request.write(json.dumps(map, indent=4, encoding='utf8'))
        request.finish()

    def render_GET(self, request):
        self.process(request)
        return server.NOT_DONE_YET
'''

def setup(port):
    root = resource.Resource()
    rpcInterface = XmlRpcInterface()
    xmlrpc.addIntrospection(rpcInterface)
    root.putChild('RPC2', rpcInterface)
    root.putChild('peers', PeerLister())
    root.putChild('list', ListQuery())
    root.putChild('get', GetQuery())
    #root.putChild('all', MassQuery())
    factory = server.Site(root)
    endpoint = TCP4ServerEndpoint(reactor, port)
    endpoint.listen(factory)

if __name__ == '__main__':
    pass
