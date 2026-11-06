import io
import os
import sys
import unittest
from contextlib import redirect_stdout

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from fizzbuzz import fizzbuzz


def run(n):
    buf = io.StringIO()
    with redirect_stdout(buf):
        fizzbuzz(n)
    return buf.getvalue().split("\n")[:-1]


class FizzBuzzTest(unittest.TestCase):
    def test_first_15(self):
        self.assertEqual(run(15), [
            "1", "2", "fizz", "4", "buzz", "fizz", "7", "8", "fizz", "buzz",
            "11", "fizz", "13", "14", "fizzbuzz"])

    def test_default_range(self):
        out = run(100)
        self.assertEqual(len(out), 100)
        self.assertEqual(out[99], "buzz")   # 100
        self.assertEqual(out[89], "fizzbuzz")  # 90
        self.assertEqual(out[96], "97")

    def test_zero(self):
        self.assertEqual(run(0), [])


if __name__ == "__main__":
    unittest.main()
