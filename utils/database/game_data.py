from typing import Optional, Dict, Any, List, Tuple
import json
from .base import DatabaseBase


class GameDataDatabase(DatabaseBase):
    """Database operations for static game data (items, enchantments, loot tables, etc.)."""
    
    # Game Items
    async def add_game_item(self, item_id: str, name: str, rarity: str, item_type: str, 
                           stats: Optional[Dict] = None, lore: Optional[List[str]] = None, 
                           special_ability: Optional[str] = None, craft_recipe: Optional[Dict] = None, 
                           npc_sell_price: int = 0, collection_req: Optional[Dict] = None,
                           default_bazaar_price: float = 100):
        await self.conn.execute('''
            INSERT OR REPLACE INTO game_items 
            (item_id, name, rarity, type, stats, lore, special_ability, craft_recipe, npc_sell_price, collection_req, default_bazaar_price)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (item_id, name, rarity, item_type, 
              json.dumps(stats or {}), 
              json.dumps(lore or []), 
              special_ability,
              json.dumps(craft_recipe or {}),
              npc_sell_price,
              json.dumps(collection_req or {}),
              default_bazaar_price))
        await self.conn.commit()
    
    async def get_game_item(self, item_id: str) -> Optional[Dict[str, Any]]:
        """Get a game item by ID."""
        async with self.conn.execute(
            'SELECT * FROM game_items WHERE item_id = ?', (item_id,)
        ) as cursor:
            row = await cursor.fetchone()
            if row:
                columns = [description[0] for description in cursor.description]
                item_dict = dict(zip(columns, row))
                item_dict['stats'] = json.loads(item_dict['stats'])
                item_dict['lore'] = json.loads(item_dict['lore'])
                item_dict['craft_recipe'] = json.loads(item_dict['craft_recipe'])
                item_dict['collection_req'] = json.loads(item_dict['collection_req'])
                return item_dict
            return None
    
    async def get_all_game_items(self) -> List[Dict[str, Any]]:
        """Get all game items."""
        async with self.conn.execute('SELECT * FROM game_items') as cursor:
            rows = await cursor.fetchall()
            columns = [description[0] for description in cursor.description]
            items = []
            for row in rows:
                item_dict = dict(zip(columns, row))
                item_dict['stats'] = json.loads(item_dict['stats'])
                item_dict['lore'] = json.loads(item_dict['lore'])
                item_dict['craft_recipe'] = json.loads(item_dict['craft_recipe'])
                item_dict['collection_req'] = json.loads(item_dict['collection_req'])
                items.append(item_dict)
            return items
    
    async def get_items_by_type(self, item_type: str) -> List[Dict[str, Any]]:
        """Get all items of a specific type."""
        async with self.conn.execute(
            'SELECT * FROM game_items WHERE type = ?', (item_type,)
        ) as cursor:
            rows = await cursor.fetchall()
            columns = [description[0] for description in cursor.description]
            items = []
            for row in rows:
                item_dict = dict(zip(columns, row))
                item_dict['stats'] = json.loads(item_dict['stats'])
                item_dict['lore'] = json.loads(item_dict['lore'])
                item_dict['craft_recipe'] = json.loads(item_dict['craft_recipe'])
                item_dict['collection_req'] = json.loads(item_dict['collection_req'])
                items.append(item_dict)
            return items
    
    # Enchantments
    async def add_enchantment(self, enchant_id: str, name: str, max_level: int,
                             applies_to: List[str], description: str, stat_bonuses: Optional[Dict] = None):
        """Add or update an enchantment."""
        await self.conn.execute('''
            INSERT OR REPLACE INTO game_enchantments 
            (enchant_id, name, max_level, applies_to, description, stat_bonuses)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (enchant_id, name, max_level, json.dumps(applies_to), description, json.dumps(stat_bonuses or {})))
        await self.conn.commit()
    
    async def get_enchantment(self, enchant_id: str) -> Optional[Dict[str, Any]]:
        """Get an enchantment by ID."""
        async with self.conn.execute(
            'SELECT * FROM game_enchantments WHERE enchant_id = ?', (enchant_id,)
        ) as cursor:
            row = await cursor.fetchone()
            if row:
                columns = [description[0] for description in cursor.description]
                enchant_dict = dict(zip(columns, row))
                enchant_dict['applies_to'] = json.loads(enchant_dict['applies_to'])
                enchant_dict['stat_bonuses'] = json.loads(enchant_dict['stat_bonuses'])
                return enchant_dict
            return None
    
    async def get_all_enchantments(self) -> List[Dict[str, Any]]:
        """Get all enchantments."""
        async with self.conn.execute('SELECT * FROM game_enchantments') as cursor:
            rows = await cursor.fetchall()
            columns = [description[0] for description in cursor.description]
            enchants = []
            for row in rows:
                enchant_dict = dict(zip(columns, row))
                enchant_dict['applies_to'] = json.loads(enchant_dict['applies_to'])
                enchant_dict['stat_bonuses'] = json.loads(enchant_dict['stat_bonuses'])
                enchants.append(enchant_dict)
            return enchants
    
    # Loot Tables
    async def add_loot_table(self, table_id: str, category: str, rarity: str, 
                            loot_data: List[Tuple], coins_min: int = 0, coins_max: int = 0, xp_reward: int = 0):
        """Add or update a loot table."""
        await self.conn.execute('''
            INSERT OR REPLACE INTO game_loot_tables 
            (table_id, category, rarity, loot_data, coins_min, coins_max, xp_reward)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (table_id, category, rarity, json.dumps(loot_data), coins_min, coins_max, xp_reward))
        await self.conn.commit()
    
    async def get_loot_table(self, table_id: str, category: Optional[str] = None) -> Dict[str, Any]:
        """Get a loot table by ID and optional category."""
        if category:
            query = 'SELECT * FROM game_loot_tables WHERE table_id = ? AND category = ?'
            params = (table_id, category)
        else:
            query = 'SELECT * FROM game_loot_tables WHERE table_id = ?'
            params = (table_id,)
        
        async with self.conn.execute(query, params) as cursor:
            rows = await cursor.fetchall()
            columns = [description[0] for description in cursor.description]
            
            loot_table = {}
            for row in rows:
                row_dict = dict(zip(columns, row))
                rarity = row_dict['rarity']
                loot_data = json.loads(row_dict['loot_data'])
                
                if rarity not in loot_table:
                    loot_table[rarity] = []
                loot_table[rarity].extend(loot_data)
                
                if rarity == 'common' and row_dict['coins_min'] > 0:
                    loot_table['coins'] = (row_dict['coins_min'], row_dict['coins_max'])
                    loot_table['xp'] = row_dict['xp_reward']
            
            return loot_table
    
    # Skills Config
    async def add_skill_config(self, skill_name: str, display_name: str, max_level: int = 50,
                              xp_requirements: Optional[Dict] = None, level_rewards: Optional[Dict] = None, 
                              stat_bonuses: Optional[Dict] = None):
        """Add or update a skill configuration."""
        await self.conn.execute('''
            INSERT OR REPLACE INTO game_skills 
            (skill_name, display_name, max_level, xp_requirements, level_rewards, stat_bonuses)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (skill_name, display_name, max_level, 
              json.dumps(xp_requirements or {}), 
              json.dumps(level_rewards or {}),
              json.dumps(stat_bonuses or {})))
        await self.conn.commit()
    
    async def get_skill_config(self, skill_name: str) -> Optional[Dict[str, Any]]:
        """Get skill configuration."""
        async with self.conn.execute(
            'SELECT * FROM game_skills WHERE skill_name = ?', (skill_name,)
        ) as cursor:
            row = await cursor.fetchone()
            if row:
                columns = [description[0] for description in cursor.description]
                skill_dict = dict(zip(columns, row))
                skill_dict['xp_requirements'] = json.loads(skill_dict['xp_requirements'])
                skill_dict['level_rewards'] = json.loads(skill_dict['level_rewards'])
                skill_dict['stat_bonuses'] = json.loads(skill_dict['stat_bonuses'])
                return skill_dict
            return None
    
    async def get_all_skill_configs(self) -> List[Dict[str, Any]]:
        """Get all skill configurations."""
        async with self.conn.execute('SELECT * FROM game_skills') as cursor:
            rows = await cursor.fetchall()
            columns = [description[0] for description in cursor.description]
            skills = []
            for row in rows:
                skill_dict = dict(zip(columns, row))
                skill_dict['xp_requirements'] = json.loads(skill_dict['xp_requirements'])
                skill_dict['level_rewards'] = json.loads(skill_dict['level_rewards'])
                skill_dict['stat_bonuses'] = json.loads(skill_dict['stat_bonuses'])
                skills.append(skill_dict)
            return skills
    
    # Reforges
    async def add_reforge(self, reforge_id: str, name: str, applies_to: List[str], 
                         stat_bonuses: Dict, cost_formula: Optional[str] = None):
        """Add or update a reforge."""
        await self.conn.execute('''
            INSERT OR REPLACE INTO game_reforges 
            (reforge_id, name, applies_to, stat_bonuses, cost_formula)
            VALUES (?, ?, ?, ?, ?)
        ''', (reforge_id, name, json.dumps(applies_to), json.dumps(stat_bonuses), cost_formula))
        await self.conn.commit()
    
    async def get_reforge(self, reforge_id: str) -> Optional[Dict[str, Any]]:
        """Get a reforge by ID."""
        async with self.conn.execute(
            'SELECT * FROM game_reforges WHERE reforge_id = ?', (reforge_id,)
        ) as cursor:
            row = await cursor.fetchone()
            if row:
                columns = [description[0] for description in cursor.description]
                reforge_dict = dict(zip(columns, row))
                reforge_dict['applies_to'] = json.loads(reforge_dict['applies_to'])
                reforge_dict['stat_bonuses'] = json.loads(reforge_dict['stat_bonuses'])
                return reforge_dict
            return None
    
    async def get_all_reforges(self) -> List[Dict[str, Any]]:
        """Get all reforges."""
        async with self.conn.execute('SELECT * FROM game_reforges') as cursor:
            rows = await cursor.fetchall()
            columns = [description[0] for description in cursor.description]
            reforges = []
            for row in rows:
                reforge_dict = dict(zip(columns, row))
                reforge_dict['applies_to'] = json.loads(reforge_dict['applies_to'])
                reforge_dict['stat_bonuses'] = json.loads(reforge_dict['stat_bonuses'])
                reforges.append(reforge_dict)
            return reforges
    
    # Pets
    async def add_game_pet(self, pet_id: str, pet_type: str, rarity: str, 
                          stats: Dict, max_level: int = 100, description: Optional[str] = None):
        """Add or update a game pet type."""
        await self.conn.execute('''
            INSERT OR REPLACE INTO game_pets 
            (pet_id, pet_type, rarity, stats, max_level, description)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (pet_id, pet_type, rarity, json.dumps(stats), max_level, description))
        await self.conn.commit()
    
    async def get_game_pet(self, pet_id: str) -> Optional[Dict[str, Any]]:
        """Get a game pet type."""
        async with self.conn.execute(
            'SELECT * FROM game_pets WHERE pet_id = ?', (pet_id,)
        ) as cursor:
            row = await cursor.fetchone()
            if row:
                columns = [description[0] for description in cursor.description]
                pet_dict = dict(zip(columns, row))
                pet_dict['stats'] = json.loads(pet_dict['stats'])
                return pet_dict
            return None
    
    async def get_all_game_pets(self) -> List[Dict[str, Any]]:
        """Get all game pet types."""
        async with self.conn.execute('SELECT * FROM game_pets') as cursor:
            rows = await cursor.fetchall()
            columns = [description[0] for description in cursor.description]
            pets = []
            for row in rows:
                pet_dict = dict(zip(columns, row))
                pet_dict['stats'] = json.loads(pet_dict['stats'])
                pets.append(pet_dict)
            return pets
    
    # Minions
    async def add_game_minion(self, minion_type: str, produces: str, base_speed: int,
                             max_tier: int = 11, category: str = 'mining', description: Optional[str] = None):
        """Add or update a game minion type."""
        await self.conn.execute('''
            INSERT OR REPLACE INTO game_minions 
            (minion_type, produces, base_speed, max_tier, category, description)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (minion_type, produces, base_speed, max_tier, category, description))
        await self.conn.commit()
    
    async def get_game_minion(self, minion_type: str) -> Optional[Dict[str, Any]]:
        """Get a game minion type."""
        async with self.conn.execute(
            'SELECT * FROM game_minions WHERE minion_type = ?', (minion_type,)
        ) as cursor:
            row = await cursor.fetchone()
            if row:
                columns = [description[0] for description in cursor.description]
                return dict(zip(columns, row))
            return None
    
    async def get_all_game_minions(self) -> List[Dict[str, Any]]:
        """Get all game minion types."""
        async with self.conn.execute('SELECT * FROM game_minions') as cursor:
            rows = await cursor.fetchall()
            columns = [description[0] for description in cursor.description]
            return [dict(zip(columns, row)) for row in rows]
    
    # Events
    async def add_game_event(self, event_id: str, name: str, description: str,
                            duration: int, occurs_every: int, bonuses: Optional[Dict] = None):
        """Add or update a game event."""
        await self.conn.execute('''
            INSERT OR REPLACE INTO game_events 
            (event_id, name, description, duration, occurs_every, bonuses)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (event_id, name, description, duration, occurs_every, json.dumps(bonuses or {})))
        await self.conn.commit()
    
    async def get_game_event(self, event_id: str) -> Optional[Dict[str, Any]]:
        """Get a game event."""
        async with self.conn.execute(
            'SELECT * FROM game_events WHERE event_id = ?', (event_id,)
        ) as cursor:
            row = await cursor.fetchone()
            if row:
                columns = [description[0] for description in cursor.description]
                event_dict = dict(zip(columns, row))
                event_dict['bonuses'] = json.loads(event_dict['bonuses'])
                return event_dict
            return None
    
    async def get_all_game_events(self) -> List[Dict[str, Any]]:
        """Get all game events."""
        async with self.conn.execute('SELECT * FROM game_events') as cursor:
            rows = await cursor.fetchall()
            columns = [description[0] for description in cursor.description]
            events = []
            for row in rows:
                event_dict = dict(zip(columns, row))
                event_dict['bonuses'] = json.loads(event_dict['bonuses'])
                events.append(event_dict)
            return events
    
    # Quests
    async def add_game_quest(self, quest_id: str, name: str, description: str,
                            requirement_type: str, requirement_item: Optional[str] = None,
                            requirement_amount: int = 0, reward_coins: int = 0,
                            reward_items: Optional[List] = None):
        """Add or update a game quest."""
        await self.conn.execute('''
            INSERT OR REPLACE INTO game_quests 
            (quest_id, name, description, requirement_type, requirement_item, 
             requirement_amount, reward_coins, reward_items)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (quest_id, name, description, requirement_type, requirement_item,
              requirement_amount, reward_coins, json.dumps(reward_items or [])))
        await self.conn.commit()
    
    async def get_game_quest(self, quest_id: str) -> Optional[Dict[str, Any]]:
        """Get a game quest."""
        async with self.conn.execute(
            'SELECT * FROM game_quests WHERE quest_id = ?', (quest_id,)
        ) as cursor:
            row = await cursor.fetchone()
            if row:
                columns = [description[0] for description in cursor.description]
                quest_dict = dict(zip(columns, row))
                quest_dict['reward_items'] = json.loads(quest_dict['reward_items'])
                return quest_dict
            return None
    
    async def get_all_game_quests(self) -> List[Dict[str, Any]]:
        """Get all game quests."""
        async with self.conn.execute('SELECT * FROM game_quests') as cursor:
            rows = await cursor.fetchall()
            columns = [description[0] for description in cursor.description]
            quests = []
            for row in rows:
                quest_dict = dict(zip(columns, row))
                quest_dict['reward_items'] = json.loads(quest_dict['reward_items'])
                quests.append(quest_dict)
            return quests
    
    async def add_collection_items(self, category: str, item_id: str, display_name: str, emoji: Optional[str] = None):
        await self.conn.execute('''
            INSERT OR REPLACE INTO game_collection_items 
            (category, item_id, display_name, emoji)
            VALUES (?, ?, ?, ?)
        ''', (category, item_id, display_name, emoji))
        await self.conn.commit()
    
    async def get_collection_items_by_category(self, category: str) -> List[Dict[str, Any]]:
        async with self.conn.execute(
            'SELECT * FROM game_collection_items WHERE category = ?', (category,)
        ) as cursor:
            rows = await cursor.fetchall()
            columns = [description[0] for description in cursor.description]
            return [dict(zip(columns, row)) for row in rows]
    
    async def add_mob_location(self, location_id: str, mob_id: str, mob_name: str, 
                              health: int, damage: int, coins_reward: int, xp_reward: int):
        await self.conn.execute('''
            INSERT OR REPLACE INTO game_mob_locations 
            (location_id, mob_id, mob_name, health, damage, coins_reward, xp_reward)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (location_id, mob_id, mob_name, health, damage, coins_reward, xp_reward))
        await self.conn.commit()
    
    async def get_mobs_by_location(self, location_id: str) -> List[Dict[str, Any]]:
        async with self.conn.execute(
            'SELECT * FROM game_mob_locations WHERE location_id = ?', (location_id,)
        ) as cursor:
            rows = await cursor.fetchall()
            columns = [description[0] for description in cursor.description]
            return [dict(zip(columns, row)) for row in rows]
    
    async def add_dungeon_floor(self, floor_id: str, name: str, rewards: int, time: int):
        await self.conn.execute('''
            INSERT OR REPLACE INTO game_dungeon_floors 
            (floor_id, name, tier, required_catacombs, mob_health_multiplier, reward_multiplier)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (floor_id, name, 0, 0, 1.0, rewards / 1000.0))
        await self.conn.commit()
    
    async def get_dungeon_floor(self, floor_id: str) -> Optional[Dict[str, Any]]:
        async with self.conn.execute(
            'SELECT * FROM game_dungeon_floors WHERE floor_id = ?', (floor_id,)
        ) as cursor:
            row = await cursor.fetchone()
            if row:
                columns = [description[0] for description in cursor.description]
                return dict(zip(columns, row))
            return None
    
    async def get_all_dungeon_floors(self) -> List[Dict[str, Any]]:
        async with self.conn.execute('SELECT * FROM game_dungeon_floors') as cursor:
            rows = await cursor.fetchall()
            columns = [description[0] for description in cursor.description]
            return [dict(zip(columns, row)) for row in rows]
    
    async def add_slayer_boss(self, boss_id: str, name: str, emoji: str, tier_data: Dict):
        await self.conn.execute('''
            INSERT OR REPLACE INTO game_slayer_bosses 
            (boss_id, name, emoji, tier_data)
            VALUES (?, ?, ?, ?)
        ''', (boss_id, name, emoji, json.dumps(tier_data)))
        await self.conn.commit()
    
    async def get_slayer_boss(self, boss_id: str) -> Optional[Dict[str, Any]]:
        async with self.conn.execute(
            'SELECT * FROM game_slayer_bosses WHERE boss_id = ?', (boss_id,)
        ) as cursor:
            row = await cursor.fetchone()
            if row:
                columns = [description[0] for description in cursor.description]
                boss_dict = dict(zip(columns, row))
                boss_dict['tier_data'] = json.loads(boss_dict['tier_data'])
                return boss_dict
            return None
    
    async def get_all_slayer_bosses(self) -> List[Dict[str, Any]]:
        async with self.conn.execute('SELECT * FROM game_slayer_bosses') as cursor:
            rows = await cursor.fetchall()
            columns = [description[0] for description in cursor.description]
            bosses = []
            for row in rows:
                boss_dict = dict(zip(columns, row))
                boss_dict['tier_data'] = json.loads(boss_dict['tier_data'])
                bosses.append(boss_dict)
            return bosses
    
    async def add_tool_tier(self, tool_type: str, tier: int, item_id: str, 
                           name: str, stats: Optional[Dict] = None, recipe: Optional[Dict] = None):
        await self.conn.execute('''
            INSERT OR REPLACE INTO game_tool_tiers 
            (tool_type, tier, item_id, name, stats, recipe)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (tool_type, tier, item_id, name, json.dumps(stats or {}), json.dumps(recipe or {})))
        await self.conn.commit()
    
    async def get_tool_tiers(self, tool_type: str) -> List[Dict[str, Any]]:
        async with self.conn.execute(
            'SELECT * FROM game_tool_tiers WHERE tool_type = ? ORDER BY tier', (tool_type,)
        ) as cursor:
            rows = await cursor.fetchall()
            columns = [description[0] for description in cursor.description]
            tiers = []
            for row in rows:
                tier_dict = dict(zip(columns, row))
                tier_dict['stats'] = json.loads(tier_dict['stats'])
                tier_dict['recipe'] = json.loads(tier_dict['recipe'])
                tiers.append(tier_dict)
            return tiers
    
    async def get_all_tool_tiers(self) -> Dict[str, List[Dict[str, Any]]]:
        async with self.conn.execute('SELECT * FROM game_tool_tiers ORDER BY tool_type, tier') as cursor:
            rows = await cursor.fetchall()
            columns = [description[0] for description in cursor.description]
            tools = {}
            for row in rows:
                tier_dict = dict(zip(columns, row))
                tier_dict['stats'] = json.loads(tier_dict['stats'])
                tier_dict['recipe'] = json.loads(tier_dict['recipe'])
                tool_type = tier_dict['tool_type']
                if tool_type not in tools:
                    tools[tool_type] = []
                tools[tool_type].append(tier_dict)
            return tools
    
    async def add_season(self, season_id: int, season_name: str):
        await self.conn.execute('''
            INSERT OR REPLACE INTO game_seasons 
            (season_id, season_name)
            VALUES (?, ?)
        ''', (season_id, season_name))
        await self.conn.commit()
    
    async def get_all_seasons(self) -> List[str]:
        async with self.conn.execute('SELECT season_name FROM game_seasons ORDER BY season_id') as cursor:
            rows = await cursor.fetchall()
            return [row[0] for row in rows]
    
    async def add_mayor(self, mayor_id: str, mayor_name: str, perks: str):
        await self.conn.execute('''
            INSERT OR REPLACE INTO game_mayors 
            (mayor_id, mayor_name, perks)
            VALUES (?, ?, ?)
        ''', (mayor_id, mayor_name, perks))
        await self.conn.commit()
    
    async def get_all_mayors(self) -> List[Dict[str, Any]]:
        async with self.conn.execute('SELECT * FROM game_mayors') as cursor:
            rows = await cursor.fetchall()
            columns = [description[0] for description in cursor.description]
            return [dict(zip(columns, row)) for row in rows]
    
    async def get_mayor(self, mayor_id: str) -> Optional[Dict[str, Any]]:
        async with self.conn.execute(
            'SELECT * FROM game_mayors WHERE mayor_id = ?', (mayor_id,)
        ) as cursor:
            row = await cursor.fetchone()
            if row:
                columns = [description[0] for description in cursor.description]
                return dict(zip(columns, row))
            return None
    
    async def add_gathering_drop(self, gathering_type: str, resource_type: str, 
                                item_id: str, drop_chance: float = 1.0, 
                                min_amount: int = 1, max_amount: int = 1):
        await self.conn.execute('''
            INSERT INTO game_gathering_drops 
            (gathering_type, resource_type, item_id, drop_chance, min_amount, max_amount)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (gathering_type, resource_type, item_id, drop_chance, min_amount, max_amount))
        await self.conn.commit()
    
    async def get_gathering_drops(self, gathering_type: str, resource_type: str) -> List[Dict[str, Any]]:
        async with self.conn.execute('''
            SELECT * FROM game_gathering_drops 
            WHERE gathering_type = ? AND resource_type = ?
        ''', (gathering_type, resource_type)) as cursor:
            rows = await cursor.fetchall()
            columns = [description[0] for description in cursor.description]
            return [dict(zip(columns, row)) for row in rows]
    
    async def add_rarity_color(self, rarity: str, color_hex: str):
        await self.conn.execute('''
            INSERT OR REPLACE INTO game_rarity_colors 
            (rarity, color_hex)
            VALUES (?, ?)
        ''', (rarity, color_hex))
        await self.conn.commit()
    
    async def get_rarity_color(self, rarity: str) -> Optional[str]:
        async with self.conn.execute(
            'SELECT color_hex FROM game_rarity_colors WHERE rarity = ?', (rarity,)
        ) as cursor:
            row = await cursor.fetchone()
            return row[0] if row else None
    
    async def get_all_rarity_colors(self) -> Dict[str, str]:
        async with self.conn.execute('SELECT * FROM game_rarity_colors') as cursor:
            rows = await cursor.fetchall()
            return {row[0]: row[1] for row in rows}
    
    async def add_crafting_recipe(self, recipe_id: str, result_item: str, ingredients: Dict):
        await self.conn.execute('''
            INSERT OR REPLACE INTO game_crafting_recipes 
            (recipe_id, result_item, ingredients, category, requires_table)
            VALUES (?, ?, ?, ?, ?)
        ''', (recipe_id, result_item, json.dumps(ingredients), None, None))
        await self.conn.commit()
    
    async def get_crafting_recipe(self, recipe_id: str) -> Optional[Dict[str, Any]]:
        async with self.conn.execute(
            'SELECT craft_recipe FROM game_items WHERE item_id = ?', (recipe_id,)
        ) as cursor:
            row = await cursor.fetchone()
            if row and row[0]:
                try:
                    recipe = json.loads(row[0])
                    if recipe:
                        return {'recipe_id': recipe_id, 'result_item': recipe_id, 'ingredients': recipe}
                except:
                    pass
        
        async with self.conn.execute(
            'SELECT * FROM game_crafting_recipes WHERE recipe_id = ?', (recipe_id,)
        ) as cursor:
            row = await cursor.fetchone()
            if row:
                columns = [description[0] for description in cursor.description]
                recipe_dict = dict(zip(columns, row))
                recipe_dict['ingredients'] = json.loads(recipe_dict['ingredients'])
                return recipe_dict
            return None
    
    async def get_all_crafting_recipes(self) -> Dict[str, Dict]:
        recipes = {}
        
        async with self.conn.execute('SELECT item_id, craft_recipe FROM game_items WHERE craft_recipe IS NOT NULL AND craft_recipe != "{}"') as cursor:
            rows = await cursor.fetchall()
            for row in rows:
                item_id = row[0]
                craft_recipe_json = row[1]
                if craft_recipe_json:
                    try:
                        recipe = json.loads(craft_recipe_json)
                        if recipe:
                            recipes[item_id] = recipe
                    except:
                        pass
        
        async with self.conn.execute('SELECT * FROM game_crafting_recipes') as cursor:
            rows = await cursor.fetchall()
            columns = [description[0] for description in cursor.description]
            for row in rows:
                recipe_dict = dict(zip(columns, row))
                recipe_dict['ingredients'] = json.loads(recipe_dict['ingredients'])
                recipes[recipe_dict['recipe_id']] = recipe_dict['ingredients']
        
        return recipes
    
    async def add_slayer_drop(self, boss_id: str, item_id: str, min_amount: int, 
                             max_amount: int, drop_chance: float = 1.0):
        await self.conn.execute('''
            INSERT OR REPLACE INTO game_slayer_drops 
            (boss_id, item_id, min_amount, max_amount, drop_chance)
            VALUES (?, ?, ?, ?, ?)
        ''', (boss_id, item_id, min_amount, max_amount, drop_chance))
        await self.conn.commit()
    
    async def get_slayer_drops(self, boss_id: str) -> List[Tuple[str, int, int]]:
        async with self.conn.execute('''
            SELECT item_id, min_amount, max_amount, drop_chance 
            FROM game_slayer_drops 
            WHERE boss_id = ?
        ''', (boss_id,)) as cursor:
            rows = await cursor.fetchall()
            return [(row[0], row[1], row[2]) for row in rows]
