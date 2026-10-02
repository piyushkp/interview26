from abc import ABC


class DigitalRecipeManager(ABC):
    """
    DigitalRecipeManager interface.
    """

    def create_recipe(
        self,
        timestamp: int,
        user_id: str,
        name: str,
        ingredients: list[str],
        steps: list[str],
    ) -> str | None:
        return None

    def rate_recipe(
        self,
        timestamp: int,
        user_id: str,
        recipe_id: str,
        rating: int,
    ) -> bool:
        return False

    def get_recipe_rating(
        self,
        timestamp: int,
        recipe_id: str,
        user_id: str,
    ) -> int | None:
        return None

    def top_rated_chefs(
        self,
        timestamp: int,
        n: int,
    ) -> list[str]:
        return []

