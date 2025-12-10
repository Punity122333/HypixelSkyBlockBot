from typing import Optional, Dict, List, Any
import aiosqlite
import json


class GameDataDB:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.conn: Optional[aiosqlite.Connection] = None
    
    async def connect(self):
        if not self.conn:
            self.conn = await aiosqlite.connect(self.db_path)
            self.conn.row_factory = aiosqlite.Row

    async def get_all_game_items(self) -> dict[str, dict]:
        if not self.conn:
            return {}

        cursor = await self.conn.execute('SELECT * FROM game_items')
        rows = await cursor.fetchall()

        items = {}
        for row in rows:
            row_dict = dict(row)
            items[row_dict['item_id']] = {
                'item_id': row_dict['item_id'],
                'name': row_dict['name'],
                'rarity': row_dict['rarity'],
                'type': row_dict['item_type'],
                'stats': json.loads(row_dict['stats']) if row_dict['stats'] else {},
                'lore': row_dict['lore'] if 'lore' in row_dict else '',
                'special_ability': row_dict['special_ability'] if 'special_ability' in row_dict else '',
                'craft_recipe': json.loads(row_dict['craft_recipe']) if row_dict.get('craft_recipe') else {},
                'npc_sell_price': row_dict['npc_sell_price'] if 'npc_sell_price' in row_dict else 0,
                'collection_req': json.loads(row_dict['collection_req']) if row_dict.get('collection_req') else {},
                'default_bazaar_price': row_dict['default_bazaar_price'] if 'default_bazaar_price' in row_dict else 0
            }

        return items

    async def get_game_item(self, item_id: str):
        if not self.conn:
            return None
        cursor = await self.conn.execute('''
            SELECT * FROM game_items WHERE item_id = ?
        ''', (item_id,))
        row = await cursor.fetchone()
        if row:
            return dict(row)
        return None

    async def get_items_by_type(self, item_type: str):
        if not self.conn:
            return []
        cursor = await self.conn.execute('''
            SELECT * FROM game_items WHERE item_type = ?
        ''', (item_type,))
        return await cursor.fetchall()

    async def add_game_item(self, item_id: str, name: str, rarity: str, item_type: str, stats: Dict, 
                           lore: str = "", special_ability: str = "", craft_recipe: Optional[Dict] = None,
                           npc_sell_price: int = 0, collection_req: Optional[Dict] = None, default_bazaar_price: int = 0):
        if not self.conn:
            return
        await self.conn.execute('''
            INSERT OR REPLACE INTO game_items (item_id, name, rarity, item_type, stats, lore, 
                                               special_ability, craft_recipe, npc_sell_price, 
                                               collection_req, default_bazaar_price)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (item_id, name, rarity, item_type, json.dumps(stats), lore, special_ability,
              json.dumps(craft_recipe or {}), npc_sell_price, json.dumps(collection_req or {}), 
              default_bazaar_price))
        await self.conn.commit()

    async def get_loot_table(self, table_id: str, category: str):
        if not self.conn:
            return None

        cursor = await self.conn.execute('''
            SELECT * FROM loot_tables
            WHERE table_id = ? AND category = ?
        ''', (table_id, category))
        row = await cursor.fetchone()
        if row:
            row_dict = dict(row)
            if 'loot_data' in row_dict and row_dict['loot_data']:
                row_dict['loot_data'] = json.loads(row_dict['loot_data'])
            return row_dict
        return None

    async def add_loot_table(self, table_id: str, category: str, loot_data: Dict,
                            coins_min: int = 0, coins_max: int = 0, xp_reward: int = 0):
        if not self.conn:
            return
        await self.conn.execute('''
            INSERT OR REPLACE INTO loot_tables (table_id, category, loot_data, coins_min, coins_max, xp_reward)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (table_id, category, json.dumps(loot_data), coins_min, coins_max, xp_reward))
        await self.conn.commit()
    
    async def get_armor_stats(self, item_id: str) -> Optional[Dict]:
        if not self.conn:
            return None
        cursor = await self.conn.execute('SELECT * FROM armor_stats WHERE item_id = ?', (item_id,))
        row = await cursor.fetchone()
        if row:
            return dict(row)
        return None
    
    async def get_weapon_stats(self, item_id: str) -> Optional[Dict]:
        if not self.conn:
            return None
        cursor = await self.conn.execute('SELECT * FROM weapon_stats WHERE item_id = ?', (item_id,))
        row = await cursor.fetchone()
        if row:
            return dict(row)
        return None
    
    async def get_tool_stats(self, item_id: str) -> Optional[Dict]:
        if not self.conn:
            return None
        cursor = await self.conn.execute('SELECT * FROM tool_stats WHERE item_id = ?', (item_id,))
        row = await cursor.fetchone()
        if row:
            return dict(row)
        return None

    async def get_enchantment(self, enchant_id: str):
        if not self.conn:
            return None
        cursor = await self.conn.execute('''
            SELECT * FROM enchantments WHERE enchant_id = ?
        ''', (enchant_id,))
        row = await cursor.fetchone()
        if row:
            enchant = dict(row)
            if 'applies_to' in enchant and enchant['applies_to']:
                enchant['applies_to'] = json.loads(enchant['applies_to'])
            if 'stat_bonuses' in enchant and enchant['stat_bonuses']:
                enchant['stat_bonuses'] = json.loads(enchant['stat_bonuses'])
            return enchant
        return None

    async def get_all_enchantments(self):
        if not self.conn:
            return []
        cursor = await self.conn.execute('SELECT * FROM enchantments')
        rows = await cursor.fetchall()
        enchants = []
        for row in rows:
            enchant = dict(row)
            if 'applies_to' in enchant and enchant['applies_to']:
                enchant['applies_to'] = json.loads(enchant['applies_to'])
            if 'stat_bonuses' in enchant and enchant['stat_bonuses']:
                enchant['stat_bonuses'] = json.loads(enchant['stat_bonuses'])
            enchants.append(enchant)
        return enchants

    async def add_enchantment(self, enchant_id: str, name: str, max_level: int, applies_to: List, 
                             description: str, stat_bonuses: Optional[Dict] = None):
        if not self.conn:
            return
        await self.conn.execute('''
            INSERT OR REPLACE INTO enchantments (enchant_id, name, max_level, applies_to, description, stat_bonuses)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (enchant_id, name, max_level, json.dumps(applies_to), description, json.dumps(stat_bonuses or {})))
        await self.conn.commit()

    async def get_reforge(self, reforge_id: str):
        if not self.conn:
            return None
        cursor = await self.conn.execute('''
            SELECT * FROM reforges WHERE reforge_id = ?
        ''', (reforge_id,))
        row = await cursor.fetchone()
        if row:
            reforge = dict(row)
            if 'applies_to' in reforge and reforge['applies_to']:
                reforge['applies_to'] = json.loads(reforge['applies_to'])
            if 'stat_bonuses' in reforge and reforge['stat_bonuses']:
                reforge['stat_bonuses'] = json.loads(reforge['stat_bonuses'])
            return reforge
        return None

    async def get_all_reforges(self):
        if not self.conn:
            return []
        cursor = await self.conn.execute('SELECT * FROM reforges')
        rows = await cursor.fetchall()
        reforges = []
        for row in rows:
            reforge = dict(row)
            if 'applies_to' in reforge and reforge['applies_to']:
                reforge['applies_to'] = json.loads(reforge['applies_to'])
            if 'stat_bonuses' in reforge and reforge['stat_bonuses']:
                reforge['stat_bonuses'] = json.loads(reforge['stat_bonuses'])
            reforges.append(reforge)
        return reforges

    async def add_reforge(self, reforge_id: str, name: str, applies_to: List, stat_bonuses: Dict, cost_formula: Optional[str] = None):
        if not self.conn:
            return
        await self.conn.execute('''
            INSERT OR REPLACE INTO reforges (reforge_id, name, applies_to, stat_bonuses, cost_formula)
            VALUES (?, ?, ?, ?, ?)
        ''', (reforge_id, name, json.dumps(applies_to), json.dumps(stat_bonuses), cost_formula))
        await self.conn.commit()

    async def get_skill_config(self, skill_name: str):
        if not self.conn:
            return None
        cursor = await self.conn.execute('''
            SELECT * FROM skill_configs WHERE skill_name = ?
        ''', (skill_name,))
        row = await cursor.fetchone()
        if row:
            config = dict(row)
            if 'xp_requirements' in config and config['xp_requirements']:
                config['xp_requirements'] = json.loads(config['xp_requirements'])
            if 'level_rewards' in config and config['level_rewards']:
                config['level_rewards'] = json.loads(config['level_rewards'])
            if 'stat_bonuses' in config and config['stat_bonuses']:
                config['stat_bonuses'] = json.loads(config['stat_bonuses'])
            return config
        return None

    async def add_skill_config(self, skill_name: str, display_name: str, max_level: int, 
                              xp_requirements: Dict, level_rewards: Dict, stat_bonuses: Dict):
        if not self.conn:
            return
        await self.conn.execute('''
            INSERT OR REPLACE INTO skill_configs (skill_name, display_name, max_level, xp_requirements, level_rewards, stat_bonuses)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (skill_name, display_name, max_level, json.dumps(xp_requirements), json.dumps(level_rewards), json.dumps(stat_bonuses)))
        await self.conn.commit()

    async def get_all_skill_configs(self):
        if not self.conn:
            return []
        cursor = await self.conn.execute('SELECT * FROM skill_configs')
        rows = await cursor.fetchall()
        skills = []
        for row in rows:
            config = dict(row)
            if 'xp_requirements' in config and config['xp_requirements']:
                config['xp_requirements'] = json.loads(config['xp_requirements'])
            if 'level_rewards' in config and config['level_rewards']:
                config['level_rewards'] = json.loads(config['level_rewards'])
            if 'stat_bonuses' in config and config['stat_bonuses']:
                config['stat_bonuses'] = json.loads(config['stat_bonuses'])
            skills.append(config)
        return skills

    async def get_crafting_recipes_by_output(self, output_item: str) -> List[Dict]:
        if not self.conn:
            return []
        cursor = await self.conn.execute('''
            SELECT * FROM crafting_recipes WHERE output_item = ?
        ''', (output_item,))
        rows = await cursor.fetchall()
        recipes = []
        for row in rows:
            recipe = dict(row)
            if 'ingredients' in recipe and recipe['ingredients']:
                recipe['ingredients'] = json.loads(recipe['ingredients'])
            recipes.append(recipe)
        return recipes

    async def get_crafting_recipe(self, recipe_id: str):
        if not self.conn:
            return None
        cursor = await self.conn.execute('''
            SELECT * FROM crafting_recipes WHERE recipe_id = ?
        ''', (recipe_id,))
        row = await cursor.fetchone()
        if row:
            recipe = dict(row)
            if 'ingredients' in recipe and recipe['ingredients']:
                recipe['ingredients'] = json.loads(recipe['ingredients'])
            return recipe
        return None

    async def add_crafting_recipe(self, recipe_id: str, output_item: str, ingredients: Dict, output_amount: int = 1):
        if not self.conn:
            return
        await self.conn.execute('''
            INSERT OR REPLACE INTO crafting_recipes (recipe_id, output_item, ingredients, output_amount)
            VALUES (?, ?, ?, ?)
        ''', (recipe_id, output_item, json.dumps(ingredients), output_amount))
        await self.conn.commit()

    async def get_all_tool_tiers(self):
        if not self.conn:
            return {}
        cursor = await self.conn.execute('SELECT * FROM tool_tiers')
        rows = await cursor.fetchall()
        tools = {}
        for row in rows:
            tool = dict(row)
            tool_type = tool['tool_type']
            if tool_type not in tools:
                tools[tool_type] = []
            if 'stats' in tool and tool['stats']:
                tool['stats'] = json.loads(tool['stats'])
            if 'recipe' in tool and tool['recipe']:
                tool['recipe'] = json.loads(tool['recipe'])
            tools[tool_type].append(tool)
        return tools

    async def add_tool_tier(self, tool_type: str, tier: int, item_id: str, name: str, stats: Dict, recipe: Dict):
        if not self.conn:
            return
        await self.conn.execute('''
            INSERT OR REPLACE INTO tool_tiers (tool_type, tier, item_id, name, stats, recipe)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (tool_type, tier, item_id, name, json.dumps(stats), json.dumps(recipe)))
        await self.conn.commit()

    async def get_rarity_color(self, rarity: str):
        if not self.conn:
            return None
        cursor = await self.conn.execute('''
            SELECT color_hex FROM rarity_colors WHERE rarity = ?
        ''', (rarity,))
        row = await cursor.fetchone()
        if row:
            return row['color_hex']
        return None

    async def add_rarity_color(self, rarity: str, color_hex: str):
        if not self.conn:
            return
        await self.conn.execute('''
            INSERT OR REPLACE INTO rarity_colors (rarity, color_hex)
            VALUES (?, ?)
        ''', (rarity, color_hex))
        await self.conn.commit()

    async def get_all_crafting_recipes(self):
        if not self.conn:
            return []
        cursor = await self.conn.execute('SELECT * FROM crafting_recipes')
        rows = await cursor.fetchall()
        recipes = []
        for row in rows:
            recipe = dict(row)
            if 'ingredients' in recipe and recipe['ingredients']:
                recipe['ingredients'] = json.loads(recipe['ingredients'])
            recipes.append(recipe)
        return recipes
