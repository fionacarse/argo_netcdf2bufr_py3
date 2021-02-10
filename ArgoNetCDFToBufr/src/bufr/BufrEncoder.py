"""
    Class to encode the bufr file in the correct format
"""

from bitstring import BitArray, Bits
from bufr.BufrBitArray import BufrBitArray
from datetime import datetime
from bufr.BufrFXYDoubleReplication import BufrFXYDoubleReplication
from bufr.BufrFXYIntReplication import BufrFXYIntReplication
from bufr.BufrFXY import BufrFXY
#from abc import ABC, abstractmethod
from abc import ABCMeta, abstractmethod
import collections
import logging

class BufrEncoder(object):
    """Class to encode the bufr file in the correct format"""

    EDITION_NUMBER = 4  # BUFR edition number

    def __init__(self):
        self.indicatorLengthPos = -1    # impossible
        self.data = collections.OrderedDict()
        pass

    #def writeMessage(self, buffer: BufrBitArray, dateTime: datetime, centre: int):
    def writeMessage(self, buffer, dateTime, centre):

        # get the data
        self.setData();  # override to provide the data

        # write each part of the message in turn
        self.writeIndicatorSection(buffer)
        self.writeIdentificationSection(buffer, centre, dateTime)
        self.writeDataDescriptionSection(buffer, 1)
        self.writeDataSection(buffer)
        self.writeEndSection(buffer)

        # add length
        length = buffer.bytePos() - self.indicatorLengthPos + 4   # length is from start, not length value position, so add for "BUFR"
        self.writeIndicatorSectionLength(buffer, length)
        pass

    @abstractmethod
    def setData(self):
        pass

    #def addDataDescription(self, key: str, dataDescription: BufrFXY):
    def addDataDescription(self, key, dataDescription):
        self.data[key] = dataDescription
        pass

    #def getDataDescription(self, key: str) -> BufrFXY:
    def getDataDescription(self, key):
        return self.data[key]
        pass

    #def writeReplication(self, replicationArray: list, buffer: BufrBitArray):
    def writeReplication(self, replicationArray, buffer):
        if len(replicationArray) > 0:
            repeats = replicationArray[0].getRepeats()  # should check they are all the same, but will generate an error later if not anyway
            # write the values
            for i in range(repeats - 1):
                for dataDescriptionReplication in replicationArray:
                    dataDescriptionReplication.writeValueToBuffer(buffer)
            del replicationArray[:]
        pass

    # SECTION 0

    #def writeIndicatorSection(self, buffer: BufrBitArray):
    def writeIndicatorSection(self, buffer):
        logging.info("Section 0 Start")
        buffer.writeString("BUFR")
        self.indicatorLengthPos = buffer.bytePos()
        buffer.writeInteger3(0) # will be length
        buffer.writeByte(self.EDITION_NUMBER)
        buffer.padBytes(2)  # pad to multiple of 2 bytes
        logging.info("Section 0 End")
        pass

    #def writeIndicatorSectionLength(self, buffer: BufrBitArray, length: int):
    def writeIndicatorSectionLength(self, buffer, length):
        buffer.writeInteger3Absolute(length, self.indicatorLengthPos)
        pass

    # SECTION 1

    #def writeIdentificationSection(self, buffer: BufrBitArray, centre: int, dateTime: datetime):
    def writeIdentificationSection(self, buffer, centre, dateTime):
        logging.info("Section 1 Start")
        lengthPos = buffer.bytePos()
        buffer.writeInteger3(0) # will be length

        buffer.writeByte(0x00)      # BUFR Master Table
        buffer.writeShort(centre)   # originating centre
        buffer.writeShort(0x00)     # originating sub-centre
        buffer.writeByte(0x00)      # update sequence  number
        buffer.writeByte(0x00)      # flag for inclusion of section 2
        buffer.writeByte(31)        # data type (oceanographic data = 31)
        buffer.writeByte(0x04)      # international data subtype (float profile = 4)
        buffer.writeByte(0x00)      # local setData subtype
        buffer.writeByte(33)        # version number of Table B
        buffer.writeByte(0)         # version number of local Table B

        year = dateTime.year
        month = dateTime.month
        day = dateTime.day
        hour = dateTime.hour
        minute = dateTime.minute
        second = dateTime.second
        buffer.writeShort(year)
        buffer.writeByte(month)
        buffer.writeByte(day)
        buffer.writeByte(hour)
        buffer.writeByte(minute)
        buffer.writeByte(second)  # octet 22

        buffer.writeShort(0x00) # make the same as Jon's output//??

        buffer.padBytes(2)  # pad to multiple of 2 bytes
        lengthDiff = buffer.getBytePosDiff(lengthPos)
        buffer.writeInteger3Absolute(lengthDiff, lengthPos)    # add length of section
        logging.info("Section 1 End")
        pass

    # SECTION 2 (optional)
    # SECTION 3

    #def writeDataDescriptionSection(self, buffer: BufrBitArray, subsets: int):
    def writeDataDescriptionSection(self, buffer, subsets):
        logging.info("Section 3 Start")
        lengthPos = buffer.bytePos()
        buffer.writeInteger3(0) # will be length

        buffer.writeByte(0x00)      # reserved
        buffer.writeShort(subsets)  # number of setData sets
        buffer.writeByte(1 << 7)    # observed setData

        # add the data descriptions to the buffer
        for key, dataDescription in self.data.items():
            dataDescription.writeDefinitionToBuffer(buffer)

        buffer.padBytes(2)  # pad to multiple of 2 bytes
        lengthDiff = buffer.getBytePosDiff(lengthPos)
        buffer.writeInteger3Absolute(lengthDiff, lengthPos)    # add length of section
        logging.info("Section 3 End")
        pass

    # SECTION 4

    #def writeDataSection(self, buffer: BufrBitArray):
    def writeDataSection(self, buffer):
        logging.info("Section 4 Start")
        lengthPos = buffer.bytePos()
        buffer.writeInteger3(0) # will be length

        buffer.writeByte(0x00)      # reserved

        # add the data to the buffer, respecting repeated descriptions
        replicationArray = list()
        for key, dataDescription in self.data.items():
            if isinstance(dataDescription, (BufrFXYDoubleReplication, BufrFXYIntReplication)):
                replicationArray.append(dataDescription)
            else:
                # replication ended?
                self.writeReplication(replicationArray, buffer)
            dataDescription.writeValueToBuffer(buffer)
        self.writeReplication(replicationArray,  buffer);

        buffer.padBytes(2)  # pad to multiple of 2 bytes
        lengthDiff = buffer.getBytePosDiff(lengthPos)
        buffer.writeInteger3Absolute(lengthDiff, lengthPos)    # add length of section
        logging.info("Section 4 End")
        pass

    # SECTION 5

    #def writeEndSection(self, buffer: BufrBitArray):
    def writeEndSection(self, buffer):
        logging.info("Section 5 Start")
        buffer.writeString("7777");
        buffer.padBytes(2); # pad to multiple of 2 bytes
        logging.info("Section 5 End")
        pass
