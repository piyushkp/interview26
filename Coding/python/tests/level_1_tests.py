import inspect
import os
import sys
import unittest

current_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

from digital_recipe_manager_impl import DigitalRecipeManagerImpl


class Level1Tests(unittest.TestCase):
    failureException = Exception

    @classmethod
    def setUpClass(cls):
        pass

    def setUp(self):
        self.system = DigitalRecipeManagerImpl()

    def test_create_recipe_success(self):
        self.assertEqual(
            self.system.create_recipe(1, 'alice', 'Pasta', ['noodles', 'sauce'], ['boil', 'mix']),
            'recipe1'
        )
        self.assertEqual(
            self.system.create_recipe(2, 'bob', 'Soup', ['water'], ['heat']),
            'recipe2'
        )
        self.assertEqual(
            self.system.create_recipe(3, 'carol', 'Salad', ['lettuce', 'tomato'], ['chop', 'toss', 'serve']),
            'recipe3'
        )

    def test_create_recipe_duplicate_name_case_insensitive(self):
        self.assertEqual(
            self.system.create_recipe(1, 'alice', 'Burger', ['meat'], ['grill']),
            'recipe1'
        )
        self.assertIsNone(
            self.system.create_recipe(2, 'alice', 'Burger', ['veg'], ['fry'])
        )
        self.assertIsNone(
            self.system.create_recipe(3, 'bob', 'BURGER', ['fish'], ['steam'])
        )
        self.assertIsNone(
            self.system.create_recipe(4, 'carol', 'bUrGeR', ['tofu'], ['bake'])
        )
        self.assertEqual(
            self.system.create_recipe(5, 'bob', 'Burgers', ['meat'], ['grill']),
            'recipe2'
        )

    def test_create_recipe_sequential_ids_across_users(self):
        self.assertEqual(self.system.create_recipe(1, 'u1', 'R1', ['i'], ['s']), 'recipe1')
        self.assertEqual(self.system.create_recipe(2, 'u2', 'R2', ['i'], ['s']), 'recipe2')
        self.assertEqual(self.system.create_recipe(3, 'u3', 'R3', ['i'], ['s']), 'recipe3')
        self.assertEqual(self.system.create_recipe(4, 'u1', 'R4', ['i'], ['s']), 'recipe4')

    def test_rate_recipe_and_get_rating(self):
        self.assertEqual(self.system.create_recipe(1, 'alice', 'Pasta', ['noodles'], ['boil']), 'recipe1')
        self.assertEqual(self.system.create_recipe(2, 'bob', 'Toast', ['bread'], ['toast']), 'recipe2')
        # bob rates recipe1 as 5
        self.assertTrue(self.system.rate_recipe(4, 'bob', 'recipe1', 5))
        # alice is author, cannot rate
        self.assertFalse(self.system.rate_recipe(5, 'alice', 'recipe1', 4))
        # carol rates recipe1 as 3
        self.assertTrue(self.system.rate_recipe(6, 'carol', 'recipe1', 3))
        # bob updates rating to 4
        self.assertTrue(self.system.rate_recipe(7, 'bob', 'recipe1', 4))

        self.assertEqual(self.system.get_recipe_rating(8, 'recipe1', 'bob'), 4)
        self.assertEqual(self.system.get_recipe_rating(9, 'recipe1', 'carol'), 3)
        self.assertIsNone(self.system.get_recipe_rating(10, 'recipe1', 'alice'))

    def test_edge_cases(self):
        self.assertFalse(self.system.rate_recipe(1, 'bob', 'nonexistent', 4))
        self.assertEqual(self.system.create_recipe(2, 'alice', 'Pizza', ['dough'], ['bake']), 'recipe1')
        self.assertFalse(self.system.rate_recipe(3, 'bob', 'recipe1', 0))
        self.assertFalse(self.system.rate_recipe(4, 'bob', 'recipe1', 6))
        self.assertIsNone(self.system.get_recipe_rating(5, 'nonexistent', 'bob'))
        self.assertIsNone(self.system.get_recipe_rating(6, 'recipe1', 'stranger'))


if __name__ == '__main__':
    unittest.main()
