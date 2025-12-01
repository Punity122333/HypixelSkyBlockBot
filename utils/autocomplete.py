from discord import app_commands
import time
from typing import Dict, List, Optional, Callable, Any


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
        
        self._items_trie: Optional[Trie] = None
        self._items_names: Dict[str, str] = {}
        self._items_cache_ts: float = 0
        
        self._recipes_trie: Optional[Trie] = None
        self._recipes_names: Dict[str, str] = {}
        self._recipes_cache_ts: float = 0
        
        self._pets_trie: Optional[Trie] = None
        self._pets_names: Dict[str, str] = {}
        self._pets_cache_ts: float = 0
        
        self._mobs_trie: Optional[Trie] = None
        self._mobs_names: Dict[str, str] = {}
        self._mobs_cache_ts: float = 0
        
        self._locations_trie: Optional[Trie] = None
        self._locations_names: Dict[str, str] = {}
        self._locations_cache_ts: float = 0
        
        self._cache_ttl = 30
    
    async def _build_items_trie(self, bot) -> None:
        all_items = await bot.game_data.get_all_items()
        if not all_items:
            all_items = {}
        if isinstance(all_items, list):
            items_dict = {}
            for item in all_items:
                if isinstance(item, dict):
                    item_id = item.get('item_id') or item.get('id')
                    if item_id:
                        items_dict[item_id] = item
            all_items = items_dict
        
        self._items_trie = Trie()
        self._items_names = {}
        
        for item_id, item_data in all_items.items():
            if isinstance(item_data, dict):
                name = item_data.get('name', item_id.replace('_', ' ').title())
            else:
                name = getattr(item_data, 'name', None) or item_id.replace('_', ' ').title()
            
            self._items_names[item_id] = name
            self._items_trie.insert(name.lower(), item_id)
            self._items_trie.insert(item_id.lower(), item_id)
        
        self._items_cache_ts = time.time()
    
    async def _build_recipes_trie(self, bot) -> None:
        all_recipes = await bot.game_data.get_all_crafting_recipes()
        if not all_recipes:
            all_recipes = {}
        
        self._recipes_trie = Trie()
        self._recipes_names = {}
        
        for recipe_id in all_recipes.keys():
            try:
                obj = await bot.game_data.get_item(recipe_id)
                name = obj.name if obj and getattr(obj, 'name', None) else recipe_id.replace('_', ' ').title()
            except:
                name = recipe_id.replace('_', ' ').title()
            
            self._recipes_names[recipe_id] = name
            self._recipes_trie.insert(name.lower(), recipe_id)
            self._recipes_trie.insert(recipe_id.lower(), recipe_id)
        
        self._recipes_cache_ts = time.time()
    
    async def _build_pets_trie(self, bot) -> None:
        all_pets = await bot.db.get_all_game_pets()
        if not all_pets:
            all_pets = []
        
        self._pets_trie = Trie()
        self._pets_names = {}
        
        for pet in all_pets:
            if isinstance(pet, dict):
                pet_id = pet.get('pet_id') or pet.get('pet_type')
                name = pet.get('name', pet_id.replace('_', ' ').title() if pet_id else 'Unknown')
            else:
                pet_id = getattr(pet, 'pet_id', None) or getattr(pet, 'pet_type', None)
                name = getattr(pet, 'name', pet_id.replace('_', ' ').title() if pet_id else 'Unknown')
            
            if pet_id:
                self._pets_names[pet_id] = name
                self._pets_trie.insert(name.lower(), pet_id)
                self._pets_trie.insert(pet_id.lower(), pet_id)
        
        self._pets_cache_ts = time.time()
    
    async def _build_mobs_trie(self, bot) -> None:
        locations = ['hub', 'forest', 'deep_caverns', 'spiders_den', 'blazing_fortress', 
                     'end', 'crimson_isle', 'park', 'mushroom_desert', 'dungeon_hub']
        
        self._mobs_trie = Trie()
        self._mobs_names = {}
        
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
                        
                        if mob_id and mob_id not in self._mobs_names:
                            self._mobs_names[mob_id] = name
                            self._mobs_trie.insert(name.lower(), mob_id)
                            self._mobs_trie.insert(mob_id.lower(), mob_id)
            except:
                pass
        
        self._mobs_cache_ts = time.time()
    
    async def _build_locations_trie(self, bot) -> None:
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
        
        self._locations_trie = Trie()
        self._locations_names = {}
        
        for loc_id, name in locations_data.items():
            self._locations_names[loc_id] = name
            self._locations_trie.insert(name.lower(), loc_id)
            self._locations_trie.insert(loc_id.lower(), loc_id)
        
        self._locations_cache_ts = time.time()
    
    def _search_and_format(self, query: str, trie: Optional[Trie], names: Dict[str, str], limit: int = 25) -> List[app_commands.Choice]:
        q = (query or "").strip().lower()
        
        if not trie or not names:
            return []
        
        if not q:
            out = list(names.keys())[:limit]
            out = sorted(out, key=lambda x: names[x].lower())
            return [app_commands.Choice(name=names[x][:100], value=x) for x in out]
        
        from_prefix = trie.search_prefix(q)
        seen = set(from_prefix)
        
        partial = [x for x in names if q in x.lower() or q in names[x].lower()]
        for x in partial:
            if x not in seen:
                from_prefix.append(x)
        
        from_prefix.sort(key=lambda x: names[x].lower())
        from_prefix = from_prefix[:limit]
        
        return [app_commands.Choice(name=names[x][:100], value=x) for x in from_prefix]
    
    async def items_autocomplete(self, bot, current: str) -> List[app_commands.Choice]:
        now = time.time()
        if not self._items_trie or now - self._items_cache_ts > self._cache_ttl:
            await self._build_items_trie(bot)
        
        return self._search_and_format(current, self._items_trie, self._items_names)
    
    async def recipes_autocomplete(self, bot, current: str) -> List[app_commands.Choice]:
        now = time.time()
        if not self._recipes_trie or now - self._recipes_cache_ts > self._cache_ttl:
            await self._build_recipes_trie(bot)
        
        return self._search_and_format(current, self._recipes_trie, self._recipes_names)
    
    async def pets_autocomplete(self, bot, current: str) -> List[app_commands.Choice]:
        now = time.time()
        if not self._pets_trie or now - self._pets_cache_ts > self._cache_ttl:
            await self._build_pets_trie(bot)
        
        return self._search_and_format(current, self._pets_trie, self._pets_names)
    
    async def mobs_autocomplete(self, bot, current: str) -> List[app_commands.Choice]:
        now = time.time()
        if not self._mobs_trie or now - self._mobs_cache_ts > self._cache_ttl:
            await self._build_mobs_trie(bot)
        
        return self._search_and_format(current, self._mobs_trie, self._mobs_names)
    
    async def locations_autocomplete(self, bot, current: str) -> List[app_commands.Choice]:
        now = time.time()
        if not self._locations_trie or now - self._locations_cache_ts > self._cache_ttl:
            await self._build_locations_trie(bot)
        
        return self._search_and_format(current, self._locations_trie, self._locations_names)


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
