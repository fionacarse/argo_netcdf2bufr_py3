"""
    Class to implement a Bufr XY element of type integer
"""

from bitstring import BitArray, Bits
from bufr.BufrFXY import BufrFXY
import sys
import math

class BufrFXYInt(BufrFXY):
    """Class to implement a Bufr XY element of type integer"""

    #def __init__(self, F: int, X: int, Y: int, bits: int, inTemplate: bool = False, min: int = None, max: int = None):
    def __init__(self, F, X, Y, bits, inTemplate = False, min = None, max = None):
        #super().__init__(F, X, Y, inTemplate)
        super(BufrFXYInt, self).__init__(F, X, Y, inTemplate)
        if (bits>32):
            raise Exception("Maximum of 32bits allowed")
        if (min == None):
            self.min = -2 ** 31
            self.max = (2 ** 31) - 1
        else:
            self.min = min
            self.max = max
        self.bits = bits
        self.invalidValue = (1 << bits) - 1
        self.value = int(0)
        self.isNull = True
        self.isValid = False
        if (min == None):
            self.min = -2 ** 31
            self.max = (2 ** 31) - 1
        else:
            self.min = min
            self.max = max

    #def setValue(self, valueObj: object):
    def setValue(self, valueObj):
        self.isNull = True
        self.isValid = False

        if (valueObj != None):
            self.isNull = False

            if (not isinstance(valueObj, (int, bytes))):
                raise Exception("Value must be an int")

            if (isinstance(valueObj, bytes)):
                valueObj = int(valueObj)

            if (valueObj >= self.min and valueObj <= self.max):
                if (self.checkBitRange(valueObj, self.bits)):
                    self.value = valueObj
                    self.isValid = True

    #def writeValueToBuffer(self, buffer: BitArray):
    def writeValueToBuffer(self, buffer):
        if (self.isNull or not self.isValid):
            # fill with 1's
            buffer.writeInteger(self.invalidValue, self.bits)
        else:            
            buffer.writeInteger(self.value, self.bits)






