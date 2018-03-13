'''
Created on 3 Mar. 2018

@author: oliver
'''

import re


class ClassificationDescriptionError(Exception):
    pass


class Matcher(object):
    (
        RE_TYPE_LINE,
        RE_TYPE_ENTRY,
        RE_TYPE_EXIT,
    ) = range(3)
    
    def __init__(self, t, path, regex):
        self.type = t
        self.description_path = path
        self.regex_str = regex
        self.regex = re.compile(self.regex_str)
    
    def __eq__(self, other):
        return self.type == other.type and self.description_path == other.description_path and self.regex_str == other.regex_str
    
    def matches(self, line):
        return self.regex.matches(line)


class ClassificationDescription(object):
    '''
    classdocs
    '''

    def __init__(self):
        '''
        Constructor
        '''
        self._descriptions = {}
        self._active_matchers = []

    def add_descriptions(self, descriptions):
        '''
        Add a description map to the current description.
        
        Incoming sections should overwrite existing sections.  Validate that overall description is valid, throw if not.
        '''
        self._merge(self._descriptions, descriptions)
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
        for name, desc in self._descriptions.iteritems():
            self._validate_section(name, desc)

    def _validate_section(self, name, desc):
        '''Recursively validate a description and its sub-descriptions.'''
        if 'based_on' in desc:
            if desc['based_on'] not in self._descriptions:
                raise ClassificationDescriptionError(
                    "A referenced ClassficationDescription does not exist: {}".format(name)
                )
            for k, v in self._descriptions[desc['based_on']].iteritems():
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
    
    def get_matchers_from_file(self, filename):
        self._active_matchers = []
        for name, desc in self._descriptions.iteritems():
            match = re.search(desc['path_regex'], filename)
            if match:
                if 'line_regex' in desc:
                    self._active_matchers.append(Matcher(Matcher.RE_TYPE_LINE, [name], desc['line_regex']))
                if 'entry_regex' in desc:
                    self._active_matchers.append(Matcher(Matcher.RE_TYPE_ENTRY, [name], desc['entry_regex']))
        return self._active_matchers
    
    def get_next_matchers(self, *matched):
        for match in matched:
            
