from discord import app_commands
import time
from typing import Dict, List, Optional, Callable, Any, Tuple


class TrieNode:
    __slots__ = ("children", "items")
    def __init__(self):
        self.children: Dict[str, 'TrieNode'] = {}
        self.items: List[str] = []


class Trie:
    def __init__(self):
        self.root = TrieNode()

    def insert(self, key: str, item_id: str):
        node = self.root
        for ch in key:
            if ch not in node.children:
                node.children[ch] = TrieNode()
            node = node.children[ch]
        node.items.append(item_id)

    def search_prefix(self, prefix: str) -> List[str]:
        node = self.root
        for ch in prefix:
            if ch not in node.children:
                return []
            node = node.children[ch]
        stack = [node]
        out = []
        while stack:
            n = stack.pop()
            out.extend(n.items)
            for child in n.children.values():
                stack.append(child)
        return out


class GlobalAutocomplete:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        
        self._data: Dict[str, Tuple[Optional[Trie], Dict[str, str], float, Callable[[Any], Any]]] = {}
        
        self._cache_ttl = 30
        
        self._data['items'] = (None, {}, 0, self._fetch_items)
        self._data['recipes'] = (None, {}, 0, self._fetch_recipes)
        self._data['pets'] = (None, {}, 0, self._fetch_pets)
        self._data['mobs'] = (None, {}, 0, self._fetch_mobs)
        self._data['locations'] = (None, {}, 0, self._fetch_locations)

    async def _fetch_items(self, bot) -> Dict[str, str]:
        all_items = await bot.game_data.get_all_items()
        if not all_items:
            return {}
        
        items_dict = {}
        if isinstance(all_items, list):
            for item in all_items:
                if isinstance(item, dict):
                    item_id = item.get('item_id') or item.get('id')
                    if item_id:
                        items_dict[item_id] = item
            all_items = items_dict
        
        out = {}
        for item_id, item_data in all_items.items():
            if isinstance(item_data, dict):
                name = item_data.get('name', item_id.replace('_', ' ').title())
            else:
                name = getattr(item_data, 'name', None) or item_id.replace('_', ' ').title()
            out[item_id] = name
        return out
    
    async def _fetch_recipes(self, bot) -> Dict[str, str]:
        all_recipes = await bot.game_data.get_all_crafting_recipes()
        if not all_recipes:
            return {}
        
        out = {}
        for recipe_id in all_recipes.keys():
            try:
                obj = await bot.game_data.get_item(recipe_id)
                name = obj.name if obj and getattr(obj, 'name', None) else recipe_id.replace('_', ' ').title()
            except:
                name = recipe_id.replace('_', ' ').title()
            out[recipe_id] = name
        return out
    
    async def _fetch_pets(self, bot) -> Dict[str, str]:
        all_pets = await bot.db.get_all_game_pets()
        if not all_pets:
            return {}
        
        out = {}
        for pet in all_pets:
            if isinstance(pet, dict):
                pet_id = pet.get('pet_id') or pet.get('pet_type')
                name = pet.get('name', pet_id.replace('_', ' ').title() if pet_id else 'Unknown')
            else:
                pet_id = getattr(pet, 'pet_id', None) or getattr(pet, 'pet_type', None)
                name = getattr(pet, 'name', pet_id.replace('_', ' ').title() if pet_id else 'Unknown')
            
            if pet_id:
                out[pet_id] = name
        return out
    
    async def _fetch_mobs(self, bot) -> Dict[str, str]:
        locations = ['hub', 'forest', 'deep_caverns', 'spiders_den', 'blazing_fortress', 
                     'end', 'crimson_isle', 'park', 'mushroom_desert', 'dungeon_hub']
        
        out = {}
        for loc in locations:
            try:
                mobs = await bot.db.get_mobs_by_location(loc)
                if mobs:
                    for mob in mobs:
                        if isinstance(mob, dict):
                            mob_id = mob.get('mob_id')
                            name = mob.get('mob_name', mob_id.replace('_', ' ').title() if mob_id else 'Unknown')
                        else:
                            mob_id = getattr(mob, 'mob_id', None)
                            name = getattr(mob, 'mob_name', mob_id.replace('_', ' ').title() if mob_id else 'Unknown')
                        
                        if mob_id and mob_id not in out:
                            out[mob_id] = name
            except:
                pass
        return out
    
    async def _fetch_locations(self, bot) -> Dict[str, str]:
        locations_data = {
            'hub': 'Hub',
            'forest': 'Forest',
            'birch_park': 'Birch Park',
            'deep_caverns': 'Deep Caverns',
            'spiders_den': "Spider's Den",
            'blazing_fortress': 'Blazing Fortress',
            'end': 'The End',
            'crimson_isle': 'Crimson Isle',
            'park': 'Park',
            'mushroom_desert': 'Mushroom Desert',
            'dungeon_hub': 'Dungeon Hub',
            'gold_mine': 'Gold Mine',
            'coal_mine': 'Coal Mine',
            'dwarven_mines': 'Dwarven Mines',
            'crystal_hollows': 'Crystal Hollows',
            'garden': 'Garden',
            'rift': 'The Rift',
            'jerry_island': "Jerry's Island",
        }
        return locations_data
    
    async def _build_trie(self, bot, data_key: str) -> None:
        trie, names, _, fetch_func = self._data[data_key]
        
        new_names = await fetch_func(bot)
        new_trie = Trie()
        
        for item_id, name in new_names.items():
            new_trie.insert(name.lower(), item_id)
            new_trie.insert(item_id.lower(), item_id)
        
        self._data[data_key] = (new_trie, new_names, time.time(), fetch_func)
    
    def _search_and_format(self, query: str, data_key: str, limit: int = 25) -> List[app_commands.Choice]:
        trie, names, _, _ = self._data[data_key]
        
        q = (query or "").strip().lower()
        
        if not trie or not names:
            return []
        
        if not q:

            out = list(names.keys())[:limit]
            out.sort(key=lambda x: names[x].lower())
            return [app_commands.Choice(name=names[x][:100], value=x) for x in out]

        unique_ids = set(trie.search_prefix(q))

        for item_id, name in names.items():
            if item_id not in unique_ids and (q in item_id.lower() or q in name.lower()):
                unique_ids.add(item_id)

        from_prefix = list(unique_ids)
        
        from_prefix.sort(key=lambda x: names[x].lower())
        from_prefix = from_prefix[:limit]

        return [app_commands.Choice(name=names[x][:100], value=x) for x in from_prefix]
    
    async def _autocomplete_handler(self, bot, current: str, data_key: str) -> List[app_commands.Choice]:
        now = time.time()
        trie, _, cache_ts, _ = self._data[data_key]
        
        if not trie or now - cache_ts > self._cache_ttl:
            await self._build_trie(bot, data_key)
        
        return self._search_and_format(current, data_key)

    async def items_autocomplete(self, bot, current: str) -> List[app_commands.Choice]:
        return await self._autocomplete_handler(bot, current, 'items')
    
    async def recipes_autocomplete(self, bot, current: str) -> List[app_commands.Choice]:
        return await self._autocomplete_handler(bot, current, 'recipes')
    
    async def pets_autocomplete(self, bot, current: str) -> List[app_commands.Choice]:
        return await self._autocomplete_handler(bot, current, 'pets')
    
    async def mobs_autocomplete(self, bot, current: str) -> List[app_commands.Choice]:
        return await self._autocomplete_handler(bot, current, 'mobs')
    
    async def locations_autocomplete(self, bot, current: str) -> List[app_commands.Choice]:
        return await self._autocomplete_handler(bot, current, 'locations')


_global_autocomplete = GlobalAutocomplete()


async def item_autocomplete(interaction, current: str) -> List[app_commands.Choice]:
    return await _global_autocomplete.items_autocomplete(interaction.client, current)


async def recipe_autocomplete(interaction, current: str) -> List[app_commands.Choice]:
    return await _global_autocomplete.recipes_autocomplete(interaction.client, current)


async def pet_autocomplete(interaction, current: str) -> List[app_commands.Choice]:
    return await _global_autocomplete.pets_autocomplete(interaction.client, current)


async def mob_autocomplete(interaction, current: str) -> List[app_commands.Choice]:
    return await _global_autocomplete.mobs_autocomplete(interaction.client, current)


async def location_autocomplete(interaction, current: str) -> List[app_commands.Choice]:
    return await _global_autocomplete.locations_autocomplete(interaction.client, current)