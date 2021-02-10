"""
    Class to implement a Bufr XY element for delayed replication elements
"""

from bitstring import BitArray, Bits
from bufr.BufrFXY import BufrFXY
import sys
import math

class BufrFXYDelayedReplication(BufrFXY):
    """Class to implement a Bufr XY element for delayed replication elements"""

    #def __init__(self, repeats: int, inTemplate: bool = False):
    def __init__(self, repeats, inTemplate = False):
        #super().__init__(1, repeats, 0, inTemplate)
        super(BufrFXYDelayedReplication, self).__init__(1, repeats, 0, inTemplate)

    #def writeValueToBuffer(self, buffer: BitArray):
    def writeValueToBuffer(self, buffer):
        # replication FXY has no value
        pass

    #def setValue(self, valueObj: object):
    def setValue(self, valueObj):
        raise Exception("Can't set a value on a delayed replication")


