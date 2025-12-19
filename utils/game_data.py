import json
from typing import Dict, Optional, List, Any, Tuple
from database import GameDatabase


class GameData:
    
    def __init__(self, db: GameDatabase):
        self.db = db
        self._item_cache: Dict[str, Any] = {}
        self._enchantment_cache: Dict[str, Any] = {}
        self._reforge_cache: Dict[str, Any] = {}
        self._pet_cache: Dict[str, Any] = {}
    
    async def get_item(self, item_id: str) -> Optional[Dict[str, Any]]:
        if item_id in self._item_cache:
            return self._item_cache[item_id]
        
        if not self.db.conn:
            return None
        
        cursor = await self.db.conn.execute(
            'SELECT * FROM game_items WHERE item_id = ?', (item_id,)
        )
        item_data = await cursor.fetchone()
        
        if not item_data:
            return None
        
        item = {
            'item_id': item_data['item_id'],
            'name': item_data['name'],
            'rarity': item_data['rarity'],
            'type': item_data['item_type'],
            'stats': json.loads(item_data['stats']) if item_data['stats'] else {},
            'lore': item_data['lore'] or '',
            'special_ability': item_data['special_ability'] or '',
            'craft_recipe': json.loads(item_data['craft_recipe']) if item_data['craft_recipe'] else {},
            'npc_sell_price': item_data['npc_sell_price'] or 0,
            'collection_req': json.loads(item_data['collection_req']) if item_data['collection_req'] else {},
            'default_bazaar_price': item_data['default_bazaar_price'] or 0
        }
        
        self._item_cache[item_id] = item
        return item
    
    async def get_enchantment(self, enchant_id: str) -> Optional[Dict[str, Any]]:
        if enchant_id in self._enchantment_cache:
            return self._enchantment_cache[enchant_id]
        
        if not self.db.conn:
            return None
        
        cursor = await self.db.conn.execute(
            'SELECT * FROM enchantments WHERE enchant_id = ?', (enchant_id,)
        )
        enchant_data = await cursor.fetchone()
        
        if not enchant_data:
            return None
        
        enchant = {
            'enchant_id': enchant_data['enchant_id'],
            'name': enchant_data['name'],
            'max_level': enchant_data['max_level'],
            'applies_to': json.loads(enchant_data['applies_to']) if enchant_data['applies_to'] else [],
            'description': enchant_data['description'] or '',
            'stat_bonuses': json.loads(enchant_data['stat_bonuses']) if enchant_data['stat_bonuses'] else {}
        }
        
        self._enchantment_cache[enchant_id] = enchant
        return enchant
    
    async def get_reforge(self, reforge_id: str) -> Optional[Dict[str, Any]]:
        if reforge_id in self._reforge_cache:
            return self._reforge_cache[reforge_id]
        
        if not self.db.conn:
            return None
        
        cursor = await self.db.conn.execute(
            'SELECT * FROM reforges WHERE reforge_id = ?', (reforge_id,)
        )
        reforge_data = await cursor.fetchone()
        
        if not reforge_data:
            return None
        
        reforge = {
            'reforge_id': reforge_data['reforge_id'],
            'name': reforge_data['name'],
            'applies_to': json.loads(reforge_data['applies_to']) if reforge_data['applies_to'] else [],
            'stat_bonuses': json.loads(reforge_data['stat_bonuses']) if reforge_data['stat_bonuses'] else {},
            'cost_formula': reforge_data['cost_formula'] or ''
        }
        
        self._reforge_cache[reforge_id] = reforge
        return reforge
    
    
    async def get_pet(self, pet_type: str, rarity: str) -> Optional[Dict[str, Any]]:
        cache_key = f'{pet_type}_{rarity}'
        if cache_key in self._pet_cache:
            return self._pet_cache[cache_key]
        
        if not self.db.conn:
            return None
        
        cursor = await self.db.conn.execute(
            'SELECT * FROM game_pets WHERE pet_type = ? AND rarity = ?', (pet_type, rarity)
        )
        pet_data = await cursor.fetchone()
        
        if not pet_data:
            return None
        
        pet = {
            'pet_id': pet_data['pet_id'],
            'pet_type': pet_data['pet_type'],
            'rarity': pet_data['rarity'],
            'stats': json.loads(pet_data['stats']) if pet_data['stats'] else {},
            'max_level': pet_data['max_level'] or 1,
            'description': pet_data['description'] or ''
        }
        
        self._pet_cache[cache_key] = pet
        return pet
    
    async def get_skill_config(self, skill_name: str) -> Optional[Dict[str, Any]]:
        if not self.db.conn:
            return None
        
        cursor = await self.db.conn.execute(
            'SELECT * FROM skill_configs WHERE skill_name = ?', (skill_name,)
        )
        skill_data = await cursor.fetchone()
        
        if not skill_data:
            return None
        
        return {
            'skill_name': skill_data['skill_name'],
            'display_name': skill_data['display_name'] or '',
            'max_level': skill_data['max_level'] or 1,
            'xp_requirements': json.loads(skill_data['xp_requirements']) if skill_data['xp_requirements'] else [],
            'level_rewards': json.loads(skill_data['level_rewards']) if skill_data['level_rewards'] else {},
            'stat_bonuses': json.loads(skill_data['stat_bonuses']) if skill_data['stat_bonuses'] else {}
        }
    
    async def get_all_items(self) -> List[Dict[str, Any]]:
        if not self.db.conn:
            return []
        
        cursor = await self.db.conn.execute('SELECT item_id FROM game_items')
        item_ids = await cursor.fetchall()
        
        items = []
        for row in item_ids:
            item = await self.get_item(row['item_id'])
            if item:
                items.append(item)
        
        return items
    
    async def search_items(self, query: str, limit: int = 20) -> List[Dict[str, Any]]:
        if not self.db.conn:
            return []
        
        cursor = await self.db.conn.execute(
            '''
            SELECT item_id FROM game_items 
            WHERE LOWER(name) LIKE ? OR LOWER(item_id) LIKE ?
            LIMIT ?
            ''', (f'%{query.lower()}%', f'%{query.lower()}%', limit)
        )
        item_ids = await cursor.fetchall()
        
        items = []
        for row in item_ids:
            item = await self.get_item(row['item_id'])
            if item:
                items.append(item)
        
        return items
    
    async def get_crafting_recipe(self, item_id: str) -> Optional[Dict[str, Any]]:
        if not self.db.conn:
            return None
        
        cursor = await self.db.conn.execute(
            'SELECT * FROM crafting_recipes WHERE output_item = ?', (item_id,)
        )
        recipe_data = await cursor.fetchone()
        
        if not recipe_data:
            return None
        
        return {
            'recipe_id': recipe_data['recipe_id'],
            'output_item': recipe_data['output_item'],
            'ingredients': json.loads(recipe_data['ingredients']) if recipe_data['ingredients'] else {},
            'output_amount': recipe_data.get('output_amount', 1) if isinstance(recipe_data, dict) else (recipe_data[3] if len(recipe_data) > 3 else 1)
        }
    
    async def can_craft(self, user_id: int, item_id: str) -> Tuple[bool, Optional[str]]:
        recipe = await self.get_crafting_recipe(item_id)
        if not recipe:
            return False, 'No recipe found'
        
        ingredients = recipe['ingredients']
        
        for ingredient_id, required_amount in ingredients.items():
            player_amount = await self.db.get_item_count(user_id, ingredient_id)
            if player_amount < required_amount:
                return False, f'Missing {ingredient_id}'
        
        return True, None
    
    async def craft_item(self, user_id: int, item_id: str) -> Dict[str, Any]:
        can_craft, error = await self.can_craft(user_id, item_id)
        if not can_craft:
            return {'success': False, 'error': error}
        
        recipe = await self.get_crafting_recipe(item_id)
        if not recipe:
            return {'success': False, 'error': 'Recipe not found'}
        
        ingredients = recipe['ingredients']
        output_amount = recipe.get('output_amount', 1)
        
        for ingredient_id, required_amount in ingredients.items():
            await self.db.remove_item_from_inventory(user_id, ingredient_id, required_amount)
        
        await self.db.add_item_to_inventory(user_id, item_id, output_amount)
        
        return {
            'success': True,
            'item_id': item_id,
            'ingredients_used': ingredients,
            'output_amount': output_amount
        }
    
    def clear_cache(self):
        self._item_cache.clear()
        self._enchantment_cache.clear()
        self._reforge_cache.clear()
        self._pet_cache.clear()
    
    async def get_all_game_events(self):
        if not self.db.conn:
            return []
        cursor = await self.db.conn.execute('SELECT * FROM game_events')
        return await cursor.fetchall()
    
    async def get_loot_table(self, table_id: str, category: str):
        return await self.db.get_loot_table(table_id, category)
    
    async def calculate_level_from_xp(self, skill_name: str, xp: int):
        config = await self.get_skill_config(skill_name)
        if not config or not config.get('xp_requirements'):
            return 1
        xp_reqs = config['xp_requirements']
        level = 0
        sorted_levels = sorted([(int(lvl), req_xp) for lvl, req_xp in xp_reqs.items()])
        for lvl, required_xp in sorted_levels:
            if xp >= required_xp:
                level = lvl
            else:
                break
        return max(level, 0)
    
    async def get_xp_for_level(self, skill_name: str, level: int):
        config = await self.get_skill_config(skill_name)
        if not config or not config.get('xp_requirements'):
            return 0
        xp_reqs = config['xp_requirements']
        return xp_reqs.get(str(level), 0)
    
    async def get_mob_loot_table(self, mob_name: str):
        loot = await self.get_loot_table(mob_name, 'mob')
        if loot and 'loot_data' in loot:
            return loot['loot_data']
        return {}
    
    async def get_mob_loot_coins(self, mob_name: str):
        loot = await self.get_loot_table(mob_name, 'mob')
        if loot:
            return {
                'min': loot.get('coins_min', 0),
                'max': loot.get('coins_max', 0)
            }
        return {'min': 0, 'max': 0}
    
    async def get_dungeon_floor(self, floor_id: str):
        if not self.db.conn:
            return None
        cursor = await self.db.conn.execute('SELECT * FROM dungeon_floors WHERE floor_id = ?', (floor_id,))
        return await cursor.fetchone()
    
    async def get_all_fairy_soul_locations(self):
        if not self.db.conn:
            return []
        cursor = await self.db.conn.execute('SELECT location FROM fairy_soul_locations')
        rows = await cursor.fetchall()
        return [row['location'] for row in rows]
    
    async def get_collection_tier_requirements(self, item_id: str):
        if not self.db.conn:
            return []
        cursor = await self.db.conn.execute('SELECT tier, amount_required FROM collection_tiers WHERE item_id = ? ORDER BY tier', (item_id,))
        rows = await cursor.fetchall()
        return [row['amount_required'] for row in rows]
    
    async def get_item_category(self, item_id: str):
        if not self.db.conn:
            return None
        cursor = await self.db.conn.execute('SELECT category FROM collection_items WHERE item_id = ?', (item_id,))
        row = await cursor.fetchone()
        return row['category'] if row else None
    
    async def get_category_items(self, category: str):
        if not self.db.conn:
            return []
        cursor = await self.db.conn.execute('SELECT item_id FROM collection_items WHERE category = ?', (category,))
        rows = await cursor.fetchall()
        return [row['item_id'] for row in rows]
    
    async def get_collection_categories(self):
        if not self.db.conn:
            return {}
        cursor = await self.db.conn.execute('SELECT DISTINCT category FROM collection_items')
        rows = await cursor.fetchall()
        categories = {}
        for row in rows:
            categories[row['category']] = row['category'].title()
        return categories
    
    async def get_all_game_quests(self):
        if not self.db.conn:
            return []
        cursor = await self.db.conn.execute('SELECT * FROM game_quests')
        return await cursor.fetchall()
    
    async def get_game_quest(self, quest_id: str):
        if not self.db.conn:
            return None
        cursor = await self.db.conn.execute('SELECT * FROM game_quests WHERE quest_id = ?', (quest_id,))
        return await cursor.fetchone()
    
    async def get_slayer_boss(self, boss_id: str):
        if not self.db.conn:
            return None
        cursor = await self.db.conn.execute('SELECT * FROM slayer_bosses WHERE boss_id = ?', (boss_id,))
        row = await cursor.fetchone()
        if row:
            row_dict = dict(row)
            if 'tier_data' in row_dict and row_dict['tier_data']:
                row_dict['tier_data'] = json.loads(row_dict['tier_data'])
            return row_dict
        return None
    
    async def get_mobs_by_location(self, location_id: str):
        if not self.db.conn:
            return []
        cursor = await self.db.conn.execute('SELECT * FROM mob_locations WHERE location_id = ?', (location_id,))
        return await cursor.fetchall()
    
    async def get_gathering_drops(self, gathering_type: str, resource_type: str):
        return await self.db.get_gathering_drops(gathering_type, resource_type)
    
    async def get_all_seasons(self):
        if not self.db.conn:
            return []
        cursor = await self.db.conn.execute('SELECT * FROM seasons')
        return await cursor.fetchall()
    
    async def get_all_mayors(self):
        if not self.db.conn:
            return []
        cursor = await self.db.conn.execute('SELECT * FROM mayors')
        return await cursor.fetchall()
    
    async def get_minion_data(self, minion_type: str):
        if not self.db.conn:
            return None
        cursor = await self.db.conn.execute('SELECT * FROM game_minions WHERE minion_type = ?', (minion_type,))
        return await cursor.fetchone()
    
    async def get_game_pet(self, pet_id: str):
        if not self.db.conn:
            return None
        cursor = await self.db.conn.execute('SELECT * FROM game_pets WHERE pet_id = ?', (pet_id,))
        row = await cursor.fetchone()
        if row:
            row_dict = dict(row)
            if 'stats' in row_dict and row_dict['stats']:
                row_dict['stats'] = json.loads(row_dict['stats'])
            return row_dict
        return None
    
    async def get_rarity_color(self, rarity: str):
        if not self.db.conn:
            return 0x808080
        cursor = await self.db.conn.execute('SELECT color_hex FROM rarity_colors WHERE rarity = ?', (rarity,))
        row = await cursor.fetchone()
        if row and row['color_hex']:
            return int(row['color_hex'].replace('#', ''), 16)
        return 0x808080
    
    async def get_all_pet_stats(self):
        if not self.db.conn:
            return []
        cursor = await self.db.conn.execute('SELECT * FROM game_pets')
        rows = await cursor.fetchall()
        pets = []
        for row in rows:
            row_dict = dict(row)
            if 'stats' in row_dict and row_dict['stats']:
                row_dict['stats'] = json.loads(row_dict['stats'])
            pets.append(row_dict)
        return pets
    
    async def get_all_tool_tiers(self):
        if not self.db.conn:
            return {}
        cursor = await self.db.conn.execute('SELECT * FROM tool_tiers ORDER BY tool_type, tier')
        rows = await cursor.fetchall()
        tools = {}
        for row in rows:
            row_dict = dict(row)
            tool_type = row_dict['tool_type']
            if tool_type not in tools:
                tools[tool_type] = []
            if 'stats' in row_dict and row_dict['stats']:
                row_dict['stats'] = json.loads(row_dict['stats'])
            if 'recipe' in row_dict and row_dict['recipe']:
                row_dict['recipe'] = json.loads(row_dict['recipe'])
            tools[tool_type].append(row_dict)
        return tools
    
    async def get_all_crafting_recipes(self):
        if not self.db.conn:
            return {}

        cursor = await self.db.conn.execute('SELECT * FROM crafting_recipes')
        rows = await cursor.fetchall()

        recipes = {}
        for row in rows:
            row_dict = dict(row)

            if row_dict.get('ingredients'):
                try:
                    row_dict['ingredients'] = json.loads(row_dict['ingredients'])
                except Exception:
                    row_dict['ingredients'] = {}
            
            if 'output_amount' not in row_dict or row_dict['output_amount'] is None:
                row_dict['output_amount'] = 1

            recipes[row_dict['recipe_id']] = row_dict

        return recipes
    
    async def get_all_collection_tier_rewards(self):
        if not self.db.conn:
            return {}
        cursor = await self.db.conn.execute('SELECT * FROM collection_tier_rewards')
        rows = await cursor.fetchall()
        rewards = {}
        for row in rows:
            row_dict = dict(row)
            item_id = row_dict['item_id']
            if item_id not in rewards:
                rewards[item_id] = []
            if 'reward' in row_dict and row_dict['reward']:
                row_dict['reward'] = json.loads(row_dict['reward'])
            rewards[item_id].append(row_dict)
        return rewards
    
    async def get_all_collection_category_bonuses(self):
        if not self.db.conn:
            return {}
        cursor = await self.db.conn.execute('SELECT * FROM collection_category_bonuses')
        rows = await cursor.fetchall()
        bonuses = {}
        for row in rows:
            row_dict = dict(row)
            category = row_dict['category']
            if category not in bonuses:
                bonuses[category] = []
            if 'bonus' in row_dict and row_dict['bonus']:
                row_dict['bonus'] = json.loads(row_dict['bonus'])
            bonuses[category].append(row_dict)
        return bonuses
