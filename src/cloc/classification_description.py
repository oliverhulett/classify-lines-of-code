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
        self._merge(self._root, descriptions)
        self.validate()

    def _merge(self, root, descriptions):
        for name, desc in descriptions.iteritems():
            if hasattr(desc, 'iteritems') and name in root:
                ## desc is a dict() and it's key already exists in root, merge it recursively.
                self._merge(root[name], desc)
            else:
                ## desc is a scalar (replace it in root) or it's key doesn't exist in root (so add it.)
                root[name] = desc

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

        if ('entry_regex' in desc) and ('exit_regex' not in desc):
            raise ClassificationDescriptionError(
                "A ClassificationDescription with an entry_regex must also have an exit_regex: {}".format(name)
            )
        if ('exit_regex' in desc) and ('entry_regex' not in desc):
            raise ClassificationDescriptionError(
                "A ClassificationDescription with an exit_regex must also have an entry_regex: {}".format(name)
            )

        if 'subsections' in desc:
            if 'line_regex' in desc:
                raise ClassificationDescriptionError(
                    "A ClassificationDescription with subsections must not have a line_regex: {}".format(name)
                )
            if 'entry_regex' not in desc or 'exit_regex' not in desc:
                raise ClassificationDescriptionError(
                    "A ClassficationDescription with subsections must have entry_regex and exit_regex: {}".format(name)
                )
        else:
            if 'classifications' not in desc:
                raise ClassificationDescriptionError(
                    "A ClassficationDescription must have a classification: {}".format(name)
                )
