"""
    Class to write a Bufr file for Argo data in a NetCDF file
"""

from bitstring import BitArray, Bits
from bufr.BufrFXYString import BufrFXYString
from bufr.BufrFXYInt import BufrFXYInt
from bufr.BufrFXYDouble import BufrFXYDouble
from bufr.BufrFXYDoubleReplication import BufrFXYDoubleReplication
from bufr.BufrFXYIntReplication import BufrFXYIntReplication
from bufr.BufrFXYTemplate import BufrFXYTemplate
from bufr.BufrFXYDelayedReplication import BufrFXYDelayedReplication
from bufr.BufrBitArray import BufrBitArray
from bufr.BufrEncoder import BufrEncoder
from channels.Channel import Channel
from datetime import datetime
import numpy as np
import pdb
from typing import Tuple

class ArgoNetCDFBufrEncoder(BufrEncoder):
    """Class to write a Bufr file for Argo data in a NetCDF file"""

    # https://archimer.ifremer.fr/doc/00187/29825/68654.pdf table 16
    verticalSamlingSchemes = (
            'Primary sampling:',
            'Near-surface sampling:',
            'Bounce sampling:',
            )

    # https://www.wmo.int/pages/prog/www/WMOCodes/WMO306_vI2/LatestVERSION/WMO306_vI2_BUFRCREX_CodeFlag_en.pdf 0 08 034
    measurementQualifiers = (
            (0, 'Secondary sampling: averaged'),
            (1, 'Secondary sampling: discrete'),
            (2, 'Secondary sampling: mixed'),
            (3, 'Near-surface sampling: averaged, pumped'),
            (4, 'Near-surface sampling: averaged, unpumped'),
            (5, 'Near-surface sampling: discrete, pumped'),
            (6, 'Near-surface sampling: discrete, unpumped'),
            (7, 'Near-surface sampling: mixed, pumped'),
            (8, 'Near-surface sampling: mixed, unpumped'),
            )

    def __init__(self, argoChannels: dict):
        super(ArgoNetCDFBufrEncoder, self).__init__()

        #pdb.set_trace()

        # main bufr sequence
        self.addDataDescription("TemplateArgo", BufrFXYTemplate(3, 15, 3))

        self.addDataDescription("WMOMarineObservingPlatform",BufrFXYInt(0, 1, 87, 23, True))
        self.addDataDescription("ObservingPlatformManufacturesModel",BufrFXYString(0, 1, 85, 20, True))
        self.addDataDescription("ObservingPlatformManufacturesSerialNumber",BufrFXYString(0, 1, 86, 32, True))
        self.addDataDescription("BuoyType",BufrFXYInt(0, 2, 36, 2, True))
        self.addDataDescription("DataCollectionAndOrLocationSystem",BufrFXYInt(0, 2, 148, 5, True))
        self.addDataDescription("DataTypeOfBuoy",BufrFXYInt(0, 2, 149, 6, True))
        self.addDataDescription("FloatCycleNumber",BufrFXYInt(0, 22, 55, 10, True))
        self.addDataDescription("DirectionOfProfile",BufrFXYInt(0, 22, 56, 2, True))
        self.addDataDescription("InstrumentTypeForWaterTemperatureProfileMeasurement",BufrFXYInt(0, 22, 67, 10, True))

        #self.addDataDescription("TemplateDate", BufrFXYTemplate(3, 1, 11))
        self.addDataDescription("Year",BufrFXYInt(0, 4, 1, 12, True))
        self.addDataDescription("Month",BufrFXYInt(0, 4, 2, 4, True))
        self.addDataDescription("Day",BufrFXYInt(0, 4, 3, 6, True))

        #self.addDataDescription("TemplateTime", BufrFXYTemplate(3, 1, 12))
        self.addDataDescription("Hour",BufrFXYInt(0, 4, 4, 5, True))
        self.addDataDescription("Minute",BufrFXYInt(0, 4, 5, 6, True))

        #self.addDataDescription("TemplatePosition", BufrFXYTemplate(3, 1, 21))
        self.addDataDescription("LatitudeCoarse",BufrFXYDouble(0, 5, 1, 5.0, 9000000.0, 25, True))
        self.addDataDescription("LongitudeCoarse",BufrFXYDouble(0, 6, 1, 5.0, 18000000.0, 26, True))

        self.addDataDescription("Position_QualifierForGTSPPQualityClass",BufrFXYInt(0, 8, 80, 6, True))
        self.addDataDescription("Position_GlobalGTSPPQualityClass",BufrFXYInt(0, 33, 50, 4, True))

        # replication descriptors
        self.addDataDescription("DelayedReplication", BufrFXYDelayedReplication(9, True)) # replication of next 9 items
        self.addDataDescription("ExtendedDelayedReplication",BufrFXYInt(0, 31, 2, 16, True))   # number of replications (i.e. levels)

        # replicated section
        self.addDataDescription("WaterPressure",BufrFXYDoubleReplication(0, 7, 65, -3.0, 0.0, 17, True))
        self.addDataDescription("WaterPressure_QualifierForGTSPPQualityClass",BufrFXYIntReplication(0, 8, 80, 6, True))    # pressure at a level = 10
        self.addDataDescription("WaterPressure_GlobalGTSPPQualityClass",BufrFXYIntReplication(0, 33, 50, 4, True))

        self.addDataDescription("SeaWaterTemperature",BufrFXYDoubleReplication(0, 22, 45, 3.0, 0.0, 19, True))
        self.addDataDescription("SeaWaterTemperature_QualifierForGTSPPQualityClass",BufrFXYIntReplication(0, 8, 80, 6, True))    # water temperature at a level = 11
        self.addDataDescription("SeaWaterTemperature_GlobalGTSPPQualityClass",BufrFXYIntReplication(0, 33, 50, 4, True))

        self.addDataDescription("Salinity",BufrFXYDoubleReplication(0, 22, 64, 3.0, 0.0, 17, True))
        self.addDataDescription("Salinity_QualifierForGTSPPQualityClass",BufrFXYIntReplication(0, 8, 80, 6, True))   # salinity at a level = 12
        self.addDataDescription("Salinity_GlobalGTSPPQualityClass",BufrFXYIntReplication(0, 33, 50, 4, True))

        # add any additional bufr templates for other Argo profiles
        self.additionalProfiles = []
        numProfiles = argoChannels["N_PROF"].value
        #numProfiles = 1 #//??
        if numProfiles>1:
            samplingSchemesInFile = argoChannels["VERTICAL_SAMPLING_SCHEME"].value
            # check that primary is first
            if not samplingSchemesInFile[0].startswith(self.verticalSamlingSchemes[0]):
                raise Exception("First vertical sampling scheme is not a primary")
            # add profiles for secondary profiles
            for profileNo, samplingScheme in enumerate(samplingSchemesInFile):
                if samplingScheme.startswith(self.verticalSamlingSchemes[1]):
                    profileNamePrefix = "Complimentary" + str(profileNo)    # used for keeping the keys unique for all profiles
                    # save a list of tuples for the additional profiles, for use when adding the data
                    salinity = argoChannels["PSAL"].value[profileNo]
                    salinityAvailable = salinity.count() > 0    # include salinity if there are some values which are not masked
                    self.additionalProfiles.append((profileNamePrefix, profileNo, samplingScheme.rstrip(), salinityAvailable))
                    if salinityAvailable:
                        self.addSupplementaryPressureSalinityProfile(profileNamePrefix)
                    else:
                        self.addSupplementaryPressureProfile(profileNamePrefix)
                pass
            pass

        self.DissolvedOxygenProfile = ""
        # add dissolved oxygen profile?
        if "DOXY" in argoChannels:
            dissolvedOxygen = argoChannels["DOXY"].value[0]
            oxygenAvailable = dissolvedOxygen.count() > 0    # include oxygen if there are some values which are not masked
            if oxygenAvailable:
                self.DissolvedOxygenProfile = "DissolvedOxygen"
                self.addDissolvedOxygenProfile(self.DissolvedOxygenProfile)
                pass
            pass

        pass

    # Bufr profile 3 06 018
    def addSupplementaryPressureSalinityProfile(self, key: str):
        self.addDataDescription(key + "TemplatePressureTempSalinity", BufrFXYTemplate(3, 6, 18))

        self.addDataDescription(key + "IndicatorForDigitization",BufrFXYInt(0, 2, 32, 2, True))
        self.addDataDescription(key + "MeasurementType",BufrFXYInt(0, 8, 34, 4, True))

        # replication descriptors
        self.addDataDescription(key + "DelayedReplication", BufrFXYDelayedReplication(9, True)) # replication of next 9 items
        self.addDataDescription(key + "ExtendedDelayedReplication",BufrFXYInt(0, 31, 2, 16, True))   # number of replications (i.e. levels)

        # replicated section
        self.addDataDescription(key + "WaterPressure",BufrFXYDoubleReplication(0, 7, 65, -3.0, 0.0, 17, True))
        self.addDataDescription(key + "WaterPressure_QualifierForGTSPPQualityClass",BufrFXYIntReplication(0, 8, 80, 6, True))   # pressure at a level = 10
        self.addDataDescription(key + "WaterPressure_GlobalGTSPPQualityClass",BufrFXYIntReplication(0, 33, 50, 4, True))

        self.addDataDescription(key + "SeaWaterTemperature",BufrFXYDoubleReplication(0, 22, 45, 3.0, 0.0, 19, True))
        self.addDataDescription(key + "SeaWaterTemperature_QualifierForGTSPPQualityClass",BufrFXYIntReplication(0, 8, 80, 6, True))    # water temperature at a level = 11
        self.addDataDescription(key + "SeaWaterTemperature_GlobalGTSPPQualityClass",BufrFXYIntReplication(0, 33, 50, 4, True))

        self.addDataDescription(key + "Salinity",BufrFXYDoubleReplication(0, 22, 64, 3.0, 0.0, 17, True))
        self.addDataDescription(key + "Salinity_QualifierForGTSPPQualityClass",BufrFXYIntReplication(0, 8, 80, 6, True))   # salinity at a level = 12
        self.addDataDescription(key + "Salinity_GlobalGTSPPQualityClass",BufrFXYIntReplication(0, 33, 50, 4, True))

        # end marker?
        self.addDataDescription(key + "MeasurementTypeCancel",BufrFXYInt(0, 8, 34, 4, True))

        pass

    # Bufr profile 3 06 017
    def addSupplementaryPressureProfile(self, key: str):
        self.addDataDescription(key + "TemplatePressureTemp", BufrFXYTemplate(3, 6, 17))

        self.addDataDescription(key + "IndicatorForDigitization",BufrFXYInt(0, 2, 32, 2, True))
        self.addDataDescription(key + "MeasurementType",BufrFXYInt(0, 8, 34, 4, True))

        # replication descriptors
        self.addDataDescription(key + "DelayedReplication", BufrFXYDelayedReplication(6, True)) # replication of next 6 items
        self.addDataDescription(key + "ExtendedDelayedReplication",BufrFXYInt(0, 31, 2, 16, True))   # number of replications (i.e. levels)

        # replicated section
        self.addDataDescription(key + "WaterPressure",BufrFXYDoubleReplication(0, 7, 65, -3.0, 0.0, 17, True))
        self.addDataDescription(key + "WaterPressure_QualifierForGTSPPQualityClass",BufrFXYIntReplication(0, 8, 80, 6, True))   # pressure at a level = 10
        self.addDataDescription(key + "WaterPressure_GlobalGTSPPQualityClass",BufrFXYIntReplication(0, 33, 50, 4, True))

        self.addDataDescription(key + "SeaWaterTemperature",BufrFXYDoubleReplication(0, 22, 45, 3.0, 0.0, 19, True))
        self.addDataDescription(key + "SeaWaterTemperature_QualifierForGTSPPQualityClass",BufrFXYIntReplication(0, 8, 80, 6, True))    # water temperature at a level = 11
        self.addDataDescription(key + "SeaWaterTemperature_GlobalGTSPPQualityClass",BufrFXYIntReplication(0, 33, 50, 4, True))

        # end marker?
        self.addDataDescription(key + "MeasurementTypeCancel",BufrFXYInt(0, 8, 34, 4, True))
        pass

    # Bufr profile 3 06 037
    def addDissolvedOxygenProfile(self, key: str):
        self.addDataDescription(key + "TemplatePressureTemp", BufrFXYTemplate(3, 6, 37))

        # replication descriptors
        self.addDataDescription(key + "DelayedReplication", BufrFXYDelayedReplication(9, True)) # replication of next 9 items
        self.addDataDescription(key + "ExtendedDelayedReplication",BufrFXYInt(0, 31, 2, 16, True))   # number of replications (i.e. levels)

        # replicated section
        self.addDataDescription(key + "Depth",BufrFXYDoubleReplication(0, 7, 62, 0.0, 0.0, 17, True))
        self.addDataDescription(key + "Depth_QualifierForGTSPPQualityClass",BufrFXYIntReplication(0, 8, 80, 6, True))   # depth at a level = 13
        self.addDataDescription(key + "Depth_GlobalGTSPPQualityClass",BufrFXYIntReplication(0, 33, 50, 4, True))

        self.addDataDescription(key + "WaterPressure",BufrFXYDoubleReplication(0, 7, 65, -3.0, 0.0, 17, True))
        self.addDataDescription(key + "WaterPressure_QualifierForGTSPPQualityClass",BufrFXYIntReplication(0, 8, 80, 6, True))   # pressure at a level = 10
        self.addDataDescription(key + "WaterPressure_GlobalGTSPPQualityClass",BufrFXYIntReplication(0, 33, 50, 4, True))

        self.addDataDescription(key + "DissolvedOxygen",BufrFXYDoubleReplication(0, 22, 188, 3.0, 0.0, 19, True))
        self.addDataDescription(key + "DissolvedOxygen_QualifierForGTSPPQualityClass",BufrFXYIntReplication(0, 8, 80, 6, True))  # dissolved oxygen at a level = 16
        self.addDataDescription(key + "DissolvedOxygen_GlobalGTSPPQualityClass",BufrFXYIntReplication(0, 33, 50, 4, True))
        pass

    # this is called by the base class when it needs the data values
    def setData(self):

        # map the Bufr data description to the Argo channel name

        # meta data
        self.getDataDescription("WMOMarineObservingPlatform").setValue(self.channels["PLATFORM_NUMBER"].value)
        self.getDataDescription("ObservingPlatformManufacturesModel").setValue(self.channels["PLATFORM_TYPE"].value)
        self.getDataDescription("ObservingPlatformManufacturesSerialNumber").setValue(self.channels["FLOAT_SERIAL_NO"].value)
        self.getDataDescription("BuoyType").setValue(2) # sub-surface float = 2

        positioningSystem = self.channels["POSITIONING_SYSTEM"].value
        positioningSystems = {"ARGOS": 1, "GPS": 2, "IRIDIUM": 3}
        self.getDataDescription("DataCollectionAndOrLocationSystem").setValue(positioningSystems.get(positioningSystem, 7)) # default to 7

        self.getDataDescription("DataTypeOfBuoy").setValue(26) # Sub-surface ARGO float = 26
        self.getDataDescription("FloatCycleNumber").setValue(self.channels["CYCLE_NUMBER"].value)

        profileDirection = self.channels["DIRECTION"].value
        profileDirections = {"A": 0, "D": 1}
        self.getDataDescription("DirectionOfProfile").setValue(profileDirections.get(profileDirection, 3)) # default to 3

        self.getDataDescription("InstrumentTypeForWaterTemperatureProfileMeasurement").setValue(self.channels["WMO_INST_TYPE"].value)

        # date/time
        measurementDateTime = self.getMeasurementTime()
        self.getDataDescription("Year").setValue(measurementDateTime.year)
        self.getDataDescription("Month").setValue(measurementDateTime.month)
        self.getDataDescription("Day").setValue(measurementDateTime.day)
        self.getDataDescription("Hour").setValue(measurementDateTime.hour)
        self.getDataDescription("Minute").setValue(measurementDateTime.minute)

        # position
        self.getDataDescription("LatitudeCoarse").setValue(self.channels["LATITUDE"].value)
        self.getDataDescription("LongitudeCoarse").setValue(self.channels["LONGITUDE"].value)
        self.getDataDescription("Position_QualifierForGTSPPQualityClass").setValue(20)  # position = 20
        self.getDataDescription("Position_GlobalGTSPPQualityClass").setValue(self.channels["POSITION_QC"].value)

        # replicated section
        profile = 0
        pressure = self.channels["PRES"].value[profile]
        temperature = self.channels["TEMP"].value[profile]
        salinity = self.channels["PSAL"].value[profile]
        pressureQC = self.channels["PRES_QC"].value[profile]
        temperatureQC = self.channels["TEMP_QC"].value[profile]
        salinityQC = self.channels["PSAL_QC"].value[profile]

        #self.dumpChannel("Pressure", 3, pressure)
        #self.dumpChannel("Temperature", 3, temperature)
        #self.dumpChannel("Salinity", 3, salinity)

        [pressureValidPoints, temperatureValidPoints, salinityValidPoints, pressureValidPointsQC, temperatureValidPointsQC, salinityValidPointsQC] =\
           self.getValidData([pressure, temperature, salinity, pressureQC, temperatureQC, salinityQC])
        validPoints = pressureValidPoints.size

        print("\nMain profile")
        print("Pressure channel has " + str(validPoints) + " valid values out of " + str(pressure.size))
        print("Temperature channel has " + str(validPoints) + " valid values out of " + str(pressure.size))
        print("Salinity channel has " + str(validPoints) + " valid values out of " + str(pressure.size))

        levels = int(validPoints)
        self.getDataDescription("ExtendedDelayedReplication").setValue(levels)

        self.getDataDescription("WaterPressure").setValue(pressureValidPoints)  # Pa
        self.getDataDescription("WaterPressure_QualifierForGTSPPQualityClass").setValue([10] * levels)  # water pressure at a level = 10
        self.getDataDescription("WaterPressure_GlobalGTSPPQualityClass").setValue(pressureValidPointsQC)

        self.getDataDescription("SeaWaterTemperature").setValue(temperatureValidPoints)  # degC
        self.getDataDescription("SeaWaterTemperature_QualifierForGTSPPQualityClass").setValue([11] * levels)  # water temperature at a level = 11
        self.getDataDescription("SeaWaterTemperature_GlobalGTSPPQualityClass").setValue(temperatureValidPointsQC)

        self.getDataDescription("Salinity").setValue(salinityValidPoints)  # g/kg
        self.getDataDescription("Salinity_QualifierForGTSPPQualityClass").setValue([12] * levels)  # salinity at a level = 12
        self.getDataDescription("Salinity_GlobalGTSPPQualityClass").setValue(salinityValidPointsQC)

        # add data to additional bufr sections for remaining profiles
        for additionalProfile in enumerate(self.additionalProfiles):

            key = additionalProfile[1][0]
            profile = additionalProfile[1][1]
            samplingScheme = additionalProfile[1][2]
            salinityAvailable = additionalProfile[1][3]

            self.getDataDescription(key + "IndicatorForDigitization").setValue(0)
            # match measurement type from profile
            measurementType = [self.measurementQualifiers[i] for i, measurementQualifier in enumerate(self.measurementQualifiers) if samplingScheme.startswith(measurementQualifier[1])]
            if measurementType == []:
                raise Exception("Can't find measurement qualifier for " +samplingScheme)
            self.getDataDescription(key + "MeasurementType").setValue(measurementType[0][0])

            pressure = self.channels["PRES"].value[profile]
            temperature = self.channels["TEMP"].value[profile]
            salinity = self.channels["PSAL"].value[profile]
            pressureQC = self.channels["PRES_QC"].value[profile]
            temperatureQC = self.channels["TEMP_QC"].value[profile]
            salinityQC = self.channels["PSAL_QC"].value[profile]

            [pressureValidPoints, temperatureValidPoints, salinityValidPoints, pressureValidPointsQC, temperatureValidPointsQC, salinityValidPointsQC] =\
               self.getValidData([pressure, temperature, salinity, pressureQC, temperatureQC, salinityQC])
            validPoints = pressureValidPoints.size

            print("\nProfile " + samplingScheme)
            print("Pressure channel has " + str(validPoints) + " valid values out of " + str(pressure.size))
            print("Temperature channel has " + str(validPoints) + " valid values out of " + str(pressure.size))
            print("Salinity channel has " + str(validPoints) + " valid values out of " + str(pressure.size))
            
            levels = int(validPoints)
            self.getDataDescription(key + "ExtendedDelayedReplication").setValue(levels)

            self.getDataDescription(key + "WaterPressure").setValue(pressureValidPoints)  # Pa
            self.getDataDescription(key + "WaterPressure_QualifierForGTSPPQualityClass").setValue([10] * levels)  # water pressure at a level = 10
            self.getDataDescription(key + "WaterPressure_GlobalGTSPPQualityClass").setValue(pressureValidPointsQC)

            self.getDataDescription(key + "SeaWaterTemperature").setValue(temperatureValidPoints)  # degC
            self.getDataDescription(key + "SeaWaterTemperature_QualifierForGTSPPQualityClass").setValue([11] * levels)  # water temperature at a level = 11
            self.getDataDescription(key + "SeaWaterTemperature_GlobalGTSPPQualityClass").setValue(temperatureValidPointsQC)

            if salinityAvailable:
                self.getDataDescription(key + "Salinity").setValue(salinityValidPoints)  # g/kg
                self.getDataDescription(key + "Salinity_QualifierForGTSPPQualityClass").setValue([12] * levels)  # salinity at a level = 12
                self.getDataDescription(key + "Salinity_GlobalGTSPPQualityClass").setValue(salinityValidPointsQC)

            self.getDataDescription(key + "MeasurementTypeCancel").setValue(None)

            pass

        # add data to dissolved oxygen profile, if it is available
        if self.DissolvedOxygenProfile:

            key = self.DissolvedOxygenProfile

            pressure = self.channels["PRES"].value[profile]
            dissolvedOxygen = self.channels["DOXY"].value[profile]
            pressureQC = self.channels["PRES_QC"].value[profile]
            dissolvedOxygenQC = self.channels["DOXY_QC"].value[profile]

            [pressureValidPoints, dissolvedOxygenValidPoints, pressureValidPointsQC, dissolvedOxygenValidPointsQC] =\
               self.getValidData([pressure, dissolvedOxygen, pressureQC, dissolvedOxygenQC])
            validPoints = pressureValidPoints.size

            print("Pressure channel has " + str(validPoints) + " valid values out of " + str(pressure.size))
            print("Dissolved oxygen channel has " + str(validPoints) + " valid values out of " + str(dissolvedOxygen.size))

            levels = int(validPoints)
            profile = 0 # oxygen will always be profile 0
            self.getDataDescription(key + "ExtendedDelayedReplication").setValue(levels)

            # check dimensions are OK
            if pressure.size != levels:
                raise Exception("The number of levels in the main file (" + str(levels) + ") and bio file (" + str(pressure.count) + ") must be the same")
            if pressure.size != dissolvedOxygen.size:
                raise Exception("The number of levels in the Pressure channel (in the main file) and Oxygen channel (in the bio file) must be the same")

            self.getDataDescription(key + "Depth").setValue([None] * levels)  # degC
            self.getDataDescription(key + "Depth_QualifierForGTSPPQualityClass").setValue([None] * levels)  # depth at a level = 13
            self.getDataDescription(key + "Depth_GlobalGTSPPQualityClass").setValue([None] * levels)

            self.getDataDescription(key + "WaterPressure").setValue(pressureValidPoints)  # Pa
            self.getDataDescription(key + "WaterPressure_QualifierForGTSPPQualityClass").setValue([10] * levels)  # water pressure at a level = 10
            self.getDataDescription(key + "WaterPressure_GlobalGTSPPQualityClass").setValue(pressureValidPointsQC)

            self.getDataDescription(key + "DissolvedOxygen").setValue(dissolvedOxygenValidPoints)  # umol/kg
            self.getDataDescription(key + "DissolvedOxygen_QualifierForGTSPPQualityClass").setValue([16] * levels)  # dissolved oxygen at a level = 16
            self.getDataDescription(key + "DissolvedOxygen_GlobalGTSPPQualityClass").setValue(dissolvedOxygenValidPointsQC)

        pass

    def getMeasurementTime(self) -> datetime:
        # date/time
        julianDay1950 = self.channels["JULD"].value
        julianDay1970 = (julianDay1950 - 7305) * 86400  # days between 1950 and 1970
        measurementDateTime = datetime.utcfromtimestamp(julianDay1970)
        return measurementDateTime
        pass

    # get the Bufr data from the channel data passed
    def getMessage(self, argoChannels: dict) -> BitArray:
        self.channels = argoChannels
        buffer = BufrBitArray()
        measurementDateTime = self.getMeasurementTime()
        self.writeMessage(buffer, measurementDateTime, 74) # Exeter = 74
        return buffer
        pass
    
    def dumpChannel(self, name: str, decimalPlaces:int, channel):
        formatString = "{0:." + str(decimalPlaces) + "f}"
        f = open(name + ".txt", "w")
        for i in range(0, channel.count()):
            floatStr = formatString.format(channel[i])
            f.write(floatStr+"\n")
        pass

    def getValidData(self, inputChannels:Tuple) -> Tuple:
        # check input
        size = -1
        for channel in inputChannels:
            if size != -1:
                if size != channel.size:
                    raise Exception("All inputs must be the same size")
            size = channel.size

        # find valid values
        validPoints = 0;
        for i in range(size):
            validPoint = True
            for channel in inputChannels:
                if np.ma.is_masked(channel) and channel.mask[i]:
                    validPoint = False
            if validPoint:
                validPoints = validPoints + 1

        # allocate new arrays
        result = []
        for channel in inputChannels:
            result.append(np.empty(validPoints, channel.dtype))

        # fill in arrays
        validPoints = 0
        for i in range(size):
            validPoint = True
            for channel in inputChannels:
                if np.ma.is_masked(channel) and channel.mask[i]:
                    validPoint = False
            if validPoint:
                for idx, channel in enumerate(inputChannels):
                    result[idx][validPoints] = channel.data[i]
                validPoints = validPoints + 1

        return result