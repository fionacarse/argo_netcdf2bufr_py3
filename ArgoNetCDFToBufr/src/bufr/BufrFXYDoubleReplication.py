"""
    Class to implement a Bufr XY element of type repeated double (i.e. an array of doubles)
"""

from bitstring import BitArray, Bits
from bufr.BufrFXYDouble import BufrFXYDouble
import sys
import math
import collections
import logging
import numpy as np

class BufrFXYDoubleReplication(BufrFXYDouble):
    """Class to implement a Bufr XY element of type repeated double (i.e. an array of doubles)"""

    #def __init__(self, F: int, X: int, Y: int, scale: float, offset: float, bits: int, inTemplate: bool = False, min: float = None, max: float = None):
    def __init__(self, F, X, Y, scale, offset, bits, inTemplate = False, min = None, max = None):
        #super().__init__(F, X, Y, scale, offset,  bits, inTemplate, min, max)
        super(BufrFXYDoubleReplication, self).__init__(F, X, Y, scale, offset,  bits, inTemplate, min, max)
        self.valuesWritten = -1
        self.repeats = 0
        pass

    #def setValue(self, valueObj: object):
    def setValue(self, valueObj):

        self.repeats = len(valueObj)
        self.bufrFXYArray = [BufrFXYDouble(self.F, self.X, self.Y, self.scale, self.offset, self.bits, self.inTemplate, self.min, self.max) for i in range(self.repeats)]

        i = 0
        for bufrFXY in self.bufrFXYArray:
            # map masked array masked values to None for BufrFXYDouble class
            value = valueObj[i]
            if (isinstance(valueObj, np.ma.MaskedArray) and value is np.ma.masked):
                value = None
            bufrFXY.setValue(value)
            i += 1
        
        self.valuesWritten = 0
        pass

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

        logging.info("Writing delayed replication index " + str(self.valuesWritten) + " for " + self.tostring())
        self.bufrFXYArray[self.valuesWritten].writeValueToBuffer(buffer)
        self.valuesWritten += 1
        pass

    #def getRepeats(self) -> int:
    def getRepeats(self):
        return self.repeats
        pass




