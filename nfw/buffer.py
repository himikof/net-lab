'''
Created on 08.11.2012

@author: Nikita Ofitserov
'''

import collections

from twisted.internet import defer
from twisted.python.failure import Failure

class BufferClearedException(Exception):
    pass

class Buffer(object):
    '''
    A simple lazy buffer class for queuing data. It is a queue of bytes.
    '''

    def __init__(self):
        '''
        Constructs an empty Buffer.
        '''
        self.data = collections.deque()
        self.requests = collections.deque()
    
    def extend(self, data):
        self.data.extend(data)
        while self._handle():
            pass
        
    def clear(self):
        for deferred, _ in self.requests:
            deferred.errback(Failure('Buffer cleared'))
        self.requests.clear()
        self.data.clear()

    def _handle(self):
        if not self.requests:
            return False
        deferred, length = self.requests[0]
        if len(self.data) >= length:
            data = bytearray((self.data.popleft() for i in range(length)))
            self.requests.popleft()
            deferred.callback(data)
            return True
        return False

    def pop(self, length):
        d = defer.Deferred()
        self.requests.append((d, length))
        self._handle()
        return d
    
    def flush(self):
        data = bytearray(self.data)
        self.clear()
        return data

    def __len__(self):
        return len(self.data)


class BufferUnderflowException(Exception):
    pass

class ConstBuffer(object):
    '''
    A read-only version of Buffer.
    '''
    def __init__(self, data):
        self.data = data
        self.offset = 0
        
    def _pop(self, length):
        new_offset = self.offset + length 
        if new_offset > len(self.data):
            raise BufferUnderflowException('ConstBuffer underflow')
        result = self.data[self.offset : new_offset]
        self.offset = new_offset
        return result

    def pop(self, length):
        return defer.succeed(self._pop(length))
    
    def flush(self):
        return self._pop(len(self))

    def __len__(self):
        return len(self.data) - self.offset
