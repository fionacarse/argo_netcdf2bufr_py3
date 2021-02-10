import unittest
from bitstring import BitStream, BitString
from bufr.BufrFXYInt import BufrFXYInt
from bufr.BufrBitArray import BufrBitArray
import math

class Test_BufrXYInt(unittest.TestCase):

    def test_BufrXYInt_Basic(self):
        eF = 2
        eX = 13
        eY = 27
        bits = 10
        eValue = 1011
        XY = BufrFXYInt(eF, eX, eY, bits)
        XY.setValue(eValue)
        buffer = BufrBitArray();
        XY.writeDefinitionToBuffer(buffer)
        XY.writeValueToBuffer(buffer)
        buffer.bytepos = 0
        F, X, Y, value = buffer.readlist([2, 6, 8, bits])
        self.assertEqual(F.uint, eF, "F incorrect")
        self.assertEqual(X.uint, eX, "X incorrect")
        self.assertEqual(Y.uint, eY, "Y incorrect")
        self.assertEqual(value.uint, eValue, "Value incorrect")

    def test_BufrXYInt_Bytes(self):
        eF = 2
        eX = 13
        eY = 27
        bits = 16
        eValue = 0xF874
        XY = BufrFXYInt(eF, eX, eY, bits)
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
        self.assertEqual(bytes[2], (eValue >> 8) & 0xFF, "Value incorrect (high byte)")
        self.assertEqual(bytes[3], eValue & 0xFF, "Value incorrect (low byte)")

if __name__ == '__main__':
    unittest.main()


