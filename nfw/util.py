'''
Created on 10.11.2012

@author: Nikita Ofitserov
'''
import binascii

class HexBytes(bytes, object):
    def __repr__(self):
        return binascii.b2a_hex(self)

