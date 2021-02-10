import unittest
import re
import numpy as np
from netCDF4 import Dataset, chartostring
from channels.Channel import Channel
from bitstring import BitStream, BitString
import logging
import pdb
import os
import sys
import math

class NetCDFDecoder(object):
    """Class to read a NetCDF file from an Argo sensor and return a map of channels"""

    def __init__(self):
        pass

    def loadFile(self, fileName: str):
        self.fileName = fileName
        self.rootgrp = Dataset(fileName, "a")
        # create an empty dictionary
        self.channels = {}

    def decode(self) -> dict:
        # decode each variable from the NetCDF file and add its data to the channels list

        # clear dictionary
        self.channels.clear

        # channels

        # headers and useful info
        self.decodeCharChannelToInteger("PLATFORM_NUMBER")      # WMO number
        self.decodeCharChannelToString("FLOAT_SERIAL_NO", "", True)       # serial number of float (missing in v2.2 files)
        self.decodeCharChannelToString("POSITIONING_SYSTEM")    # positioning system - Argo reference table 9
        self.decodeCharChannelToString("PLATFORM_TYPE", "", True)         # type of platform - Argo reference table 23 (missing in v2.2 files)
        self.decodeIntegerChannel("CYCLE_NUMBER")               # cycle number
        self.decodeCharChannelToString("DIRECTION")             # direction of profile A : ascending profile D : descending profile
        self.decodeCharChannelToInteger("WMO_INST_TYPE")        # instrument type
        self.decodeFloatChannel("JULD")                         # Julian day of measurement (1 = a day, starting at 1970)
        self.decodeFloatChannel("LONGITUDE")                    # longitude
        self.decodeFloatChannel("LATITUDE")                     # latitude
        self.decodeCharChannelToInteger("POSITION_QC")          # quality of position measurement
        self.decodeDimension("N_LEVELS")                        # number of levels in profiles
        self.decodeDimension("N_PROF")                          # number of profiles
        if "VERTICAL_SAMPLING_SCHEME" in self.rootgrp.variables:
            self.decodeCharChannelToStringsChannel("VERTICAL_SAMPLING_SCHEME")        # sampling scheme of each profile (table 16)

        # data
        dataChannelNames = ["PRES", "TEMP", "PSAL"]
        self.readChannels(dataChannelNames)

        # more than one profile?
        numProfiles = self.channels["N_PROF"].value
        # check for bio file
        path, file = os.path.split(self.fileName)
        bioFileName = os.path.join(path, "B" + file)
        if os.path.isfile(bioFileName):
            # read bio file
            self.rootgrp = Dataset(bioFileName, "a")    # replace the root with the bio data
            dataChannelNames = ["DOXY"]
            self.readChannels(dataChannelNames)
            pass

        return self.channels

    def readChannels(self, channelNames: [str]):
        self.decodeCharChannelToString("DATA_MODE")
        dataMode = self.channels["DATA_MODE"].value
        for channelName in channelNames:
            [scale, offset] = self.getScaleOffsetForChannel(channelName)
            decodedChannel = False
            if (dataMode=="D" or dataMode=="A"):
                # not guaranteed the adjusted values will be available for all channels
                if self.channelExists(channelName + "_ADJUSTED") and self.channelExists(channelName + "_ADJUSTED_QC"):
                    # check there are values
                    if self.channelHasNonMaskedValues(channelName + "_ADJUSTED") and self.channelHasNonMaskedValues(channelName + "_ADJUSTED_QC"):
                        self.decodeFloatsChannel(channelName + "_ADJUSTED", scale, offset, channelName)
                        self.decodeIntsChannel(channelName + "_ADJUSTED_QC", channelName + "_QC")
                        decodedChannel = True
                        logging.info("Using " + channelName + "_ADJUSTED")
                        print("Using " + channelName + "_ADJUSTED")
            #  if not decoded use the non-adjusted channel
            if not decodedChannel:
                self.decodeFloatsChannel(channelName, scale, offset)
                self.decodeIntsChannel(channelName + "_QC")
                logging.info("Using " + channelName)
                print("Using " + channelName)
        pass

    # add units here using the units from the ARGO file
    def getScaleOffsetForChannel(self, channelName: str) -> [float, float]:
        # conversion factors
        DBAR_TO_PASCAL = 10000.0
        HPASCAL_TO_PASCAL = 100.0
        DEGC_TO_KELVIN = 273.15
        # mapping from ARGO units to scale/offset
        pressureUnitsConvertersScale = {"decibar": DBAR_TO_PASCAL, "hectopascal": HPASCAL_TO_PASCAL}
        temperatureUnitsConvertersOffset = {"degree_Celsius": DEGC_TO_KELVIN}
        # mapping from channel name to unit conversions
        channelUnitsScale = {"PRES": pressureUnitsConvertersScale, "TEMP": {}, "PSAL": {}, "DOXY": {}}
        channelUnitsOffset = {"PRES": {}, "TEMP": temperatureUnitsConvertersOffset, "PSAL": {}, "DOXY": {}}
        unitsConvertersScale = channelUnitsScale[channelName]
        unitsConvertersOffset = channelUnitsOffset[channelName]
        units = self.getChannelUnits(channelName)
        scale = unitsConvertersScale.get(units, 1.0)    # default to make no change
        offset = unitsConvertersOffset.get(units, 0.0)
        return [scale, offset]
        pass

    def getKey(self, key: str, name: str):
        return name if (key=="") else key
        pass

    def decodeCharChannelToInteger(self, name: str, key: str = ""):
        v = self.rootgrp.variables[name]
        vbytes = v[0]
        if type(vbytes) is np.ma.core.MaskedArray:
            vbytes = vbytes[vbytes.mask == False]   # get the data without any missing values (assumed to be at the end)
            vstr = vbytes.tobytes().decode("US-ASCII")  # extract as bytes and decode to string
        else:
            vstr = vbytes.decode("US-ASCII")
        vmissing = v._FillValue
        vint = int(vstr)
        logging.info("CDF data " + name + " = " + str(vint))
        self.channels[self.getKey(key, name)] = Channel(name, vint, vmissing, v)

    def decodeCharChannelToString(self, name: str, key: str = "", allowMissing: bool = False):
        if name in self.rootgrp.variables or not allowMissing:
            v = self.rootgrp.variables[name]
            vbytes = v[0]
            if type(vbytes) is np.ma.core.MaskedArray:
                #vbytes = vbytes[vbytes.mask == False]   # get the data without any missing values (assumed to be at the end)
                vstr = vbytes.tobytes().decode("US-ASCII")  # extract as bytes and decode to string
            else:
                vstr = vbytes.decode("US-ASCII")
            vstr = vstr.strip(" ")
            vmissing = v._FillValue
            vmissing = vmissing.decode("US-ASCII")
            vstr = re.sub(vmissing, '', vstr)
        else: 
            vstr = ""
            vmissing = ""
            v = ""
        logging.info("CDF data " + name + " = " + vstr)
        self.channels[self.getKey(key, name)] = Channel(name, vstr, vmissing, v)

    def decodeIntegerChannel(self, name: str, key: str = ""):
        v = self.rootgrp.variables[name]
        vint = int(v[0])
        vmissing = v._FillValue
        if (vint == vmissing):
            vint = None
        logging.info("CDF data " + name + " = " + str(vint))
        self.channels[self.getKey(key, name)] = Channel(name, vint, vmissing, v)

    def decodeFloatChannel(self, name: str, key: str = ""):
        v = self.rootgrp.variables[name]
        vfloat = float(v[0])
        vmissing = v._FillValue
        if (vfloat == vmissing):
            vfloat = None
        logging.info("CDF data " + name + " = " + str(vfloat))
        self.channels[self.getKey(key, name)] = Channel(name, vfloat, vmissing, v)

    def decodeDimension(self, name: str, key: str = ""):
        v = self.rootgrp.dimensions[name]
        #vint = v.size
        vint = len(v)
        logging.info("CDF dimension " + name + " = " + str(vint))
        self.channels[self.getKey(key, name)] = Channel(name, vint, None, v)

    def decodeCharChannelToStringsChannel(self, name: str, key: str = ""):
        v = self.rootgrp.variables[name]
        vstrs = v[:]
        if type(vstrs) is np.ma.core.MaskedArray:
            vstrs._sharedmask = False   # this will be the default behaviour with Numpy 1.12
        vstr = [None] * len(vstrs)
        for i, val in enumerate(vstrs):
            str = vstrs[i]
            vbytes = vstrs[i]
            if type(vbytes) is np.ma.core.MaskedArray:
                str = vbytes.tobytes().decode("US-ASCII")  # extract as bytes and decode to string
            else:
                str = vbytes.decode("US-ASCII")
            vstr[i] = str
            pass
        vmissing = v._FillValue
        vmissing = vmissing.decode("US-ASCII")
        #vstr = re.sub(vmissing, '', vstr)
        self.channels[self.getKey(key, name)] = Channel(name, vstr, vmissing, v)

    def trunc(self, values, decs=0):
        return np.trunc(values*10**decs)/(10**decs)

    def round(self, value, decs=0):
        value = value * 10 ** decs
        if value - math.trunc(value) >=0.5:
            return math.trunc(value + 1) / (10 ** decs)
        else:
            return math.trunc(value) / (10 ** decs)

    def decodeFloatsChannel(self, name: str, scaleFactor: float, offset: float, key: str = ""):
        v = self.rootgrp.variables[name]
        # round (there is some evidence that scaling/offset is adjusted within the importer but not rounded again)
        decimalPlaces = int(-1.0*np.log10(v.resolution))
        vfloats = v[:]
        for level, f in enumerate(vfloats):
#            for i in range(0, f.count()):
            for i in range(0, f.size):
                vfloats[level][i] = round(f.data[i], decimalPlaces)
        vfloats = (vfloats * scaleFactor) + offset
        vmissing = v._FillValue
        if type(vfloats) is np.ma.core.MaskedArray:
            vfloats._sharedmask = False # this will be the default behaviour with Numpy 1.12
        self.channels[self.getKey(key, name)] = Channel(name, vfloats, vmissing, v)
        pass

    def decodeIntsChannel(self, name: str, key: str = ""):
        v = self.rootgrp.variables[name]
        vints = v[:]
        vmissing = v._FillValue
        if type(vints) is np.ma.core.MaskedArray:
            vints._sharedmask = False   # this will be the default behaviour with Numpy 1.12
        vints[vints==vmissing] = None
        self.channels[self.getKey(key, name)] = Channel(name, vints, vmissing, v)
        pass

    def decodeBitsChannel(self, name: str, key: str = ""):
        v = self.rootgrp.variables[name]
        vstr = chartostring(v[:]).tostring()
        vstr = vstr.decode("US-ASCII")
        # 1 is good, everything else is bad
        vstr = re.sub('[023456789]', '0', vstr)
        bits = BitString(bin="0b"+vstr)
        vmissing = v._FillValue
        self.channels[self.getKey(key, name)] = Channel(name, bits, vmissing, v)   # add as a sequence of bits, which is more efficient
        pass

    def getChannelUnits(self, name: str) -> str:
        v = self.rootgrp.variables[name]
        return v.units
        pass

    def channelExists(self, name: str) -> bool:
        return name in self.rootgrp.variables
        pass

    def channelHasNonMaskedValues(self, name: str) -> bool:
        v = self.rootgrp.variables[name]
        vfloats = v[:]
        notAllMasked = vfloats.count() > 0
        return notAllMasked
        pass

    def channelHasQCOKValues(self, name: str) -> bool:
        v = self.rootgrp.variables[name]
        values = v[:]
        nonMasked = values[values.mask == False]
        someQCOK = np.count_nonzero(nonMasked == b'1') > 0
        return someQCOK
        pass
