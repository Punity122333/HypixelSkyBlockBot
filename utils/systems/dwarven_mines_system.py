from typing import Dict, Any, List, Optional
import random
import time


class DwarvenMinesSystem:
    
    COMMISSION_TYPES = {
        'mithril_mining': {
            'name': 'Mithril Miner',
            'description': 'Mine {amount} Mithril',
            'rewards': {'mithril_powder': 500, 'coins': 2000},
            'amount_range': (100, 250)
        },
        'titanium_mining': {
            'name': 'Titanium Collector',
            'description': 'Mine {amount} Titanium',
            'rewards': {'mithril_powder': 800, 'coins': 3500},
            'amount_range': (50, 100)
        },
        'goblin_slayer': {
            'name': 'Goblin Slayer',
            'description': 'Kill {amount} Goblins',
            'rewards': {'mithril_powder': 400, 'coins': 1500},
            'amount_range': (30, 60)
        },
        'hard_stone_mining': {
            'name': 'Hard Stone Miner',
            'description': 'Mine {amount} Hard Stone',
            'rewards': {'mithril_powder': 300, 'coins': 1000},
            'amount_range': (200, 400)
        },
        'treasure_hunter': {
            'name': 'Treasure Hunter',
            'description': 'Find {amount} Treasures',
            'rewards': {'mithril_powder': 600, 'coins': 2500},
            'amount_range': (5, 15)
        },
        'lapis_mining': {
            'name': 'Lapis Collector',
            'description': 'Mine {amount} Lapis',
            'rewards': {'mithril_powder': 350, 'coins': 1200},
            'amount_range': (150, 300)
        },
        'redstone_mining': {
            'name': 'Redstone Collector',
            'description': 'Mine {amount} Redstone',
            'rewards': {'mithril_powder': 350, 'coins': 1200},
            'amount_range': (150, 300)
        }
    }
    
    @classmethod
    async def get_dwarven_progress(cls, db, user_id: int) -> Dict[str, Any]:
        if not db.conn:
            return cls._get_default_progress()
        
        progress = await db.dwarven_mines.get_dwarven_progress(user_id)
        if not progress:
            await db.dwarven_mines.initialize_dwarven_progress(user_id)
            return await cls.get_dwarven_progress(db, user_id)
        
        return progress
    
    @classmethod
    async def initialize_dwarven_progress(cls, db, user_id: int):
        if not db.conn:
            return
        await db.dwarven_mines.initialize_dwarven_progress(user_id)
    
    @classmethod
    def _get_default_progress(cls) -> Dict[str, Any]:
        return {
            'commissions_completed': 0,
            'reputation': 0,
            'king_yolkar_unlocked': 0,
            'mithril_unlocked': 1,
            'titanium_unlocked': 0
        }
    
    @classmethod
    async def generate_daily_commissions(cls, db, user_id: int) -> List[Dict[str, Any]]:
        if not db.conn:
            return []
        
        await db.dwarven_mines.clear_incomplete_commissions(user_id)
        
        commission_count = 4
        available_types = list(cls.COMMISSION_TYPES.keys())
        selected_types = random.sample(available_types, min(commission_count, len(available_types)))
        
        commissions = []
        expires_at = int(time.time()) + 86400
        
        for comm_type in selected_types:
            comm_data = cls.COMMISSION_TYPES[comm_type]
            requirement = random.randint(*comm_data['amount_range'])
            
            await db.dwarven_mines.create_commission(
                user_id,
                comm_type,
                requirement,
                comm_data['rewards'].get('mithril_powder', 0),
                comm_data['rewards'].get('coins', 0),
                expires_at
            )
            
            commissions.append({
                'type': comm_type,
                'name': comm_data['name'],
                'description': comm_data['description'].format(amount=requirement),
                'requirement': requirement,
                'progress': 0,
                'rewards': comm_data['rewards']
            })
        
        return commissions
    
    @classmethod
    async def get_active_commissions(cls, db, user_id: int) -> List[Dict[str, Any]]:
        if not db.conn:
            return []
        
        rows = await db.dwarven_mines.get_active_commissions(user_id)
        
        commissions = []
        for row in rows:
            comm_data = cls.COMMISSION_TYPES.get(row['commission_type'], {})
            row['name'] = comm_data.get('name', 'Unknown')
            row['description'] = comm_data.get('description', '').format(amount=row['requirement'])
            commissions.append(row)
        
        return commissions
    
    @classmethod
    async def update_commission_progress(cls, db, user_id: int, commission_type: str, amount: int) -> Dict[str, Any]:
        if not db.conn:
            return {'success': False}
        
        commission = await db.dwarven_mines.get_commission_by_type(user_id, commission_type)
        
        if not commission:
            return {'success': False, 'error': 'No active commission of this type'}
        
        new_progress = commission['progress'] + amount
        completed = new_progress >= commission['requirement']
        
        await db.dwarven_mines.update_commission_progress(
            commission['commission_id'],
            min(new_progress, commission['requirement']),
            completed
        )
        
        rewards = {}
        if completed:
            from utils.systems.hotm_system import HeartOfTheMountainSystem
            
            if commission['reward_mithril'] > 0:
                await HeartOfTheMountainSystem.add_powder(db, user_id, 'mithril', commission['reward_mithril'])
                rewards['mithril_powder'] = commission['reward_mithril']
            
            if commission['reward_coins'] > 0:
                rewards['coins'] = commission['reward_coins']
            
            await db.dwarven_mines.increment_commissions_and_reputation(user_id, 10)
        
        return {
            'success': True,
            'completed': completed,
            'progress': new_progress,
            'requirement': commission['requirement'],
            'rewards': rewards if completed else {}
        }
