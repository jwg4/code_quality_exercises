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


class TestLongStrings(TestCase):
    LARGE_NUMBER = 100_000

    @classmethod
    def setUpClass(cls):
        cls.open_round = "(" * cls.LARGE_NUMBER
        cls.close_round = ")" * cls.LARGE_NUMBER
        cls.open_multi = "{[" * cls.LARGE_NUMBER
        cls.close_multi = "]}" * cls.LARGE_NUMBER

    def test_many_matched_round_pairs(self):
        s = self.open_round + "X" + self.close_round
        self.assertTrue(validate(s))

    def test_many_unmatched_round_pairs(self):
        s = self.open_round + ")" + self.close_round
        self.assertFalse(validate(s))

    def test_many_matched_round_pairs_then_stray_open(self):
        s = "" + self.open_round + self.close_round + "("
        self.assertFalse(validate(s))

    def test_many_matched_square_and_curly(self):
        s = "()" + self.open_multi + "()" + self.close_multi + "()"
        self.assertTrue(validate(s))

    def test_interspersed_round_pair(self):
        s = "(" + self.open_multi + ")" + self.close_multi + "()"
        self.assertFalse(validate(s))

    def test_two_interspersed_round_pairs(self):
        s = "()" + self.open_multi + ")(" + self.close_multi + "()"
        self.assertFalse(validate(s))

    def test_completely_wrong(self):
        s = "[[]" + self.open_round + "){{}}" + self.close_multi + "(][][])"
        self.assertFalse(validate(s))
