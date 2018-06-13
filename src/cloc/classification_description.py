"""
Created on 3 Mar. 2018

@author: oliver
"""

import re


class ClassificationDescriptionError(Exception):
    def __init__(self, error, description_path):
        self.error = error
        self.description_path = description_path
        super(ClassificationDescriptionError, self).__init__(error + ": {}".format("/".join(description_path)))


class Matcher(object):
    (RE_TYPE_LINE, RE_TYPE_ENTRY, RE_TYPE_EXIT) = range(3)

    @classmethod
    def type_to_str(cls, t):
        if t == cls.RE_TYPE_ENTRY:
            return "entry"
        if t == cls.RE_TYPE_EXIT:
            return "exit"
        if t == cls.RE_TYPE_LINE:
            return "line"

    def __init__(self, t, path, regex, classifications):
        self.type = t
        self.description_path = path
        self.regex_str = regex
        self.classifications = classifications
        self.regex = re.compile(self.regex_str)

    def __eq__(self, other):
        if len(self.description_path) != len(other.description_path):
            return False
        for i in xrange(len(self.description_path)):
            if self.description_path[i] != other.description_path[i]:
                return False
        return self.type == other.type

    def __lt__(self, other):
        return str(self) < str(other)

    def __str__(self):
        return "/".join(self.description_path) + ":" + Matcher.type_to_str(self.type)

    def matches(self, line):
        return self.regex.matches(line)


class ClassificationDescription(object):
    """
    classdocs
    """

    def __init__(self):
        """
        Constructor
        """
        self._descriptions = {}
        self._active_matchers = []

    def add_descriptions(self, descriptions):
        """
        Add a description map to the current description.
        
        Incoming sections should overwrite existing sections.  Validate that overall description is valid, throw if not.
        """
        self._merge(self._descriptions, descriptions)
        self.validate()

    def _merge(self, root, descriptions):
        for name, desc in descriptions.iteritems():
            if hasattr(desc, "iteritems") and name in root:
                ## desc is a dict() and it's key already exists in root, merge it recursively.
                self._merge(root[name], desc)
            else:
                ## desc is a scalar (replace it in root) or it's key doesn't exist in root (so add it.)
                root[name] = desc

    def validate(self):
        """Validate description sanity, throw if overall description is invalid."""
        for name, desc in self._descriptions.iteritems():
            self._validate_section([], name, desc)

    def _validate_section(self, path, name, desc):
        """Recursively validate a description and its sub-descriptions."""
        if "based_on" in desc:
            if desc["based_on"] not in self._descriptions:
                raise ClassificationDescriptionError(
                    "A referenced ClassificationDescription does not exist", path + [name]
                )
            for k, v in self._descriptions[desc["based_on"]].iteritems():
                if k not in desc:
                    desc[k] = v

        if (len(path) == 0) and ("path_regex" not in desc):
            raise ClassificationDescriptionError("A top level ClassificationDescription must have a path_regex", [name])

        if ("entry_regex" in desc) and ("exit_regex" not in desc):
            raise ClassificationDescriptionError(
                "A ClassificationDescription with an entry_regex must also have an exit_regex", path + [name]
            )
        if ("exit_regex" in desc) and ("entry_regex" not in desc):
            raise ClassificationDescriptionError(
                "A ClassificationDescription with an exit_regex must also have an entry_regex", path + [name]
            )

        if ("line_regex" not in desc) and ("entry_regex" not in desc) and ("exit_regex" not in desc):
            raise ClassificationDescriptionError(
                "A ClassificationDescription must have either a line_regex or an entry_regex and an exit_regex",
                path + [name],
            )

        if "subsections" in desc:
            if "line_regex" in desc:
                raise ClassificationDescriptionError(
                    "A ClassificationDescription with subsections must not have a line_regex", path + [name]
                )
            if "entry_regex" not in desc or "exit_regex" not in desc:
                raise ClassificationDescriptionError(
                    "A ClassificationDescription with subsections must have an entry_regex and an exit_regex",
                    path + [name],
                )
            for n, d in desc["subsections"].iteritems():
                self._validate_section(path + [name], n, d)
        else:
            if "classifications" not in desc:
                raise ClassificationDescriptionError(
                    "A ClassificationDescription must have a classification or subsections", path + [name]
                )

    def get_matchers_for_file(self, filename):
        self._active_matchers = []
        for name, desc in self._descriptions.iteritems():
            match = re.search(desc["path_regex"], filename)
            if match:
                classifications = desc["classifications"] if "classifications" in desc else []
                if "line_regex" in desc:
                    self._active_matchers.append(
                        Matcher(Matcher.RE_TYPE_LINE, [name], desc["line_regex"], classifications)
                    )
                if "entry_regex" in desc:
                    self._active_matchers.append(
                        Matcher(Matcher.RE_TYPE_ENTRY, [name], desc["entry_regex"], classifications)
                    )
        return self._active_matchers

    def get_next_matchers(self, *matched):
        for match in matched:
            if match.type == Matcher.RE_TYPE_ENTRY:
                self._get_next_matchers_from_entry(match)
            if match.type == Matcher.RE_TYPE_EXIT:
                self._get_next_matchers_from_exit(match)
        return self._active_matchers

    def _get_description(self, path):
        d = self._descriptions
        for p in path:
            d = d[p]
        return d

    def _get_next_matchers_from_entry(self, match):
        self._active_matchers.remove(match)
        d = self._get_description(match.description_path)
        self._active_matchers.append(
            Matcher(Matcher.RE_TYPE_EXIT, match.description_path, d["exit_regex"], match.classifications)
        )
        if "subsections" in d:
            for name, sub_d in d["subsections"].iteritems():
                classifications = match.classifications + sub_d["classifications"] if "classifications" in sub_d else []
                path = match.description_path + [name]
                if "line_regex" in sub_d:
                    self._active_matchers.append(
                        Matcher(Matcher.RE_TYPE_LINE, path, sub_d["line_regex"], classifications)
                    )
                if "entry_regex" in sub_d:
                    self._active_matchers.append(
                        Matcher(Matcher.RE_TYPE_ENTRY, path, sub_d["entry_regex"], classifications)
                    )

    def _get_next_matchers_from_exit(self, match):
        p = "/".join(match.description_path)
        for m in self._active_matchers[:]:
            if "/".join(m.description_path).startswith(p):
                self._active_matchers.remove(m)
        d = self._get_description(match.description_path)
        self._active_matchers.append(
            Matcher(Matcher.RE_TYPE_ENTRY, match.description_path, d["entry_regex"], match.classifications)
        )
