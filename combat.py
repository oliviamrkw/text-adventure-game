import time
import re
from game_updates import update_game_state, update_player_state
from proj1_event_logger import Event

class Combat:
    def __init__(self, game) -> None:
        self.player = game
        self.game = game
        self.combat_ongoing = False

    def start_combat(self, enemy) -> list[Event]:
        action_list = []
        self.combat_ongoing = True
        prev_location = self.player.game_state[1]
        update_game_state(self.player, location_id=10)
        location = self.game.get_location()
        time.sleep(0.5)
        print(f"\n{location.brief_description} with a {enemy.name}.\n")
        print(f"Your health: {self.player.player_state[0]} HP.")
        print(f"{enemy.name} health: {enemy.health} HP.\n")
        
        while self.combat_ongoing and enemy.is_alive() and self.player.player_state[0] > 0:
            action = input("\nType 'attack': ").strip().lower()
            attack_event = Event(self.player.get_location().location_id, self.player)
            if action == "attack":
                time.sleep(0.2)
                self.player_attack(enemy)
                attack_event.description = "Player attacked {enemy.name}"
            else:
                print("\nYou miss.\n")
                attack_event.description = "Player missed an attack on {enemy.name}"

            attack_event.next_command = action
            # action_list.append(attack_event)
            self.game.event_log.add_event(attack_event, "attack")
            
            if enemy.is_alive():
                time.sleep(0.2)
                self.enemy_attack(enemy)

        self.resolve_combat(self.player, enemy, prev_location)

        return action_list

    def player_attack(self, enemy) -> None:
        """Handles player attack, automatically uses the best weapon in their inventory."""
        weapon = None
        weapon_damage = 0

        for item in self.player.inventory.inventory_items:
            if isinstance(item, dict):
                item_obj = list(item.values())[0]
            else:
                item_obj = item

            match = re.search(r"(\d+)\s*damage", item_obj.get_description().lower())  
            if match:
                damage = int(match.group(1))
                if damage > weapon_damage:
                    weapon = item_obj
                    weapon_damage = damage  
        
        if self.player.inventory.has_item("sugar"):
            print("The sugar in your inventory fuels you. +1 damage")
            weapon_damage += 1

        if weapon:
            print(f"\n   > You attack with {weapon.get_name()}, dealing {weapon_damage} damage!\n")
            enemy.health -= weapon_damage
        else:
            print("\n   > You have no weapons! You punch for 0.5 damage.\n")
            enemy.health -= 0.5
        
        if enemy.is_alive():
            print(f"\n{enemy.name} has {enemy.health} HP remaining.\n")

    def enemy_attack(self, enemy) -> None:
        """Handles enemy attacks."""
        print(f"\n{enemy.name} attacks, dealing {enemy.attack} damage!\n")
        update_player_state(self.player, health=self.player.player_state[0] - enemy.attack)
        if self.player.player_state[0] > 0:
            print(f"\nYou have {self.player.player_state[0]} HP remaining.\n")

    def resolve_combat(self, game, enemy, prev_location: int) -> None:
        if self.player.player_state[0] <= 0:
            time.sleep(1)
            print("\nYou have been knocked out... \n")
            time.sleep(1)
            self.combat_ongoing = False
            self.game.ongoing = False
            if not self.player.inventory.has_item("USB stick"):
                print("USB Guy: Wow you suck at this. I'll just give you your USB stick back.")
                self.player.inventory.add_item("usb stick", self.player.inventory, self.player.player_state[2])
        elif not enemy.is_alive():
            print(f"\nYou defeated the {enemy.name}!\n")
            self.handle_enemy_defeat(enemy)
            time.sleep(0.5)
            self.combat_ongoing = False
        
        if not self.combat_ongoing and self.player.player_state[0] > 0:
            update_game_state(self.player, location_id=prev_location)
            print("\nYou return to your previous location:")
            print(self.player.get_location().brief_description)
    
    def handle_enemy_defeat(self, enemy) -> None:
        if enemy.name == "demon":
            self.player.inventory.add_item("lucky UofT mug", self.player._items, self.player.player_state[2])
            print("\nYou got your lucky UofT mug back!\n")
        elif enemy.name == "USB Guy":
            self.player.inventory.add_item("USB stick", self.player._items, self.player.player_state[2])
            print("\nYou got your USB stick back!\n")
        elif enemy.name == "lion":
            self.player.inventory.add_item("laptop charger", self.player._items, self.player.player_state[2])
            print("\nYou got your laptop charger back!\n")

