"""
    Class to hold channel data
"""

class Channel(object):
    """Class to hold channel data"""

    #def __init__(self, name: str, value: object, missingValue: object, originalValue: object):
    def __init__(self, name, value, missingValue, originalValue):
        self.name = name
        self.value = value
        self.originalValue = originalValue
        self.missingValue = missingValue


