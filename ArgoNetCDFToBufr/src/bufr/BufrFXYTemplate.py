"""
    Class to implement a Bufr XY element for including a template
"""

from bitstring import BitArray, Bits
from bufr.BufrFXY import BufrFXY

class BufrFXYTemplate(BufrFXY):
    """Class to implement a Bufr XY element for including a template"""

    #def __init__(self, F: int, X: int, Y: int):
    def __init__(self, F, X, Y):
        #super().__init__(F, X, Y)
        super(BufrFXYTemplate, self).__init__(F, X, Y)

    #def writeValueToBuffer(self, buffer: BitArray):
    def writeValueToBuffer(self, buffer):
        # template FXY has no value
        pass

    #def setValue(self, valueObj: object):
    def setValue(self, valueObj):
        raise Exception("Can't set a value on a template")

