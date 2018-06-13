"""
Created on 3 Mar. 2018

@author: oliver
"""
import sys

import unittest2 as unittest

from cloc.classification_description import ClassificationDescription, Matcher


class TestClassificationDescription(unittest.TestCase):
    def setUp(self):
        self.maxDiff = None
        self.description = ClassificationDescription()
        self.description.add_descriptions(
            {
                "top-level-1": {
                    "path_regex": "path-regex-1",
                    "line_regex": "line-regex-1",
                    "classifications": ["classification-1"],
                },
                "top-level-2": {
                    "path_regex": "path-regex-2",
                    "entry_regex": "entry-regex-2",
                    "exit_regex": "exit-regex-2",
                    "classifications": ["classification-2"],
                },
                "top-level-3": {
                    "path_regex": "path-regex-3",
                    "entry_regex": "entry-regex-3",
                    "exit_regex": "exit-regex-3",
                    "classifications": ["classification-3"],
                    "subsections": {
                        "nested-1": {"line_regex": "line-regex-3-1", "classifications": ["classification-3-1"]},
                        "nested-2": {
                            "entry_regex": "entry-regex-3-2",
                            "exit_regex": "exit-regex-3-2",
                            "classifications": ["classification-3-2"],
                        },
                    },
                },
            }
        )
        self.matchers = {
            "top-level-1": {
                "line": Matcher(Matcher.RE_TYPE_LINE, ["top-level-1"], "line-regex-1", ["classification-1"])
            },
            "top-level-2": {
                "entry": Matcher(Matcher.RE_TYPE_ENTRY, ["top-level-2"], "entry-regex-2", ["classification-2"]),
                "exit": Matcher(Matcher.RE_TYPE_EXIT, ["top-level-2"], "exit-regex-2", ["classification-2"]),
            },
            "top-level-3": {
                "entry": Matcher(Matcher.RE_TYPE_ENTRY, ["top-level-3"], "entry-regex-3", ["classification-3"]),
                "exit": Matcher(Matcher.RE_TYPE_EXIT, ["top-level-3"], "exit-regex-3", ["classification-3"]),
                "nested-1": {
                    "line": Matcher(
                        Matcher.RE_TYPE_LINE, ["top-level-3", "nested-1"], "line-regex-3-1", ["classification-3-1"]
                    )
                },
                "nested-2": {
                    "entry": Matcher(
                        Matcher.RE_TYPE_ENTRY, ["top-level-3", "nested-2"], "line-regex-3-2", ["classification-3-2"]
                    ),
                    "exit": Matcher(
                        Matcher.RE_TYPE_EXIT, ["top-level-3", "nested-2"], "line-regex-3-2", ["classification-3-2"]
                    ),
                },
            },
        }

    def tearDown(self):
        pass

    def test_get_matchers_from_file_single_match(self):
        matchers = self.description.get_matchers_for_file("path/to/path-regex-1")
        self.assertItemsEqual(matchers, [self.matchers["top-level-1"]["line"]])
        self.assertItemsEqual(matchers, self.description._active_matchers)

    def test_get_matchers_from_file_multiple_matches(self):
        matchers = self.description.get_matchers_for_file("path/to/path-regex-1/path-regex-2")
        self.assertItemsEqual(matchers, [self.matchers["top-level-1"]["line"], self.matchers["top-level-2"]["entry"]])
        self.assertItemsEqual(matchers, self.description._active_matchers)

    def test_get_matchers_from_file_no_match(self):
        self.description._active_matchers = [
            self.matchers["top-level-1"]["line"],
            self.matchers["top-level-2"]["entry"],
        ]
        matchers = self.description.get_matchers_for_file("path/to/file")
        self.assertItemsEqual(matchers, [])
        self.assertItemsEqual(matchers, self.description._active_matchers)

    def test_get_next_matchers_line_regex_matched(self):
        self.description._active_matchers = [
            self.matchers["top-level-1"]["line"],
            self.matchers["top-level-2"]["entry"],
        ]
        matchers = self.description.get_next_matchers(self.matchers["top-level-1"]["line"])
        self.assertItemsEqual(matchers, self.description._active_matchers)

    def test_get_next_matchers_entry_regex_matched(self):
        self.description._active_matchers = [
            self.matchers["top-level-1"]["line"],
            self.matchers["top-level-2"]["entry"],
        ]
        matchers = self.description.get_next_matchers(self.matchers["top-level-2"]["entry"])
        self.assertItemsEqual(matchers, [self.matchers["top-level-1"]["line"], self.matchers["top-level-2"]["exit"]])
        self.assertItemsEqual(matchers, self.description._active_matchers)

    def test_get_next_matchers_entry_regex_with_subsections_matched(self):
        self.description._active_matchers = [
            self.matchers["top-level-1"]["line"],
            self.matchers["top-level-3"]["entry"],
        ]
        matchers = self.description.get_next_matchers(self.matchers["top-level-3"]["entry"])
        self.assertItemsEqual(
            matchers,
            [
                self.matchers["top-level-1"]["line"],
                self.matchers["top-level-3"]["exit"],
                self.matchers["top-level-3"]["nested-1"]["line"],
                self.matchers["top-level-3"]["nested-2"]["entry"],
            ],
        )
        self.assertItemsEqual(matchers, self.description._active_matchers)

    def test_get_next_matchers_exit_regex_matched(self):
        self.description._active_matchers = [self.matchers["top-level-1"]["line"], self.matchers["top-level-2"]["exit"]]
        matchers = self.description.get_next_matchers(self.matchers["top-level-2"]["exit"])
        self.assertItemsEqual(matchers, [self.matchers["top-level-1"]["line"], self.matchers["top-level-2"]["entry"]])
        self.assertItemsEqual(matchers, self.description._active_matchers)

    def test_get_next_matchers_exit_regex_with_subsection_matched(self):
        self.description._active_matchers = [
            self.matchers["top-level-1"]["line"],
            self.matchers["top-level-3"]["exit"],
            self.matchers["top-level-3"]["nested-1"]["line"],
            self.matchers["top-level-3"]["nested-2"]["entry"],
        ]
        matchers = self.description.get_next_matchers(self.matchers["top-level-3"]["exit"])
        self.assertItemsEqual(matchers, [self.matchers["top-level-1"]["line"], self.matchers["top-level-3"]["entry"]])
        self.assertItemsEqual(matchers, self.description._active_matchers)

    def test_get_next_matchers_multiple_entry_regexes_matched(self):
        self.description._active_matchers = [
            self.matchers["top-level-2"]["entry"],
            self.matchers["top-level-3"]["entry"],
        ]
        matchers = self.description.get_next_matchers(
            self.matchers["top-level-2"]["entry"], self.matchers["top-level-3"]["entry"]
        )
        self.assertItemsEqual(
            matchers,
            [
                self.matchers["top-level-2"]["exit"],
                self.matchers["top-level-3"]["exit"],
                self.matchers["top-level-3"]["nested-1"]["line"],
                self.matchers["top-level-3"]["nested-2"]["entry"],
            ],
        )
        self.assertItemsEqual(matchers, self.description._active_matchers)


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
