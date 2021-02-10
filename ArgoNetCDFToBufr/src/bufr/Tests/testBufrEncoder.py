import unittest
from bufr.BufrEncoder import BufrEncoder
from bufr.BufrFXYTemplate import BufrFXYTemplate
from bufr.BufrFXYString import BufrFXYString
from datetime import datetime
from bitstring import BitArray, Bits
from bufr.BufrBitArray import BufrBitArray

class ExampleBufrEncoder(BufrEncoder):

    def __init__(self):
        super(ExampleBufrEncoder, self).__init__()

        self.addDataDescription("Template", BufrFXYTemplate(3, 15, 3))
        self.addDataDescription("WMOMarineObservingPlatform",BufrFXYString(0, 1, 87, 7))
        pass

    def setData(self):
        self.getDataDescription("WMOMarineObservingPlatform").setValue("1234567")
        pass

    #def getMessage(self, dateTime: datetime) -> BitArray:
    def getMessage(self, dateTime):
        buffer = BufrBitArray()
        exeter = 74
        self.writeMessage(buffer, dateTime, exeter)
        return buffer
        pass

class Test_testBufrEncoder(unittest.TestCase):

    def test_BufrEncoder_BasicExample(self):
        # create an exampleBufrEncoder
        exampleBufrEncoder = ExampleBufrEncoder()
        # get the bufr data
        buffer = exampleBufrEncoder.getMessage(datetime(2016, 9, 8, 9, 31, 0))
        # write to file
        f = open('test_BufrEncoder_BasicExample_File', 'wb')
        buffer.tofile(f)
        # compare with what we should get
        #//??
        pass

if __name__ == '__main__':
    unittest.main()
