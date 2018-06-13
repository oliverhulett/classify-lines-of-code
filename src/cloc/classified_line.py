"""
Created on 2 Mar. 2018

@author: oliver
"""


class ClassifiedLine(object):
    """
    classdocs
    """

    def __init__(self, filename, line_number, classification):
        """
        Constructor
        """
        self.filename = filename
        self.line_number = line_number
        self.classification = classification
        self._secondary_classifications = []

    def add_secondary_classification(self, classification):
        """Add secondary classification.  Mostly for debugging purposes"""
        self._secondary_classifications.append(classification)
