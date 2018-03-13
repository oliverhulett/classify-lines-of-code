'''
Created on 3 Mar. 2018

@author: oliver
'''
import sys

import unittest
import pytest

from cloc.classification_description import ClassificationDescription, ClassificationDescriptionError


class TestClassificationDescription(unittest.TestCase):
    def setUp(self):
        self.description = ClassificationDescription()
        self.d = {
            "top-level-1": {
                "path_regex": 'path-regex-1',
                "line_regex": 'line-regex-1',
                "classifications": ['classification-1'],
            },
            "top-level-2": {
                "path_regex": 'path-regex-2',
                "entry_regex": 'entry-regex-2',
                "exit_regex": 'exit-regex-2',
                "classifications": ['classification-2'],
            },
            "top-level-3": {
                "path_regex": 'path-regex-3',
                "entry_regex": 'entry-regex-3',
                "exit_regex": 'exit-regex-3',
                "subsections": {
                    "nested-1": {
                        "line_regex": 'line-regex-3-1',
                        "classifications": ['classification-3-1'],
                    },
                    "nested-2": {
                        "entry_regex": 'entry-regex-3-2',
                        "exit_regex": 'exit-regex-3-2',
                        "classifications": ['classification-3-2'],
                    },
                },
            },
        }

    def tearDown(self):
        pass

    def test_add_description_good(self):
        try:
            self.description.add_descriptions(self.d)
            assert self.description._descriptions == self.d
        except Exception as e:
            pytest.fail("Unexpected exception raised: " + str(e))

    def test_add_descriptions_empty(self):
        with pytest.raises(ClassificationDescriptionError,
                           match="A top level ClassficationDescription must have a path_regex: name"):
            self.description.add_descriptions({
                "name": {},
            })
        try:
            self.description.add_descriptions({})
            assert self.description._descriptions == {}
        except Exception as e:
            pytest.fail("Unexpected exception raised: " + str(e))
    
    def test_add_descriptions_top_level_no_path_regex(self):
        for name in self.d.iterkeys():
            descriptions = self.d
            with pytest.raises(ClassificationDescriptionError, match="A top level ClassificationDescription must specify a path_regex: " + name):
                del descriptions[name]["path_regex"]
                self.description.add_descriptions(descriptions)

    def test_add_descriptions_line_regex_or_entry_exit(self):
        with pytest.raises(ClassificationDescriptionError,
                           match="A ClassificationDescription must have either a line_regex or entry and exit regexes: top-level-1"):
            del self.d["top-level-1"]["line_regex"]
            self.description.add_descriptions(self.d)
        with pytest.raises(ClassificationDescriptionError,
                           match="A ClassificationDescription must have either a line_regex or entry and exit regexes: top-level-2"):
            del self.d["top-level-2"]["entry_regex"]
            del self.d["top-level-2"]["exit_regex"]
            self.description.add_descriptions(self.d)

    def test_add_descriptions_line_regex_no_classifications(self):
        with pytest.raises(ClassificationDescriptionError,
                           match="A ClassficationDescription must have a classification or subsections: top-level-1"):
            del self.d["top-level-1"]["classifications"]
            self.description.add_descriptions(self.d)

    def test_add_descriptions_entry_and_exit_regexes_no_classifications(self):
        with pytest.raises(ClassificationDescriptionError,
                           match="A ClassficationDescription must have a classification or subsections: top-level-2"):
            del self.d["top-level-2"]["classifications"]
            self.description.add_descriptions(self.d)

    def test_add_descriptions_subsections_and_line_regex(self):
        with pytest.raises(ClassificationDescriptionError,
                           match="A ClassificationDescription with subsections must not have a line_regex: top-level-1"):
            self.d["top-level-1"]["subsections"] = {
                "name": {
                    "line_regex": 'asdf',
                    "classifications": ['code'],
                },
            }
            self.description.add_descriptions(self.d)
    
    def test_add_descriptions_subsections_require_entry_and_exit_regexes(self):
        with pytest.raises(
                ClassificationDescriptionError,
                match="A ClassficationDescription with subsections must have entry_regex and exit_regex: top-level-3"):
            del self.d["top-level-3"]["entry_regex"]
            del self.d["top-level-3"]["exit_regex"]
            self.description.add_descriptions(self.d)

    def test_add_descriptions_entry_regex_without_exit_regex(self):
        with pytest.raises(ClassificationDescriptionError,
                           match="A ClassificationDescription with an entry_regex must also have an exit_regex: top-level-2"):
            del self.d["top-level-2"]["exit_regex"]
            self.description.add_descriptions(self.d)

    def test_add_descriptions_exit_regex_without_entry_regex(self):
        with pytest.raises(ClassificationDescriptionError,
                           match="A ClassificationDescription with an exit_regex must also have an entry_regex: top-level-2"):
            del self.d["top-level-2"]["entry_regex"]
            self.description.add_descriptions(self.d)

    def test_add_descriptions_based_on_does_not_exist(self):
        with pytest.raises(ClassificationDescriptionError,
                           match="A referenced ClassficationDescription does not exist: doctag"):
            self.description.add_descriptions({
                "doctag": {
                    "based_on": "docstring_multiline",
                    "line_regex": '(^|\\s)@[a-z]+:\\s',
                },
            })

    def test_add_descriptions_based_on(self):
        d1 = {
            "docstring_singleline": {
                "path_regex": '\\.py$',
                "line_regex": '^\\s*(\'\'\'|""").*\\1\\s*$',
                "classifications": ["Comments"],
            },
            "docstring_multiline": {
                "path_regex": '\\.py$',
                "entry_regex": '^\\s*(\'\'\'|""")',
                "exit_regex": '\\1\\s*$',
                "classifications": ["Comments"],
            },
        }
        d2 = {
            "doctag": {
                "based_on": "docstring_multiline",
                "line_regex": '(^|\\s)@[a-z]+:\\s',
            },
        }
        try:
            self.description.add_descriptions(d1)
            self.description.add_descriptions(d2)
            d3 = d1["docstring_multiline"]
            d3.update(d2["doctag"])
            assert self.description._descriptions == {
                "docstring_singleline": d1["docstring_singleline"],
                "docstring_multiline": d1["docstring_multiline"],
                "doctag": d3
            }
        except Exception as e:
            pytest.fail("Unexpected exception raised: " + str(e))

    def test_add_description_merge_multiple(self):
        d1 = {
            "comment": {
                "path_regex": '\\.py$',
                "line_regex": '^\\s*#',
                "classifications": ["Comments"],
            },
        }
        d2 = {
            "docstring_singleline": {
                "path_regex": '\\.py$',
                "line_regex": '^\\s*(\'\'\'|""").*\\1\\s*$',
                "classifications": ["Comments"],
            },
            "docstring_multiline": {
                "path_regex": '\\.py$',
                "entry_regex": '^\\s*(\'\'\'|""")',
                "exit_regex": '\\1\\s*$',
                "classifications": ["Comments"],
            },
        }
        try:
            self.description.add_descriptions(d1)
            self.description.add_descriptions(d2)
            assert self.description._descriptions == {
                "comment": d1["comment"],
                "docstring_singleline": d2["docstring_singleline"],
                "docstring_multiline": d2["docstring_multiline"]
            }
        except Exception as e:
            pytest.fail("Unexpected exception raised: " + str(e))

    def test_add_descriptions_merging_overwrite_top_level_name(self):
        try:
            self.description.add_descriptions({
                "name": {
                    "classifications": ['Everything'],
                },
            })
            self.description.add_descriptions({
                "name": {
                    "line_regex": '^$',
                    "classifications": ['Nothing'],
                },
            })
            assert self.description._descriptions == {"name": {"line_regex": '^$', "classifications": ['Nothing']}}
        except Exception as e:
            pytest.fail("Unexpected exception raised: " + str(e))

    def test_add_descriptions_merging_add_subsections(self):
        d1 = {
            "docstring_multiline": {
                "path_regex": '\\.py$',
                "entry_regex": '^\\s*(\'\'\'|""")',
                "exit_regex": '\\1\\s*$',
                "classifications": ["Comments"],
            },
        }
        d2 = {
            "docstring_multiline": {
                "subsections": {
                    "doctag": {
                        "classifications": ['Documentation'],
                        "line_regex": '(^|\\s)@[a-z]+:\\s',
                    },
                },
            },
        }
        try:
            self.description.add_descriptions(d1)
            self.description.add_descriptions(d2)
            d1["docstring_multiline"]["subsections"] = d2["docstring_multiline"]["subsections"]
            assert self.description._descriptions == d1
        except Exception as e:
            pytest.fail("Unexpected exception raised: " + str(e))

    def test_add_descriptions_merging_nested_subsections(self):
        try:
            self.description.add_descriptions({
                "name1": {
                    "entry_regex": 'asdf',
                    "exit_regex": 'fdsa',
                    "subsections": {
                        "name2": {
                            "classifications": ['Class'],
                        },
                    },
                },
            })
            self.description.add_descriptions({
                "name1": {
                    "subsections": {
                        "name3": {
                            "classifications": ['Klass'],
                        },
                    },
                },
            })
            assert self.description._descriptions == {
                "name1": {
                    "entry_regex": 'asdf',
                    "exit_regex": 'fdsa',
                    "subsections": {
                        "name2": {
                            "classifications": ['Class'],
                        },
                        "name3": {
                            "classifications": ['Klass'],
                        },
                    },
                },
            }
        except Exception as e:
            pytest.fail("Unexpected exception raised: " + str(e))


if __name__ == "__main__":
    sys.exit(pytest.main())
