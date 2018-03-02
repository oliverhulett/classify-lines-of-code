'''
Created on 2 Mar. 2018

@author: oliver
'''

class ClassifiedLine(object):
    '''
    classdocs
    '''


    def __init__(self, filename, line_number, classifications=[], tags=[]):
        '''
        Constructor
        '''
        self.filename = filename
        self.line_number = line_number
        self.classifications = classifications
        self.tags = tags