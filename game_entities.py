from dataclasses import dataclass
from typing import Optional

@dataclass
class Item:
    """An item in our text adventure game world.

    Instance Attributes:
        - name: The name of the item.
        - description: A brief description of the item.
        - start_position: The initial position of the item.
        - target_position: The position where the item needs to be moved.
        - target_points: The points awarded for moving the item to the target position.

    Representation Invariants:
        - name != ''
        - start_position >= 0
        - target_position >= 0
        - target_points >= 0
    """

    name: str
    description: str
    start_position: int
    target_position: int
    target_points: int

    def __init__(self, name: str, description: str, start_position: int, target_position: int, target_points: int) -> None:
        self.name = name
        self.description = description
        self.start_position = start_position
        self.target_position = target_position
        self.target_points = target_points

    def get_name(self) -> str:
        return self.name

    def get_description(self) -> str:
        return self.description
    
    def get_target_position(self) -> int:
        return self.target_position
    
    def get_target_points(self) -> int:
        return self.target_points

@dataclass
class Wallet(Item):
    """A wallet that stores money.
    
    Instance Attributes:
        - money: The amount of money in the wallet.
        - start_position: The initial position of the weapon.
        - target_position: The position where the weapon needs to be moved.
        - target_points: The points awarded for moving the weapon to the target position.
        
    Representation Invariants:
        - money >= 0
        - start_position >= 0
        - target_position >= 0
        - target_points >= 0
    """
    money: int

    def __init__(self, money: int = 0, start_position: int = 0, target_position: int = 0, target_points: int = 0):
        super().__init__("Wallet", "A leather wallet holding your money.", start_position, target_position, target_points)
        self.money = money

    def get_money(self) -> int:
        return self.money

    def add_money(self, amount: int) -> None:
        self.money += amount

    def remove_money(self, amount: int) -> bool:
        """Remove money if possible, return True if successful, False if insufficient funds."""
        if self.money >= amount:
            self.money -= amount
            return True
        return False

@dataclass
class Location:
    """A location in our text adventure game world.

    Instance Attributes:
        - location_id:  A unique identifier for this location.
        - brief_description: A short description of the location.
        - long_description: A detailed description of the location.
        - available_commands: A list of commands that can be used at this location.
        - items: A list of items available at this location.
        - visited: Whether this location has been visited before.

    Representation Invariants:
        - location_id >= 0
        - brief_description != ''
        - long_description != ''
        - all(isinstance(command, str) for command in available_commands)
        - all(isinstance(item, Item) for item in items)
    """

    location_id: int
    name: str
    brief_description: str
    long_description: str 
    available_commands: list[str]
    items: list[Item]
    visited: bool


    def __init__(self, location_id, name, brief_description, long_description, available_commands, items,
                 visited=False) -> None:
        """Initialize a new location.

        # TODO Add more details here about the initialization if needed
        """

        self.location_id = location_id
        self.name = name
        self.brief_description = brief_description
        self.long_description = long_description
        self.available_commands = available_commands
        self.items = items
        self.visited = visited


@dataclass
class Enemy:
    """An enemy in our text adventure game world.
    
    Instance Attributes:
        - name: The name of the penemylayer.
        - health: The health points of the enemy.
        - damage: the damage the enemy does

    Representation Invariants:
        - name != ''
        - health_points >= 0
    """
    name: str
    health: int
    damage: int

    def __init__(self, name: str, health: int, attack: int):
        self.name = name
        self.health = health
        self.attack = attack
    
    def is_alive(self) -> bool:
        return self.health > 0

if __name__ == "__main__":
    import python_ta
    python_ta.check_all(config={
        'max-line-length': 120,
        'disable': ['R1705', 'E9998', 'E9999']
    })
