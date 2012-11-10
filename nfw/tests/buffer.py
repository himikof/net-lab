'''
Created on 08.11.2012

@author: himikof
'''
import unittest

from nfw.buffer import Buffer, ConstBuffer, BufferUnderflowException

class TestBuffer(unittest.TestCase):
    
    def setUp(self):
        self.b = Buffer()
    
    def tearDown(self):
        del self.b
    
    def testPop(self):
        d1 = self.b.pop(2)
        d2 = self.b.pop(1)
        self.assertFalse(d1.called)
        self.assertFalse(d2.called)
        self.b.extend(b'1')
        self.assertFalse(d1.called)
        self.assertFalse(d2.called)
        self.b.extend(b'2')
        self.assertTrue(d1.called)
        self.assertEqual(d1.result, b'12')
        self.assertFalse(d2.called)
        self.b.extend(b'3')
        self.assertTrue(d2.called)
        self.assertEqual(d2.result, b'3')
        self.b.extend(b'134')
        d3 = self.b.pop(2)
        self.assertTrue(d3.called)
        self.assertEqual(d3.result, b'13')
        d4 = self.b.pop(4)
        d5 = self.b.pop(1)
        self.assertFalse(d4.called)
        self.assertFalse(d5.called)
        self.b.extend(b'56543')
        self.assertTrue(d4.called)
        self.assertEqual(d4.result, b'4565')
        self.assertTrue(d5.called)
        self.assertEqual(d5.result, b'4')
        self.assertEqual(len(self.b), 1)


class TestConstBuffer(unittest.TestCase):
    
    def setUp(self):
        self.b = ConstBuffer(b'12345')
    
    def tearDown(self):
        del self.b
    
    def testPop(self):
        d1 = self.b.pop(2)
        d2 = self.b.pop(1)
        self.assertTrue(d1.called)
        self.assertEqual(d1.result, b'12')
        self.assertTrue(d2.called)
        self.assertEqual(d2.result, b'3')
        self.assertRaises(BufferUnderflowException, lambda: self.b.pop(3))
        self.assertEqual(len(self.b), 2)


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
