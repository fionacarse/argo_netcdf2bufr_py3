"""
    Class to implement a Bufr XY element of type repeated int (i.e. an array of integers)
"""

from bitstring import BitArray, Bits
from bufr.BufrFXYInt import BufrFXYInt
import sys
import math
import collections

class BufrFXYIntReplication(BufrFXYInt):
    """Class to implement a Bufr XY element of type repeated int (i.e. an array of integers)"""

    #def __init__(self, F: int, X: int, Y: int, bits: int, inTemplate: bool = False, min: int = None, max: int = None):
    def __init__(self, F, X, Y, bits, inTemplate = False, min = None, max = None):
        #super().__init__(F, X, Y, bits, inTemplate, min, max)
        super(BufrFXYIntReplication, self).__init__(F, X, Y, bits, inTemplate, min, max)
        self.valuesWritten = -1

    #def setValue(self, valueObj: object):
    def setValue(self, valueObj):

        self.repeats = len(valueObj)
        self.bufrFXYArray = [BufrFXYInt(self.F, self.X, self.Y, self.bits, self.inTemplate, self.min, self.max) for i in range(self.repeats)]

        i = 0
        for bufrFXY in self.bufrFXYArray:
            bufrFXY.setValue(valueObj[i])
            i += 1
        
        self.valuesWritten = 0

    #def writeValueToBuffer(self, buffer: BitArray):
    def writeValueToBuffer(self, buffer):
        if (not hasattr(self, "bufrFXYArray")):
            raise Exception(self.tostring() + " - no data has been set")
        if (len(self.bufrFXYArray) == 0):
            return  # nothing to write
        if (self.valuesWritten >= len(self.bufrFXYArray)):
            raise Exception(self.tostring() + " - can't write any more data to the buffer " + str(len(self.bufrFXYArray)))
        if (self.valuesWritten < 0):
            raise Exception(self.tostring() + " - can't write as data not initialised")

        self.bufrFXYArray[self.valuesWritten].writeValueToBuffer(buffer)
        self.valuesWritten += 1
        pass







