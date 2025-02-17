from __future__ import annotations
import json
from typing import Optional

import re   # for matching words in strings

from game_entities import Location, Item
from combat import Combat
from inventory import Inventory
from proj1_event_logger import Event, EventList
from event_handlers import (
    handle_combat, handle_inventory_event, handle_npc_interaction,
    handle_dialogue, handle_item_pickup, handle_location_event, handle_menu_order
)
from menu_handlers import handle_menu_command
from game_updates import (
    display_time, display_location, update_game_state, check_win,
    print_objective
)

MENU = ["look", "inventory", "use", "score", "undo", "log", "quit"]
DIALOGUE_CHECKS = ["$20", "powder", "review", "USB"]
EVENT_HANDLERS = {
    "pass out": handle_combat,
    "overhear": handle_npc_interaction,
    "attack the lions": handle_combat,
    "gifts": handle_inventory_event,
    "review": handle_inventory_event,
    "menu": handle_menu_order,
    "fall asleep": handle_inventory_event
}
LOCATION_CHECKS = {2, 8}


class AdventureGame:
    """A text adventure game class storing all location, item and map data.

    Instance Attributes:
        - _locations: a mapping of location IDs to location objects
        - _items: a list of all item objects
        - player_state: a tuple representing the player's health, money, and score
        - game_state: a tuple representing the moves so far, current location ID,
            whether the game is ongoing, and whether dialogue is ongoing
        - puzzle_state: a tuple representing the state of the puzzles (book, orange, torch, shield)
        - inventory: the player's inventory
        - event_log: a log of all events in the game
        - combat_system: the combat system used in the game

    Representation Invariants:
        - all(location_id in self._locations for location_id in self._locations.keys())
        - all(item in self._items for item in self._items)
        - self.game_state[1] in self._locations
        - self.player_state[2] >= 0  # score
        - self.player_state[1] >= 0  # money
        - self.player_state[0] >= 0  # health
    """

    # Private Instance Attributes (do NOT remove these two attributes):
    #   - _locations: a mapping from location id to Location object.
    #                       This represents all the locations in the game.
    #   - _items: a list of Item objects, representing all items in the game.

    _locations: dict[int, Location]
    _items: dict[str, Item]

    player_state: tuple[int, int, int]  # (health, money, score)
    game_state: tuple[int, int, bool, bool]  # (moves_so_far, current_location_id, ongoing, dialogue_ongoing)
    puzzle_state: tuple[bool, bool, bool, bool]  # (book_correct, orange_correct, torch_correct, shield_correct)

    inventory: Inventory
    event_log: EventList
    combat_system: Combat

    def __init__(self, game_data_file: str, initial_location_id: int) -> None:
        """
        Initialize a new text adventure game, based on the data in the given file, setting starting location of game
        at the given initial location ID.
        (note: you are allowed to modify the format of the file as you see fit)

        Preconditions:
        - game_data_file is the filename of a valid game data JSON file
        - initial_location_id in self._locations
        """
        self._locations, self._items = self._load_game_data(game_data_file)

        self.player_state = (10, 0, 0)  # (health, money, score)
        self.game_state = (0, initial_location_id, True, False)  # (moves_so_far, current_location_id, ongoing)
        self.puzzle_state = (
            False, False, False, False  # (book_correct, orange_correct, torch_correct, shield_correct)
        )

        self.inventory, self.event_log, self.combat_system = (Inventory(), EventList(), Combat(self))

    @staticmethod
    def _load_game_data(filename: str) -> tuple[dict[int, Location], list[Item]]:
        """Load locations and items from a JSON file with the given filename and
        return a tuple consisting of (1) a dictionary of locations mapping each game location's ID to a Location object,
        and (2) a dictionary of all Item objects mapping item names to Item objects.

        Preconditions:
        - filename is a valid JSON file containing game data
        """
        with open(filename, 'r') as f:
            data = json.load(f)  # This loads all the data from the JSON file

        items = {}
        for item in data['items']:
            items[item['name']] = Item(
                item['name'], item['description'], item['start_position'],
                item['target_position'], item.get('target_points', 0)
            )

        locations = {}
        for loc in data['locations']:
            item_objects = [items[item_name] for item_name in loc['items']]
            locations[loc['id']] = Location(
                loc['id'], loc['name'], loc['brief_description'], loc['long_description'],
                loc['available_commands'], item_objects
            )

        return locations, items

    @staticmethod
    def _string_in_text(string: str, text: str) -> bool:
        """Return True if the exact word appears by itself in the text, otherwise False.

        Preconditions:
        - string is a non-empty string
        - text is a non-empty string
        """
        pattern = rf'(?<!\w){re.escape(string)}(?!\w)'
        return bool(re.search(pattern, text, re.IGNORECASE))

    def get_location(self, loc_id: Optional[int] = None) -> Location:
        """Return Location object associated with the provided location ID.
        If no ID is provided, return the Location object associated with the current location.

        Preconditions:
        - loc_id is None or loc_id in self._locations
        """
        if loc_id is None:
            return self._locations[self.game_state[1]]
        return self._locations[loc_id]

    def move(self, command: str) -> None:
        """Move player to the destination, if possible. Assumes valid command.

        Preconditions:
        - command is a valid command in the current location's available commands
        """
        location = self.get_location()
        if command in location.available_commands:
            new_location_id = location.available_commands[command]
            update_game_state(self, location_id=new_location_id)
            display_location(self)
        else:
            print("Not a valid location.")

    def handle_event(self, command: str) -> None:
        """Handle special events.

        Preconditions:
        - command is a valid command in the current location's available commands
        """
        result = ''
        location = self.get_location()

        if command in location.available_commands:
            result = location.available_commands[command]
            print(result)
            if not (
                "go" in command or "talk to the people outside" in command
                or "visit" in command or "computer" in command
            ):
                del location.available_commands[command]

        if any(option in result for option in DIALOGUE_CHECKS):
            update_game_state(self, dialogue_ongoing=True)
            handle_dialogue(self, result)
            return

        if self.game_state[1] in LOCATION_CHECKS:
            handle_location_event(self, self.game_state[1])

        for key, func in EVENT_HANDLERS.items():
            if self._string_in_text(key, result):
                func(self, command, result)
                return

        for item_name, item in self._items.items():
            if self._string_in_text(item_name, result):
                handle_item_pickup(self, item_name, item)

    def get_choice(self) -> str:
        """Prompts player for input.

        Preconditions:
        - The game is ongoing and not in dialogue mode
        """
        location = self.get_location()
        print("\n\nWhat to do? Choose from: ", MENU)
        print("\nAt this location, you can also:")
        for action in location.available_commands:
            print("-", action)

        choice = input("\nEnter action: ").lower().strip()
        while choice not in location.available_commands and choice not in MENU:
            print("That was an invalid option; try again.")
            choice = input("\nEnter action: ").lower().strip()

        print(f"\n\n========\nYou decided to: {choice}\n\n\n")
        update_game_state(self, moves=self.game_state[0] + 1)
        return choice

    def handle_game_action(self, choice: str) -> None:
        """Handles non-menu input.

        Preconditions:
        - choice is a valid command in the current location's available commands or in MENU
        """
        event = Event(self.get_location().location_id, self)
        event.description = self.get_location().brief_description
        event.next_command = choice
        self.event_log.add_event(event, choice)

        if "go" in choice:
            self.move(choice)
        else:
            self.handle_event(choice)

    def play(self) -> None:
        """MAIN GAME LOOP"""
        self.event_log = EventList()

        print_objective()

        while self.game_state[2] and self.game_state[0] < 60:
            display_time(self)

            if self.game_state[3]:
                continue
            else:
                choice = self.get_choice()

            if choice in MENU and not self.game_state[3]:
                handle_menu_command(self, choice)
            else:
                self.handle_game_action(choice)

            if check_win(self):
                quit()

        print("You lose, sorry!")
        quit()


if __name__ == "__main__":
    import python_ta
    python_ta.check_all(config={
        'max-line-length': 120,
        'disable': ['R1705', 'E9998', 'E9999']
    })

    game = AdventureGame("game_data.json", 1)
    game.play()
