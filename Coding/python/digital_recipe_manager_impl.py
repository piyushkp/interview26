from digital_recipe_manager import DigitalRecipeManager


class DigitalRecipeManagerImpl(DigitalRecipeManager):

    def __init__(self):
        self.recipe_counter = 0
        self.recipes = {}  # recipe_id -> dict(author, name, ingredients, steps)
        self.recipe_names = set()  # set of lowercase recipe names
        self.ratings = {}  # (recipe_id, user_id) -> int

    def create_recipe(
        self,
        timestamp: int,
        user_id: str,
        name: str,
        ingredients: list[str],
        steps: list[str],
    ) -> str | None:
        name_lower = name.lower()
        if name_lower in self.recipe_names:
            return None

        self.recipe_counter += 1
        recipe_id = f"recipe{self.recipe_counter}"

        self.recipe_names.add(name_lower)
        self.recipes[recipe_id] = {
            "author": user_id,
            "name": name,
            "ingredients": ingredients,
            "steps": steps,
        }
        return recipe_id

    def rate_recipe(
        self,
        timestamp: int,
        user_id: str,
        recipe_id: str,
        rating: int,
    ) -> bool:
        # Check if recipe exists
        if recipe_id not in self.recipes:
            return False

        # Rating must be between 1 and 5 inclusive
        if not (1 <= rating <= 5):
            return False

        # User cannot rate their own recipe
        if self.recipes[recipe_id]["author"] == user_id:
            return False

        # Record / update rating
        self.ratings[(recipe_id, user_id)] = rating
        return True

    def get_recipe_rating(
        self,
        timestamp: int,
        recipe_id: str,
        user_id: str,
    ) -> int | None:
        if recipe_id not in self.recipes:
            return None

        return self.ratings.get((recipe_id, user_id), None)

    def top_rated_chefs(
        self,
        timestamp: int,
        n: int,
    ) -> list[str]:
        # Collect chefs who have created at least one recipe
        # Calculate sum and count of all ratings across all recipes of that chef
        chef_stats = {}
        for recipe_id, recipe_info in self.recipes.items():
            author = recipe_info["author"]
            if author not in chef_stats:
                chef_stats[author] = [0, 0]

        for (recipe_id, user_id), rating in self.ratings.items():
            author = self.recipes[recipe_id]["author"]
            chef_stats[author][0] += rating
            chef_stats[author][1] += 1

        def sort_key(chef_id):
            total_sum, count = chef_stats[chef_id]
            avg = (total_sum / count) if count > 0 else -1.0
            return (-avg, chef_id)

        sorted_chefs = sorted(chef_stats.keys(), key=sort_key)
        top_n = sorted_chefs[:n]

        result = []
        for chef in top_n:
            s, c = chef_stats[chef]
            result.append(f"{chef}({s}, {c})")
        return result