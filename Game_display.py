
import pygame
import sys
from Game_Logic import Player, Enemy, GameEngine


pygame.init()

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (220, 53, 69)
GREEN = (40, 167, 69)

BLUE = (0, 123, 255)
YELLOW = (255, 193, 7)
DARK_GRAY = (52, 58, 64)
LIGHT_GRAY = (108, 117, 125)
PURPLE = (111, 66, 193)

ORANGE = (253, 126, 20)
CYAN = (23, 162, 184)


DARK_RED = (139, 0, 0)
DARK_GREEN = (0, 100, 0)



class StatBar:
    """Visual stat bar (HP, EXP, etc)"""
    
    def __init__(self, x, y, width, height, max_value, current_value, color=GREEN):
        self.x = x
        self.y = y
        
        self.width = width
        
        
        self.height = height
        self.max_value = max_value
        
        self.current_value = current_value
        self.color = color
    
    def update(self, current_value, max_value=None):
        """(bar values)"""
        self.current_value = current_value
        if max_value:
            self.max_value = max_value
    
    def draw(self, screen, font):
        """Draw stat bar"""
        # Background
        pygame.draw.rect(screen, DARK_GRAY, (self.x, self.y, self.width, self.height))
        
        # Fill bar
        if self.max_value > 0:
            fill_width = int((self.current_value / self.max_value) * self.width)
            
            pygame.draw.rect(screen, self.color, (self.x, self.y, fill_width, self.height))
        
        # Border
        pygame.draw.rect(screen, WHITE, (self.x, self.y, self.width, self.height), 2)
        
        # Text
        text = f"{int(self.current_value)}/{int(self.max_value)}"
        
        text_surface = font.render(text, True, WHITE)
        text_rect = text_surface.get_rect(center=(self.x + self.width // 2, self.y + self.height // 2))
        
        screen.blit(text_surface, text_rect)


class Button:
    """Interactive button"""
    
    def __init__(self, x, y, width, height, text, color=BLUE, text_color=WHITE, font=None):
        self.rect = pygame.Rect(x, y, width, height)
        
        self.text = text
        self.color = color
        
        
        self.text_color = text_color
        self.font = font or pygame.font.Font(None, 24)
        self.hovered = False
    
    def draw(self, screen):
        """Draw button"""
        color = tuple(min(c + 30, 255) for c in self.color) if self.hovered else self.color
        pygame.draw.rect(screen, color, self.rect, border_radius=8)
        
        pygame.draw.rect(screen, WHITE, self.rect, 2, border_radius=8)
        
        text_surface = self.font.render(self.text, True, self.text_color)
        
        
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)
    
    def check_hover(self, mouse_pos):
        """Check mouse hovering"""
        self.hovered = self.rect.collidepoint(mouse_pos)
        
        return self.hovered
    
    def is_clicked(self, mouse_pos):
        """Check if button was clicked"""
        
        
        return self.rect.collidepoint(mouse_pos)


class Panel:
    """Display panel container"""
    
    def __init__(self, x, y, width, height, bg_color=DARK_GRAY, title=None):
        self.rect = pygame.Rect(x, y, width, height)
        self.bg_color = bg_color
        
        
        self.title = title
    
    def draw(self, screen, font=None):
        """Draw the panel"""
        pygame.draw.rect(screen, self.bg_color, self.rect, border_radius=10)
        
        
        pygame.draw.rect(screen, LIGHT_GRAY, self.rect, 2, border_radius=10)
        
        if self.title and font:
            title_surface = font.render(self.title, True, YELLOW)
            
            screen.blit(title_surface, (self.rect.x + 10, self.rect.y + 10))


# ========== MAIN GAME CLASS ==========

class RPGGame:
    """Main game display and controller"""
    
    def __init__(self):
        self.screen = pygame.display.set_mode((1100, 750))
        
        pygame.display.set_caption("Fantasy RPG Adventure")
        self.clock = pygame.time.Clock()
        
        
        self.running = True
        
        # Fonts
        self.title_font = pygame.font.Font(None, 56)
        self.header_font = pygame.font.Font(None, 32)
        self.normal_font = pygame.font.Font(None, 24)
        
        self.small_font = pygame.font.Font(None, 20)
        
        # Game engine
        self.engine = GameEngine()
        
        # Game state
        self.state = "start"  # start, exploration, combat, shop, gameover, victory
        self.message = ""
        self.combat_log = []
        
        self.buttons = []
        
        
        self.button_actions = []
        self.on_victory_callback = None
        
        # UI Components
        self.setup_ui()
    
    def setup_ui(self):
        """Setup UI components"""
        # Stats panel
        self.stats_panel = Panel(20, 20, 380, 220, title="Hero Stats")
        self.hp_bar = StatBar(50, 80, 320, 25, 100, 100, RED)
        
        self.exp_bar = StatBar(50, 130, 320, 25, 100, 0, CYAN)
        
        
        # Enemy panel
        self.enemy_panel = Panel(700, 20, 380, 180, bg_color=DARK_RED, title="Enemy")
        self.enemy_hp_bar = StatBar(730, 80, 320, 30, 100, 100, RED)
        
        
        # Message panel
        
        self.message_panel = Panel(20, 260, 1060, 200, title="Story")
        
        # Combat log panel
        self.combat_panel = Panel(700, 220, 380, 240, title="Combat Log")
    
    def wrap_text(self, text, font, max_width):
        """Wrap text to fit width"""
        words = text.split(' ')
        lines = []
        
        
        current_line = []
        
        for word in words:
            
            test_line = ' '.join(current_line + [word])
            if font.size(test_line)[0] <= max_width:
                
                current_line.append(word)
            else:
                if current_line:
                    
                    lines.append(' '.join(current_line))
                current_line = [word]
        
        if current_line:
            lines.append(' '.join(current_line))
        
        return lines
    
    def add_combat_log(self, msg):
        """Add message to combat log"""
        self.combat_log.append(msg)
        
        if len(self.combat_log) > 8:
            self.combat_log.pop(0)
    
    def draw_player_stats(self):
        """Draw player stats panel"""
        
        player = self.engine.player
        self.stats_panel.draw(self.screen, self.header_font)
        
        # Level
        level_text = f"Level {player.level}"
        
        
        level_surf = self.normal_font.render(level_text, True, YELLOW)
        self.screen.blit(level_surf, (320, 30))
        
        # HP Bar
        hp_label = self.normal_font.render("HP:", True, WHITE)
        self.screen.blit(hp_label, (50, 55))
        self.hp_bar.update(player.hp, player.max_hp)
        
        self.hp_bar.draw(self.screen, self.small_font)
        
        # EXP Bar
        exp_label = self.normal_font.render("EXP:", True, WHITE)
        self.screen.blit(exp_label, (50, 105))
        
        
        self.exp_bar.update(player.exp, player.exp_needed)
        self.exp_bar.draw(self.screen, self.small_font)
        
        # Stats
        stats_y = 165
        atk_text = f"⚔️ ATK: {player.attack}"
        
        def_text = f"🛡️ DEF: {player.defense}"
        gold_text = f"💰 Gold: {player.gold}"
        
        
        atk_surf = self.normal_font.render(atk_text, True, RED)
        def_surf = self.normal_font.render(def_text, True, BLUE)
        
        
        gold_surf = self.normal_font.render(gold_text, True, YELLOW)
        
        self.screen.blit(atk_surf, (50, stats_y))
        self.screen.blit(def_surf, (180, stats_y))
        
        self.screen.blit(gold_surf, (50, stats_y + 30))
        
        # Equipment
        equip_y = 470
        
        equip_panel = Panel(20, equip_y, 380, 120, title="Equipment")
        equip_panel.draw(self.screen, self.header_font)
        
        y_off = equip_y + 40
        for slot, item in player.armor.items():
            text = f"{slot.capitalize()}: {item or 'None'}"
            
            surf = self.small_font.render(text, True, WHITE)
            self.screen.blit(surf, (40, y_off))
            y_off += 22
        
        # Inventory
        inv_y = 600
        inv_panel = Panel(20, inv_y, 660, 130, title="Inventory")
        
        inv_panel.draw(self.screen, self.header_font)
        
        if player.inventory:
            inv_count = player.get_inventory_count()
            
            inv_text = ", ".join([f"{item} x{count}" if count > 1 else item 
                                 for item, count in inv_count.items()])
            
            inv_surf = self.small_font.render(inv_text, True, WHITE)
            self.screen.blit(inv_surf, (40, inv_y + 40))
        else:
            inv_surf = self.small_font.render("Empty", True, LIGHT_GRAY)
            
            self.screen.blit(inv_surf, (40, inv_y + 40))
    
    def draw_enemy_stats(self):
        """Draw enemy stats panel"""
        
        enemy = self.engine.current_enemy
        if not enemy:
            
            return
        
        self.enemy_panel.draw(self.screen, self.header_font)
        
        # Name
        name = enemy.name
        if enemy.boss:
            
            name = f"💀 {name} 💀"
            
            
        name_surf = self.normal_font.render(name, True, WHITE)
        self.screen.blit(name_surf, (730, 30))
        
        
        # HP Bar
        hp_label = self.normal_font.render("HP:", True, WHITE)
        self.screen.blit(hp_label, (730, 55))
        
        self.enemy_hp_bar.update(enemy.hp, enemy.max_hp)
        
        
        self.enemy_hp_bar.draw(self.screen, self.small_font)
        
        # Stats
        stats_y = 120
        atk_text = f"ATK: {enemy.attack}"
        
        def_text = f"DEF: {enemy.defense}"
        
        atk_surf = self.normal_font.render(atk_text, True, RED)
        
        def_surf = self.normal_font.render(def_text, True, BLUE)
        
        self.screen.blit(atk_surf, (730, stats_y))
        
        self.screen.blit(def_surf, (900, stats_y))
        
        # Strength boost indicator
        if self.engine.strength_turns > 0:
            boost_text = f"💪 +{self.engine.strength_boost} ATK ({self.engine.strength_turns} turns)"
            boost_surf = self.normal_font.render(boost_text, True, YELLOW)
            
            self.screen.blit(boost_surf, (730, stats_y + 30))
    
    def draw_message(self):
        """Draw message box"""
        self.message_panel.draw(self.screen, self.header_font)
        
        lines = self.wrap_text(self.message, self.normal_font, 1020)
        y_offset = 300
        
        for line in lines[:5]:
            line_surf = self.normal_font.render(line, True, WHITE)
            self.screen.blit(line_surf, (40, y_offset))
            
            y_offset += 30
    
    def draw_combat_log(self):
        """Draw combat log"""
        self.combat_panel.draw(self.screen, self.header_font)
        
        y_offset = 260
        for log in self.combat_log[-8:]:
            
            log_surf = self.small_font.render(log, True, WHITE)
            self.screen.blit(log_surf, (720, y_offset))
            
            y_offset += 25
    
    def draw_buttons(self):
        """Draw all buttons"""
        for button in self.buttons:
            
            button.draw(self.screen)
    
    def handle_events(self):
        """Handle pygame events"""
        
        mouse_pos = pygame.mouse.get_pos()
        
        for button in self.buttons:
            
            button.check_hover(mouse_pos)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                
                self.running = False
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                for i, button in enumerate(self.buttons):
                    
                    if button.is_clicked(mouse_pos):
                        if i < len(self.button_actions):
                            
                            self.button_actions[i]()
    
    # ========== GAME STATES ==========
    
    def start_screen(self):
        """Start screen"""
        self.screen.fill(BLACK)
        
        title = self.title_font.render("⚔️ Fantasy RPG Adventure ⚔️", True, YELLOW)
        
        
        title_rect = title.get_rect(center=(550, 200))
        self.screen.blit(title, title_rect)
        
        subtitle = self.header_font.render("Embark on an epic quest!", True, WHITE)
        
        subtitle_rect = subtitle.get_rect(center=(550, 300))
        self.screen.blit(subtitle, subtitle_rect)
        
        self.buttons = [Button(400, 400, 300, 60, "Start Adventure", GREEN, font=self.header_font)]
        self.button_actions = [self.start_game]
        
        self.draw_buttons()
    
    def start_game(self):
        """Initialize new game"""
        self.engine.reset_game()
        
        self.state = "exploration"
        self.message = "You wake up in a mysterious forest with no memory of how you got here. The air is thick with magic, and you can hear strange sounds in the distance."
        self.combat_log = []
        
        
        self.buttons = [
            Button(420, 480, 280, 50, "Explore north", BLUE, font=self.normal_font),
            Button(420, 540, 280, 50, "Search the area", BLUE, font=self.normal_font),
            
            Button(420, 600, 280, 50, "Head to sounds", BLUE, font=self.normal_font)
        ]
        self.button_actions = [
            self.explore_north,
            self.search_area,
            
            lambda: self.start_combat(self.engine.create_enemy("dire_wolf"), self.reach_village)
        ]
    
    def exploration_screen(self):
        """Exploration state screen"""
        self.screen.fill(BLACK)
        self.draw_player_stats()
        
        self.draw_message()
        
        self.draw_buttons()
    
    # ========== STORY EVENTS ==========
    
    def search_area(self):
        """Search area"""
        self.message = self.engine.event_search_area()
        
        self.buttons = [
            Button(420, 480, 280, 50, "Go to village", BLUE, font=self.normal_font),
            Button(420, 540, 280, 50, "Explore cave", BLUE, font=self.normal_font),
            
            Button(420, 600, 280, 50, "Explore forest", BLUE, font=self.normal_font)
        ]
        self.button_actions = [self.reach_village, self.explore_cave, self.explore_north]
    
    def explore_north(self):
        """Explore north"""
        self.message = "You venture deeper into the forest. The trees grow thicker. You spot a glowing mushroom circle and hear rustling nearby."
        
        self.buttons = [
            Button(420, 480, 280, 50, "Investigate mushrooms", BLUE, font=self.normal_font),
            
            Button(420, 540, 280, 50, "Follow rustling", BLUE, font=self.normal_font),
            
            Button(420, 600, 280, 50, "Go to village", BLUE, font=self.normal_font)
        ]
        self.button_actions = [
            self.find_potion,
            lambda: self.start_combat(self.engine.create_enemy("goblin"), self.reach_village),
            
            self.reach_village
        ]
    
    def find_potion(self):
        """Find potion"""
        self.message = self.engine.event_find_potion()
        
        self.buttons = [
            Button(420, 480, 280, 50, "Go to village", BLUE, font=self.normal_font),
            
            Button(420, 540, 280, 50, "Explore cave", BLUE, font=self.normal_font)
        ]
        self.button_actions = [self.reach_village, self.explore_cave]
    
    def explore_cave(self):
        """Cave exploration"""
        self.message = "You enter a dark, damp cave. The sound of dripping water echoes. You see two tunnels - one with markings, one with light."
        
        self.buttons = [
            Button(420, 480, 280, 50, "Marked tunnel", BLUE, font=self.normal_font),
            
            
            Button(420, 540, 280, 50, "Follow light", BLUE, font=self.normal_font),
            
            Button(420, 600, 280, 50, "Go to village", BLUE, font=self.normal_font)
        ]
        self.button_actions = [
            lambda: self.start_combat(self.engine.create_enemy("cave_troll"), self.find_treasure),
            
            self.find_treasure,
            self.reach_village
        ]
    
    def find_treasure(self):
        """Find treasure"""
        self.message = self.engine.event_find_treasure()
        
        self.buttons = [Button(420, 520, 280, 50, "Return to village", GREEN, font=self.normal_font)]
        
        self.button_actions = [self.reach_village]
    
    def reach_village(self):
        """Reach village"""
        self.state = "exploration"
        
        self.message = "You arrive at a bustling village. The villagers look worried. An elder approaches: 'We need a hero. Many threats plague our land. Will you help us?'"
        
        self.buttons = [
            Button(350, 480, 200, 45, "🏪 Shop", BLUE, font=self.normal_font),
            
            Button(560, 480, 200, 45, "🛏️ Inn (20g)", GREEN, font=self.normal_font),
            Button(350, 535, 200, 45, "📜 Threats", ORANGE, font=self.normal_font),
            
            Button(560, 535, 200, 45, "🗺️ Outskirts", PURPLE, font=self.normal_font)
        ]
        self.button_actions = [self.visit_shop, self.rest_inn, self.learn_threats, self.explore_outskirts]
    
    def learn_threats(self):
        """Learn about threats"""
        
        defeated = ", ".join(self.engine.player.defeated_bosses) if self.engine.player.defeated_bosses else "None"
        
        self.message = f"The elder explains:\n• Bandits in western ruins\n• Troll King in mountains\n• Shadows in castle\n• Ancient Dragon in volcano\n\nDefeated: {defeated}"
        
        self.buttons = []
        
        self.button_actions = []
        
        if not self.engine.player.has_defeated_boss("Bandit Leader"):
            self.buttons.append(Button(350, 480, 200, 45, "Bandit Ruins", RED, font=self.small_font))
            
            self.button_actions.append(self.bandit_quest)
        
        if not self.engine.player.has_defeated_boss("Troll King"):
            
            self.buttons.append(Button(560, 480, 200, 45, "Troll Mountain", RED, font=self.small_font))
            self.button_actions.append(self.troll_quest)
        
        if not self.engine.player.has_defeated_boss("Shadow Wraith"):
            
            
            self.buttons.append(Button(350, 535, 200, 45, "Haunted Castle", RED, font=self.small_font))
            self.button_actions.append(self.castle_quest)
        
        self.buttons.append(Button(560, 535, 200, 45, "🐉 Dragon", DARK_RED, font=self.small_font))
        self.button_actions.append(self.dragon_quest)
        
        self.buttons.append(Button(420, 590, 280, 45, "← Back to village", BLUE, font=self.normal_font))
        
        
        self.button_actions.append(self.reach_village)
    
    def explore_outskirts(self):
        """Random encounter"""
        
        
        enemy = self.engine.get_random_outskirts_enemy()
        self.start_combat(enemy, self.reach_village)
    
    # ========== QUEST CHAINS ==========
    
    def bandit_quest(self):
        """Bandit quest"""
        
        self.engine.setup_bandit_quest()
        
        self.on_victory_callback = lambda: self.complete_boss("Bandit Leader", "Rogue's Dagger")
        self.next_quest_fight()
    
    def troll_quest(self):
        """Troll quest"""
        self.engine.setup_troll_quest()
        
        self.on_victory_callback = lambda: self.complete_boss("Troll King", "Troll Hide Armor")
        self.next_quest_fight()
    
    def castle_quest(self):
        """Castle quest"""
        
        self.engine.setup_castle_quest()
        
        self.on_victory_callback = lambda: self.complete_boss("Shadow Wraith", "Dark Crystal")
        self.next_quest_fight()
    
    def dragon_quest(self):
        """Dragon quest"""
        self.engine.setup_dragon_quest()
        
        
        self.on_victory_callback = self.victory
        self.next_quest_fight()
    
    def next_quest_fight(self):
        """Start next fight in quest"""
        if self.engine.has_next_quest_enemy():
            
            enemy = self.engine.get_next_quest_enemy()
            if self.engine.has_next_quest_enemy():
                
                self.start_combat(enemy, self.next_quest_fight)
            else:
                self.start_combat(enemy, self.on_victory_callback)
    
    def complete_boss(self, boss_name, loot):
        """Complete boss"""
        msg = self.engine.complete_boss(boss_name, loot)
        self.message = msg
        
        self.buttons = [Button(420, 520, 280, 50, "Return to village", GREEN, font=self.normal_font)]
        
        self.button_actions = [self.reach_village]
    
    # ========== SHOP & INN ==========
    
    def visit_shop(self):
        """Shop screen"""
        self.state = "shop"
        
        
        self.message = "Welcome to the Village Shop! Buy items and equipment."
        
        self.buttons = [
            Button(330, 480, 220, 40, "Health Potion (50g)", BLUE, font=self.small_font),
            
            Button(560, 480, 220, 40, "Strength Elixir (80g)", BLUE, font=self.small_font)
        ]
        self.button_actions = [
            lambda: self.buy_item("Health Potion", 50),
            
            lambda: self.buy_item("Strength Elixir", 80)
        ]
        
        y = 530
        player = self.engine.player
        
        if not player.armor["weapon"]:
            self.buttons.append(Button(330, y, 220, 40, "Steel Sword (100g)", ORANGE, font=self.small_font))
            
            self.button_actions.append(lambda: self.buy_armor("Steel Sword", "weapon", "attack", 10, 100))
            y += 50
        
        if not player.armor["helmet"]:
            self.buttons.append(Button(330, y, 220, 40, "Iron Helmet (120g)", ORANGE, font=self.small_font))
            self.button_actions.append(lambda: self.buy_armor("Iron Helmet", "helmet", "defense", 5, 120))
            y += 50
        
        if not player.armor["chest"]:
            self.buttons.append(Button(330, y, 220, 40, "Chainmail (200g)", ORANGE, font=self.small_font))
            
            self.button_actions.append(lambda: self.buy_armor("Chainmail Armor", "chest", "defense", 8, 200))
            y += 50
        
        if not player.armor["boots"]:
            self.buttons.append(Button(330, y, 220, 40, "Leather Boots (80g)", ORANGE, font=self.small_font))
            self.button_actions.append(lambda: self.buy_armor("Leather Boots", "boots", "defense", 3, 80))
            
            
        
        self.buttons.append(Button(420, 670, 280, 40, "← Leave shop", GREEN, font=self.normal_font))
        
        self.button_actions.append(self.reach_village)
    
    def buy_item(self, item, cost):
        """Buy item"""
        self.message = self.engine.buy_item(item, cost)
        
        pygame.time.wait(500)
        self.visit_shop()
    
    def buy_armor(self, item, slot, bonus_type, bonus, cost):
        """Buy armor"""
        self.message = self.engine.buy_armor(item, slot, bonus_type, bonus, cost)
        
        pygame.time.wait(500)
        self.visit_shop()
    
    def rest_inn(self):
        """Rest at inn"""
        self.message = self.engine.event_rest_inn()
        
        self.buttons = [Button(420, 520, 280, 50, "Continue", GREEN, font=self.normal_font)]
        
        
        self.button_actions = [self.reach_village]
    
    # ========== COMBAT ==========
    
    def start_combat(self, enemy, on_victory):
        """Start combat"""
        self.state = "combat"
        
        
        self.on_victory_callback = on_victory
        self.combat_log = []
        
        self.message = self.engine.start_combat(enemy)
        
        self.add_combat_log(f"Battle vs {enemy.name}!")
        
        self.buttons = [
            Button(420, 480, 130, 45, "⚔️ Attack", RED, font=self.normal_font),
            Button(560, 480, 130, 45, "🛡️ Defend", BLUE, font=self.normal_font),
            
            Button(420, 535, 130, 45, "🧪 Potion", GREEN, font=self.normal_font),
            Button(560, 535, 130, 45, "⚡ Elixir", ORANGE, font=self.normal_font)
        ]
        self.button_actions = [
            self.player_attack,
            self.player_defend,
            
            self.use_health_potion,
            self.use_strength_elixir
        ]
    
    def combat_screen(self):
        """Combat screen"""
        self.screen.fill(BLACK)
        self.draw_player_stats()
        self.draw_enemy_stats()
        
        self.draw_message()
        self.draw_combat_log()
        self.draw_buttons()
    
    def player_attack(self):
        """Player attacks"""
        messages = self.engine.player_attack()
        
        for msg in messages:
            self.add_combat_log(msg)
        
        if self.engine.is_combat_over():
            if self.engine.player_is_alive():
                pygame.time.wait(2000)
                self.state = "exploration"
                
                self.on_victory_callback()
            else:
                pygame.time.wait(1000)
                self.game_over()
    
    def player_defend(self):
        """Player defends"""
        messages = self.engine.player_defend()
        
        
        for msg in messages:
            self.add_combat_log(msg)
        
        if not self.engine.player_is_alive():
            pygame.time.wait(1000)
            self.game_over()
    
    def use_health_potion(self):
        """Use health potion"""
        messages = self.engine.use_health_potion()
        for msg in messages:
            
            self.add_combat_log(msg)
        
        if not self.engine.player_is_alive():
            pygame.time.wait(1000)
            self.game_over()
    
    def use_strength_elixir(self):
        """Use strength elixir"""
        messages = self.engine.use_strength_elixir()
        for msg in messages:
            self.add_combat_log(msg)
        
        if not self.engine.player_is_alive():
            pygame.time.wait(1000)
            self.game_over()
    
    # ========== END SCREENS ==========
    
    def game_over(self):
        """Game over"""
        self.state = "gameover"
        
        self.message = "💀 You have been defeated..."
        
        self.buttons = [
            Button(350, 520, 200, 50, "Play Again", GREEN, font=self.normal_font),
            
            Button(560, 520, 200, 50, "Quit", RED, font=self.normal_font)
        ]
        self.button_actions = [self.start_game, lambda: setattr(self, 'running', False)]
    
    def gameover_screen(self):
        """Game over screen"""
        self.screen.fill(BLACK)
        
        title = self.title_font.render("💀 GAME OVER 💀", True, RED)
        
        title_rect = title.get_rect(center=(550, 250))
        
        self.screen.blit(title, title_rect)
        
        lines = self.wrap_text(self.message, self.normal_font, 800)
        y = 350
        for line in lines:
            surf = self.normal_font.render(line, True, WHITE)
            
            rect = surf.get_rect(center=(550, y))
            self.screen.blit(surf, rect)
            y += 35
        
        self.draw_buttons()
    
    def victory(self):
        """Victory"""
        self.state = "victory"
        
        player = self.engine.player
        
        self.message = f"🐉 The dragon falls! You are a legendary hero! Final Level: {player.level} | Gold: {player.gold}"
        
        self.buttons = [
            Button(350, 520, 200, 50, "Play Again", GREEN, font=self.normal_font),
            
            Button(560, 520, 200, 50, "Quit", RED, font=self.normal_font)
        ]
        self.button_actions = [self.start_game, lambda: setattr(self, 'running', False)]
    
    def victory_screen(self):
        """Victory screen"""
        self.screen.fill(BLACK)
        
        title = self.title_font.render("🎊 VICTORY! 🎊", True, YELLOW)
        
        title_rect = title.get_rect(center=(550, 200))
        self.screen.blit(title, title_rect)
        
        lines = self.wrap_text(self.message, self.normal_font, 800)
        y = 320
        for line in lines:
            
            surf = self.normal_font.render(line, True, WHITE)
            rect = surf.get_rect(center=(550, y))
            
            self.screen.blit(surf, rect)
            y += 35
        
        self.draw_buttons()
    
    # ========== MAIN LOOP ==========
    
    def run(self):
        """Main game loop"""
        while self.running:
            self.handle_events()
            
            if self.state == "start":
                self.start_screen()
                
            elif self.state == "exploration" or self.state == "shop":
                self.exploration_screen()
                
            elif self.state == "combat":
                self.combat_screen()
                
            elif self.state == "gameover":
                self.gameover_screen()
                
            elif self.state == "victory":
                self.victory_screen()
            
            pygame.display.flip()
            self.clock.tick(60)
        
        pygame.quit()
        sys.exit()


# ========== RUN GAME ==========

if __name__ == "__main__":
    game = RPGGame()
    game.run()