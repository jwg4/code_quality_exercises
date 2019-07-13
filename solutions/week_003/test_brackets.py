from unittest import TestCase

from brackets import validate


class TestValidateSanityCheck(TestCase):
    def test_empty_string(self):
        self.assertTrue(validate(""))

    def test_single_pair(self):
        self.assertTrue(validate("[]"))

    def test_single_bracket(self):
        self.assertFalse(validate("{"))


class TestSomeValidStrings(TestCase):
    def test_nested_brackets(self):
        self.assertTrue(validate("(((())))"))

    def test_nested_brackets_of_different_kinds(self):
        self.assertTrue(validate("{[()]}"))

    def test_consecutive_brackets(self):
        self.assertTrue(validate("()()()()()"))

    def test_consecutive_brackets_of_different_kinds(self):
        self.assertTrue(validate("{}()[]{}"))


class TestSomeInvalidStrings(TestCase):
    def test_close_one_more_than_you_open(self):
        self.assertFalse(validate("((((())))))"))

    def test_close_one_fewer_than_you_open(self):
        self.assertFalse(validate("((((())))"))

    def test_one_outward_pair(self):
        self.assertFalse(validate(")()()()()()("))

    def test_switched_different_kinds(self):
        self.assertFalse(validate("[}{]"))

    def test_overlapping_different_kinds(self):
        self.assertFalse(validate("({)}"))
