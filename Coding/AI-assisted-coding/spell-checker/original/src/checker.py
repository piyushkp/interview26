"""You'll implement this."""

from typing import Dict, List

from distance import EditDistance


class Checker:
    """Suggests spelling corrections ranked by edit distance and frequency."""

    def __init__(self, dictionary: Dict[str, int]):
        self.dictionary = dictionary
        self.ed = EditDistance()

    def suggest(self, word: str, max_distance: int = 2, max_suggestions: int = 5) -> List[str]:
        return []
