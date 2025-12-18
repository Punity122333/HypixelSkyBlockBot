from typing import Optional, Dict, List
import aiosqlite
import json

class GameConstantsDB:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.conn: Optional[aiosqlite.Connection] = None
    
    async def connect(self):
        if not self.conn:
            self.conn = await aiosqlite.connect(self.db_path)
            self.conn.row_factory = aiosqlite.Row
    
    async def get_skill_xp_requirements(self, skill: str) -> Dict[int, int]:
        if not self.conn:
            return {}
        
        skill_type = 'runecrafting' if skill == 'runecrafting' else ('social' if skill == 'social' else 'standard')
        
        cursor = await self.conn.execute(
            'SELECT level, xp_required FROM skill_xp_requirements WHERE skill_type = ? ORDER BY level',
            (skill_type,)
        )
        rows = await cursor.fetchall()
        return {row['level']: row['xp_required'] for row in rows}
    
    async def get_xp_for_level(self, skill: str, level: int) -> int:
        requirements = await self.get_skill_xp_requirements(skill)
        return requirements.get(level, 0)
    
    async def calculate_level_from_xp(self, skill: str, xp: int) -> int:
        requirements = await self.get_skill_xp_requirements(skill)
        level = 0
        for lvl, req_xp in sorted(requirements.items()):
            if xp >= req_xp:
                level = lvl
            else:
                break
        return level
    
    async def get_skill_bonuses(self, skill: str) -> Dict[str, any]:
        if not self.conn:
            return {'stat': 'none', 'per_level': 0}
        
        cursor = await self.conn.execute(
            'SELECT stat_type, per_level FROM skill_bonuses WHERE skill_name = ?',
            (skill,)
        )
        row = await cursor.fetchone()
        if row:
            return {'stat': row['stat_type'], 'per_level': row['per_level']}
        return {'stat': 'none', 'per_level': 0}
    
    async def get_skill_stat_bonus(self, skill: str, level: int) -> Dict[str, any]:
        bonus_info = await self.get_skill_bonuses(skill)
        return {
            'stat': bonus_info['stat'],
            'value': level * bonus_info['per_level']
        }
    
    async def get_dungeon_floor_requirements(self, floor_id: str) -> Optional[Dict]:
        if not self.conn:
            return None
        
        cursor = await self.conn.execute(
            'SELECT catacombs_level, gear_score FROM dungeon_floor_requirements WHERE floor_id = ?',
            (floor_id,)
        )
        row = await cursor.fetchone()
        if row:
            return {'catacombs_level': row['catacombs_level'], 'gear_score': row['gear_score']}
        return None
    
    async def get_all_dungeon_floor_requirements(self) -> Dict[str, Dict]:
        if not self.conn:
            return {}
        
        cursor = await self.conn.execute('SELECT floor_id, catacombs_level, gear_score FROM dungeon_floor_requirements')
        rows = await cursor.fetchall()
        return {row['floor_id']: {'catacombs_level': row['catacombs_level'], 'gear_score': row['gear_score']} for row in rows}
    
    async def get_dungeon_floor_difficulty(self, floor_id: str) -> int:
        if not self.conn:
            return 1
        
        cursor = await self.conn.execute(
            'SELECT difficulty FROM dungeon_floor_difficulty WHERE floor_id = ?',
            (floor_id,)
        )
        row = await cursor.fetchone()
        if row:
            return row['difficulty']
        return 1
    
    async def get_all_dungeon_floor_difficulties(self) -> Dict[str, int]:
        if not self.conn:
            return {}
        
        cursor = await self.conn.execute('SELECT floor_id, difficulty FROM dungeon_floor_difficulty')
        rows = await cursor.fetchall()
        return {row['floor_id']: row['difficulty'] for row in rows}
    
    async def get_dwarven_commission_types(self) -> Dict[str, Dict]:
        if not self.conn:
            return {}
        
        cursor = await self.conn.execute('SELECT * FROM dwarven_commission_types')
        rows = await cursor.fetchall()
        result = {}
        for row in rows:
            result[row['commission_id']] = {
                'name': row['name'],
                'description': row['description'],
                'rewards': {
                    'mithril_powder': row['mithril_powder_reward'],
                    'coins': row['coins_reward']
                },
                'amount_range': (row['amount_min'], row['amount_max'])
            }
        return result
    
    async def get_hotm_tiers(self) -> Dict[int, Dict]:
        if not self.conn:
            return {}
        
        cursor = await self.conn.execute('SELECT tier, xp_required, token_reward FROM hotm_tiers ORDER BY tier')
        rows = await cursor.fetchall()
        return {row['tier']: {'xp_required': row['xp_required'], 'token_reward': row['token_reward']} for row in rows}
    
    async def calculate_hotm_tier_from_xp(self, xp: int) -> int:
        tiers = await self.get_hotm_tiers()
        tier = 1
        for t, data in sorted(tiers.items()):
            if xp >= data['xp_required']:
                tier = t
            else:
                break
        return tier
    
    async def get_crystal_hollows_zones(self) -> Dict[str, Dict]:
        if not self.conn:
            return {}
        
        cursor = await self.conn.execute('SELECT * FROM crystal_hollows_zones')
        rows = await cursor.fetchall()
        result = {}
        for row in rows:
            result[row['zone_id']] = {
                'name': row['name'],
                'unlock_reputation': row['unlock_reputation'],
                'resources': json.loads(row['resources']),
                'mobs': json.loads(row['mobs'])
            }
        return result
    
    async def get_combat_location_unlocks(self) -> Dict[str, Dict]:
        if not self.conn:
            return {}
        
        cursor = await self.conn.execute('SELECT * FROM combat_location_unlocks')
        rows = await cursor.fetchall()
        result = {}
        for row in rows:
            result[row['location_id']] = {
                'name': row['name'],
                'min_level': row['min_level'],
                'min_coins': row['min_coins'],
                'difficulty': row['difficulty']
            }
        return result
    
    async def get_slayer_unlocks(self, slayer_type: Optional[str] = None) -> Dict:
        if not self.conn:
            return {}
        
        if slayer_type:
            cursor = await self.conn.execute(
                'SELECT * FROM slayer_unlocks WHERE slayer_type = ? ORDER BY tier',
                (slayer_type,)
            )
            rows = await cursor.fetchall()
            rows_list = list(rows)
            if not rows_list:
                return {}
            
            first_row = rows_list[0]
            result = {
                'min_combat_level': first_row['min_combat_level'],
                'min_coins': first_row['min_coins'],
                'tiers': {}
            }
            
            for row in rows_list:
                result['tiers'][row['tier']] = {
                    'cost': row['cost'],
                    'min_level': row['min_level'],
                    'xp': row['xp_reward']
                }
            
            return result
        else:
            cursor = await self.conn.execute('SELECT DISTINCT slayer_type FROM slayer_unlocks')
            slayer_types = await cursor.fetchall()
            result = {}
            for st in slayer_types:
                result[st['slayer_type']] = await self.get_slayer_unlocks(st['slayer_type'])
            return result
    
    async def get_dungeon_unlocks(self) -> Dict[str, Dict]:
        if not self.conn:
            return {}
        
        cursor = await self.conn.execute('SELECT * FROM dungeon_unlocks')
        rows = await cursor.fetchall()
        result = {}
        for row in rows:
            result[row['floor_id']] = {
                'name': row['name'],
                'min_level': row['min_level'],
                'min_coins': row['min_coins']
            }
        return result

    async def get_collection_tiers(self, collection_name: Optional[str] = None):
        if not self.conn:
            return {} if not collection_name else []
        
        if collection_name:
            cursor = await self.conn.execute(
                'SELECT tier, amount_required FROM collection_tiers WHERE collection_name = ? ORDER BY tier',
                (collection_name,)
            )
            rows = await cursor.fetchall()
            return [row['amount_required'] for row in rows]
        else:
            cursor = await self.conn.execute('SELECT collection_name, tier, amount_required FROM collection_tiers ORDER BY collection_name, tier')
            rows = await cursor.fetchall()
            result = {}
            for row in rows:
                if row['collection_name'] not in result:
                    result[row['collection_name']] = []
                result[row['collection_name']].append(row['amount_required'])
            return result
    
    async def get_collection_tier_for_amount(self, collection_name: str, amount: int) -> int:
        tiers = await self.get_collection_tiers(collection_name)
        if not tiers:
            return 0
        tier = 0
        for i, requirement in enumerate(tiers):
            if amount >= requirement:
                tier = i + 1
            else:
                break
        return tier
    
    async def get_party_dungeon_floors(self) -> Dict[int, Dict]:
        if not self.conn:
            return {}
        
        cursor = await self.conn.execute('SELECT * FROM party_dungeon_floors ORDER BY floor_number')
        rows = await cursor.fetchall()
        return {
            row['floor_number']: {
                'name': row['name'],
                'min_level': row['min_level'],
                'recommended_level': row['recommended_level'],
                'gear_score': row['gear_score']
            }
            for row in rows
        }
    
    async def get_dungeon_classes(self) -> List[str]:
        if not self.conn:
            return []
        
        cursor = await self.conn.execute('SELECT class_name FROM dungeon_classes ORDER BY display_order')
        rows = await cursor.fetchall()
        return [row['class_name'] for row in rows]
    
    async def get_gathering_requirements(self) -> Dict[str, Dict]:
        if not self.conn:
            return {}
        
        cursor = await self.conn.execute('SELECT * FROM gathering_requirements')
        rows = await cursor.fetchall()
        return {
            row['activity']: {
                'min_level': row['min_level'],
                'required_tool': row['required_tool']
            }
            for row in rows
        }
    
    async def get_gathering_categories(self) -> Dict[str, List[str]]:
        if not self.conn:
            return {}
        
        cursor = await self.conn.execute('SELECT category, tool_types FROM gathering_categories')
        rows = await cursor.fetchall()
        return {row['category']: json.loads(row['tool_types']) for row in rows}
    
    async def get_potion_effect(self, potion_id: str) -> Optional[Dict]:
        if not self.conn:
            return None
        
        cursor = await self.conn.execute(
            'SELECT * FROM potion_effects WHERE potion_id = ?',
            (potion_id,)
        )
        row = await cursor.fetchone()
        if not row:
            return None
        
        result = {
            'effect_type': row['effect_type'],
            'stat_name': row['stat_name'],
            'amount': row['amount'],
            'duration': row['duration']
        }
        
        if row['special_effects']:
            result['special_effects'] = json.loads(row['special_effects'])
        
        if row['effect_type'] == 'instant_heal':
            result['type'] = 'instant_heal'
        elif row['effect_type'] == 'god':
            result['type'] = 'god'
            result['effects'] = result.get('special_effects', {})
        elif row['effect_type'] == 'stat_boost':
            result['stat'] = row['stat_name']
        
        return result
    
    async def get_all_potion_effects(self) -> Dict[str, Dict]:
        if not self.conn:
            return {}
        
        cursor = await self.conn.execute('SELECT potion_id FROM potion_effects')
        rows = await cursor.fetchall()
        result = {}
        for row in rows:
            potion_data = await self.get_potion_effect(row['potion_id'])
            if potion_data:
                result[row['potion_id']] = potion_data
        return result
