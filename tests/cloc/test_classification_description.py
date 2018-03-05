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
        self.whitespace_description = {
            "whitespace": {
                "line_regex": '^\\s*$',
                "classifications": ["Whitespace"],
            },
        }
        self.comment_description = {
            "comment": {
                "path_regex": '\\.py$',
                "line_regex": '^\\s*#',
                "classifications": ["Comments"],
            },
        }
        self.docstring_description = {
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
        self.doctag_description = {
            "doctag": {
                "based_on": "docstring_multiline",
                "line_regex": '(^|\\s)@[a-z]+:\\s',
            },
        }

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
            self.description.add_descriptions(self.comment_description)
            self.description.add_descriptions(self.docstring_description)
            assert 3 == len(self.description._root.keys())
        except Exception as e:
            pytest.fail("Unexpected exception raised: " + str(e))

    def test_add_descriptions_no_classifications(self):
        with pytest.raises(ClassificationDescriptionError, match="A ClassficationDescription must have a classification: name"):
            self.description.add_descriptions({
                "name": {
                    "line_regex": 'asdf',
                },
            })

    def test_add_descriptions_based_on_does_not_exist(self):
        with pytest.raises(ClassificationDescriptionError, match="A referenced ClassficationDescription does not exist: doctag"):
            self.description.add_descriptions(self.doctag_description)

    def test_add_descriptions_based_on(self):
        try:
            self.description.add_descriptions(self.docstring_description)
            self.description.add_descriptions(self.doctag_description)
            assert 1 == len(self.description._root['doctag']['classifications'])
            assert "Comments" == self.description._root['doctag']['classifications'][0]
        except Exception as e:
            pytest.fail("Unexpected exception raised: " + str(e))


if __name__ == "__main__":
    sys.exit(pytest.main())