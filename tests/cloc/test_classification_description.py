'''
Created on 3 Mar. 2018

@author: oliver
'''
import unittest
import pytest

from cloc.classification_description import ClassificationDescription, ClassificationError


class TestClassificationDescription(unittest.TestCase):
    def setUp(self):
        self.description = ClassificationDescription()
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

    def tearDown(self):
        pass

    def test_add_description_good(self):
        try:
            self.description.add_descriptions(self.comment_description)
        except Exception as e:
            pytest.fail("Unexpected exception raised: " + str(e))

    def test_add_description_multiple(self):
        try:
            self.description.add_descriptions(self.comment_description)
            self.description.add_descriptions(self.docstring_description)
            assert 3 == len(self.description._root.keys())
        except Exception as e:
            pytest.fail("Unexpected exception raised: " + str(e))

    def test_add_description_entry_exit_and_line_regexes(self):
        with pytest.raises(ClassificationError):
            self.description.add_descriptions({
                "name": {
                    "line_regex": 'asdf',
                    "entry_regex": 'asdf',
                    "exit_regex": 'asdf',
                },
            })


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()