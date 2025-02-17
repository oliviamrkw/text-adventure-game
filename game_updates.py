from typing import Optional
from time import sleep

from proj1_event_logger import EventList


def display_time(game) -> None:
    """Displays current in-game time."""
    print(f"3:{game.game_state[0]:02}PM")

def display_location(game) -> None:
    """Displays location information only when location changes."""
    location = game.get_location()

    description = location.brief_description if location.visited else location.long_description
    print(f"LOCATION: {location.name}\n====================")
    print(description)

def update_player_state(
    game, health: Optional[int] = None, money: Optional[int] = None,
    score: Optional[int] = None
) -> None:
    """Update player stats."""
    current_health, current_money, current_score = game.player_state
    game.player_state = (
        health if health is not None else current_health,
        money if money is not None else current_money,
        score if score is not None else current_score
    )

def update_game_state(
    game, moves: Optional[int] = None, location_id: Optional[int] = None,
    ongoing: Optional[bool] = None, dialogue_ongoing: Optional[bool] = None
) -> None:
    """Update game state while keeping other values unchanged."""
    current_moves, current_location, current_ongoing, current_dialogue_ongoing = game.game_state
    game.game_state = (
        moves if moves is not None else current_moves,
        location_id if location_id is not None else current_location,
        ongoing if ongoing is not None else current_ongoing,
        dialogue_ongoing if dialogue_ongoing is not None else current_dialogue_ongoing
    )

def update_puzzle_state(
    game, book_correct: Optional[bool] = None, orange_correct: Optional[bool] = None,
    torch_correct: Optional[bool] = None, shield_correct: Optional[bool] = None
) -> None:
    """Update puzzle state while keeping other values unchanged."""
    current_book, current_orange, current_torch, current_shield = game.puzzle_state
    game.puzzle_state = (
        book_correct if book_correct is not None else current_book,
        orange_correct if orange_correct is not None else current_orange,
        torch_correct if torch_correct is not None else current_torch,
        shield_correct if shield_correct is not None else current_shield
    )

def check_win(game) -> bool:
    """Check if the player has won."""
    if game.inventory.has_item("lucky UofT mug") and game.game_state[1] not in {11, 12, 13, 14}:
        print("Now, after you got all of your items, you can finally submit your project.")
        game.get_location().available_commands["go back to dorm room"] = 11

    if all(game.puzzle_state):
        print("\nAfter placing the final item in the pedestal, a booming voice speaks.")
        print("\nVoice: You have proven yourself worthy. You may now submit your project.")
        sleep(1)
        print("\nYour laptop appears in front of you, floating in the air.")
        print("You submit your project, and breathe a sigh of relief.")
        sleep(5)
        print("You have won the game!")
        display_time(game)
        print(f"You took {game.game_state[0]} moves to complete the game.")
        print(f"Your final score is {game.player_state[2]} points. Great job!")
        sleep(5)
        return True

    return False

def print_objective() -> None:
    print("You are in your dorm room. \n\nYour room is a mess. Clothes are scattered all around.")
    print("There's a box in the corner, and a few loose papers on the desk. The door is to the east.\n\n")
    print("""Your project is due at 4pm. But before you submit, you need to find 3 items:
    1. your project USB drive
    2. your laptop charger
    3. your lucky UofT mug""")