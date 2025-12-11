from typing import Optional, Dict, List, Any, Tuple
import aiosqlite
from .core import DatabaseCore
from .players import PlayersDB
from .skills import SkillsDB
from .inventory import InventoryDB
from .market import MarketDB
from .game_data import GameDataDB
from .world import WorldDB
from .events import EventsDB
from .coop import CoopDB
from .party_finder import PartyFinderDB
from .badges import BadgeDB
from .item_modifiers import ItemModifierDB
from .market_graphing import MarketGraphingDB
from .minion_upgrades import MinionUpgradeDB
from .hotm import HotmDB
from .dwarven_mines import DwarvenMinesDB
from .crystal_hollows import CrystalHollowsDB
from .potions import PotionsDB
from .talismans import TalismansDB
from .methods import GameDatabaseMethods
import json
import time


class GameDatabase(GameDatabaseMethods):
    def __init__(self, db_path: str):
        self.db_path = db_path
        self._core = DatabaseCore(db_path)
        self.players = PlayersDB(db_path)
        self.skills = SkillsDB(db_path)
        self.inventory = InventoryDB(db_path)
        self.market = MarketDB(db_path)
        self.game_data = GameDataDB(db_path)
        self.world = WorldDB(db_path)
        self.events = EventsDB(db_path)
        self.coop = CoopDB(db_path)
        self.party_finder = PartyFinderDB(db_path)
        self.badges = BadgeDB(db_path)
        self.item_modifiers = ItemModifierDB(db_path)
        self.market_graphing = MarketGraphingDB(db_path)
        self.minion_upgrades = MinionUpgradeDB(db_path)
        self.hotm = HotmDB(db_path)
        self.dwarven_mines = DwarvenMinesDB(db_path)
        self.crystal_hollows = CrystalHollowsDB(db_path)
        self.potions = PotionsDB(db_path)
        self.talismans = TalismansDB(db_path)
        self.conn: Optional[aiosqlite.Connection] = None

    async def initialize(self):
        await self._core.connect()
        self.conn = self._core.conn
        
        await self.players.connect()
        self.players.conn = self.conn
        
        await self.skills.connect()
        self.skills.conn = self.conn
        
        await self.inventory.connect()
        self.inventory.conn = self.conn
        
        await self.market.connect()
        self.market.conn = self.conn
        
        await self.game_data.connect()
        self.game_data.conn = self.conn
        
        await self.world.connect()
        self.world.conn = self.conn
        
        await self.events.connect()
        self.events.conn = self.conn
        
        await self.coop.connect()
        self.coop.conn = self.conn
        
        await self.party_finder.connect()
        self.party_finder.conn = self.conn
        
        await self.badges.connect()
        self.badges.conn = self.conn
        
        await self.item_modifiers.connect()
        self.item_modifiers.conn = self.conn
        
        await self.market_graphing.connect()
        self.market_graphing.conn = self.conn
        
        await self.minion_upgrades.connect()
        self.minion_upgrades.conn = self.conn
        
        await self.hotm.connect()
        self.hotm.conn = self.conn
        
        await self.dwarven_mines.connect()
        self.dwarven_mines.conn = self.conn
        
        await self.crystal_hollows.connect()
        self.crystal_hollows.conn = self.conn
        
        await self.potions.connect()
        self.potions.conn = self.conn
        
        await self.talismans.connect()
        self.talismans.conn = self.conn
        
        await self._create_dungeon_loot_tables()

    async def _create_dungeon_loot_tables(self):
        if not self.conn:
            return
        await self.conn.execute('''
            CREATE TABLE IF NOT EXISTS dungeon_loot (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                floor_id TEXT NOT NULL,
                item_id TEXT NOT NULL,
                drop_chance REAL NOT NULL,
                min_amount INTEGER DEFAULT 1,
                max_amount INTEGER DEFAULT 1,
                score_requirement INTEGER DEFAULT 0,
                UNIQUE(floor_id, item_id)
            )
        ''')
        await self.conn.commit()

    async def close(self):
        if self._core:
            await self._core.close()

    async def fetchone(self, query: str, params: tuple = ()):
        """Execute a query and fetch one result."""
        return await self._core.fetchone(query, params)
    
    async def fetchall(self, query: str, params: tuple = ()):
        """Execute a query and fetch all results."""
        return await self._core.fetchall(query, params)
    
    async def execute(self, query: str, params: tuple = ()):
        """Execute a query."""
        return await self._core.execute(query, params)
    
    async def commit(self):
        """Commit the transaction."""
        return await self._core.commit()

    async def create_player(self, user_id: int, username: str):
        return await self.players.create_player(user_id, username)

    async def get_player(self, user_id: int):
        return await self.players.get_player(user_id)

    async def update_player(self, user_id: int, **kwargs):
        return await self.players.update_player(user_id, **kwargs)

    async def get_skills(self, user_id: int):
        return await self.skills.get_skills(user_id)

    async def update_skill(self, user_id: int, skill_name: str, **kwargs):
        return await self.skills.update_skill(user_id, skill_name, **kwargs)

    async def get_collection(self, user_id: int, collection_name: str):
        return await self.skills.get_collection(user_id, collection_name)

    async def add_collection(self, user_id: int, collection_name: str, amount: int):
        return await self.skills.add_collection(user_id, collection_name, amount)

    async def get_inventory(self, user_id: int):
        return await self.inventory.get_inventory(user_id)

    async def equip_item(self, user_id: int, slot_id: int, equipment_slot: str):
        return await self.inventory.equip_item(user_id, slot_id, equipment_slot)

    async def unequip_item(self, user_id: int, equipment_slot: str):
        return await self.inventory.unequip_item(user_id, equipment_slot)

    async def get_equipped_items(self, user_id: int):
        return await self.inventory.get_equipped_items(user_id)

    async def add_item_to_inventory(self, user_id: int, item_id: str, amount: int = 1):
        return await self.inventory.add_item_to_inventory(user_id, item_id, amount)

    async def remove_item_from_inventory(self, user_id: int, item_id: str, amount: int = 1):
        return await self.inventory.remove_item_from_inventory(user_id, item_id, amount)

    async def get_item_count(self, user_id: int, item_id: str):
        return await self.inventory.get_item_count(user_id, item_id)

    async def has_tool(self, user_id: int, tool_type: str):
        return await self.inventory.has_tool(user_id, tool_type)

    async def get_tool_multiplier(self, user_id: int, tool_type: str):
        return await self.inventory.get_tool_multiplier(user_id, tool_type)

    async def get_fairy_souls(self, user_id: int):
        return await self.skills.get_fairy_souls(user_id)

    async def collect_fairy_soul(self, user_id: int, location: str):
        return await self.skills.collect_fairy_soul(user_id, location)

    async def get_player_progression(self, user_id: int):
        return await self.players.get_player_progression(user_id)

    async def update_progression(self, user_id: int, **kwargs):
        return await self.players.update_progression(user_id, **kwargs)

    async def get_leaderboard(self, category: str, limit: int = 100):
        return await self.players.get_leaderboard(category, limit)

    async def log_rare_drop(self, user_id: int, item_id: str, rarity: str, source: str):
        return await self.players.log_rare_drop(user_id, item_id, rarity, source)

    async def get_active_auctions(self, limit: int = 100):
        return await self.market.get_active_auctions(limit)

    async def get_bazaar_product(self, product_id: str):
        return await self.market.get_bazaar_product(product_id)

    async def update_bazaar_product(self, product_id: str, buy_price: float, sell_price: float,
                                   buy_volume: int, sell_volume: int):
        return await self.market.update_bazaar_product(product_id, buy_price, sell_price, 
                                                       buy_volume, sell_volume)

    async def execute_bazaar_transaction(self, buyer_id: int, seller_id: int, product_id: str,
                                        amount: int, price: float):
        return await self.market.execute_bazaar_transaction(buyer_id, seller_id, product_id,
                                                            amount, price)

    async def get_all_stocks(self):
        return await self.market.get_all_stocks()

    async def get_stock(self, symbol: str):
        return await self.market.get_stock(symbol)

    async def get_player_stocks(self, user_id: int):
        return await self.market.get_player_stocks(user_id)

    async def buy_stock(self, user_id: int, symbol: str, shares: int, price: float):
        return await self.market.buy_stock(user_id, symbol, shares, price)

    async def sell_stock(self, user_id: int, symbol: str, shares: int, price: float):
        return await self.market.sell_stock(user_id, symbol, shares, price)

    async def get_market_history(self, symbol: str, limit: int = 50):
        return await self.market.get_market_history(symbol, limit)

    async def add_stock_history(self, symbol: str, price: float, volume: int = 0):
        return await self.market.add_stock_history(symbol, price, volume)

    async def update_stock_price(self, symbol: str, price: float, change_percent: float, volume: int):
        return await self.market.update_stock_price(symbol, price, change_percent, volume)

    async def get_top_collections(self, collection_name: str, limit: int = 10):
        return await self.skills.get_top_collections(collection_name, limit)

    async def unlock_achievement(self, user_id: int, achievement_id: str):
        return await self.players.unlock_achievement(user_id, achievement_id)

    async def get_achievements(self, user_id: int):
        return await self.players.get_achievements(user_id)

    async def unlock_location(self, user_id: int, location_id: str):
        return await self.players.unlock_location(user_id, location_id)

    async def get_unlocked_locations(self, user_id: int):
        return await self.players.get_unlocked_locations(user_id)

    async def place_bid(self, user_id: int, auction_id: int, bid_amount: int) -> bool:
        return await self.market.place_bid(user_id, auction_id, bid_amount)

    async def create_auction(self, seller_id: int, item_id: str, starting_bid: int,
                           buy_now_price: Optional[int], duration: int, bin: bool = False):
        return await self.market.create_auction(seller_id, item_id, starting_bid,
                                                buy_now_price, duration, bin)

    async def get_game_pet(self, pet_id: str):
        return await self.events.get_game_pet(pet_id)

    async def get_all_game_items(self):
        return await self.game_data.get_all_game_items()

    async def get_game_item(self, item_id: str):
        return await self.game_data.get_game_item(item_id)
    
    async def get_armor_stats(self, item_id: str):
        return await self.game_data.get_armor_stats(item_id)
    
    async def get_weapon_stats(self, item_id: str):
        return await self.game_data.get_weapon_stats(item_id)
    
    async def get_tool_stats(self, item_id: str):
        return await self.game_data.get_tool_stats(item_id)

    async def get_items_by_type(self, item_type: str):
        return await self.game_data.get_items_by_type(item_type)

    async def add_game_item(self, item_id: str, name: str, rarity: str, item_type: str, stats: Dict,
                           lore: str = "", special_ability: str = "", craft_recipe: Optional[Dict] = None,
                           npc_sell_price: int = 0, collection_req: Optional[Dict] = None, default_bazaar_price: int = 0):
        return await self.game_data.add_game_item(item_id, name, rarity, item_type, stats, lore,
                                                   special_ability, craft_recipe, npc_sell_price,
                                                   collection_req, default_bazaar_price)

    async def get_loot_table(self, table_id: str, category: str):
        return await self.game_data.get_loot_table(table_id, category)

    async def add_loot_table(self, table_id: str, category: str, loot_data: Dict,
                            coins_min: int = 0, coins_max: int = 0, xp_reward: int = 0):
        return await self.game_data.add_loot_table(table_id, category, loot_data, coins_min, coins_max, xp_reward)

    async def get_enchantment(self, enchant_id: str):
        return await self.game_data.get_enchantment(enchant_id)

    async def get_all_enchantments(self):
        return await self.game_data.get_all_enchantments()

    async def add_enchantment(self, enchant_id: str, name: str, max_level: int, applies_to: List,
                             description: str, stat_bonuses: Optional[Dict] = None):
        return await self.game_data.add_enchantment(enchant_id, name, max_level, applies_to, description, stat_bonuses)

    async def get_reforge(self, reforge_id: str):
        return await self.game_data.get_reforge(reforge_id)

    async def get_all_reforges(self):
        return await self.game_data.get_all_reforges()

    async def add_reforge(self, reforge_id: str, name: str, applies_to: List, stat_bonuses: Dict, cost_formula: Optional[str] = None):
        return await self.game_data.add_reforge(reforge_id, name, applies_to, stat_bonuses, cost_formula)

    async def get_skill_config(self, skill_name: str):
        return await self.game_data.get_skill_config(skill_name)

    async def add_skill_config(self, skill_name: str, display_name: str, max_level: int,
                              xp_requirements: Dict, level_rewards: Dict, stat_bonuses: Dict):
        return await self.game_data.add_skill_config(skill_name, display_name, max_level,
                                                      xp_requirements, level_rewards, stat_bonuses)

    async def get_crafting_recipes_by_output(self, output_item: str) -> List[Dict]:
        return await self.game_data.get_crafting_recipes_by_output(output_item)

    async def get_crafting_recipe(self, recipe_id: str):
        return await self.game_data.get_crafting_recipe(recipe_id)

    async def add_crafting_recipe(self, recipe_id: str, output_item: str, ingredients: Dict, output_amount: int = 1):
        return await self.game_data.add_crafting_recipe(recipe_id, output_item, ingredients, output_amount)

    async def get_all_tool_tiers(self):
        return await self.game_data.get_all_tool_tiers()

    async def add_tool_tier(self, tool_type: str, tier: int, item_id: str, name: str, stats: Dict, recipe: Dict):
        return await self.game_data.add_tool_tier(tool_type, tier, item_id, name, stats, recipe)

    async def get_rarity_color(self, rarity: str):
        return await self.game_data.get_rarity_color(rarity)

    async def add_rarity_color(self, rarity: str, color_hex: str):
        return await self.game_data.add_rarity_color(rarity, color_hex)

    async def get_all_crafting_recipes(self):
        return await self.game_data.get_all_crafting_recipes()

    async def get_slayer_boss(self, boss_type: str):
        return await self.world.get_slayer_boss(boss_type)

    async def get_slayer_drops(self, boss_type: str):
        return await self.world.get_slayer_drops(boss_type)

    async def add_slayer_boss(self, boss_id: str, name: str, emoji: str, tier_data: Dict):
        return await self.world.add_slayer_boss(boss_id, name, emoji, tier_data)

    async def add_slayer_drop(self, boss_id: str, item_id: str, min_amt: int, max_amt: int, drop_chance: float):
        return await self.world.add_slayer_drop(boss_id, item_id, min_amt, max_amt, drop_chance)

    async def get_dungeon_floor(self, floor_id: str):
        return await self.world.get_dungeon_floor(floor_id)

    async def add_dungeon_floor(self, floor_id: str, name: str, rewards: int, time: int):
        return await self.world.add_dungeon_floor(floor_id, name, rewards, time)

    async def get_mobs_by_location(self, location_id: str):
        return await self.world.get_mobs_by_location(location_id)

    async def get_mob_loot_table(self, mob_name: str):
        return await self.world.get_mob_loot_table(mob_name)

    async def get_mob_loot_coins(self, mob_name: str):
        return await self.world.get_mob_loot_coins(mob_name)

    async def add_mob_location(self, location_id: str, mob_id: str, mob_name: str, health: int,
                              damage: int, coins: int, xp: int):
        return await self.world.add_mob_location(location_id, mob_id, mob_name, health, damage, coins, xp)

    async def get_mob_stats(self, mob_id: str):
        return await self.world.get_mob_stats(mob_id)

    async def get_gathering_drops(self, gathering_type: str, resource_type: str):
        return await self.world.get_gathering_drops(gathering_type, resource_type)

    async def add_gathering_drop(self, gathering_type: str, resource_type: str, item_id: str,
                                drop_chance: float, min_amt: int, max_amt: int):
        return await self.world.add_gathering_drop(gathering_type, resource_type, item_id, drop_chance, min_amt, max_amt)

    async def get_all_fairy_soul_locations(self):
        return await self.world.get_all_fairy_soul_locations()

    async def get_collection_categories(self):
        return await self.world.get_collection_categories()

    async def get_category_items(self, category: str):
        return await self.world.get_category_items(category)

    async def get_item_category(self, item_id: str):
        return await self.world.get_item_category(item_id)

    async def add_collection_items(self, category: str, item_id: str, display_name: str, emoji: str):
        return await self.world.add_collection_items(category, item_id, display_name, emoji)

    async def get_collection_tier_requirements(self, item_id: str):
        return await self.world.get_collection_tier_requirements(item_id)

    async def get_all_collection_tier_requirements(self):
        return await self.world.get_all_collection_tier_requirements()

    async def get_collection_tier_reward(self, tier: int):
        return await self.world.get_collection_tier_reward(tier)

    async def get_all_collection_tier_rewards(self):
        return await self.world.get_all_collection_tier_rewards()

    async def get_collection_category_bonuses(self, category: str):
        return await self.world.get_collection_category_bonuses(category)

    async def get_all_collection_category_bonuses(self):
        return await self.world.get_all_collection_category_bonuses()

    async def get_all_game_events(self):
        return await self.events.get_all_game_events()

    async def get_game_event(self, event_id: str):
        return await self.events.get_game_event(event_id)

    async def add_game_event(self, event_id: str, name: str, description: str, duration: int,
                            occurs_every: int, bonuses: Dict):
        return await self.events.add_game_event(event_id, name, description, duration, occurs_every, bonuses)

    async def get_all_seasons(self):
        return await self.events.get_all_seasons()

    async def add_season(self, season_id: int, season_name: str):
        return await self.events.add_season(season_id, season_name)

    async def get_all_mayors(self):
        return await self.events.get_all_mayors()

    async def add_mayor(self, mayor_id: str, name: str, perks: str):
        return await self.events.add_mayor(mayor_id, name, perks)

    async def get_all_game_quests(self):
        return await self.events.get_all_game_quests()

    async def get_game_quest(self, quest_id: str):
        return await self.events.get_game_quest(quest_id)

    async def add_game_quest(self, quest_id: str, name: str, description: str, requirement_type: str,
                            requirement_item: Optional[str] = None, requirement_amount: int = 0,
                            reward_coins: int = 0, reward_items: Optional[List] = None):
        return await self.events.add_game_quest(quest_id, name, description, requirement_type,
                                                requirement_item, requirement_amount, reward_coins, reward_items)

    async def add_game_pet(self, pet_id: str, pet_type: str, rarity: str, stats: Dict, max_level: int, description: str):
        return await self.events.add_game_pet(pet_id, pet_type, rarity, stats, max_level, description)

    async def get_minion_data(self, minion_type: str):
        return await self.events.get_minion_data(minion_type)

    async def add_game_minion(self, minion_type: str, produces: str, base_speed: int, max_tier: int,
                             category: str, description: str):
        return await self.events.add_game_minion(minion_type, produces, base_speed, max_tier, category, description)

    async def add_dungeon_loot(self, floor_id: str, item_id: str, drop_chance: float,
                               min_amount: int = 1, max_amount: int = 1, score_requirement: int = 0):
        if not self.conn:
            return
        await self.conn.execute('''
            INSERT OR REPLACE INTO dungeon_loot (floor_id, item_id, drop_chance, min_amount, max_amount, score_requirement)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (floor_id, item_id, drop_chance, min_amount, max_amount, score_requirement))
        await self.conn.commit()

    async def get_dungeon_loot(self, floor_id: str, score: int = 0):
        if not self.conn:
            return []
        cursor = await self.conn.execute('''
            SELECT item_id, drop_chance, min_amount, max_amount, score_requirement 
            FROM dungeon_loot WHERE floor_id = ? AND score_requirement <= ?
        ''', (floor_id, score))
        rows = await cursor.fetchall()
        return [{'item_id': r[0], 'drop_chance': r[1], 'min_amount': r[2], 'max_amount': r[3], 'score_requirement': r[4]} for r in rows]

    async def add_player_pet(self, user_id: int, pet_type: str, rarity: str, level: int = 1, xp: int = 0):
        if not self.conn:
            return None
        cursor = await self.conn.execute('''
            INSERT INTO player_pets (user_id, pet_type, rarity, level, xp, active)
            VALUES (?, ?, ?, ?, ?, 0)
        ''', (user_id, pet_type, rarity, level, xp))
        await self.conn.commit()
        
        from utils.systems.badge_system import BadgeSystem
        pets = await self.fetchall('SELECT id FROM player_pets WHERE user_id = ?', (user_id,))
        pet_count = len(list(pets)) if pets else 0
        if pet_count == 1:
            await BadgeSystem.unlock_badge(self, user_id, 'first_pet')
        elif pet_count >= 10:
            await BadgeSystem.unlock_badge(self, user_id, 'pet_collector')
        
        return cursor.lastrowid

    async def get_all_game_pets(self):
        if not self.conn:
            return []
        cursor = await self.conn.execute('SELECT * FROM game_pets')
        rows = await cursor.fetchall()
        return [dict(row) for row in rows]
    
    async def _try_drop_pet(self, mob_id: str, magic_find: float) -> Optional[Tuple[str, str]]:
        from random import random, choices
        mob_key = mob_id.lower().replace(' ', '_')
        if not self.conn:
            return None
        cursor = await self.conn.execute(
            "SELECT pet, base_chance, rarities FROM pet_drop_table WHERE mob = ?",
            (mob_key,)
        )
        row = await cursor.fetchone()
        if not row:
            return None

        pet = row["pet"]
        base_chance = row["base_chance"]
        rarities = json.loads(row["rarities"])
        adjusted_chance = base_chance * (1 + magic_find / 100)

        if random() >= adjusted_chance:
            return None

        rarity_weights = []
        for rarity in rarities:
            if rarity == 'COMMON':
                rarity_weights.append(50)
            elif rarity == 'UNCOMMON':
                rarity_weights.append(30)
            elif rarity == 'RARE':
                rarity_weights.append(15)
            elif rarity == 'EPIC':
                rarity_weights.append(4)
            elif rarity == 'LEGENDARY':
                rarity_weights.append(1)
            else:
                rarity_weights.append(1)

        selected_rarity = choices(rarities, weights=rarity_weights)[0]
        return (pet, selected_rarity)
    
    
    async def get_dungeon_stats(self, user_id: int):
        if not self.conn:
            return None
        cursor = await self.conn.execute('''
            SELECT * FROM player_dungeon_stats WHERE user_id = ?
        ''', (user_id,))
        return await cursor.fetchone()

    async def update_dungeon_stats(self, user_id: int, **kwargs):
        if not self.conn:
            return
        await self.conn.execute('''
            INSERT OR IGNORE INTO player_dungeon_stats (user_id) VALUES (?)
        ''', (user_id,))
        
        valid_fields = ['catacombs_level', 'catacombs_xp', 'total_runs', 'secrets_found', 'best_score', 'fastest_run', 'total_deaths']
        updates = {k: v for k, v in kwargs.items() if k in valid_fields}
        
        if not updates:
            return
        
        set_clause = ', '.join([f"{k} = ?" for k in updates.keys()])
        values = list(updates.values()) + [user_id]
        
        await self.conn.execute(f'''
            UPDATE player_dungeon_stats SET {set_clause} WHERE user_id = ?
        ''', values)
        await self.conn.commit()

    async def increment_dungeon_stats(self, user_id: int, **kwargs):
        if not self.conn:
            return
        await self.conn.execute('''
            INSERT OR IGNORE INTO player_dungeon_stats (user_id) VALUES (?)
        ''', (user_id,))
        
        valid_fields = ['total_runs', 'secrets_found', 'total_deaths', 'catacombs_xp']
        increments = {k: v for k, v in kwargs.items() if k in valid_fields}
        
        if not increments:
            return
        
        set_clause = ', '.join([f"{k} = {k} + ?" for k in increments.keys()])
        values = list(increments.values()) + [user_id]
        
        await self.conn.execute(f'''
            UPDATE player_dungeon_stats SET {set_clause} WHERE user_id = ?
        ''', values)
        await self.conn.commit()
