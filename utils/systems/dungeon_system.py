import random
import json
from typing import Dict, List, Optional, Any, Tuple
from ..stat_calculator import StatCalculator
from .combat_system import CombatSystem


class DungeonSystem:
    
    DUNGEON_CLASSES = ['healer', 'mage', 'berserk', 'archer', 'tank']
    
    FLOOR_REQUIREMENTS = {
        'entrance': {'level': 0, 'gear_score': 0},
        'floor1': {'level': 5, 'gear_score': 50},
        'floor2': {'level': 10, 'gear_score': 100},
        'floor3': {'level': 15, 'gear_score': 150},
        'floor4': {'level': 20, 'gear_score': 250},
        'floor5': {'level': 25, 'gear_score': 400},
        'floor6': {'level': 30, 'gear_score': 600},
        'floor7': {'level': 35, 'gear_score': 900},
    }
    
    @classmethod
    async def can_enter_floor(cls, db, user_id: int, floor_id: str) -> Tuple[bool, str]:
        if floor_id not in cls.FLOOR_REQUIREMENTS:
            return False, 'Invalid floor'
        
        requirements = cls.FLOOR_REQUIREMENTS[floor_id]
        
        player = await db.get_player(user_id)
        if not player:
            return False, 'Player not found'
        
        player_level = player.get('level', 1)
        if player_level < requirements['level']:
            return False, f"Level {requirements['level']} required"
        
        gear_score = await cls.calculate_gear_score(db, user_id)
        if gear_score < requirements['gear_score']:
            return False, f"Gear score {requirements['gear_score']} required"
        
        return True, 'OK'
    
    @classmethod
    async def calculate_gear_score(cls, db, user_id: int) -> int:
        inventory = await db.get_inventory(user_id)
        total_score = 0
        
        for item_row in inventory:
            if item_row.get('equipped') == 1:
                item_id = item_row['item_id']
                
                if not db.conn:
                    continue
                
                cursor = await db.conn.execute('''
                    SELECT * FROM game_items WHERE item_id = ?
                ''', (item_id,))
                item_data = await cursor.fetchone()
                
                if not item_data:
                    continue
                
                rarity = item_data['rarity']
                rarity_score = {
                    'COMMON': 5,
                    'UNCOMMON': 10,
                    'RARE': 25,
                    'EPIC': 50,
                    'LEGENDARY': 100,
                    'MYTHIC': 200
                }
                
                item_score = rarity_score.get(rarity, 5)
                
                stars = item_row.get('stars', 0)
                item_score += stars * 10
                
                total_score += item_score
        
        return total_score
    
    @classmethod
    async def start_dungeon_run(cls, db, user_id: int, floor_id: str, 
                               dungeon_class: str = 'berserk') -> Dict[str, Any]:
        can_enter, reason = await cls.can_enter_floor(db, user_id, floor_id)
        if not can_enter:
            return {
                'success': False,
                'error': reason
            }
        
        if dungeon_class not in cls.DUNGEON_CLASSES:
            return {
                'success': False,
                'error': 'Invalid class'
            }
        
        if not db.conn:
            return {'success': False, 'error': 'Database not connected'}
        
        cursor = await db.conn.execute('''
            SELECT * FROM dungeon_floors WHERE floor_id = ?
        ''', (floor_id,))
        floor_data = await cursor.fetchone()
        
        if not floor_data:
            return {'success': False, 'error': 'Floor not found'}
        
        rooms = cls._generate_dungeon_rooms(floor_id)
        
        return {
            'success': True,
            'floor_id': floor_id,
            'dungeon_class': dungeon_class,
            'rooms': rooms,
            'time_limit': floor_data['time'],
            'expected_rewards': floor_data['rewards']
        }
    
    @classmethod
    def _generate_dungeon_rooms(cls, floor_id: str) -> List[Dict[str, Any]]:
        base_difficulty = {
            'entrance': 1,
            'floor1': 2,
            'floor2': 3,
            'floor3': 5,
            'floor4': 7,
            'floor5': 10,
            'floor6': 15,
            'floor7': 20
        }
        
        difficulty = base_difficulty.get(floor_id, 1)
        num_rooms = 5 + (difficulty * 2)
        
        rooms = []
        
        for i in range(num_rooms):
            room_type = random.choice(['mob', 'puzzle', 'trap', 'miniboss'])
            
            if i == num_rooms - 1:
                room_type = 'boss'
            
            room = {
                'room_id': i,
                'type': room_type,
                'difficulty': difficulty,
                'cleared': False
            }
            
            if room_type in ['mob', 'miniboss', 'boss']:
                room['mobs'] = cls._generate_room_mobs(room_type, difficulty)
            elif room_type == 'puzzle':
                room['puzzle_type'] = random.choice(['lever', 'quiz', 'parkour'])
            
            rooms.append(room)
        
        return rooms
    
    @classmethod
    def _generate_room_mobs(cls, room_type: str, difficulty: int) -> List[Dict[str, Any]]:
        mob_count = {
            'mob': random.randint(3, 6),
            'miniboss': 1,
            'boss': 1
        }
        
        count = mob_count.get(room_type, 3)
        mobs = []
        
        for i in range(count):
            health_multiplier = {
                'mob': 1.0,
                'miniboss': 5.0,
                'boss': 20.0
            }
            
            base_health = 100 * difficulty
            mob_health = int(base_health * health_multiplier.get(room_type, 1.0))
            
            mob = {
                'mob_id': f'{room_type}_{i}',
                'health': mob_health,
                'damage': 10 * difficulty,
                'alive': True
            }
            
            mobs.append(mob)
        
        return mobs
    
    @classmethod
    async def clear_room(cls, db, user_id: int, room: Dict[str, Any]) -> Dict[str, Any]:
        room_type = room['type']
        
        if room_type in ['mob', 'miniboss', 'boss']:
            return await cls._clear_combat_room(db, user_id, room)
        elif room_type == 'puzzle':
            return await cls._clear_puzzle_room(db, user_id, room)
        elif room_type == 'trap':
            return await cls._clear_trap_room(db, user_id, room)
        
        return {'success': False, 'error': 'Unknown room type'}
    
    @classmethod
    async def _clear_combat_room(cls, db, user_id: int, room: Dict[str, Any]) -> Dict[str, Any]:
        mobs = room.get('mobs', [])
        
        combat_log = []
        total_damage_dealt = 0
        total_damage_taken = 0
        
        stats = await StatCalculator.calculate_full_stats(db, user_id)
        player_health = stats['health']
        
        for mob in mobs:
            if not mob['alive']:
                continue
            
            mob_health = mob['health']
            mob_damage = mob['damage']
            
            while mob_health > 0 and player_health > 0:
                damage_result = await CombatSystem.calculate_player_damage(db, user_id, 0)
                damage = damage_result['damage']
                
                mob_health -= damage
                total_damage_dealt += damage
                
                combat_log.append({
                    'actor': 'player',
                    'target': mob['mob_id'],
                    'damage': damage,
                    'is_crit': damage_result['is_crit']
                })
                
                if mob_health <= 0:
                    mob['alive'] = False
                    break
                
                player_dmg = CombatSystem._calculate_mob_damage(mob_damage, stats['defense'])
                player_health -= player_dmg
                total_damage_taken += player_dmg
                
                combat_log.append({
                    'actor': mob['mob_id'],
                    'target': 'player',
                    'damage': player_dmg
                })
        
        all_dead = all(not mob['alive'] for mob in mobs)
        
        return {
            'success': all_dead,
            'player_survived': player_health > 0,
            'combat_log': combat_log,
            'total_damage_dealt': total_damage_dealt,
            'total_damage_taken': total_damage_taken,
            'final_player_health': max(0, player_health)
        }
    
    @classmethod
    async def _clear_puzzle_room(cls, db, user_id: int, room: Dict[str, Any]) -> Dict[str, Any]:
        puzzle_type = room.get('puzzle_type', 'lever')
        
        success_chance = 0.8
        success = random.random() < success_chance
        
        return {
            'success': success,
            'puzzle_type': puzzle_type
        }
    
    @classmethod
    async def _clear_trap_room(cls, db, user_id: int, room: Dict[str, Any]) -> Dict[str, Any]:
        stats = await StatCalculator.calculate_full_stats(db, user_id)
        
        trap_damage = room['difficulty'] * 50
        damage_taken = CombatSystem._calculate_mob_damage(trap_damage, stats['defense'])
        
        return {
            'success': True,
            'damage_taken': damage_taken
        }
    
    @classmethod
    async def complete_dungeon(cls, db, user_id: int, floor_id: str, 
                              score: int, time_taken: int) -> Dict[str, Any]:
        if not db.conn:
            return {'success': False, 'error': 'Database not connected'}
        
        cursor = await db.conn.execute('''
            SELECT * FROM dungeon_floors WHERE floor_id = ?
        ''', (floor_id,))
        floor_data = await cursor.fetchone()
        
        if not floor_data:
            return {'success': False, 'error': 'Floor not found'}
        
        base_rewards = floor_data['rewards']
        
        score_multiplier = 1.0 + (score / 1000)
        time_multiplier = 1.0 if time_taken < floor_data['time'] else 0.8
        
        coins = int(base_rewards * score_multiplier * time_multiplier)
        xp = int(coins / 10)
        
        drops = await cls._generate_dungeon_loot(db, floor_id, score_multiplier)
        
        return {
            'success': True,
            'floor_id': floor_id,
            'score': score,
            'time_taken': time_taken,
            'rewards': {
                'coins': coins,
                'xp': xp,
                'drops': drops
            }
        }
    
    @classmethod
    async def _generate_dungeon_loot(cls, db, floor_id: str, multiplier: float) -> List[Dict[str, Any]]:
        if not db.conn:
            return []
        
        cursor = await db.conn.execute('''
            SELECT * FROM loot_tables WHERE table_id = ? AND category = 'dungeon'
        ''', (floor_id,))
        loot_tables = await cursor.fetchall()
        
        drops = []
        
        for loot_table in loot_tables:
            rarity = loot_table['rarity']
            loot_data = json.loads(loot_table['loot_data']) if loot_table['loot_data'] else []
            
            rarity_chance = {
                'common': 0.5,
                'uncommon': 0.3,
                'rare': 0.15,
                'epic': 0.04,
                'legendary': 0.01
            }
            
            base_chance = rarity_chance.get(rarity.lower(), 0.3)
            actual_chance = base_chance * multiplier
            
            if random.random() < actual_chance:
                for item_entry in loot_data:
                    if isinstance(item_entry, dict):
                        drops.append({
                            'item_id': item_entry.get('item_id'),
                            'amount': item_entry.get('amount', 1),
                            'rarity': rarity
                        })
        
        return drops
    
    @classmethod
    async def get_class_level(cls, db, user_id: int, dungeon_class: str) -> int:
        player = await db.get_player(user_id)
        if not player:
            return 0
        
        return player.get(f'{dungeon_class}_level', 0)
    
    @classmethod
    async def add_class_xp(cls, db, user_id: int, dungeon_class: str, xp: int):
        current_level = await cls.get_class_level(db, user_id, dungeon_class)
        await db.update_player(user_id, **{f'{dungeon_class}_level': current_level})
