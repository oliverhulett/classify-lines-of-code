'''
Created on 3 Mar. 2018

@author: oliver
'''
import unittest
import pytest

from cloc.classification_description import ClassificationDescription, Matcher


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
                "classifications": ['classification-3'],
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
        self.description._active_matchers = [Matcher(Matcher.RE_TYPE_LINE, ["top-level-1"], 'line-regex-1'), Matcher(Matcher.RE_TYPE_ENTRY, ["top-level-2"], 'entry-regex-2')]

    def tearDown(self):
        pass

    def test_get_matchers_from_file_single_match(self):
        matchers = self.description.get_matchers_for_file("path/to/path-regex-1")
        assert matchers == [Matcher(Matcher.RE_TYPE_LINE, ["top-level-1"], 'line-regex-1')]
        assert matchers == self.description._active_matchers

    def test_get_matchers_from_file_multiple_matches(self):
        matchers = self.description.get_matchers_for_file("path/to/path-regex-1/path-regex-2")
        assert matchers == [Matcher(Matcher.RE_TYPE_LINE, ["top-level-1"], 'line-regex-1'), Matcher(Matcher.RE_TYPE_ENTRY, ["top-level-2"], 'entry-regex-2')]
        assert matchers == self.description._active_matchers
    
    def test_get_matchers_from_file_no_match(self):
        matchers = self.description.get_matchers_for_file("path/to/file")
        assert matchers == []
        assert matchers == self.description._active_matchers
    
    def test_get_next_matchers_line_regex_matched(self):
        matchers = self.description.get_next_matchers(Matcher(Matcher.RE_TYPE_LINE, ["top-level-1"], 'line-regex-1'))


if __name__ == "__main__":
    sys.exit(pytest.main())
