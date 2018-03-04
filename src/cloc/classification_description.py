'''
Created on 3 Mar. 2018

@author: oliver
'''

class ClassificationError(Exception):
    pass

class ClassificationDescription(object):
    '''
    classdocs
    '''


    def __init__(self):
        '''
        Constructor
        '''
        self._root = {}
        self._current_section = None
    
    def add_descriptions(self, descriptions):
        '''
        Add a description map to the current description.
        
        Incoming sections should overwrite existing sections.  Validate that overall description is valid, throw if not.
        '''
        self._root.update(descriptions)
        self.validate()
    
    def validate(self):
        '''Validate description sanity, throw if overall description is invalid.'''
        for name, desc in self._root.iteritems():
            self._validate_section(name, desc)
    
    def _validate_section(self, name, desc):
        '''Recursively validate a description and its sub-descriptions.'''
        
            # TODO: validate classifications/tags?  Do reporters need semantic knowledge about them?