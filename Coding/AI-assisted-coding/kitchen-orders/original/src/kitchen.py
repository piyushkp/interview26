"""You'll implement this."""

from chefs import Chef
from order import Order
from schedule import Schedule


class Kitchen:
    def __init__(self, chefs: list[Chef]) -> None:
        self._chefs = chefs

    @property
    def chefs(self) -> list[Chef]:
        return self._chefs

    def schedule(self, order: Order) -> Schedule:
        raise NotImplementedError("Kitchen.schedule is not implemented yet")
