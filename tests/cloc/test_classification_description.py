'''
Created on 3 Mar. 2018

@author: oliver
'''
import unittest
import pytest

from cloc.classification_description import ClassificationDescription, ClassificationDescriptionError


class TestClassificationDescription(unittest.TestCase):
    def setUp(self):
        self.description = ClassificationDescription()

    def tearDown(self):
        pass

    def test_add_description_good(self):
        d = {
            "name": {
                "line_regex": 'asdf',
                "classifications": ['nothing'],
            },
        }
        try:
            self.description.add_descriptions(d)
            assert self.description._root == d
        except Exception as e:
            pytest.fail("Unexpected exception raised: " + str(e))

    def test_add_description_multiple(self):
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
            assert self.description._root == {
                "comment": d1["comment"],
                "docstring_singleline": d2["docstring_singleline"],
                "docstring_multiline": d2["docstring_multiline"]
            }
        except Exception as e:
            pytest.fail("Unexpected exception raised: " + str(e))

    def test_add_descriptions_empty(self):
        with pytest.raises(ClassificationDescriptionError,
                           match="A ClassficationDescription must have a classification: name"):
            self.description.add_descriptions({
                "name": {},
            })
        try:
            self.description.add_descriptions({
                "name": {
                    "classifications": ["Everything"],
                },
            })
            assert self.description._root == {"name": {"classifications": ["Everything"]}}
        except Exception as e:
            pytest.fail("Unexpected exception raised: " + str(e))

    def test_add_descriptions_line_regex_no_classifications(self):
        with pytest.raises(ClassificationDescriptionError,
                           match="A ClassficationDescription must have a classification: name"):
            self.description.add_descriptions({
                "name": {
                    "line_regex": 'asdf',
                },
            })

    def test_add_descriptions_subsections_require_entry_and_exit_regexes(self):
        with pytest.raises(
                ClassificationDescriptionError,
                match="A ClassficationDescription with subsections must have entry_regex and exit_regex: name1"):
            self.description.add_descriptions({
                "name1": {
                    "subsections": {
                        "name2": {
                            "classifications": ["Classification"],
                        },
                    },
                },
            })

    def test_add_descriptions_subsections_and_line_regex(self):
        with pytest.raises(ClassificationDescriptionError,
                           match="A ClassificationDescription with subsections must not have a line_regex: name1"):
            self.description.add_descriptions({
                "name1": {
                    "line_regex": 'asdf',
                    "subsections": {
                        "name2": {
                            "classifications": ["Classification"],
                        },
                    },
                },
            })

    def test_add_descriptions_entry_regex_without_exit_regex(self):
        with pytest.raises(ClassificationDescriptionError,
                           match="A ClassificationDescription with an entry_regex must also have an exit_regex: name1"):
            self.description.add_descriptions({
                "name1": {
                    "entry_regex": 'asdf',
                },
            })

    def test_add_descriptions_exit_regex_without_entry_regex(self):
        with pytest.raises(ClassificationDescriptionError,
                           match="A ClassificationDescription with an exit_regex must also have an entry_regex: name1"):
            self.description.add_descriptions({
                "name1": {
                    "exit_regex": 'asdf',
                },
            })

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
            assert self.description._root == {
                "docstring_singleline": d1["docstring_singleline"],
                "docstring_multiline": d1["docstring_multiline"],
                "doctag": d3
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
            assert self.description._root == {"name": {"line_regex": '^$', "classifications": ['Nothing']}}
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
            assert self.description._root == d1
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
            assert self.description._root == {
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
