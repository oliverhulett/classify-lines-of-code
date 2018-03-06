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
        try:
            self.description.add_descriptions({
                "name": {
                    "line_regex": 'asdf',
                    "classifications": ['nothing'],
                },
            })
            assert 1 == len(self.description._root.keys())
        except Exception as e:
            pytest.fail("Unexpected exception raised: " + str(e))

    def test_add_description_multiple(self):
        try:
            self.description.add_descriptions({
                "comment": {
                    "path_regex": '\\.py$',
                    "line_regex": '^\\s*#',
                    "classifications": ["Comments"],
                },
            })
            self.description.add_descriptions({
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
            })
            assert 3 == len(self.description._root.keys())
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
        try:
            self.description.add_descriptions({
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
            })
            self.description.add_descriptions({
                "doctag": {
                    "based_on": "docstring_multiline",
                    "line_regex": '(^|\\s)@[a-z]+:\\s',
                },
            })
            assert 1 == len(self.description._root['doctag']['classifications'])
            assert "Comments" == self.description._root['doctag']['classifications'][0]
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
            assert 1 == len(self.description._root)
            assert "Nothing" == self.description._root['name']['classifications'][0]
        except Exception as e:
            pytest.fail("Unexpected exception raised: " + str(e))

    def test_add_descriptions_merging_add_subsections(self):
        try:
            self.description.add_descriptions({
                "docstring_multiline": {
                    "path_regex": '\\.py$',
                    "entry_regex": '^\\s*(\'\'\'|""")',
                    "exit_regex": '\\1\\s*$',
                    "classifications": ["Comments"],
                },
            })
            self.description.add_descriptions({
                "docstring_multiline": {
                    "subsections": {
                        "doctag": {
                            "classifications": ['Documentation'],
                            "line_regex": '(^|\\s)@[a-z]+:\\s',
                        },
                    },
                },
            })
            assert self.description._root == {
                "docstring_multiline": {
                    "path_regex": '\\.py$',
                    "entry_regex": '^\\s*(\'\'\'|""")',
                    "exit_regex": '\\1\\s*$',
                    "classifications": ["Comments"],
                    "subsections": {
                        "doctag": {
                            "classifications": ['Documentation'],
                            "line_regex": '(^|\\s)@[a-z]+:\\s',
                        },
                    },
                },
            }
        except Exception as e:
            pytest.fail("Unexpected exception raised: " + str(e))


if __name__ == "__main__":
    sys.exit(pytest.main())
