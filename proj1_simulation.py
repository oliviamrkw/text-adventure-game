from __future__ import annotations

from adventure import AdventureGame
from game_entities import Location
from game_updates import check_win
from proj1_event_logger import Event, EventList


class AdventureGameSimulation:
    """A simulation of an adventure game playthrough.
    """
    # Private Instance Attributes:
    #   - _game: The AdventureGame instance that this simulation uses.
    #   - _events: A collection of the events to process during the simulation.
    _game: AdventureGame
    _events: EventList

    def __init__(self, game_data_file: str, initial_location_id: int, commands: list[str]) -> None:
        """Initialize a new game simulation based on the given game data, that runs through the given commands.

        Preconditions:
        - len(commands) > 0
        - all commands in the given list are valid commands at each associated location in the game
        """
        self._game = AdventureGame(game_data_file, initial_location_id)
        self._events = self._game.event_log

        initial_location = self._game.get_location()
        first_event = Event(initial_location_id, self._game)
        first_event.description = initial_location.long_description
        self._events.add_event(first_event)

        self.generate_events(commands, initial_location)

    def generate_events(self, commands: list[str], current_location: Location) -> None:
        """Generate all events in this simulation.

        Preconditions:
        - len(commands) > 0
        - all commands in the given list are valid commands at each associated location in the game
        """
        for command in commands:
            if self._game.game_state[3]:
                AdventureGame.handle_dialogue(self._game, "", response="yes")
                print("response")

            self._game.handle_game_action(command)

            check_win(self._game)

            current_location = self._game.get_location()

            event = Event(current_location.location_id, self._game)
            event.description = current_location.long_description
            self._events.add_event(event, command)

    def get_id_log(self) -> list[int]:
        """
        Get back a list of all location IDs in the order that they are visited within a game simulation
        that follows the given commands.

        Preconditions:
        - The simulation has been initialized with valid commands

        >>> sim = AdventureGameSimulation('sample_locations.json', 1, ["go east"])
        >>> sim.get_id_log()
        [1, 2]

        >>> sim = AdventureGameSimulation('sample_locations.json', 1, ["go east", "go east", "buy coffee"])
        >>> sim.get_id_log()
        [1, 2, 3, 3]
        """
        return self._events.get_id_log()

    def run(self) -> None:
        """Run the game simulation and log location descriptions.

        Preconditions:
        - The simulation has been initialized and events have been generated
        """
        current_event = self._events.first  # Start from the first event in the list

        while current_event:
            print(current_event.description)
            if current_event is not self._events.last:
                print("You choose:", current_event.next_command)

            # Move to the next event in the linked list
            current_event = current_event.next


if __name__ == "__main__":
    # When you are ready to check your work with python_ta, uncomment the following lines.
    # (Delete the "#" and space before each line.)
    # IMPORTANT: keep this code indented inside the "if __name__ == '__main__'" block
    import python_ta
    python_ta.check_all(config={
        'max-line-length': 120,
        'disable': ['R1705', 'E9998', 'E9999']
    })

    # Walkthrough to win the game, solution 2
    win_walkthrough = [
        "check papers", "go east", "go east", "go north", "go north", "go north", 
        "talk to the person studying", "talk to the person on the computer",
        "go south", "go south", "go south", "go west", "talk to the people",
        "go south", "go south", "fight the lions", "go north", "go north", "visit the blue truck",
        "cross the road", "go back to dorm room", "inspect torch", "go east",
        "inspect book", "go north", "inspect shield", "go west", "inspect orange",
        "go south", "use", "book", "go east", "use", "shield", "go north", "use", "orange",
        "go west", "use", "torch"
    ]
    expected_log = [1, 1, 1, 1, 2, 2, 3, 3, 4, 4, 5, 5, 6, 6, 6, 6, 6, 6, 10, 6, 6, 5, 5,
                    4, 4, 3, 3, 2, 2, 2, 2, 7, 7, 8, 8, 10, 8, 8, 9, 9, 9, 9, 9, 9, 10, 9,
                    9, 11, 11, 11, 11, 12, 12, 12, 12, 13, 13, 13, 13, 14, 14, 14, 14, 11,
                    11, 11, 11, 11, 11, 12, 12, 12, 12, 12, 12, 13, 13, 13, 13, 13, 13, 14, 14, 14, 14, 14]
    sim = AdventureGameSimulation('game_data.json', 1, win_walkthrough)
    print(f"Actual: {sim.get_id_log()}")
    assert expected_log == sim.get_id_log()

    # Walkthrough to lose the game
    lose_demo = [
        "go outside", "cross the road", "attack"
    ]
    expected_log = [1, 1, 1, 1, 1, 1, 1]
    sim = AdventureGameSimulation('game_data.json', 1, lose_demo)
    assert expected_log == sim.get_id_log()

    # Walkthrough to demonstrate inventory
    inventory_demo = [
        "check clothes", "inventory", "use", "candy"
    ]
    expected_log = [1, 1, 1, 1, 1, 1, 1, 1, 1]
    sim = AdventureGameSimulation('game_data.json', 1, inventory_demo)
    assert expected_log == sim.get_id_log()

    # Walkthrough to demonstrate score
    scores_demo = [
        "check clothes", "score"
    ]
    expected_log = [1, 1, 1, 1, 1]
    sim = AdventureGameSimulation('game_data.json', 1, scores_demo)
    assert expected_log == sim.get_id_log()

    # Walkthrough to demonstrate combat
    combat_demo = [
        "check clothes", "go east", "go east", "go north", "go north", "go north",
        "talk to the person on the computer", "yes", "attack"
    ]
    expected_log = [1, 1, 1, 1, 2, 2, 3, 3, 4, 4, 5, 5, 6, 6, 6, 10, 10, 10, 10, 10, 6, 6, 6, 6, 6]
    sim = AdventureGameSimulation('game_data.json', 1, combat_demo)
    assert expected_log == sim.get_id_log()

    # Walkthrough to demonstrate purchasing
    purchase_demo = [
        "check box", "go east", "go east", "go north", "wait in line", "order tea for lions"
    ]
    expected_log = [1, 1, 1, 1, 2, 2, 3, 3, 4, 4, 4, 4, 4]
    sim = AdventureGameSimulation('game_data.json', 1, purchase_demo)
    assert expected_log == sim.get_id_log()

    # Walkthrough to demonstrate dialogue
    purchase_demo = [
        "go east", "go east", "go north", "go north", "go north", 
        "talk to the person studying"
    ]
    expected_log = [1, 1, 2, 2, 3, 3, 4, 4, 5, 5, 6, 6, 6, 6]
    sim = AdventureGameSimulation('game_data.json', 1, purchase_demo)
    assert expected_log == sim.get_id_log()
