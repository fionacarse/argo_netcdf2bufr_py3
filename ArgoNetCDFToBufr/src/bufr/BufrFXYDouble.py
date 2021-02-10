"""
    Class to implement a Bufr XY element of type double
"""

from bitstring import BitArray, Bits
from bufr.BufrFXY import BufrFXY
import sys
import math
import logging

class BufrFXYDouble(BufrFXY):
    """Class to implement a Bufr XY element of type double"""

    #def __init__(self, F: int, X: int, Y: int, scale: float, offset: float, bits: int, inTemplate: bool = False, min: float = None, max: float = None):
    def __init__(self, F, X, Y, scale, offset, bits, inTemplate = False, min = None, max = None):
        #super().__init__(F, X, Y, inTemplate)
        super(BufrFXYDouble, self).__init__(F, X, Y, inTemplate)
        self.__storeParams(F, X, Y, scale, offset, bits)
        if (min is None):
            self.min = -sys.float_info.max
            self.max = sys.float_info.max
        else:
            self.min = min
            self.max = max

    #def __storeParams(self, F: int, X: int, Y: int, scale: float, offset: float, bits: int):
    def __storeParams(self, F, X, Y, scale, offset, bits):
        self.scale = scale
        self.offset = offset
        if (bits>32):
            raise Exception("Maximum of 32bits allowed")
        self.bits = bits
        self.invalidValue = (1 << bits) - 1
        self.value = int(0)
        self.isNull = True
        self.isValid = False

    #def setValue(self, valueObj: object):
    def setValue(self, valueObj):
        self.isNull = True
        self.isValid = False

        if (valueObj != None):
            self.isNull = False

            if (not math.isnan(valueObj) and valueObj >= self.min and valueObj <= self.max):
                val = (valueObj * (10.0 ** self.scale)) + self.offset;
                val = math.trunc(val + 0.5)

                if (self.checkBitRange(val, self.bits)):
                    self.value = int(val)
                    self.isValid = True
                    self.valueObj = valueObj

    #def writeValueToBuffer(self, buffer: BitArray):
    def writeValueToBuffer(self, buffer):
        if (self.isNull or not self.isValid):
            # fill with 1's
            logging.info("Writing value 'all ones'")
            buffer.writeInteger(self.invalidValue, self.bits)
        else:                     
            logging.info("Writing value {:.4f}".format(self.valueObj))
            buffer.writeInteger(self.value, self.bits)




