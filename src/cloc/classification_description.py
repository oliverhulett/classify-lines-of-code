'''
Created on 3 Mar. 2018

@author: oliver
'''


class ClassificationDescriptionError(Exception):
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
        if 'based_on' in desc:
            if desc['based_on'] not in self._root:
                raise ClassificationDescriptionError(
                    "A referenced ClassficationDescription does not exist: {}".format(name)
                )
            for k, v in self._root[desc['based_on']].iteritems():
                if k not in desc:
                    desc[k] = v
        if 'classifications' not in desc:
            raise ClassificationDescriptionError(
                "A ClassficationDescription must have a classification: {}".format(name)
            )
