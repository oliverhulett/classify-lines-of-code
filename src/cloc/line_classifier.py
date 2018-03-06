'''
Created on 3 Mar. 2018

@author: oliver
'''


class LineClassifier(object):
    '''
    classdocs
    '''

    def __init__(self, classification_description, line_collection):
        '''
        Constructor
        '''
        self._descr = classification_description
        self._collection = line_collection
