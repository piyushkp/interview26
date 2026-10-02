import unittest
from digital_recipe_manager_impl import DigitalRecipeManagerImpl

class Level2Tests(unittest.TestCase):
    @classmethod
    def setUp(cls):
        cls.system = DigitalRecipeManagerImpl()

    def test_top_rated_basic_single_rating(self):
        self.assertEqual(self.system.create_recipe(1, 'alice', 'Pasta', ['i'], ['s']), 'recipe1')
        self.assertTrue(self.system.rate_recipe(2, 'bob', 'recipe1', 5))
        expected = ['alice(5, 1)']
        self.assertEqual(self.system.top_rated_chefs(3, 1), expected)

    def test_top_rated_average_determines_order(self):
        self.assertEqual(self.system.create_recipe(1, 'alice', 'R1', ['i'], ['s']), 'recipe1')
        self.assertEqual(self.system.create_recipe(2, 'bob', 'R2', ['i'], ['s']), 'recipe2')
        self.assertTrue(self.system.rate_recipe(3, 'carol', 'recipe1', 3))
        self.assertTrue(self.system.rate_recipe(4, 'dave', 'recipe1', 3))
        self.assertTrue(self.system.rate_recipe(5, 'carol', 'recipe2', 4))
        expected = ['bob(4, 1)', 'alice(6, 2)']
        self.assertEqual(self.system.top_rated_chefs(6, 2), expected)

    def test_top_rated_tie_break_alphabetically(self):
        self.assertEqual(self.system.create_recipe(1, 'bob', 'R1', ['i'], ['s']), 'recipe1')
        self.assertEqual(self.system.create_recipe(2, 'alice', 'R2', ['i'], ['s']), 'recipe2')
        self.assertTrue(self.system.rate_recipe(3, 'carol', 'recipe1', 4))
        self.assertTrue(self.system.rate_recipe(4, 'carol', 'recipe2', 4))
        expected = ['alice(4, 1)', 'bob(4, 1)']
        self.assertEqual(self.system.top_rated_chefs(5, 2), expected)

if __name__ == '__main__':
    unittest.main()
