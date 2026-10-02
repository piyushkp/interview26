import inspect
import os
import sys
import unittest

current_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

from digital_recipe_manager_impl import DigitalRecipeManagerImpl


class Level2Tests(unittest.TestCase):
    failureException = Exception

    def setUp(self):
        self.system = DigitalRecipeManagerImpl()

    def test_top_rated_basic_single_rating(self):
        self.assertEqual(self.system.create_recipe(1, 'alice', 'Pasta', ['i'], ['s']), 'recipe1')
        self.assertTrue(self.system.rate_recipe(2, 'bob', 'recipe1', 5))
        expected = ['alice(5, 1)']
        self.assertEqual(self.system.top_rated_chefs(3, 1), expected)

    def test_top_rated_multiple_ratings_one_recipe(self):
        self.assertEqual(self.system.create_recipe(1, 'alice', 'Pasta', ['i'], ['s']), 'recipe1')
        self.assertTrue(self.system.rate_recipe(2, 'bob', 'recipe1', 5))
        self.assertTrue(self.system.rate_recipe(3, 'carol', 'recipe1', 3))
        expected = ['alice(8, 2)']
        self.assertEqual(self.system.top_rated_chefs(4, 1), expected)

    def test_top_rated_multiple_recipes_per_chef(self):
        self.assertEqual(self.system.create_recipe(1, 'alice', 'R1', ['i'], ['s']), 'recipe1')
        self.assertEqual(self.system.create_recipe(2, 'alice', 'R2', ['i'], ['s']), 'recipe2')
        self.assertTrue(self.system.rate_recipe(3, 'bob', 'recipe1', 5))
        self.assertTrue(self.system.rate_recipe(4, 'bob', 'recipe2', 3))
        expected = ['alice(8, 2)']
        self.assertEqual(self.system.top_rated_chefs(5, 1), expected)

    def test_top_rated_sorting_by_average_descending(self):
        self.assertEqual(self.system.create_recipe(1, 'alice', 'R1', ['i'], ['s']), 'recipe1')
        self.assertEqual(self.system.create_recipe(2, 'bob', 'R2', ['i'], ['s']), 'recipe2')
        self.assertTrue(self.system.rate_recipe(3, 'carol', 'recipe1', 3))
        self.assertTrue(self.system.rate_recipe(4, 'carol', 'recipe2', 5))
        expected = ['bob(5, 1)', 'alice(3, 1)']
        self.assertEqual(self.system.top_rated_chefs(5, 2), expected)

    def test_top_rated_tie_break_alphabetically(self):
        self.assertEqual(self.system.create_recipe(1, 'bob', 'R1', ['i'], ['s']), 'recipe1')
        self.assertEqual(self.system.create_recipe(2, 'alice', 'R2', ['i'], ['s']), 'recipe2')
        self.assertTrue(self.system.rate_recipe(3, 'carol', 'recipe1', 4))
        self.assertTrue(self.system.rate_recipe(4, 'carol', 'recipe2', 4))
        expected = ['alice(4, 1)', 'bob(4, 1)']
        self.assertEqual(self.system.top_rated_chefs(5, 2), expected)

    def test_top_rated_chefs_with_no_ratings(self):
        self.assertEqual(self.system.create_recipe(1, 'alice', 'R1', ['i'], ['s']), 'recipe1')
        self.assertEqual(self.system.create_recipe(2, 'bob', 'R2', ['i'], ['s']), 'recipe2')
        self.assertTrue(self.system.rate_recipe(3, 'carol', 'recipe1', 5))
        expected = ['alice(5, 1)', 'bob(0, 0)']
        self.assertEqual(self.system.top_rated_chefs(4, 3), expected)

    def test_top_rated_complex_multi_chef(self):
        # alice creates R1, R2
        self.assertEqual(self.system.create_recipe(1, 'alice', 'R1', ['i'], ['s']), 'recipe1')
        self.assertEqual(self.system.create_recipe(2, 'bob', 'R2', ['i'], ['s']), 'recipe2')
        self.assertEqual(self.system.create_recipe(3, 'carol', 'R3', ['i'], ['s']), 'recipe3')
        self.assertEqual(self.system.create_recipe(4, 'alice', 'R4', ['i'], ['s']), 'recipe4')
        # carol rates alice's R1 5, and R4 4 -> alice: sum=9, count=2 (avg 4.5)
        self.assertTrue(self.system.rate_recipe(5, 'carol', 'recipe1', 5))
        self.assertTrue(self.system.rate_recipe(6, 'carol', 'recipe4', 4))
        # alice rates carol's R3 5, bob rates carol's R3 5 -> carol: sum=10, count=2 (avg 5.0)
        self.assertTrue(self.system.rate_recipe(7, 'alice', 'recipe3', 5))
        self.assertTrue(self.system.rate_recipe(8, 'bob', 'recipe3', 5))
        # alice rates bob's R2 2, carol rates bob's R2 3 -> bob: sum=5, count=2 (avg 2.5)
        self.assertTrue(self.system.rate_recipe(9, 'alice', 'recipe2', 2))
        self.assertTrue(self.system.rate_recipe(10, 'carol', 'recipe2', 3))

        expected = ['carol(10, 2)', 'alice(9, 2)', 'bob(5, 2)']
        self.assertEqual(self.system.top_rated_chefs(11, 3), expected)

    def test_top_rated_average_determines_order(self):
        self.assertEqual(self.system.create_recipe(1, 'alice', 'R1', ['i'], ['s']), 'recipe1')
        self.assertEqual(self.system.create_recipe(2, 'bob', 'R2', ['i'], ['s']), 'recipe2')
        # alice has 2 ratings: 3 and 3 -> avg 3.0
        self.assertTrue(self.system.rate_recipe(3, 'carol', 'recipe1', 3))
        self.assertTrue(self.system.rate_recipe(4, 'dave', 'recipe1', 3))
        # bob has 1 rating: 4 -> avg 4.0
        self.assertTrue(self.system.rate_recipe(5, 'carol', 'recipe2', 4))
        expected = ['bob(4, 1)', 'alice(6, 2)']
        self.assertEqual(self.system.top_rated_chefs(6, 2), expected)


if __name__ == '__main__':
    unittest.main()
