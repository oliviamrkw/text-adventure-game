from event_handlers import use_item
from game_updates import update_game_state, update_player_state, display_location

def handle_menu_command(game, choice: str) -> None:
    """Handles all the menu commands."""
    location = game.get_location()

    if choice == "look":
        print(location.long_description)
    elif choice == "inventory":
        game.inventory.show_inventory()
    elif choice == "use":
        use_item(game)
    elif choice == "score":
        print(f"Current score: {game.inventory.get_score(game.player_state[2])}")
    elif choice == "undo":
        undo(game)
    elif choice == "log":
        if game.event_log.first:
            game.event_log.display_events()
        else:
            print("Nothing to display!")
    elif choice == "quit":
        update_game_state(game, ongoing=False)
        quit()

def undo(game) -> None:
    """Undo the last move. Reverts the player's state, including location, inventory, money, and health."""
    if game.event_log.is_empty():
        print("No actions to undo.")
        return

    last_event = game.event_log.last
    if last_event is None or last_event.prev is None:
        print("No actions to undo.")
        return

    print("Undoing last move...")

    prev_event = last_event.prev

    update_game_state(game, location_id=prev_event.id_num)

    current_inventory = {item.get_name() for item in game.inventory.inventory_items}
    prev_inventory = set(prev_event.current_inventory)

    for item_name in current_inventory - prev_inventory:
        game.inventory.remove_item(item_name, game._items)

    for item_name in prev_inventory - current_inventory:
        game.inventory.add_item(item_name, game._items, game.player_state[2])

    game.inventory.wallet.money = prev_event.current_money
    update_player_state(game, health=prev_event.current_health)

    if game.game_state[0] > 0:
        update_game_state(game, moves=game.game_state[0] - 1)

    game.event_log.remove_last_event()

    display_location(game)