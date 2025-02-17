from __future__ import annotations
from dataclasses import dataclass
from typing import Optional


@dataclass
class Event:
    """
    A node representing one event in an adventure game.

    Instance Attributes:
    - id_num: Integer id of this event's location
    - description: Long description of this event's location
    - next_command: String command which leads this event to the next event, None if this is the last game event
    - next: Event object representing the next event in the game, or None if this is the last game event
    - prev: Event object representing the previous event in the game, None if this is the first game event
    """

    id_num: int
    description: str
    next_command: Optional[str]
    next: Optional[Event]
    prev: Optional[Event]

    current_inventory: list[str]
    current_money: int
    current_health: int

    def __init__(self, id_num: int, game) -> None:
        """Initialize a new event"""
        self.id_num = id_num
        self.description = ""
        self.next_command = None
        self.next = None
        self.prev = None

        self.current_inventory = [item.get_name() for item in game.inventory.inventory_items]
        self.current_money = game.inventory.get_money()
        self.current_health = game.player_state[0]


class EventList:
    """
    A linked list of game events.

    Instance Attributes:
        - first: first event in the list
        - last: last event in the list

    Representation Invariants:
        - (self.first is None and self.last is None) or (self.first is not None and self.last is not None)
        - self.first is None or self.first.prev is None
        - self.last is None or self.last.next is None
    """
    first: Optional[Event]
    last: Optional[Event]

    def __init__(self) -> None:
        """Initialize a new empty event list."""

        self.first = None
        self.last = None

    def display_events(self) -> None:
        """Display all events in chronological order."""
        curr = self.first
        while curr:
            print(f"Location: {curr.id_num}, Command: {curr.next_command}")
            curr = curr.next

    def is_empty(self) -> bool:
        """Return whether this event list is empty."""
        return self.first is None

    def add_event(self, event: Event, command: Optional[str] = None) -> None:
        """Add the given new event to the end of this event list.
        The given command is the command which was used to reach this new event, or None if this is the first
        event in the game.
        """

        if self.is_empty():
            self.first = event
            self.last = event
            event.next_command = command
            event.prev = None
        else:
            self.last.next = event
            event.prev = self.last
            event.next_command = command
            self.last = event

    def remove_last_event(self) -> None:
        """Remove the last event from this event list.
        If the list is empty, do nothing."""

        if self.is_empty():
            return
        if self.first == self.last:
            self.first = None
            self.last = None
        else:
            self.last = self.last.prev
            if self.last:
                self.last.next = None

    def get_id_log(self) -> list[int]:
        """Return a list of all location IDs visited for each event in this list, in sequence."""
        lst = []
        curr = self.first
        while curr:
            lst.append(curr.id_num)
            curr = curr.next
        return lst


if __name__ == "__main__":
    import python_ta
    python_ta.check_all(config={
        'max-line-length': 120,
        'disable': ['R1705', 'E9998', 'E9999']
    })
