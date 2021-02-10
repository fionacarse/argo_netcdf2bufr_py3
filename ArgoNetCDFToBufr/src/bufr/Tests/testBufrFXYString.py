import unittest
from bitstring import BitStream, BitString
from bufr.BufrFXYString import BufrFXYString
from bufr.BufrBitArray import BufrBitArray

class Test_BufrXYString(unittest.TestCase):

    def test_BufrXYString_Basic(self):
        eF = 2
        eX = 13
        eY = 27
        length = 10
        eValue = "BUFR"
        XY = BufrFXYString(eF, eX, eY, length)
        XY.setValue(eValue)
        buffer = BufrBitArray();
        XY.writeDefinitionToBuffer(buffer)
        XY.writeValueToBuffer(buffer)
        buffer.bytepos = 0
        F, X, Y = buffer.readlist([2, 6, 8])
        value = buffer.read('bytes:{0}'.format(length))
        self.assertEqual(F.uint, eF, "F incorrect")
        self.assertEqual(X.uint, eX, "X incorrect")
        self.assertEqual(Y.uint, eY, "Y incorrect")
        for i in range(length):
            if i>len(eValue)-1:
                self.assertEqual(value[i], '  '.encode('US-ASCII')[0], "Value incorrect")   # spaces
            else:
                self.assertEqual(value[i], eValue.encode('US-ASCII')[i], "Value incorrect")

    def test_BufrXYString_Bytes(self):
        eF = 2
        eX = 13
        eY = 27
        length = 5
        eValue = "BUFR"
        XY = BufrFXYString(eF, eX, eY, length)
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
        b = bytearray(bytes[2:length+2])
        for i in range(len(eValue)):
            self.assertEqual(b.decode('US-ASCII')[i], eValue[i], "Value incorrect ({0})".format(i))

if __name__ == '__main__':
    unittest.main()


