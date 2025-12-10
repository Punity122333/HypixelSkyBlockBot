from typing import Dict, List, Optional

class CoopSystem:
    
    @staticmethod
    async def create_coop(db, owner_id: int, coop_name: str) -> int:
        return await db.coop.create_coop(owner_id, coop_name)
    
    @staticmethod
    async def invite_member(db, coop_id: int, inviter_id: int, invitee_id: int, role: str = 'member') -> bool:
        return await db.coop.invite_member(coop_id, inviter_id, invitee_id, role)
    
    @staticmethod
    async def kick_member(db, coop_id: int, kicker_id: int, kickee_id: int) -> bool:
        return await db.coop.kick_member(coop_id, kicker_id, kickee_id)
    
    @staticmethod
    async def leave_coop(db, coop_id: int, user_id: int) -> bool:
        return await db.coop.leave_coop(coop_id, user_id)
    
    @staticmethod
    async def get_player_coop(db, user_id: int) -> Optional[Dict]:
        return await db.coop.get_player_coop(user_id)
    
    @staticmethod
    async def get_coop_members(db, coop_id: int) -> List[Dict]:
        return await db.coop.get_coop_members(coop_id)
    
    @staticmethod
    async def has_permission(db, user_id: int, coop_id: int, permission: str) -> bool:
        return await db.coop.has_permission(user_id, coop_id, permission)
    
    @staticmethod
    async def deposit_to_bank(db, user_id: int, coop_id: int, amount: int) -> bool:
        return await db.coop.deposit_to_bank(user_id, coop_id, amount)
    
    @staticmethod
    async def withdraw_from_bank(db, user_id: int, coop_id: int, amount: int) -> bool:
        return await db.coop.withdraw_from_bank(user_id, coop_id, amount)
    
    @staticmethod
    async def get_shared_minions(db, coop_id: int) -> List[Dict]:
        return await db.coop.get_shared_minions(coop_id)
    
    @staticmethod
    async def change_member_role(db, changer_id: int, coop_id: int, target_id: int, new_role: str) -> bool:
        return await db.coop.change_member_role(changer_id, coop_id, target_id, new_role)
