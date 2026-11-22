"""Tests for Kitchen scheduling."""

import unittest

from chefs import ChefId, make_default_chefs
from kitchen import Kitchen


class TestKitchen(unittest.TestCase):
    def test_kitchen_constructs_with_default_chefs(self) -> None:
        kitchen = Kitchen(make_default_chefs())
        self.assertEqual([chef.id for chef in kitchen.chefs], [ChefId.ALICE, ChefId.BOB, ChefId.CAROL])


if __name__ == "__main__":
    unittest.main()
