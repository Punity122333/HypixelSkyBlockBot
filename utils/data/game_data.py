from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
import json
import random
import json

@dataclass
class Item:
    id: str
    name: str
    rarity: str
    type: str
    stats: Dict[str, int] = field(default_factory=dict)
    lore: List[str] = field(default_factory=list)
    special_ability: Optional[str] = None
    craft_recipe: Optional[Dict[str, int]] = None
    npc_sell_price: int = 0
    collection_req: Optional[Dict[str, int]] = None
    default_bazaar_price: float = 100

class GameDataManager:
    def __init__(self, db):
        self.db = db
        self._items_cache: Dict[str, Item] = {}
        self._enchants_cache: Dict[str, Dict] = {}
        self._loot_cache: Dict[Tuple[str, str], Dict] = {}
        self._skills_cache: Dict[str, Dict] = {}
        self._reforges_cache: Dict[str, Dict] = {}
        self._pets_cache: Dict[str, Dict] = {}
        self._minions_cache: Dict[str, Dict] = {}
        self._events_cache: Dict[str, Dict] = {}
        self._quests_cache: Dict[str, Dict] = {}
        self._dungeons_cache: Dict[str, Dict] = {}
        self._slayers_cache: Dict[str, Dict] = {}
        self._slayer_drops_cache: Dict[str, List[Tuple[str, int, int]]] = {}
        self._item_cache = {}
    
    async def get_item(self, item_id: str) -> Optional[Item]:
        if item_id in self._items_cache:
            return self._items_cache[item_id]
        
        item_data = await self.db.get_game_item(item_id)
        if item_data:
            item_type = item_data.get('item_type') or item_data.get('type', 'misc')
            item = Item(
                id=item_data['item_id'],
                name=item_data['name'],
                rarity=item_data['rarity'],
                type=item_type,
                stats=json.loads(item_data['stats']) if isinstance(item_data.get('stats'), str) else item_data.get('stats', {}),
                lore=item_data.get('lore', '').split('\n') if isinstance(item_data.get('lore'), str) else item_data.get('lore', []),
                special_ability=item_data.get('special_ability'),
                craft_recipe=json.loads(item_data['craft_recipe']) if isinstance(item_data.get('craft_recipe'), str) else item_data.get('craft_recipe'),
                npc_sell_price=item_data.get('npc_sell_price', 0),
                collection_req=json.loads(item_data['collection_req']) if isinstance(item_data.get('collection_req'), str) else item_data.get('collection_req'),
                default_bazaar_price=item_data.get('default_bazaar_price', 100)
            )
            self._items_cache[item_id] = item
            return item
        return None
    
    async def get_items_by_type(self, item_type: str) -> List[Item]:
        items_data = await self.db.get_items_by_type(item_type)
        items = []
        for item_data in items_data:
            item = Item(
                id=item_data['item_id'],
                name=item_data['name'],
                rarity=item_data['rarity'],
                type=item_data['type'],
                stats=item_data['stats'],
                lore=item_data['lore'],
                special_ability=item_data['special_ability'],
                craft_recipe=item_data['craft_recipe'],
                npc_sell_price=item_data['npc_sell_price'],
                collection_req=item_data['collection_req'],
                default_bazaar_price=item_data.get('default_bazaar_price', 100)
            )
            items.append(item)
            self._items_cache[item.id] = item
        return items
    
    async def get_all_items(self) -> List[Dict[str, Any]]:
        if not self.db.conn:
            return []

        rows = await self.db.get_all_game_items()
        items = []

        # rows is a dict → loop properly
        for item_id, row_dict in rows.items():

            # Ensure row_dict is actually a dict
            if not isinstance(row_dict, dict):
                try:
                    row_dict = dict(row_dict)
                except Exception:
                    continue

            # Safe JSON loader
            def safe_json(value, default):
                if not value:
                    return default
                try:
                    return json.loads(value)
                except Exception:
                    return default

            # Build normalized item
            item = {
                'item_id': item_id,
                'name': row_dict.get('name', '') or '',
                'rarity': row_dict.get('rarity', '') or '',
                'type': row_dict.get('item_type') or row_dict.get('type') or '',
                'stats': safe_json(row_dict.get('stats'), {}),
                'lore': row_dict.get('lore', '') or '',
                'special_ability': row_dict.get('special_ability', '') or '',
                'craft_recipe': safe_json(row_dict.get('craft_recipe'), {}),
                'npc_sell_price': row_dict.get('npc_sell_price', 0) or 0,
                'collection_req': safe_json(row_dict.get('collection_req'), {}),
                'default_bazaar_price': row_dict.get('default_bazaar_price', 0) or 0
            }

            # Cache it
            self._item_cache[item_id] = item
            items.append(item)

        return items



    
    async def get_enchantment(self, enchant_id: str) -> Optional[Dict]:
        if enchant_id in self._enchants_cache:
            return self._enchants_cache[enchant_id]
        
        enchant_data = await self.db.get_enchantment(enchant_id)
        if enchant_data:
            self._enchants_cache[enchant_id] = enchant_data
        return enchant_data
    
    async def get_all_enchantments(self) -> Dict[str, Dict]:
        if self._enchants_cache:
            return self._enchants_cache
        
        enchants_data = await self.db.get_all_enchantments()
        for enchant in enchants_data:
            self._enchants_cache[enchant['enchant_id']] = enchant
        return self._enchants_cache
    
    async def get_loot_table(self, table_id: str, category: str) -> Dict[str, Any]:
        cache_key = (table_id, category)
        if cache_key in self._loot_cache:
            return self._loot_cache[cache_key]
        
        loot_data = await self.db.get_loot_table(table_id, category)
        if loot_data:
            # Return the loot_data field which contains the rarity mappings
            # Plus add coins/xp metadata to the same level for compatibility
            result = loot_data.get('loot_data', {}).copy() if isinstance(loot_data.get('loot_data'), dict) else {}
            if 'coins_min' in loot_data and 'coins_max' in loot_data:
                result['coins'] = (loot_data['coins_min'], loot_data['coins_max'])
            if 'xp_reward' in loot_data:
                result['xp'] = loot_data['xp_reward']
            self._loot_cache[cache_key] = result
            return result
        return {}
    
    async def get_skill_config(self, skill_name: str) -> Optional[Dict]:
        if skill_name in self._skills_cache:
            return self._skills_cache[skill_name]
        
        skill_data = await self.db.get_skill_config(skill_name)
        if skill_data:
            self._skills_cache[skill_name] = skill_data
        return skill_data
    
    async def get_all_skill_configs(self) -> Dict[str, Dict]:
        if self._skills_cache:
            return self._skills_cache
        
        skills_data = await self.db.get_all_skill_configs()
        for skill in skills_data:
            self._skills_cache[skill['skill_name']] = skill
        return self._skills_cache
    
    async def get_reforge(self, reforge_id: str) -> Optional[Dict]:
        if reforge_id in self._reforges_cache:
            return self._reforges_cache[reforge_id]
        
        reforge_data = await self.db.get_reforge(reforge_id)
        if reforge_data:
            self._reforges_cache[reforge_id] = reforge_data
        return reforge_data
    
    async def get_all_reforges(self) -> Dict[str, Dict]:
        if self._reforges_cache:
            return self._reforges_cache
        
        reforges_data = await self.db.get_all_reforges()
        for reforge in reforges_data:
            self._reforges_cache[reforge['reforge_id']] = reforge
        return self._reforges_cache
    
    async def roll_loot(self, loot_table: Dict, magic_find: float = 0, fortune: int = 0) -> List[Tuple[str, int]]:
        drops = []
        
        rarity_chances = {
            'common': 1.0,
            'uncommon': 0.25 + (magic_find * 0.01),
            'rare': 0.05 + (magic_find * 0.005),
            'epic': 0.01 + (magic_find * 0.002),
            'legendary': 0.001 + (magic_find * 0.0005),
            'mythic': 0.0001 + (magic_find * 0.0001),
        }
        
        for rarity, chance in rarity_chances.items():
            if rarity in loot_table and random.random() < chance:
                rarity_drops = loot_table[rarity]
                if not rarity_drops:
                    continue
                chosen_drop = random.choice(rarity_drops)
                # Handle both list and tuple formats
                if isinstance(chosen_drop, (list, tuple)) and len(chosen_drop) >= 3:
                    item_id, min_amt, max_amt = chosen_drop[0], chosen_drop[1], chosen_drop[2]
                else:
                    continue
                
                amount = random.randint(min_amt, max_amt)
                fortune_bonus = int((fortune / 100) * amount)
                total_amount = amount + fortune_bonus
                
                if total_amount > 0:
                    drops.append((item_id, total_amount))
        
        if not drops and 'common' in loot_table:
            rarity_drops = loot_table['common']
            if rarity_drops:
                chosen_drop = random.choice(rarity_drops)
                # Handle both list and tuple formats
                if isinstance(chosen_drop, (list, tuple)) and len(chosen_drop) >= 3:
                    item_id, min_amt, max_amt = chosen_drop[0], chosen_drop[1], chosen_drop[2]
                    amount = random.randint(min_amt, max_amt)
                    fortune_bonus = int((fortune / 100) * amount)
                    drops.append((item_id, amount + fortune_bonus))
        
        return drops
    
    async def get_xp_for_level(self, skill_name: str, level: int) -> int:
        return await self.db.game_constants.get_xp_for_level(skill_name, level)
    
    async def calculate_level_from_xp(self, skill_name: str, xp: int) -> int:
        return await self.db.game_constants.calculate_level_from_xp(skill_name, xp)
    
    async def get_skill_stat_bonuses(self, skill_name: str, level: int) -> Dict[str, float]:
        skill_config = await self.get_skill_config(skill_name)
        if not skill_config or 'stat_bonuses' not in skill_config:
            return {}
        
        stat_bonuses = skill_config['stat_bonuses']
        return {stat: value * level for stat, value in stat_bonuses.items()}
    
    async def get_pet_stats(self, pet_type: str, rarity: str) -> Optional[Dict]:
        pet_id = f"{pet_type}_{rarity.lower()}"
        if pet_id in self._pets_cache:
            return self._pets_cache[pet_id]
        
        pet_data = await self.db.get_game_pet(pet_id)
        if pet_data:
            self._pets_cache[pet_id] = pet_data
            return pet_data
        return None
    
    async def get_all_pet_stats(self) -> Dict[str, Dict]:
        if self._pets_cache:
            return self._pets_cache
        
        pets_data = await self.db.get_all_game_pets()
        for pet in pets_data:
            self._pets_cache[pet['pet_id']] = pet
        return self._pets_cache
    
    async def get_minion_data(self, minion_type: str) -> Optional[Dict]:
        if minion_type in self._minions_cache:
            return self._minions_cache[minion_type]
        
        minion_data = await self.db.get_game_minion(minion_type)
        if minion_data:
            self._minions_cache[minion_type] = minion_data
            return minion_data
        return None
    
    async def get_all_minion_data(self) -> Dict[str, Dict]:
        if self._minions_cache:
            return self._minions_cache
        
        minions_data = await self.db.get_all_game_minions()
        for minion in minions_data:
            self._minions_cache[minion['minion_type']] = minion
        return self._minions_cache
    
    async def get_event_data(self, event_id: str) -> Optional[Dict]:
        if event_id in self._events_cache:
            return self._events_cache[event_id]
        
        event_data = await self.db.get_game_event(event_id)
        if event_data:
            self._events_cache[event_id] = event_data
            return event_data
        return None
    
    async def get_all_event_data(self) -> Dict[str, Dict]:
        if self._events_cache:
            return self._events_cache
        
        events_data = await self.db.get_all_game_events()
        for event in events_data:
            self._events_cache[event['event_id']] = event
        return self._events_cache
    
    async def get_all_game_events(self) -> List[Dict]:
        events_data = await self.db.get_all_game_events()
        return events_data
    
    async def get_quest_data(self, quest_id: str) -> Optional[Dict]:
        if quest_id in self._quests_cache:
            return self._quests_cache[quest_id]
        
        quest_data = await self.db.get_game_quest(quest_id)
        if quest_data:
            self._quests_cache[quest_id] = quest_data
            return quest_data
        return None
    
    async def get_all_quest_data(self) -> Dict[str, Dict]:
        if self._quests_cache:
            return self._quests_cache
        
        quests_data = await self.db.get_all_game_quests()
        for quest in quests_data:
            self._quests_cache[quest['quest_id']] = quest
        return self._quests_cache
    
    async def get_slayer_boss(self, boss_type: str) -> Optional[Dict]:
        if boss_type in self._slayers_cache:
            return self._slayers_cache[boss_type]
        
        slayer_data = await self.db.get_slayer_boss(boss_type)
        if slayer_data:
            self._slayers_cache[boss_type] = slayer_data
        return slayer_data
    
    async def get_slayer_drops(self, boss_type: str) -> Optional[List[Tuple[str, int, int]]]:
        if boss_type in self._slayer_drops_cache:
            return self._slayer_drops_cache[boss_type]
        
        drops_data = await self.db.get_slayer_drops(boss_type)
        if drops_data:
            self._slayer_drops_cache[boss_type] = drops_data
        return drops_data
    
    async def get_dungeon_floor(self, floor_id: str) -> Optional[Dict]:
        if floor_id in self._dungeons_cache:
            return self._dungeons_cache[floor_id]
        
        floor_data = await self.db.get_dungeon_floor(floor_id)
        if floor_data:
            self._dungeons_cache[floor_id] = floor_data
        return floor_data
    
    async def get_crafting_recipe(self, item_id: str) -> Optional[Dict]:
        # First check database for recipe with output_amount
        if self.db.conn:
            cursor = await self.db.conn.execute(
                'SELECT * FROM crafting_recipes WHERE output_item = ?', (item_id,)
            )
            recipe_data = await cursor.fetchone()
            if recipe_data:
                return {
                    'ingredients': json.loads(recipe_data['ingredients']) if recipe_data['ingredients'] else {},
                    'output_amount': recipe_data.get('output_amount', 1) if isinstance(recipe_data, dict) else (recipe_data[3] if len(recipe_data) > 3 else 1)
                }
        
        # Fallback to item's craft_recipe
        item = await self.get_item(item_id)
        if item and item.craft_recipe:
            return {'ingredients': item.craft_recipe, 'output_amount': 1}
        return None
    
    async def get_all_crafting_recipes(self) -> dict[str, dict]:
        if not self.db.conn:
            return {}

        cursor = await self.db.conn.execute('SELECT output_item, ingredients, output_amount FROM crafting_recipes')
        rows = await cursor.fetchall()
        recipes = {}

        for row in rows:
            output_item = row['output_item'] if isinstance(row, dict) else row[0]
            ingredients = row['ingredients'] if isinstance(row, dict) else row[1]
            output_amount = row['output_amount'] if isinstance(row, dict) and 'output_amount' in row else (row[2] if len(row) > 2 else 1)

            if not output_item or not ingredients:
                continue

            try:
                ingredients_dict = json.loads(ingredients)
            except Exception:
                continue

            if isinstance(ingredients_dict, dict):
                recipes[output_item] = {
                    'ingredients': ingredients_dict,
                    'output_amount': output_amount if output_amount else 1
                }

        return recipes
    
    async def get_all_tool_tiers(self) -> Dict[str, List[Dict]]:
        tool_types = {
            'pickaxe': ['wooden_pickaxe', 'stone_pickaxe', 'iron_pickaxe', 'gold_pickaxe', 'diamond_pickaxe'],
            'axe': ['wooden_axe', 'stone_axe', 'iron_axe', 'diamond_axe'],
            'hoe': ['wooden_hoe', 'stone_hoe', 'iron_hoe', 'diamond_hoe'],
            'sword': ['wooden_sword', 'stone_sword', 'iron_sword', 'diamond_sword'],
            'fishing_rod': ['wooden_fishing_rod', 'iron_fishing_rod', 'diamond_fishing_rod']
        }
        
        result = {}
        for tool_type, tier_list in tool_types.items():
            tiers = []
            for tier, item_id in enumerate(tier_list):
                tiers.append({
                    'tier': tier,
                    'item_id': item_id,
                    'name': item_id.replace('_', ' ').title()
                })
            result[tool_type] = tiers
        
        return result
    
    async def get_xp_table(self):
        # fetch all rows from the DB
        rows = await self.db.get_xp_table()  # returns list of tuples like [(item_id, base_xp), ...]
        
        # convert to dictionary
        xp_table = {item_id: base_xp for item_id, base_xp in rows}
        
        return xp_table

    
    async def get_gathering_drops(self, gathering_type: str, resource_type: str) -> List[Dict[str, Any]]:
        drops_data = await self.db.get_gathering_drops(gathering_type, resource_type)
        return drops_data
    
    async def get_all_seasons(self) -> List[str]:
        seasons_data = await self.db.get_all_seasons()
        return seasons_data
    
    async def get_all_mayors(self) -> List[Dict]:
        mayors_data = await self.db.get_all_mayors()
        return mayors_data
    
    async def get_mobs_by_location(self, location_id: str) -> List[Dict]:
        mobs_data = await self.db.get_mobs_by_location(location_id)
        return mobs_data
    
    async def get_mob_loot_table(self, mob_name: str) -> Dict[str, Any]:
        loot_table = await self.db.get_mob_loot_table(mob_name)
        return loot_table
    
    async def get_mob_loot_coins(self, mob_name: str) -> Optional[Dict[str, int]]:
        coin_data = await self.db.get_mob_loot_coins(mob_name)
        return coin_data
    
    async def get_collection_tier_requirements(self, item_id: str) -> List[int]:
        return await self.db.get_collection_tier_requirements(item_id)
    
    async def get_all_collection_tier_requirements(self) -> Dict[str, List[int]]:
        return await self.db.get_all_collection_tier_requirements()
    
    async def get_collection_tier_reward(self, tier: int) -> Optional[Dict[str, Any]]:
        return await self.db.get_collection_tier_reward(tier)
    
    async def get_all_collection_tier_rewards(self) -> Dict[int, Dict[str, Any]]:
        return await self.db.get_all_collection_tier_rewards()
    
    async def get_collection_category_bonuses(self, category: str) -> Dict[int, Dict[str, int]]:
        return await self.db.get_collection_category_bonuses(category)
    
    async def get_all_collection_category_bonuses(self) -> Dict[str, Dict[int, Dict[str, int]]]:
        return await self.db.get_all_collection_category_bonuses()
    
    async def get_collection_categories(self) -> Dict[str, List[str]]:
        return await self.db.get_collection_categories()
    
    async def get_category_items(self, category: str) -> List[str]:
        return await self.db.get_category_items(category)
    
    async def get_item_category(self, item_id: str) -> Optional[str]:
        return await self.db.get_item_category(item_id)
    
    async def get_all_fairy_soul_locations(self) -> List[str]:
        return await self.db.get_all_fairy_soul_locations()
    
    async def get_all_game_quests(self) -> List[Dict]:
        quests_data = await self.db.get_all_game_quests()
        return quests_data
    
    async def get_game_quest(self, quest_id: str) -> Optional[Dict]:
        quest_data = await self.db.get_game_quest(quest_id)
        return quest_data
    
    async def get_rarity_color(self, rarity: str) -> Optional[str]:
        return await self.db.get_rarity_color(rarity)
    
    async def get_game_pet(self, pet_id: str) -> Optional[Dict]:
        return await self.db.get_game_pet(pet_id)
    
    async def _try_drop_pet(self, mob_id: str, magic_find: float) -> Optional[Tuple[str, str]]:
        return await self.db._try_drop_pet(mob_id, magic_find)
    
    async def add_game_pet(self, pet_id: str, pet_type: str, rarity: str, stats: Dict, max_level: int, description: str):
        return await self.db.add_game_pet(pet_id, pet_type, rarity, stats, max_level, description)
    
    def clear_cache(self):
        self._items_cache.clear()
        self._enchants_cache.clear()
        self._loot_cache.clear()
        self._skills_cache.clear()
        self._reforges_cache.clear()
        self._pets_cache.clear()
        self._minions_cache.clear()
        self._events_cache.clear()
        self._quests_cache.clear()
        self._dungeons_cache.clear()
        self._slayers_cache.clear()
        self._slayer_drops_cache.clear()
