"""
    Class to implement a Bufr XY element of type string
"""

from bitstring import BitArray, Bits
from bufr.BufrFXY import BufrFXY
import sys
import math

class BufrFXYString(BufrFXY):
    """Class to implement a Bufr XY element of type string"""

    #def __init__(self, F: int, X: int, Y: int, length: int, inTemplate: bool = False):
    def __init__(self, F, X, Y, length, inTemplate = False):
        #super().__init__(F, X, Y, inTemplate)
        super(BufrFXYString, self).__init__(F, X, Y, inTemplate)
        self.length = length

    #def setValue(self, valueObj: object):
    def setValue(self, valueObj):
        self.isNull = True

        if (valueObj != None):
            self.isNull = False

            if (not isinstance(valueObj, str)):
                raise Exception("Value must be a string")
            self.value = valueObj
            self.isValid = True

    #def writeValueToBuffer(self, buffer: BitArray):
    def writeValueToBuffer(self, buffer):
        if (self.isNull):
            # fill with spaces
            value = "".ljust(self.length)
        else:
            # pad with spaces or truncate
            value = self.value.ljust(self.length)[:self.length]
            buffer.writeString(value)


