"""Calendar conflict detection.

Port of java/Calendar.java (original package code.ds).

Schedules events (each with a start/end Date) onto a timeline and reports the
time windows during which more than one event overlaps.

Java's nested Pair<Pair<Date,Integer>,Boolean> is represented here as a plain
tuple: ((datetime, event_id), is_start_boolean).
"""

from __future__ import annotations

import datetime
from typing import List, Set, Tuple


class Event:
    """A scheduled event with an id and a start/end timestamp."""

    def __init__(self, event_id: int, start_date: datetime.datetime,
                 end_date: datetime.datetime):
        self.id = event_id
        self.start_date = start_date
        self.end_date = end_date

    def __repr__(self) -> str:
        return (f"Event{{id={self.id}, startDate={self.start_date}, "
                f"endDate={self.end_date}}}")


class ConflictedTimeWindow:
    """A window [start, end] during which several events overlap."""

    def __init__(self, start_date: datetime.datetime, end_date: datetime.datetime,
                 conflicted_event_ids: Set[int]):
        self.start_date = start_date
        self.end_date = end_date
        self.conflicted_event_ids = conflicted_event_ids

    def get_start_date(self) -> datetime.datetime:
        return self.start_date

    def get_end_date(self) -> datetime.datetime:
        return self.end_date

    def get_conflicted_event_ids(self) -> Set[int]:
        return self.conflicted_event_ids

    def __repr__(self) -> str:
        ids = sorted(self.conflicted_event_ids)
        return (f"ConflictedTimeWindow{{startDate={self.start_date}, "
                f"endDate={self.end_date}, conflictedEventIds={ids}}}")


class Calendar:
    """Allows multiple events over the same window and finds the conflicts."""

    def __init__(self):
        # Each entry is ((date, event_id), is_start_boolean).
        self._sche_events: List[Tuple[Tuple[datetime.datetime, int], bool]] = []

    def schedule(self, event: Event) -> None:
        """Schedule an event; records its start and end as timeline points."""
        if event is not None:
            self._sche_events.append(((event.start_date, event.id), True))
            self._sche_events.append(((event.end_date, event.id), False))

    def find_conflicted_time_window(self) -> List[ConflictedTimeWindow]:
        """Sweep the sorted timeline and emit windows where >1 event overlaps.

        Sweep-line over start/end points. Time: O(n log n) for the sort.
        """
        # Sort by timestamp, breaking ties by event id (matches Java comparator).
        self._sche_events.sort(key=lambda p: (p[0][0], p[0][1]))

        output: List[ConflictedTimeWindow] = []
        if not self._sche_events:
            return output

        ongoing: Set[int] = set()
        ongoing.add(self._sche_events[0][0][1])
        start = self._sche_events[0][0][0]

        n = len(self._sche_events)
        for i in range(1, n):
            is_start = self._sche_events[i][1]
            cur_date = self._sche_events[i][0][0]
            cur_id = self._sche_events[i][0][1]
            if is_start:
                ongoing.add(cur_id)
                start = cur_date
                # Java peeks at index i+1 directly; guard it (the last event is
                # always an end event for valid input, so this never drops a
                # required window).
                if (len(ongoing) > 1 and i + 1 < n
                        and start != self._sche_events[i + 1][0][0]):
                    temp = set(ongoing)
                    res = ConflictedTimeWindow(
                        start, self._sche_events[i + 1][0][0], temp)
                    output.append(res)
                    start = self._sche_events[i + 1][0][0]
            else:
                if len(ongoing) > 1 and start != cur_date:
                    temp = set(ongoing)
                    res2 = ConflictedTimeWindow(start, cur_date, temp)
                    output.append(res2)
                    start = cur_date
                ongoing.discard(cur_id)
        return output


if __name__ == "__main__":
    calendar = Calendar()

    # Java `new Date(114, 0, 1, 10, 0)` -> year 1900+114 = 2014, month 0 = Jan.
    calendar.schedule(Event(1, datetime.datetime(2014, 1, 1, 10, 0),
                            datetime.datetime(2014, 1, 1, 11, 0)))
    calendar.schedule(Event(2, datetime.datetime(2014, 1, 1, 11, 0),
                            datetime.datetime(2014, 1, 1, 12, 0)))
    calendar.schedule(Event(3, datetime.datetime(2014, 1, 1, 12, 0),
                            datetime.datetime(2014, 1, 1, 13, 0)))

    calendar.schedule(Event(4, datetime.datetime(2014, 1, 2, 10, 0),
                            datetime.datetime(2014, 1, 2, 11, 0)))
    calendar.schedule(Event(5, datetime.datetime(2014, 1, 2, 9, 30),
                            datetime.datetime(2014, 1, 2, 11, 30)))
    calendar.schedule(Event(6, datetime.datetime(2014, 1, 2, 8, 30),
                            datetime.datetime(2014, 1, 2, 12, 30)))

    calendar.schedule(Event(7, datetime.datetime(2014, 1, 3, 10, 0),
                            datetime.datetime(2014, 1, 3, 11, 0)))
    calendar.schedule(Event(8, datetime.datetime(2014, 1, 3, 9, 30),
                            datetime.datetime(2014, 1, 3, 10, 30)))
    calendar.schedule(Event(9, datetime.datetime(2014, 1, 3, 9, 45),
                            datetime.datetime(2014, 1, 3, 10, 45)))

    conflicted_time_windows = calendar.find_conflicted_time_window()
    print(conflicted_time_windows)
    # Expected (matches the Java reference output):
    # [ConflictedTimeWindow{... conflictedEventIds=[5, 6]},
    #  ConflictedTimeWindow{... conflictedEventIds=[4, 5, 6]},
    #  ConflictedTimeWindow{... conflictedEventIds=[5, 6]},
    #  ConflictedTimeWindow{... conflictedEventIds=[8, 9]},
    #  ConflictedTimeWindow{... conflictedEventIds=[7, 8, 9]},
    #  ConflictedTimeWindow{... conflictedEventIds=[7, 9]}]
