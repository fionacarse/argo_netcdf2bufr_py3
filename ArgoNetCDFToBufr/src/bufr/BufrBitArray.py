"""
    Class to add writing of Bufr data to BitStream
"""

from bitstring import BitStream, Bits
import logging

def twoDigitHex(number):
    s = '%02X' % number
    return '0x' + s

def hexString(buffer):
    # have to get as bits as you can't get bytes when incomplete number of btyes
    numBits = len(buffer)
    hex = ""
    startByte = max([1, (numBits//8) - 10])
    for i in range(startByte, numBits//8):
        num = 0
        for j in range(8):
            num = (num << 1) + buffer[(i*8)+j]
        if i==0:
            hex = twoDigitHex(num)
        else:
            hex +=" " + twoDigitHex(num)

    # add bits left dangling after complete bytes
    bitsLeft = numBits % 8
    if (bitsLeft>0):
        buff = buffer[numBits-bitsLeft:numBits]
        hex += " " + str(bitsLeft) + " bits in next byte = 0x" + str(buff)

    return hex

#def buffertostring(buffer: BitStream) -> str:
def buffertostring(buffer):
    return hexString(buffer)

class BufrBitArray(BitStream):
    """Class to add writing of Bufr data to BitStream"""

    #def writeString(self, value: str):
    def writeString(self, value):
        byteValue = bytearray(str.encode(value, encoding='US-ASCII'))
        if (self.posEnd()):
            self.insert(byteValue)
        else:
            self.overwrite(byteValue)
        self.log("Writing " + value + " Buffer = ")
        pass

    #def writeInteger3(self, value: int):
    def writeInteger3(self, value):
        if (self.posEnd()):
            self.insert(Bits(uint=value, length=24))
        else:
            self.overwrite(Bits(uint=value, length=24))
        self.log("Writing 3 bytes " + str(value) + " Buffer = ")
        pass

    #def writeInteger(self, value: int, bits: int):
    def writeInteger(self, value, bits):
        if (self.posEnd()):
            self.insert(Bits(uint=value, length=bits))
        else:
            self.overwrite(Bits(uint=value, length=bits))
        self.log("Writing " + str(bits) + " bits " + str(value) + " Buffer = ")
        pass

    #def writeByte(self, value: int):
    def writeByte(self, value):
        if (self.posEnd()):
            self.insert(Bits(uint=value, length=8))
        else:
            self.overwrite(Bits(uint=value, length=8))
        self.log("Writing 1 byte " + str(value) + " Buffer = ")
        pass

    #def writeBits(self, value: int, bits: int):
    def writeBits(self, value, bits):
        if (self.posEnd()):
            self.insert(Bits(uint=value, length=bits))
        else:
            self.overwrite(Bits(uint=value, length=bits))
        self.log("Writing " + str(bits) + " bits " + str(value) + " Buffer = ")
        pass

    #def writeShort(self, value: int):
    def writeShort(self, value):
        if (self.posEnd()):
            self.insert(Bits(uint=value, length=16))
        else:
            self.overwrite(Bits(uint=value, length=16))
        self.log("Writing 2 bytes " + str(value) + " Buffer = ")
        pass

    #def padBytes(self, multiplesOf: int):
    def padBytes(self, multiplesOf):
        self.padToNextByte()
        bytes = self.bytePos()
        bytesToPad = bytes % multiplesOf
        for i in range(bytesToPad):
            self.writeByte(0x00)
        self.log("Padding to multiples of " + str(multiplesOf) + " bytes Buffer = ")
        pass

    def padToNextByte(self):
        bits = self.bitpos % 8
        if (bits>0):
            self.insert(Bits(uint=0x00, length=8-bits))
        self.log("Padding to next byte Buffer = ")
        pass

    #def writeInteger3Absolute(self, value: int, bytePos: int):
    def writeInteger3Absolute(self, value, bytePos):
        currentBits = self.bitpos
        self.bytepos = bytePos
        self.writeInteger3(value)
        self.bitpos = currentBits
        pass

    def bytePos(self):
        return self.bytepos
        pass

    def posEnd(self):
        return self.bitpos==self.len
        pass

    #def getBytePosDiff(self, otherBytePos: int):
    def getBytePosDiff(self, otherBytePos):
        return self.bytePos() - otherBytePos
        pass

    # only get the buffer as a string if debug is required as it is expensive
    #def log(self, message: str):
    def log(self, message):
        logger = logging.getLogger()
        if logger.level == logging.DEBUG:
            logging.info(message + buffertostring(self))
        pass
