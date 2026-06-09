"""Idiomatic Python 3 port of java/design.java (original package code.ds).

Object-oriented design exercise: a parking lot with small / compact / large
slots, several vehicle types, and park / un-park bookkeeping.

The Java ``Slot`` class had a field ``isOccupied`` and a method
``isOccupied()``; in Python the field is renamed ``_occupied`` and the accessor
stays ``is_occupied()``. Note the source's vehicles never override the
``canFit*`` predicates, so every ``canFit`` returns ``False`` and ``park``
always returns the sentinel token ``-1`` -- this behaviour is preserved. The
Java source has no ``main``; a demonstrative one is added.
"""


# ---------------------------------------------------------------------------
# Vehicles
# ---------------------------------------------------------------------------
class Vehicle:
    _counter = 0  # supplies a stable identity hash (Java Object.hashCode)

    def __init__(self):
        self.licence_plate = None
        Vehicle._counter += 1
        self._hash = Vehicle._counter

    def can_fit_in_small_slot(self):
        return False

    def can_fit_in_compact_slot(self):
        return False

    def can_fit_in_large_slot(self):
        return False

    def hash_code(self):
        return self._hash


class Car(Vehicle):
    pass


class Motorcycle(Vehicle):
    pass


class Bus(Vehicle):
    pass


class Truck(Vehicle):
    pass


# ---------------------------------------------------------------------------
# Slots
# ---------------------------------------------------------------------------
class Slot:
    def __init__(self, slot_number):
        self._occupied = False  # Java field isOccupied (renamed)
        self.slot_number = slot_number

    def is_occupied(self):
        return self._occupied

    def get_slot_number(self):
        return self.slot_number

    def park(self):
        self._occupied = True

    def un_park(self):
        self._occupied = False

    def __eq__(self, other):
        return isinstance(other, Slot) and other.slot_number == self.slot_number

    def __hash__(self):
        h = 5
        h = 53 * h + self.slot_number
        return h


class SmallSlot(Slot):
    pass


class CompactSlot(Slot):
    pass


class LargeSlot(Slot):
    pass


# ---------------------------------------------------------------------------
# Parking lot
# ---------------------------------------------------------------------------
class ParkingLot:
    NUMBER_OF_SMALL_SLOTS = 10
    NUMBER_OF_COMPACT_SLOTS = 10
    NUMBER_OF_LARGE_SLOTS = 10

    def __init__(self):
        self.small_slots = []   # stacks
        self.compact_slots = []
        self.large_slots = []
        self._create_slots()
        self.occupied_slots = {}  # token -> Slot

    def _create_slots(self):
        for i in range(1, self.NUMBER_OF_SMALL_SLOTS + 1):
            self.small_slots.append(SmallSlot(i))
        for i in range(1, self.NUMBER_OF_COMPACT_SLOTS + 1):
            self.compact_slots.append(CompactSlot(i))
        for i in range(1, self.NUMBER_OF_LARGE_SLOTS + 1):
            self.large_slots.append(LargeSlot(i))

    def park(self, vehicle):
        slot = None
        unique_token = -1

        if vehicle.can_fit_in_small_slot():
            slot = self.small_slots.pop()
            if slot is not None:
                unique_token = self._park_helper(slot, vehicle)
        if vehicle.can_fit_in_compact_slot():
            slot = self.compact_slots.pop()
            if slot is not None:
                unique_token = self._park_helper(slot, vehicle)
        if vehicle.can_fit_in_large_slot():
            slot = self.large_slots.pop()
            if slot is not None:
                unique_token = self._park_helper(slot, vehicle)
        return unique_token

    def un_park(self, unique_token):
        slot = self.occupied_slots.get(unique_token)
        slot.un_park()
        if isinstance(slot, SmallSlot):
            self.small_slots.append(slot)
        self.occupied_slots.pop(unique_token, None)

    def _park_helper(self, slot, vehicle):
        slot.park()
        unique_token = vehicle.hash_code() * 43
        self.occupied_slots[unique_token] = slot
        return unique_token


# ---------------------------------------------------------------------------
# Floors / areas (placeholder scaffolding from the source)
# ---------------------------------------------------------------------------
class ParkingFloor:
    def __init__(self):
        self.available_car_parking_slots = []
        self.available_bike_parking_slots = []
        self.occupied_car_parking_slots = []
        self.occupied_bike_parking_slots = []

    def get_number_of_available_car_parking_slots(self):
        return []

    def get_number_of_available_bike_parking_slots(self):
        return []


class ParkingArea:
    def __init__(self):
        self.parking_floors = []


if __name__ == "__main__":
    lot = ParkingLot()
    car = Car()
    token = lot.park(car)
    # -1: Car never overrides the canFit* predicates (faithful to the source).
    print("token:", token)

    slot = SmallSlot(7)
    slot.park()
    print("slot", slot.get_slot_number(), "occupied:", slot.is_occupied())
