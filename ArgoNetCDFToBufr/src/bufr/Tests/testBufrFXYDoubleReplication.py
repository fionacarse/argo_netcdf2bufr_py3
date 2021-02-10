import unittest
from bitstring import BitStream, BitString
from bufr.BufrFXYDoubleReplication import BufrFXYDoubleReplication
from bufr.BufrBitArray import BufrBitArray
import math
import sys

class Test_BufrFXYDoubleReplication(unittest.TestCase):
    def test_BufrFXYDoubleReplication_Basic(self):
        eF = 2
        eX = 13
        eY = 27
        bits = 10
        eValues = [1.3, 1.4, 101.3, 102.3, 10.6, 98.3, 1.3, 101.3, 101.3, 101.3]
        scale = 1.0
        offset = -2.0
        repeats = len(eValues)
        min = sys.float_info.min
        max = sys.float_info.max
        XY = BufrFXYDoubleReplication(eF, eX, eY, scale, offset, bits, False, min, max)
        XY.setValue(eValues)
        buffer = BufrBitArray();
        XY.writeDefinitionToBuffer(buffer)
        # write all the data
        for i in range(repeats):
            XY.writeValueToBuffer(buffer)
        buffer.bytepos = 0
        F, X, Y = buffer.readlist([2, 6, 8])
        self.assertEqual(F.uint, eF, "F incorrect")
        self.assertEqual(X.uint, eX, "X incorrect")
        self.assertEqual(Y.uint, eY, "Y incorrect")
        for i in range(repeats):
            value = buffer.read(bits)
            eValueInt = (eValues[i] * 10 ** scale) + offset
            eValueInt = int(math.trunc(eValueInt + 0.5))
            self.assertEqual(value.uint, eValueInt, "Value incorrect for repeat " + str(i))

if __name__ == '__main__':
    unittest.main()
