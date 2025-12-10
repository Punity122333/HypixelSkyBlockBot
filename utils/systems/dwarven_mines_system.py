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
        
        row = await db.fetchone('SELECT * FROM dwarven_mines_progress WHERE user_id = ?', (user_id,))
        if not row:
            await cls.initialize_dwarven_progress(db, user_id)
            return await cls.get_dwarven_progress(db, user_id)
        
        return dict(row)
    
    @classmethod
    async def initialize_dwarven_progress(cls, db, user_id: int):
        if not db.conn:
            return
        await db.execute('''
            INSERT OR IGNORE INTO dwarven_mines_progress 
            (user_id, commissions_completed, reputation, king_yolkar_unlocked, mithril_unlocked, titanium_unlocked)
            VALUES (?, 0, 0, 0, 1, 0)
        ''', (user_id,))
        await db.commit()
    
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
        
        await db.execute('''
            DELETE FROM player_commissions 
            WHERE user_id = ? AND completed = 0
        ''', (user_id,))
        
        commission_count = 4
        available_types = list(cls.COMMISSION_TYPES.keys())
        selected_types = random.sample(available_types, min(commission_count, len(available_types)))
        
        commissions = []
        expires_at = int(time.time()) + 86400
        
        for comm_type in selected_types:
            comm_data = cls.COMMISSION_TYPES[comm_type]
            requirement = random.randint(*comm_data['amount_range'])
            
            await db.execute('''
                INSERT INTO player_commissions 
                (user_id, commission_type, requirement, progress, reward_mithril, reward_coins, expires_at)
                VALUES (?, ?, ?, 0, ?, ?, ?)
            ''', (
                user_id,
                comm_type,
                requirement,
                comm_data['rewards'].get('mithril_powder', 0),
                comm_data['rewards'].get('coins', 0),
                expires_at
            ))
            
            commissions.append({
                'type': comm_type,
                'name': comm_data['name'],
                'description': comm_data['description'].format(amount=requirement),
                'requirement': requirement,
                'progress': 0,
                'rewards': comm_data['rewards']
            })
        
        await db.commit()
        return commissions
    
    @classmethod
    async def get_active_commissions(cls, db, user_id: int) -> List[Dict[str, Any]]:
        if not db.conn:
            return []
        
        current_time = int(time.time())
        rows = await db.fetchall('''
            SELECT * FROM player_commissions 
            WHERE user_id = ? AND completed = 0 AND expires_at > ?
        ''', (user_id, current_time))
        
        commissions = []
        for row in rows:
            row_dict = dict(row)
            comm_data = cls.COMMISSION_TYPES.get(row_dict['commission_type'], {})
            row_dict['name'] = comm_data.get('name', 'Unknown')
            row_dict['description'] = comm_data.get('description', '').format(amount=row_dict['requirement'])
            commissions.append(row_dict)
        
        return commissions
    
    @classmethod
    async def update_commission_progress(cls, db, user_id: int, commission_type: str, amount: int) -> Dict[str, Any]:
        if not db.conn:
            return {'success': False}
        
        current_time = int(time.time())
        commission = await db.fetchone('''
            SELECT * FROM player_commissions 
            WHERE user_id = ? AND commission_type = ? AND completed = 0 AND expires_at > ?
        ''', (user_id, commission_type, current_time))
        
        if not commission:
            return {'success': False, 'error': 'No active commission of this type'}
        
        commission = dict(commission)
        new_progress = commission['progress'] + amount
        completed = new_progress >= commission['requirement']
        
        await db.execute('''
            UPDATE player_commissions 
            SET progress = ?, completed = ?
            WHERE commission_id = ?
        ''', (min(new_progress, commission['requirement']), 1 if completed else 0, commission['commission_id']))
        
        rewards = {}
        if completed:
            from utils.systems.hotm_system import HeartOfTheMountainSystem
            
            if commission['reward_mithril'] > 0:
                await HeartOfTheMountainSystem.add_powder(db, user_id, 'mithril', commission['reward_mithril'])
                rewards['mithril_powder'] = commission['reward_mithril']
            
            if commission['reward_coins'] > 0:
                rewards['coins'] = commission['reward_coins']
            
            await db.execute('''
                UPDATE dwarven_mines_progress 
                SET commissions_completed = commissions_completed + 1,
                    reputation = reputation + ?
                WHERE user_id = ?
            ''', (10, user_id))
        
        await db.commit()
        
        return {
            'success': True,
            'completed': completed,
            'progress': new_progress,
            'requirement': commission['requirement'],
            'rewards': rewards if completed else {}
        }
