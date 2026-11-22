"""You'll implement this."""

# NEW: permutations import for the brute force.
from itertools import permutations

from chefs import Chef
from order import Order
from schedule import Schedule, ScheduleEntry

# n = dishes, S = total steps, C = chefs, R = distinct recipes,
# M = distinct recipe orderings = n! / (count_1! * ... * count_R!).


class Kitchen:
    def __init__(self, chefs: list[Chef]) -> None:
        self._chefs = chefs

    @property
    def chefs(self) -> list[Chef]:
        return self._chefs

    # Optimized: search distinct recipe orderings only, and stop once a schedule hits the lower bound.
    # Time O(M·S·C) worst case, usually far less; Space O(S + n)
    def schedule(self, order: Order) -> Schedule:
        # CHANGED (original kitchen.py line 17): implemented. Old code:
        #     raise NotImplementedError("Kitchen.schedule is not implemented yet")
        groups: dict = {}  # recipe -> its dishes; dishes with the same recipe are interchangeable
        for dish in order.dishes:
            groups.setdefault(dish.recipe, []).append(dish)
        recipes = list(groups)
        remaining = [len(groups[r]) for r in recipes]
        lower_bound = self._lower_bound(order.dishes)
        best = Schedule([])

        def search(sequence: list[int]) -> bool:  # returns True once the lower bound is reached
            nonlocal best
            if len(sequence) == len(order.dishes):
                taken = [0] * len(recipes)
                dishes = []
                for r in sequence:
                    dishes.append(groups[recipes[r]][taken[r]])
                    taken[r] += 1
                candidate = self._simulate(dishes)
                if not best.entries or candidate.makespan < best.makespan:
                    best = candidate
                return best.makespan <= lower_bound  # provably optimal: stop everything
            for r in range(len(recipes)):  # O(R) branches; identical dishes are never reordered
                if remaining[r]:
                    remaining[r] -= 1
                    sequence.append(r)
                    done = search(sequence)
                    sequence.pop()
                    remaining[r] += 1
                    if done:
                        return True
            return False

        search([])
        return best

    # NEW: brute force kept so tests can compare it with the optimized schedule.
    # Brute force: simulate every ordering of the dishes. Time O(n!·S·C), Space O(S)
    def schedule_brute_force(self, order: Order) -> Schedule:
        best = Schedule([])
        for dishes in permutations(order.dishes):  # n! orderings
            candidate = self._simulate(dishes)
            if not best.entries or candidate.makespan < best.makespan:
                best = candidate
        return best

    # NEW: places each step in recipe order at the earliest time its chef, its station and the dish's
    # previous step are all free, using the chef who would finish it first. Entries are only appended
    # after everything already placed, so no chef or station is ever double-booked. Time O(S·C), Space O(S)
    def _simulate(self, dishes) -> Schedule:
        chef_free = {chef.id: 0 for chef in self._chefs}
        station_free: dict = {}
        entries = []
        for dish in dishes:
            ready = 0  # end time of this dish's previous step
            for step_index, (station, base_seconds) in enumerate(dish.recipe.ordered_steps):
                choice = None
                for chef in self._chefs:  # O(C): pick the earliest finish, not the earliest start
                    start = max(ready, chef_free[chef.id], station_free.get(station, 0))
                    end = start + chef.time_for_step(station, base_seconds)
                    if choice is None or end < choice[0]:
                        choice = (end, start, chef)
                end, start, chef = choice
                entries.append(ScheduleEntry(dish, step_index, station, chef, start, end))
                chef_free[chef.id] = station_free[station] = ready = end
        return Schedule(entries)

    # NEW: no schedule can finish sooner than this. For each station: the shortest wait before any dish
    # can reach it + all work on it (each step at its fastest chef) + the shortest work left after it.
    # Also at least the longest single dish. Time O(S·C), Space O(stations)
    def _lower_bound(self, dishes) -> int:
        bound = 0
        load: dict = {}
        head: dict = {}
        tail: dict = {}
        for dish in dishes:
            times = [(station, min(chef.time_for_step(station, base) for chef in self._chefs))
                     for station, base in dish.recipe.ordered_steps]
            total = sum(t for _, t in times)
            bound = max(bound, total)
            before = 0
            for station, t in times:
                after = total - before - t
                load[station] = load.get(station, 0) + t
                head[station] = min(head.get(station, before), before)
                tail[station] = min(tail.get(station, after), after)
                before += t
        for station in load:
            bound = max(bound, head[station] + load[station] + tail[station])
        return bound
