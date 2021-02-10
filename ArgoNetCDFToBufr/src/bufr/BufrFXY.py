"""
    Class to encapsulate basic Bufr XY data element
"""

#from abc import ABC, abstractmethod
from abc import ABCMeta, abstractmethod
from bufr.BufrBitArray import BufrBitArray
from bitstring import BitString, Bits
import logging

#class BufrFXY(ABCMeta):
class BufrFXY(object):
    """Class to encapsulate basic Bufr XY data element"""

    #def __init__(self, F: int, X: int, Y: int, inTemplate: bool = False):
    def __init__(self, F, X, Y, inTemplate = False):
        self.F = F
        self.X = X
        self.Y = Y
        self.inTemplate = inTemplate

    #def writeDefinitionToBuffer(self, buffer: BufrBitArray):
    def writeDefinitionToBuffer(self, buffer):
        # if this descriptor is inside a template then it should not
        # output its descriptor
        if (not self.inTemplate):
            logging.info("Writing " + self.tostring())
            buffer.writeBits(self.F, 2)
            buffer.writeBits(self.X, 6)
            buffer.writeBits(self.Y, 8)
            bufferTmp = self.getLastBytes(buffer, 2)

    #def checkBitRange(self, value: int, bits: int) -> bool:
    def checkBitRange(self, value, bits):
        return not (value<0 or value>(1 << bits) -1)

    @abstractmethod
    #def setValue(self, valueObj: object):
    def setValue(self, valueObj):
        pass

    @abstractmethod
    #def writeValueToBuffer(self, buffer: BufrBitArray):
    def writeValueToBuffer(self, buffer):
        pass

    #def tostring(self) -> str:
    def tostring(self):
        return "FXY Element F=" + str(self.F) + " X=" + str(self.X) + " Y=" + str(self.Y)

    #def getLastBytes(self, buffer: BufrBitArray, bytes: int) -> BitString:
    def getLastBytes(self, buffer, bytes):
        l = len(buffer)
        return buffer[l-(bytes*8):l]
