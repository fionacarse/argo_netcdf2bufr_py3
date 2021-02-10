import unittest
from bitstring import BitStream, BitString
from bufr.BufrBitArray import BufrBitArray
from bufr.BufrFXYDouble import BufrFXYDouble
from bufr.BufrFXY import BufrFXY
import math

class Test_testBufrFXYDouble(unittest.TestCase):

    def test_BufrFXYDouble_Basic(self):
        eF = 2
        eX = 13
        eY = 27
        bits = 10
        eValue = 101.3
        scale = 1.0
        offset = -2.0
        XY = BufrFXYDouble(eF, eX, eY, scale, offset, bits)
        XY.setValue(eValue)
        buffer = BufrBitArray();
        XY.writeDefinitionToBuffer(buffer)
        XY.writeValueToBuffer(buffer)
        buffer.bytepos = 0
        F, X, Y, value = buffer.readlist([2, 6, 8, bits])
        self.assertEqual(F.uint, eF, "F incorrect")
        self.assertEqual(X.uint, eX, "X incorrect")
        self.assertEqual(Y.uint, eY, "Y incorrect")
        eValueInt = (eValue * 10 ** scale) + offset
        eValueInt = int(math.trunc(eValueInt + 0.5))
        self.assertEqual(value.uint, eValueInt, "Value incorrect")

    def test_BufrFXYDouble_Bytes(self):
        eF = 2
        eX = 13
        eY = 27
        bits = 16
        eValue = 101.3
        scale = 1.0
        offset = -2.0
        XY = BufrFXYDouble(eF, eX, eY, scale, offset, bits)
        XY.setValue(eValue)
        buffer = BufrBitArray();
        XY.writeDefinitionToBuffer(buffer)
        XY.writeValueToBuffer(buffer)
        f = open('test_Bytes_Bufr_File', 'wb')
        buffer.tofile(f)
        f.close()
        f = open('test_Bytes_Bufr_File', 'rb')
        bytes = bytearray(f.read())
        self.assertEqual((bytes[0] & 0b11000000) >> 6, eF, "F incorrect")
        self.assertEqual(bytes[0] & 0b00111111, eX, "X incorrect")
        self.assertEqual(bytes[1], eY, "Y incorrect")
        eValueInt = (eValue * 10 ** scale) + offset
        eValueInt = int(math.trunc(eValueInt + 0.5))
        self.assertEqual(bytes[2], (eValueInt >> 8) & 0xFF, "Value incorrect (high byte)")
        self.assertEqual(bytes[3], eValueInt & 0xFF, "Value incorrect (low byte)")

if __name__ == '__main__':
    unittest.main()
