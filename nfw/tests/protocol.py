'''
Created on 08.11.2012

@author: himikof
'''
import unittest
import struct

from nfw.protocol import StatefulProtocol

from twisted.internet.defer import inlineCallbacks

class MockProtocol(StatefulProtocol):
    @inlineCallbacks
    def stateMachine(self):
        self.cmd = yield self.readInt32()
        self.str = yield self.readString()
    
    def protocolError(self, failure):
        raise failure

class TestProtocol(unittest.TestCase):
    
    def setUp(self):
        self.p = MockProtocol()
    
    def tearDown(self):
        del self.p
    
    def testRead(self):
        d1 = self.p.readBytes(4)
        d2 = self.p.readUnpacked('3s')
        self.assertFalse(d1.called)
        self.assertFalse(d2.called)
        self.p.dataReceived(b'1234567')
        self.assertTrue(d1.called)
        self.assertEqual(d1.result, b'1234')
        self.assertTrue(d2.called)
        self.assertEqual(d2.result, ('567',))

    def testSM(self):
        teststr = u'\u041f\u0440\u0438\u0432\u0435\u0442!'
        encoded = teststr.encode('utf8')
        self.p.dataReceived(struct.pack('!I', 42))
        self.p.dataReceived(struct.pack('!I', len(encoded)) + encoded)
        self.assertEqual(self.p.cmd, 42)
        self.assertEqual(self.p.str, teststr)

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
