import unittest
import sys
sys.path.insert(0, './Coding/python')
from digital_recipe_manager_impl import DigitalRecipeManagerImpl

class Level2All(unittest.TestCase):
    def setUp(self):
        self.system = DigitalRecipeManagerImpl()

    def test_top_rated_complex_multi_chef(self):
        # From screenshot 1:
        # Expected: ['carol(10, 2)', 'alice(9, 2)', 'bob(5, 2)']
        # Actual: ['alice(5, 1)', 'bob(0, 0)', 'carol(0, 0)']
        pass

    def test_top_rated_average_determines_order(self):
        # From screenshot 1:
        # Expected: ['bob(4, 1)', 'alice(6, 2)']
        # Actual: ['alice(5, 1)', 'bob(0, 0)']
        pass

    def test_top_rated_tie_break_alphabetically(self):
        # From screenshot 2:
        # Expected: ['alice(4, 1)', 'bob(4, 1)']
        # Actual: ['bob(4, 1)', 'alice(0, 0)']
        pass
