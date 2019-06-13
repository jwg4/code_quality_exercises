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
        self.assertTrue(validate("(((())))")

    def test_nested_brackets_of_different_kinds(self):
        self.assertTrue(validate("{[()]}")
    
    def test_consecutive_brackets(self):
        self.assertTrue(validate("()()()()()")

    def test_consecutive_brackets_of_different_kinds(self):
        self.assertTrue(validate("{}()[]{}")
    
