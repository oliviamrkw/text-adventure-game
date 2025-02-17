from game_entities import Item, Wallet

class Inventory:
    """Handles inventory management."""
    
    def __init__(self) -> None:
        self.inventory_items = []
        self.wallet = Wallet(money=0)

    def show_inventory(self) -> None:
        """Show the player's inventory"""
        print(f"Money: ${self.wallet.get_money()}")
        
        inventory_items = [item for item in self.inventory_items if not isinstance(item, Wallet)]

        if inventory_items:
            for item in inventory_items:
                print('   >', item.get_name(), '-', item.get_description())
        else:
            print("Your inventory is empty :(")

    def get_score(self, score: int) -> int:
        """Return the updated player's score based on inventory items."""
        for item in self.inventory_items:
            if isinstance(item, Item):
                score += item.get_target_points()
        return score
    
    def has_item(self, item_name: str) -> bool:
        """Return True if the player has an item with the given name."""
        return any(item.get_name().lower() == item_name.lower() for item in self.inventory_items)

    def add_item(self, item: str | Item, items, score: int) -> None:
        """Adds an item to the player's inventory."""
        if isinstance(item, Item):
            item = item.get_name()
        if not self.has_item(item):
            self.inventory_items.append(items[item])
            score += items[item].get_target_points()
            print(f"    - Added {item} to the inventory.")
        else:
            print("You already have this item!")

    def remove_item(self, item: str, items) -> None:
        """Removes an item from the player's inventory."""
        if isinstance(item, Item):
            item = item.get_name()
        
        for inv_item in self.inventory_items:
            if inv_item.get_name().lower() == item.lower():
                self.inventory_items.remove(inv_item)
                print(f"   - Removed {item} from inventory.")
                return

    def get_money(self) -> int:
        return self.wallet.money

    def add_money(self, amount: int) -> None:
        self.wallet.money += amount

    def remove_money(self, amount: int) -> bool:
        """Remove money if possible, return True if successful, False if insufficient funds."""
        if self.wallet.money >= amount:
            self.wallet.money -= amount
            return True
        return False
