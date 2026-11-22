"""
Runs your Scheduler. It's useful to see how Kitchen.schedule is called.
You may want to change the order or inspect the returned schedule.
"""

from chefs import make_default_chefs
from dish import Dish
from kitchen import Kitchen
from order import Order
from recipes import RecipeId, make_recipe


def banner(legend: str) -> None:
    border = "#" * (len(legend) + 8)
    print(border)
    print(f"#   {legend}   #")
    print(border)


def main() -> None:
    banner("BEGIN CODE OUTPUT")

    kitchen = Kitchen(make_default_chefs())
    order = Order(
        1001,
        [
            Dish(1, make_recipe(RecipeId.BURGER)),
            Dish(2, make_recipe(RecipeId.SALAD)),
            Dish(3, make_recipe(RecipeId.PASTA)),
        ],
    )

    try:
        schedule = kitchen.schedule(order)
    except NotImplementedError:
        print("no schedule yet")
        banner("END CODE OUTPUT")
        return

    order.assign()

    for entry in schedule.entries:
        print(
            f"dish={entry.dish.id} "
            f"step={entry.step_index} "
            f"station={entry.station.value} "
            f"chef={entry.chef.name} "
            f"start={entry.start} "
            f"end={entry.end}"
        )
    print(f"makespan={schedule.makespan}")
    print(f"order_status={order.status.value}")

    banner("END CODE OUTPUT")


if __name__ == "__main__":
    main()
