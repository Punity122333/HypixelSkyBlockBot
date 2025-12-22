from typing import Dict, List, Optional
import time
import json
from .core import DatabaseCore

class CoopDB(DatabaseCore):
    
    async def get_role_permissions(self, role: str) -> List[str]:
        row = await self.fetchone(
            'SELECT permissions FROM coop_permissions WHERE role = ?',
            (role,)
        )
        if not row:
            return []
        return json.loads(row['permissions'])
    
    async def create_coop(self, owner_id: int, coop_name: str) -> int:
        existing = await self.fetchone(
            'SELECT coop_id FROM coop_members WHERE user_id = ?',
            (owner_id,)
        )
        if existing:
            raise ValueError('Already in a co-op')
        
        cursor = await self.execute(
            '''INSERT INTO coops (coop_name, created_at, shared_bank, bank_capacity)
               VALUES (?, ?, 0, 10000)''',
            (coop_name, int(time.time()))
        )
        await self.commit()
        
        coop_id = cursor.lastrowid
        
        owner_permissions = await self.get_role_permissions('owner')
        await self.execute(
            '''INSERT INTO coop_members (coop_id, user_id, role, permissions, joined_at)
               VALUES (?, ?, 'owner', ?, ?)''',
            (coop_id, owner_id, json.dumps(owner_permissions), int(time.time()))
        )
        await self.commit()
        
        return coop_id if coop_id else 0
    
    async def invite_member(self, coop_id: int, inviter_id: int, invitee_id: int, role: str = 'member') -> bool:
        if not await self.has_permission(inviter_id, coop_id, 'invite_members'):
            return False
        
        existing = await self.fetchone(
            'SELECT coop_id FROM coop_members WHERE user_id = ?',
            (invitee_id,)
        )
        if existing:
            return False
        
        role_permissions = await self.get_role_permissions(role)
        if not role_permissions and role != 'guest':
            return False
        
        await self.execute(
            '''INSERT INTO coop_members (coop_id, user_id, role, permissions, joined_at)
               VALUES (?, ?, ?, ?, ?)''',
            (coop_id, invitee_id, role, json.dumps(role_permissions), int(time.time()))
        )
        await self.commit()
        
        return True
    
    async def kick_member(self, coop_id: int, kicker_id: int, kickee_id: int) -> bool:
        if not await self.has_permission(kicker_id, coop_id, 'kick_members'):
            return False
        
        kickee_role = await self.fetchone(
            'SELECT role FROM coop_members WHERE coop_id = ? AND user_id = ?',
            (coop_id, kickee_id)
        )
        
        if not kickee_role:
            return False
        
        if kickee_role['role'] == 'owner':
            return False
        
        await self.execute(
            'DELETE FROM coop_members WHERE coop_id = ? AND user_id = ?',
            (coop_id, kickee_id)
        )
        await self.commit()
        
        return True
    
    async def leave_coop(self, coop_id: int, user_id: int) -> bool:
        member = await self.fetchone(
            'SELECT role FROM coop_members WHERE coop_id = ? AND user_id = ?',
            (coop_id, user_id)
        )
        
        if not member:
            return False
        
        if member['role'] == 'owner':
            return False
        
        await self.execute(
            'DELETE FROM coop_members WHERE coop_id = ? AND user_id = ?',
            (coop_id, user_id)
        )
        await self.commit()
        
        return True
    
    async def get_player_coop(self, user_id: int) -> Optional[Dict]:
        row = await self.fetchone(
            '''SELECT c.* FROM coops c
               INNER JOIN coop_members cm ON c.id = cm.coop_id
               WHERE cm.user_id = ?''',
            (user_id,)
        )
        return dict(row) if row else None
    
    async def get_coop_members(self, coop_id: int) -> List[Dict]:
        rows = await self.fetchall(
            '''SELECT cm.*, p.username FROM coop_members cm
               LEFT JOIN players p ON cm.user_id = p.user_id
               WHERE cm.coop_id = ?
               ORDER BY cm.role DESC, cm.joined_at ASC''',
            (coop_id,)
        )
        return [dict(row) for row in rows]
    
    async def has_permission(self, user_id: int, coop_id: int, permission: str) -> bool:
        member = await self.fetchone(
            'SELECT permissions FROM coop_members WHERE coop_id = ? AND user_id = ?',
            (coop_id, user_id)
        )
        
        if not member:
            return False
        
        permissions = json.loads(member['permissions'])
        return permission in permissions
    
    async def deposit_to_bank(self, user_id: int, coop_id: int, amount: int) -> bool:
        if not await self.has_permission(user_id, coop_id, 'use_bank'):
            return False
        
        player = await self.fetchone('SELECT coins FROM player_economy WHERE user_id = ?', (user_id,))
        if not player or player['coins'] < amount:
            return False
        
        coop = await self.fetchone('SELECT shared_bank, bank_capacity FROM coops WHERE id = ?', (coop_id,))
        if not coop:
            return False
        
        new_balance = coop['shared_bank'] + amount
        if new_balance > coop['bank_capacity']:
            return False
        
        await self.execute('UPDATE player_economy SET coins = coins - ? WHERE user_id = ?', (amount, user_id))
        await self.execute('UPDATE coops SET shared_bank = ? WHERE id = ?', (new_balance, coop_id))
        await self.commit()
        
        return True
    
    async def withdraw_from_bank(self, user_id: int, coop_id: int, amount: int) -> bool:
        if not await self.has_permission(user_id, coop_id, 'use_bank'):
            return False
        
        coop = await self.fetchone('SELECT shared_bank FROM coops WHERE id = ?', (coop_id,))
        if not coop or coop['shared_bank'] < amount:
            return False
        
        await self.execute('UPDATE coops SET shared_bank = shared_bank - ? WHERE id = ?', (amount, coop_id))
        await self.execute('UPDATE player_economy SET coins = coins + ? WHERE user_id = ?', (amount, user_id))
        await self.commit()
        
        return True
    
    async def get_shared_minions(self, coop_id: int) -> List[Dict]:
        rows = await self.fetchall(
            '''SELECT m.* FROM player_minions m
               INNER JOIN coop_members cm ON m.user_id = cm.user_id
               WHERE cm.coop_id = ?
               ORDER BY m.id ASC''',
            (coop_id,)
        )
        return [dict(row) for row in rows]
    
    async def change_member_role(self, changer_id: int, coop_id: int, target_id: int, new_role: str) -> bool:
        if not await self.has_permission(changer_id, coop_id, 'manage_permissions'):
            return False
        
        new_role_permissions = await self.get_role_permissions(new_role)
        if not new_role_permissions and new_role != 'guest':
            return False
        
        target_member = await self.fetchone(
            'SELECT role FROM coop_members WHERE coop_id = ? AND user_id = ?',
            (coop_id, target_id)
        )
        
        if not target_member or target_member['role'] == 'owner':
            return False
        
        await self.execute(
            'UPDATE coop_members SET role = ?, permissions = ? WHERE coop_id = ? AND user_id = ?',
            (new_role, json.dumps(new_role_permissions), coop_id, target_id)
        )
        await self.commit()
        
        return True
