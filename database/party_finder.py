from typing import Dict, List, Optional
import time
import json
from .core import DatabaseCore

class PartyFinderDB(DatabaseCore):
    
    DUNGEON_CLASSES = ['healer', 'mage', 'berserker', 'archer', 'tank']
    
    DUNGEON_FLOORS = {
        1: {'name': 'Floor 1', 'min_level': 0, 'recommended_level': 5},
        2: {'name': 'Floor 2', 'min_level': 3, 'recommended_level': 10},
        3: {'name': 'Floor 3', 'min_level': 7, 'recommended_level': 15},
        4: {'name': 'Floor 4', 'min_level': 10, 'recommended_level': 20},
        5: {'name': 'Floor 5', 'min_level': 15, 'recommended_level': 25},
        6: {'name': 'Floor 6', 'min_level': 20, 'recommended_level': 30},
        7: {'name': 'Floor 7', 'min_level': 25, 'recommended_level': 35},
    }
    
    async def create_party(self, leader_id: int, floor: int, requirements: Optional[Dict] = None, description: str = '') -> int:
        if floor not in self.DUNGEON_FLOORS:
            raise ValueError('Invalid floor')
        
        min_cata_level = requirements.get('min_catacombs_level', 0) if requirements else 0
        class_reqs = json.dumps(requirements.get('classes', {})) if requirements else json.dumps({})
        
        cursor = await self.execute(
            '''INSERT INTO dungeon_parties (party_leader, dungeon_floor, class_requirements, min_catacombs_level, description, created_at, status)
               VALUES (?, ?, ?, ?, ?, ?, 'open')''',
            (leader_id, floor, class_reqs, min_cata_level, description, int(time.time()))
        )
        await self.commit()
        
        party_id = cursor.lastrowid if cursor.lastrowid else 0
        
        player_class = await self._get_player_preferred_class(leader_id)
        await self.execute(
            '''INSERT INTO dungeon_party_members (party_id, user_id, dungeon_class, joined_at)
               VALUES (?, ?, ?, ?)''',
            (party_id, leader_id, player_class, int(time.time()))
        )
        await self.commit()
        
        return party_id
    
    async def join_party(self, party_id: int, user_id: int, dungeon_class: str) -> bool:
        if dungeon_class not in self.DUNGEON_CLASSES:
            return False
        
        party = await self.get_party(party_id)
        if not party or party['status'] != 'open':
            return False
        
        members = await self.get_party_members(party_id)
        if len(members) >= 5:
            return False
        
        if any(m['user_id'] == user_id for m in members):
            return False
        
        player = await self.fetchone('SELECT catacombs_level FROM player_dungeon_stats WHERE user_id = ?', (user_id,))
        if not player:
            return False
        
        cata_level = player['catacombs_level'] or 0
        if cata_level < party['min_catacombs_level']:
            return False
        
        class_reqs = json.loads(party.get('class_requirements', '{}'))
        if class_reqs and dungeon_class in class_reqs:
            current_count = sum(1 for m in members if m['dungeon_class'] == dungeon_class)
            if current_count >= class_reqs.get(dungeon_class, 5):
                return False
        
        await self.execute(
            '''INSERT INTO dungeon_party_members (party_id, user_id, dungeon_class, joined_at)
               VALUES (?, ?, ?, ?)''',
            (party_id, user_id, dungeon_class, int(time.time()))
        )
        await self.commit()
        
        members = await self.get_party_members(party_id)
        if len(members) >= 5:
            await self.execute(
                'UPDATE dungeon_parties SET status = ? WHERE party_id = ?',
                ('full', party_id)
            )
            await self.commit()
        
        return True
    
    async def leave_party(self, party_id: int, user_id: int) -> bool:
        party = await self.get_party(party_id)
        if not party:
            return False
        
        if party['party_leader'] == user_id:
            await self.execute('DELETE FROM dungeon_party_members WHERE party_id = ?', (party_id,))
            await self.execute('DELETE FROM dungeon_parties WHERE party_id = ?', (party_id,))
            await self.commit()
            return True
        
        await self.execute(
            'DELETE FROM dungeon_party_members WHERE party_id = ? AND user_id = ?',
            (party_id, user_id)
        )
        await self.commit()
        
        await self.execute(
            'UPDATE dungeon_parties SET status = ? WHERE party_id = ? AND status = ?',
            ('open', party_id, 'full')
        )
        await self.commit()
        
        return True
    
    async def get_party(self, party_id: int) -> Optional[Dict]:
        row = await self.fetchone(
            'SELECT * FROM dungeon_parties WHERE party_id = ?',
            (party_id,)
        )
        return dict(row) if row else None
    
    async def get_party_members(self, party_id: int) -> List[Dict]:
        rows = await self.fetchall(
            '''SELECT dpm.*, p.username FROM dungeon_party_members dpm
               LEFT JOIN players p ON dpm.user_id = p.user_id
               WHERE dpm.party_id = ?
               ORDER BY dpm.joined_at ASC''',
            (party_id,)
        )
        return [dict(row) for row in rows]
    
    async def get_open_parties(self, floor: Optional[int] = None) -> List[Dict]:
        if floor is not None:
            rows = await self.fetchall(
                '''SELECT dp.*, p.username as leader_name FROM dungeon_parties dp
                   LEFT JOIN players p ON dp.party_leader = p.user_id
                   WHERE dp.status = 'open' AND dp.dungeon_floor = ?
                   ORDER BY dp.created_at DESC''',
                (floor,)
            )
        else:
            rows = await self.fetchall(
                '''SELECT dp.*, p.username as leader_name FROM dungeon_parties dp
                   LEFT JOIN players p ON dp.party_leader = p.user_id
                   WHERE dp.status = 'open'
                   ORDER BY dp.created_at DESC'''
            )
        return [dict(row) for row in rows]
    
    async def start_dungeon(self, party_id: int) -> bool:
        party = await self.get_party(party_id)
        if not party or party['status'] != 'full':
            return False
        
        await self.execute(
            'UPDATE dungeon_parties SET status = ? WHERE party_id = ?',
            ('in_progress', party_id)
        )
        await self.commit()
        
        return True
    
    async def recommend_class(self, party_id: int) -> str:
        members = await self.get_party_members(party_id)
        
        class_counts = {cls: 0 for cls in self.DUNGEON_CLASSES}
        for member in members:
            class_counts[member['dungeon_class']] += 1
        
        min_class = min(class_counts.items(), key=lambda x: x[1])[0]
        return min_class
    
    async def _get_player_preferred_class(self, user_id: int) -> str:
        row = await self.fetchone(
            'SELECT preferred_dungeon_class FROM player_dungeon_stats WHERE user_id = ?',
            (user_id,)
        )
        
        if row and row['preferred_dungeon_class']:
            return row['preferred_dungeon_class']
        
        return 'mage'
    
    async def get_player_party(self, user_id: int) -> Optional[int]:
        row = await self.fetchone(
            'SELECT party_id FROM dungeon_party_members WHERE user_id = ?',
            (user_id,)
        )
        return row['party_id'] if row else None
