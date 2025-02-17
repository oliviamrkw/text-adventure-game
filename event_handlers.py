import re
from game_entities import Enemy, Item, Location
from inventory import Inventory
from combat import Combat
from time import sleep
from typing import Optional
from game_updates import update_game_state, update_player_state, update_puzzle_state
from proj1_event_logger import Event

def handle_combat(game, command: str, result: str) -> None:
    """Handles all combat scenarios."""
    if game._string_in_text("pass out", result):
        if game.inventory.has_item("USB stick") and game.inventory.has_item("laptop charger"):
            print("Demon: I have taken your lucky UofT mug and you will never get it back!")
            demon = Enemy("demon", 100, 50)
            game.combat_system.start_combat(demon)
    elif game._string_in_text("attack the lions", result):
        lions = Enemy("lion", 50, 20)
        game.combat_system.start_combat(lions)

def handle_inventory_event(game, command: str, result: str) -> None:
    """Handles events that change inventory."""
    if game._string_in_text("gifts", result):
        if game.inventory.has_item("membership card"):
            if not game.inventory.has_item("uoft hoodie"):
                sleep(1)
                print("Merchant: Let me see... Ah, wonderful, ya have it! Here ya go. Check yer inventory for some goodies.")
                game.inventory.add_money(100)
                game.inventory.add_item("uoft hoodie", game._items, game.player_state[2])
                game.inventory.add_item("a very sharp stick", game._items, game.player_state[2])
            else:
                print("Merchant: I already gave ya yer gifts!")
        else:
            print("Merchant: Ah, shoo, shoo! Come back when you have yer card.")
    elif game._string_in_text("fall asleep", result):
        game.inventory.remove_item("tea for lions", game.inventory.inventory_items)
        game.inventory.add_item("laptop charger", game._items, game.player_state[2])

def handle_npc_interaction(game, command: str, result: str) -> None:
    """Handles NPC interactions."""
    if game._string_in_text("overhear", result):
        if game.inventory.has_item("USB stick"):
            print("They mention someone left their laptop charger at Bahen.")
        else:
            print("They mention someone stole a USB stick at Robarts.")

def handle_dialogue(game, result: str, choice: Optional[str] = None) -> None:
    """Handles player yes/no choices."""
    if choice is None:
        choice = input("\nEnter response: ").lower().strip()

    dialogue_event = Event(game.get_location().location_id, game)
    dialogue_event.description = choice
    dialogue_event.next_command = choice

    if choice == "yes":
        game.event_log.add_event(dialogue_event, choice)
        if game._string_in_text("$20", result):
            print("You steal the $20 bill. You feel guilty.")
            game.inventory.add_money(20)
        elif game._string_in_text("powder", result):
            print("\nYou bought the sugar for $5.")
            game.inventory.add_item("sugar", game._items, game.player_state[2])
            print(f"Remaining money in wallet: ${game.inventory.get_money()}\n")
        elif game._string_in_text("test", result):
            print("You help them review for their test.")
            print("They say: Hey, thanks for helping me out. Here's a cool sword I found!")
            game.inventory.add_item("sword", game._items, game.player_state[2])
        elif game._string_in_text("USB", result):
            print("You say: Hey, is that my USB?")
            # sleep(1)
            print("USB Guy: Maybe. If you want it back, you have to fight me for it!")
            # sleep(1)
            usb_guy = Enemy("USB Guy", 5, 0.5)
            game.combat_system.start_combat(usb_guy)
    else:
        print("You walk away.")
        game.event_log.add_event(dialogue_event, choice)
    update_game_state(game, dialogue_ongoing=False)

def handle_menu_order(game, command: str, result: str) -> None:
    """Handles ordering from the Starbucks in Robarts. Use reponse instead if it's provided."""
    if game._string_in_text("the menu", result):
        menu = {
            "order a matcha latte": 5,
            "order a brown sugar espresso": 7,
            "order tea for lions": 3
        }

        for order in menu.keys():
            game.get_location().available_commands[order] = f"You {order} from the menu."

        if command in menu:
            name = command
            price = menu[command]
    
            if game.inventory.remove_money(price):  # check if wallet has enough money
                print(f"\nYou {name} for ${price}.")
                print(f"Remaining money in wallet: ${game.inventory.get_money()}\n")
                game.inventory.add_item("tea for lions", game._items, game.player_state[2])
            else:
                print("\nYou don't have enough money to buy that!\n")
        return  # exit so we don't add the items to the inventory
    
def handle_location_event(game, location_id: int) -> None:
    """Handles events at specific locations."""
    if game.game_state[1] == 2:
        if game.inventory.has_item("USB stick"):
            game.get_location().available_commands["go south"] = 7

    elif game.game_state[1] == 8:
        if game.inventory.has_item("tea for lions"):
            game.get_location().available_commands["use tea for lions"] = "You put the cup of tea on the ground, and the lions slowly come up to drink it. They instantly fall asleep, allowing you to grab your laptop charger!"
            if game.inventory.has_item("laptop charger"):
                game.get_location().available_commands = []
                game.get_location().available_commands["go north"] = 9

def handle_item_pickup(game, item_name: str, item: Item) -> None:
    """Handles picking up items from events."""
    if "$" in item_name:
        match = re.search(r'\$(\d+)', item_name)
        if match:
            amount = int(match.group(1))
            game.inventory.add_money(amount)
    else:
        game.inventory.add_item(item, game._items, game.player_state[2])

def use_item(game) -> None:
    """Handles using an item."""
    item = input("Which item in your inventory would you like to use? ").strip().lower()

    if not game.inventory.has_item(item):
        print("You don't have that item.")
        return

    if item in ["candy", "uoft hoodie"]:
        consume_item(game, item)
    elif item in ["book", "orange", "torch", "shield"]:
        place_item(game, item)
    else:
        print("You can't use that here!")

    use_event, item_event = Event(game.get_location().location_id, game), Event(game.get_location().location_id, game)
    use_event.description, item_event.description = "use", item
    use_event.next_command, item_event.next_command = "use", item
    game.event_log.add_event(use_event, use_event.next_command)
    game.event_log.add_event(item_event, item_event.next_command)

def consume_item(game, item: str) -> None:
    """Consume an item and apply its effects."""
    if item == "candy":
        print("You ate the candy and got +1 hp")
        update_player_state(game, health=game.player_state[0] + 1)
    elif item == "uoft hoodie":
        print("You put on the UofT hoodie and feel a surge of power. +40hp")
        update_player_state(game, health=game.player_state[0] + 40)
    game.inventory.remove_item(item, game._items)

def place_item(game, item: str) -> None:
    """Handles item placing in the backrooms."""
    print(f"You place the {item} on the pedestal.")

    if game.game_state[1] == game._items[item].get_target_position():
        print("The room lights up, it seems you've solved something.")
        update_player_state(game, score=game.player_state[2] + 25)
        if item == "book":
            update_puzzle_state(game, book_correct=True)
        elif item == "orange":
            update_puzzle_state(game, orange_correct=True)
        elif item == "torch":
            update_puzzle_state(game, torch_correct=True)
        elif item == "shield":
            update_puzzle_state(game, shield_correct=True)
    else:
        print("Something seems off... nothing happens. Maybe you should try this somewhere else.")
