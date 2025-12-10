from typing import Dict, Any, Optional, List
import json


class HeartOfTheMountainSystem:
    
    HOTM_TIERS = {
        1: {'xp_required': 0, 'token_reward': 2},
        2: {'xp_required': 5000, 'token_reward': 2},
        3: {'xp_required': 15000, 'token_reward': 2},
        4: {'xp_required': 35000, 'token_reward': 2},
        5: {'xp_required': 70000, 'token_reward': 2},
        6: {'xp_required': 150000, 'token_reward': 2},
        7: {'xp_required': 300000, 'token_reward': 2},
        8: {'xp_required': 550000, 'token_reward': 2},
        9: {'xp_required': 1000000, 'token_reward': 2},
        10: {'xp_required': 1500000, 'token_reward': 2},
    }
    
    @classmethod
    async def get_hotm_data(cls, db, user_id: int) -> Dict[str, Any]:
        if not db.conn:
            return cls._get_default_hotm()
        
        row = await db.fetchone('SELECT * FROM player_hotm WHERE user_id = ?', (user_id,))
        if not row:
            await cls.initialize_hotm(db, user_id)
            return await cls.get_hotm_data(db, user_id)
        
        return dict(row)
    
    @classmethod
    async def initialize_hotm(cls, db, user_id: int):
        if not db.conn:
            return
        await db.execute('''
            INSERT OR IGNORE INTO player_hotm (user_id, hotm_level, hotm_xp, hotm_tier, token_of_the_mountain)
            VALUES (?, 1, 0, 1, 2)
        ''', (user_id,))
        await db.commit()
    
    @classmethod
    def _get_default_hotm(cls) -> Dict[str, Any]:
        return {
            'hotm_level': 1,
            'hotm_xp': 0,
            'hotm_tier': 1,
            'token_of_the_mountain': 2,
            'powder_mithril': 0,
            'powder_gemstone': 0,
            'powder_glacite': 0
        }
    
    @classmethod
    async def add_hotm_xp(cls, db, user_id: int, xp: int) -> Dict[str, Any]:
        hotm_data = await cls.get_hotm_data(db, user_id)
        new_xp = hotm_data['hotm_xp'] + xp
        new_tier = cls._calculate_tier_from_xp(new_xp)
        
        tokens_gained = 0
        if new_tier > hotm_data['hotm_tier']:
            for tier in range(hotm_data['hotm_tier'] + 1, new_tier + 1):
                tokens_gained += cls.HOTM_TIERS.get(tier, {}).get('token_reward', 2)
        
        await db.execute('''
            UPDATE player_hotm 
            SET hotm_xp = ?, hotm_tier = ?, token_of_the_mountain = token_of_the_mountain + ?
            WHERE user_id = ?
        ''', (new_xp, new_tier, tokens_gained, user_id))
        await db.commit()
        
        return {
            'xp_gained': xp,
            'new_xp': new_xp,
            'new_tier': new_tier,
            'tier_up': new_tier > hotm_data['hotm_tier'],
            'tokens_gained': tokens_gained
        }
    
    @classmethod
    def _calculate_tier_from_xp(cls, xp: int) -> int:
        tier = 1
        for t, data in sorted(cls.HOTM_TIERS.items()):
            if xp >= data['xp_required']:
                tier = t
            else:
                break
        return tier
    
    @classmethod
    async def unlock_perk(cls, db, user_id: int, perk_id: str) -> Dict[str, Any]:
        if not db.conn:
            return {'success': False, 'error': 'Database not connected'}
        
        perk_data = await db.fetchone('SELECT * FROM hotm_perks WHERE perk_id = ?', (perk_id,))
        if not perk_data:
            return {'success': False, 'error': 'Perk not found'}
        
        perk_data = dict(perk_data)
        
        hotm_data = await cls.get_hotm_data(db, user_id)
        
        unlock_reqs = json.loads(perk_data.get('unlock_requirements', '{}'))
        required_tier = unlock_reqs.get('hotm_tier', 1)
        
        if hotm_data['hotm_tier'] < required_tier:
            return {
                'success': False,
                'error': f'Requires HOTM Tier {required_tier}',
                'current_tier': hotm_data['hotm_tier']
            }
        
        player_perk = await db.fetchone(
            'SELECT * FROM player_hotm_perks WHERE user_id = ? AND perk_id = ?',
            (user_id, perk_id)
        )
        
        current_level = 0
        if player_perk:
            current_level = player_perk['perk_level']
        
        if current_level >= perk_data['max_level']:
            return {'success': False, 'error': 'Perk already maxed'}
        
        cost = cls._calculate_perk_cost(perk_data['cost_formula'], current_level + 1)
        
        if hotm_data['token_of_the_mountain'] < cost:
            return {
                'success': False,
                'error': f'Not enough tokens (need {cost}, have {hotm_data["token_of_the_mountain"]})',
                'cost': cost
            }
        
        new_level = current_level + 1
        
        await db.execute('''
            INSERT INTO player_hotm_perks (user_id, perk_id, perk_level)
            VALUES (?, ?, ?)
            ON CONFLICT(user_id, perk_id) DO UPDATE SET perk_level = ?
        ''', (user_id, perk_id, new_level, new_level))
        
        await db.execute('''
            UPDATE player_hotm SET token_of_the_mountain = token_of_the_mountain - ?
            WHERE user_id = ?
        ''', (cost, user_id))
        
        await db.commit()
        
        return {
            'success': True,
            'perk_name': perk_data['perk_name'],
            'new_level': new_level,
            'cost': cost,
            'remaining_tokens': hotm_data['token_of_the_mountain'] - cost
        }
    
    @classmethod
    def _calculate_perk_cost(cls, formula: str, level: int) -> int:
        if formula == 'level':
            return level
        elif formula.startswith('level'):
            try:
                multiplier = int(formula.split('*')[1].strip())
                return level * multiplier
            except:
                return level
        else:
            try:
                return int(formula)
            except:
                return 1
    
    @classmethod
    async def get_player_perks(cls, db, user_id: int) -> List[Dict[str, Any]]:
        if not db.conn:
            return []
        
        rows = await db.fetchall('''
            SELECT pp.*, hp.perk_name, hp.max_level, hp.tier, hp.description, hp.stat_bonuses
            FROM player_hotm_perks pp
            JOIN hotm_perks hp ON pp.perk_id = hp.perk_id
            WHERE pp.user_id = ?
        ''', (user_id,))
        
        return [dict(row) for row in rows]
    
    @classmethod
    async def get_available_perks(cls, db, user_id: int) -> List[Dict[str, Any]]:
        if not db.conn:
            return []
        
        hotm_data = await cls.get_hotm_data(db, user_id)
        
        rows = await db.fetchall('SELECT * FROM hotm_perks')
        
        available = []
        for row in rows:
            perk = dict(row)
            unlock_reqs = json.loads(perk.get('unlock_requirements', '{}'))
            required_tier = unlock_reqs.get('hotm_tier', 1)
            
            if hotm_data['hotm_tier'] >= required_tier:
                player_perk = await db.fetchone(
                    'SELECT perk_level FROM player_hotm_perks WHERE user_id = ? AND perk_id = ?',
                    (user_id, perk['perk_id'])
                )
                perk['current_level'] = player_perk['perk_level'] if player_perk else 0
                perk['next_cost'] = cls._calculate_perk_cost(perk['cost_formula'], perk['current_level'] + 1)
                available.append(perk)
        
        return available
    
    @classmethod
    async def calculate_hotm_stats(cls, db, user_id: int) -> Dict[str, float]:
        perks = await cls.get_player_perks(db, user_id)
        
        stats = {
            'mining_speed': 0,
            'mining_fortune': 0,
            'mining_speed_percent': 0,
            'powder_percent': 0,
            'mining_wisdom': 0,
            'titanium_chance': 0,
            'gemstone_fortune': 0,
            'orb_chance': 0,
            'daily_powder': 0,
            'strength': 0,
            'defense': 0,
            'speed': 0
        }
        
        for perk in perks:
            stat_bonuses = json.loads(perk.get('stat_bonuses', '{}'))
            for stat, bonus in stat_bonuses.items():
                if stat != 'ability':
                    stats[stat] = stats.get(stat, 0) + (bonus * perk['perk_level'])
        
        # Convert all stat values to float to match the return type
        stats = {k: float(v) for k, v in stats.items()}
        return stats
    
    @classmethod
    async def add_powder(cls, db, user_id: int, powder_type: str, amount: int):
        if not db.conn:
            return
        
        column_map = {
            'mithril': 'powder_mithril',
            'gemstone': 'powder_gemstone',
            'glacite': 'powder_glacite'
        }
        
        column = column_map.get(powder_type, 'powder_mithril')
        
        await db.execute(f'''
            UPDATE player_hotm SET {column} = {column} + ?
            WHERE user_id = ?
        ''', (amount, user_id))
        await db.commit()
