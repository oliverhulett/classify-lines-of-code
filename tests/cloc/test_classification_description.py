'''
Created on 3 Mar. 2018

@author: oliver
'''
import unittest

from cloc.classification_description import ClassificationDescription


class TestClassificationDescription(unittest.TestCase):


    def setUp(self):
        self.description = ClassificationDescription()
        self.python_description_1 = {
            "comment": {
                "path_regex": '\\.py$',
                "line_regex": '^\\s*#',
                "classifications": ["Comments"],
            },
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
            self.description.add_descriptions(self.python_description_1)
        except Exception as e:
            pytest.fail("Unexpected exception raised: " + str(e))

    def test_add_description_multiple(self):
        try:
            self.description.add_descriptions(self.python_description_1)
        except Exception as e:
            pytest.fail("Unexpected exception raised: " + str(e))


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()