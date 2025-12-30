"""
game_logic.py
RPG Game Logic Module - Contains all game mechanics, player, enemy, and story logic
"""

import random

class Player:
    """Player character class"""
    
    def __init__(self):
        self.level = 1
        self.hp = 100
        self.max_hp = 100
        self.attack = 10
        self.defense = 5
        self.gold = 20
        self.exp = 0
        self.exp_needed = 100
        self.inventory = []
        self.armor = {
            "helmet": None,
            "chest": None,
            "boots": None,
            "weapon": None
        }
        self.defeated_bosses = []
    
    def take_damage(self, damage):
        """Take damage reduced by defense"""
        
        actual_damage = max(1, damage - self.defense)
        self.hp -= actual_damage
        
        if self.hp < 0:
            self.hp = 0
        return actual_damage
    
    def heal(self, amount):
        """Heal HP up to max"""
        self.hp = min(self.hp + amount, self.max_hp)
    
    def gain_exp(self, amount):
        """Gain experience and level up if needed"""
        
        self.exp += amount
        messages = [f"✨ +{amount} EXP"]
        
        while self.exp >= self.exp_needed:
            messages.extend(self.level_up())
        
        return messages
    
    def level_up(self):
        """Level up and increase stats"""
        
        self.level += 1
        self.exp -= self.exp_needed
        self.exp_needed = int(self.exp_needed * 1.5)
        
        self.max_hp += 20
        self.hp = self.max_hp
        
        self.attack += 5
        self.defense += 2
        return [
            f"🎉 LEVEL UP! Now level {self.level}!",
            "Max HP +20, Attack +5, Defense +2"
        ]
    
    def equip_armor(self, item_name, slot, bonus_type, bonus_value):
        """Equip armor and apply bonuses"""
        self.armor[slot] = item_name
        if bonus_type == "defense":
            
            self.defense += bonus_value
        elif bonus_type == "attack":
            self.attack += bonus_value
            
        elif bonus_type == "hp":
            self.max_hp += bonus_value
            self.hp += bonus_value
    
    def has_item(self, item_name):
        """Check if player has an item"""
        return item_name in self.inventory
    
    def use_item(self, item_name):
        """Use and remove an item from inventory"""
        if item_name in self.inventory:
            self.inventory.remove(item_name)
            
            return True
        return False
    
    def add_item(self, item_name):
        """Add item to inventory"""
        
        self.inventory.append(item_name)
    
    def get_inventory_count(self):
        """Get inventory with item counts"""
        inv_count = {}
        
        for item in self.inventory:
            inv_count[item] = inv_count.get(item, 0) + 1
        return inv_count
    
    def has_defeated_boss(self, boss_name):
        """Check if boss has been defeated"""
        
        return boss_name in self.defeated_bosses
    
    def defeat_boss(self, boss_name):
        """Mark boss as defeated"""
        if boss_name not in self.defeated_bosses:
            
            self.defeated_bosses.append(boss_name)


class Enemy:
    """Enemy character class"""
    
    def __init__(self, name, hp, attack, defense, gold_reward, exp_reward, boss=False):
        self.name = name
        self.hp = hp
        self.max_hp = hp
        self.attack = attack
        
        self.defense = defense
        self.gold_reward = gold_reward
        self.exp_reward = exp_reward
        
        self.boss = boss
    
    def take_damage(self, damage):
        """Take damage reduced by defense"""
        actual_damage = max(1, damage - self.defense)
        self.hp -= actual_damage
        
        
        if self.hp < 0:
            self.hp = 0
        return actual_damage
    
    def is_alive(self):
        """Check if enemy is still alive"""
        
        return self.hp > 0
    
    def attack_player(self):
        """Calculate attack damage"""
        
        return self.attack + random.randint(0, 3)


class GameEngine:
    """Main game engine that manages game state and logic"""
    
    def __init__(self):
        self.player = Player()
        self.current_enemy = None
        
        self.strength_boost = 0
        
        self.strength_turns = 0
        self.quest_chain = []
        self.quest_callback = None
    
    def reset_game(self):
        """Reset game to initial state"""
        self.player = Player()
        self.current_enemy = None
        
        self.strength_boost = 0
        self.strength_turns = 0
        
        self.quest_chain = []
        self.quest_callback = None
    
    def start_combat(self, enemy):
        """Initialize combat with an enemy"""
        self.current_enemy = enemy
        self.strength_boost = 0
        
        self.strength_turns = 0
        return f"A {enemy.name} appears!{' 💀 BOSS BATTLE 💀' if enemy.boss else ''}"
    
    def player_attack(self):
        """Execute player attack"""
        if not self.current_enemy or not self.current_enemy.is_alive():
            
            return []
        
        total_attack = self.player.attack + self.strength_boost
        
        damage = total_attack + random.randint(0, 5)
        actual_damage = self.current_enemy.take_damage(damage)
        
        messages = [f"💥 You dealt {actual_damage} damage!"]
        
        # Update strength boost
        if self.strength_turns > 0:
            self.strength_turns -= 1
            if self.strength_turns == 0:
                
                self.strength_boost = 0
                messages.append("⏳ Strength boost wore off!")
        
        # Check if enemy defeated
        if not self.current_enemy.is_alive():
            
            messages.extend(self.handle_victory())
            return messages
        
        # Enemy counterattack
        messages.extend(self.enemy_attack())
        
        return messages
    
    def player_defend(self):
        """Execute player defend action"""
        
        messages = ["🛡️ You brace for attack!"]
        
        if self.current_enemy and self.current_enemy.is_alive():
            damage = max(1, self.current_enemy.attack // 2 + random.randint(0, 2))
            
            actual_damage = self.player.take_damage(damage)
            messages.append(f"Reduced damage to {actual_damage}!")
        
        # Update strength boost
        if self.strength_turns > 0:
            self.strength_turns -= 1
            
            if self.strength_turns == 0:
                self.strength_boost = 0
                messages.append("⏳ Strength boost wore off!")
        
        return messages
    
    def use_health_potion(self):
        """Use health potion"""
        if self.player.use_item("Health Potion"):
            
            self.player.heal(40)
            messages = ["🧪 Restored 40 HP!"]
            
            messages.extend(self.enemy_attack())
            return messages
        return ["❌ No Health Potions!"]
    
    def use_strength_elixir(self):
        """Use strength elixir"""
        if self.player.use_item("Strength Elixir"):
            self.strength_boost = 15
            
            self.strength_turns = 3
            messages = ["⚡ Attack +15 for 3 turns!"]
            
            messages.extend(self.enemy_attack())
            return messages
        return ["❌ No Strength Elixirs!"]
    
    def enemy_attack(self):
        """Execute enemy attack"""
        
        if not self.current_enemy or not self.current_enemy.is_alive():
            return []
        
        damage = self.current_enemy.attack_player()
        actual_damage = self.player.take_damage(damage)
        
        return [f"💢 {self.current_enemy.name} dealt {actual_damage} damage!"]
    
def handle_victory(self):
    """Handle combat victory"""
    messages = [f"🎊 Victory! +{self.current_enemy.gold_reward} gold"]
    self.player.gold += self.current_enemy.gold_reward
    
    messages.extend(self.player.gain_exp(self.current_enemy.exp_reward))
    
    # Mark boss as defeated and give special loot
    if self.current_enemy.boss:
        
        self.player.defeat_boss(self.current_enemy.name)
        
        # Give boss-specific loot
        boss_loot = {
            "Bandit Leader": "Bandit's Trophy",
            "Troll King": "Troll King's Crown",
            
            "Shadow Wraith": "Wraith's Essence",
            "Ancient Dragon": "Dragon Scale"
        }
        
        if self.current_enemy.name in boss_loot:
            loot_item = boss_loot[self.current_enemy.name]
            self.player.add_item(loot_item)
            
            messages.append(f"🏆 Obtained {loot_item}!")
    
    return messages
    def is_combat_over(self):
        """Check if combat has ended"""
        
        if not self.current_enemy:
            return True
        return not self.current_enemy.is_alive() or self.player.hp <= 0
    
    def player_is_alive(self):
        """Check if player is alive"""
        return self.player.hp > 0
    
    # Story Events
    
    def event_search_area(self):
        """Search area event"""
        self.player.gold += 50
        
        self.player.add_item("Old Map")
        return "You find 50 gold coins and an old map showing multiple paths!"
    
    def event_find_potion(self):
        """Find potion event"""
        self.player.gold += 40
        
        self.player.add_item("Health Potion")
        self.player.add_item("Strength Elixir")
        return "The mushroom circle pulses with energy! You find a Health Potion, Strength Elixir, and 40 gold!"
    
    def event_find_treasure(self):
        """Find treasure event"""
        self.player.gold += 150
        
        self.player.add_item("Health Potion")
        self.player.add_item("Strength Elixir")
        self.player.add_item("Health Potion")
        
        return "You discover a hidden treasure chamber! You find 150 gold, 2 Health Potions, and a Strength Elixir!"
    
    def event_rest_inn(self):
        """Rest at inn"""
        if self.player.gold >= 20:
            self.player.gold -= 20
            
            self.player.hp = self.player.max_hp
            return "You rest at the inn and fully restore your health!"
        return "❌ Not enough gold! (20 gold needed)"
    
    def buy_item(self, item_name, cost):
        """Buy consumable item"""
        if self.player.gold >= cost:
            self.player.gold -= cost
            
            self.player.add_item(item_name)
            return f"✅ Purchased {item_name}!"
        return "❌ Not enough gold!"
    
    def buy_armor(self, item_name, slot, bonus_type, bonus_value, cost):
        """Buy and equip armor"""
        if self.player.armor[slot]:
            
            return f"❌ You already have {slot} equipped!"
        if self.player.gold >= cost:
            self.player.gold -= cost
            
            self.player.equip_armor(item_name, slot, bonus_type, bonus_value)
            return f"✅ Equipped {item_name}! {bonus_type} +{bonus_value}"
        return "❌ Not enough gold!"
    
    def complete_boss(self, boss_name, loot):
        """Complete boss and give loot"""
        self.player.defeat_boss(boss_name)
        
        self.player.add_item(loot)
        return f"🎊 Victory! You defeated {boss_name} and obtained {loot}!"
    
    # Enemy Creation
    
    @staticmethod
    def create_enemy(enemy_type):
        """Factory method to create enemies"""
        enemies = {
            "dire_wolf": Enemy("Dire Wolf", 35, 7, 2, 40, 40),
            "alpha_wolf": Enemy("Alpha Wolf", 50, 10, 3, 60, 60),
            "goblin": Enemy("Goblin Warrior", 40, 8, 1, 60, 50),
            "cave_troll": Enemy("Cave Troll", 60, 12, 4, 80, 70),
            "bandit_scout": Enemy("Bandit Scout", 45, 9, 2, 70, 55),
            "wild_boar": Enemy("Wild Boar", 40, 8, 3, 50, 45),
            "rogue_merc": Enemy("Rogue Mercenary", 50, 11, 2, 80, 60),
            
            "bandit_thug": Enemy("Bandit Thug", 45, 10, 2, 70, 60),
            "bandit_archer": Enemy("Bandit Archer", 40, 12, 1, 75, 65),
            "bandit_leader": Enemy("Bandit Leader", 80, 14, 3, 200, 150, boss=True),
            "mountain_troll": Enemy("Mountain Troll", 70, 13, 5, 90, 80),
            
            "troll_king": Enemy("Troll King", 100, 16, 6, 250, 180, boss=True),
            "skeleton": Enemy("Skeleton Warrior", 50, 11, 2, 80, 70),
            "zombie": Enemy("Zombie Knight", 60, 13, 4, 90, 80),
            "wraith": Enemy("Shadow Wraith", 90, 15, 3, 300, 200, boss=True),
            "dragon": Enemy("Ancient Dragon", 120, 18, 5, 500, 250, boss=True)
        }
        return enemies.get(enemy_type)
    
    @staticmethod
    def get_random_outskirts_enemy():
        """Get random enemy for outskirts"""
        enemy_types = ["bandit_scout", "wild_boar", "rogue_merc"]
        
        return GameEngine.create_enemy(random.choice(enemy_types))
    
    # Quest Chains
    
    def setup_bandit_quest(self):
        """Setup bandit quest chain"""
        self.quest_chain = [
            self.create_enemy("bandit_thug"),
            
            self.create_enemy("bandit_archer"),
            self.create_enemy("bandit_leader")
        ]
    
    def setup_troll_quest(self):
        """Setup troll quest chain"""
        self.quest_chain = [
            self.create_enemy("mountain_troll"),
            
            self.create_enemy("troll_king")
        ]
    
    def setup_castle_quest(self):
        """Setup castle quest chain"""
        self.quest_chain = [
            self.create_enemy("skeleton"),
            self.create_enemy("zombie"),
            
            self.create_enemy("wraith")
        ]
    
    def setup_dragon_quest(self):
        """Setup dragon quest"""
        self.quest_chain = [self.create_enemy("dragon")]
    
    def has_next_quest_enemy(self):
        """Check if quest chain has more enemies"""
        
        return len(self.quest_chain) > 0
    
    def get_next_quest_enemy(self):
        """Get next enemy in quest chain"""
        if self.quest_chain:
            
            return self.quest_chain.pop(0)
        return None