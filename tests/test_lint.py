import unittest

import surveykit.lint as lint


class TestLint(unittest.TestCase):
    def test_defines_variable(self):
        self.assertFalse(lint.defines_variable({"type": ""}))
        self.assertFalse(lint.defines_variable({"type": "note"}))
        self.assertTrue(lint.defines_variable({"type": "integer"}))

    def test_defines_select(self):
        self.assertFalse(lint.defines_select({"type": ""}))
        self.assertFalse(lint.defines_select({"type": "integer"}))
        self.assertTrue(lint.defines_select({"type": "select_one foo"}))
        self.assertTrue(lint.defines_select({"type": "select_multiple foo"}))

    def test_extract_list_names(self):
        self.assertTupleEqual(
            lint.extract_list_names({"type": "integer"}),
            tuple())
        self.assertTupleEqual(
            lint.extract_list_names({"type": "select_one foo"}),
            ("foo",))
        self.assertTupleEqual(
            lint.extract_list_names({"type": "select_one foo or_other"}),
            ("foo",))
        self.assertTupleEqual(
            lint.extract_list_names({"type": "select_one foo bar"}),
            ("foo", "bar"))

    def test_extract_variables(self):
        self.assertTupleEqual(
            lint.extract_variables("foo barbaz"),
            tuple())
        self.assertTupleEqual(
            lint.extract_variables("foo ${bar}${baz}"),
            ("bar", "baz"))
