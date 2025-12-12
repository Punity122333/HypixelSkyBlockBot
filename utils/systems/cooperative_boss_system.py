from typing import Dict, List, Optional, Any
import time
import random


class CooperativeBossSystem:
    
    @staticmethod
    async def create_coop_boss_session(db, boss_id: str, host_user_id: int, party_id: Optional[int] = None) -> Dict[str, Any]:
        member_ids = [host_user_id]
        
        if party_id:
            from utils.systems.party_system import PartySystem
            party = PartySystem.get_party(party_id)
            if party:
                member_ids = [m['user_id'] for m in party['members']]
        
        session_id = f"{boss_id}_{host_user_id}_{int(time.time())}"
        
        session = {
            'session_id': session_id,
            'boss_id': boss_id,
            'host_user_id': host_user_id,
            'party_id': party_id,
            'member_ids': member_ids,
            'member_damage': {uid: 0 for uid in member_ids},
            'start_time': int(time.time()),
            'completed': False
        }
        
        return session
    
    @staticmethod
    async def record_member_damage(session: Dict[str, Any], user_id: int, damage: int):
        if user_id in session['member_damage']:
            session['member_damage'][user_id] += damage
    
    @staticmethod
    async def calculate_rewards(session: Dict[str, Any], base_coins: int, base_xp: int) -> Dict[int, Dict[str, int]]:
        total_damage = sum(session['member_damage'].values())
        rewards = {}
        
        for user_id, damage in session['member_damage'].items():
            contribution = damage / total_damage if total_damage > 0 else 1 / len(session['member_ids'])
            
            user_coins = int(base_coins * contribution * random.uniform(0.8, 1.2))
            user_xp = int(base_xp * contribution)
            
            rewards[user_id] = {
                'coins': user_coins,
                'xp': user_xp,
                'contribution': contribution
            }
        
        return rewards
    
    @staticmethod
    async def complete_boss_session(db, session: Dict[str, Any], rewards: Dict[int, Dict[str, int]]):
        session['completed'] = True
        session['end_time'] = int(time.time())
        
        for user_id, reward_data in rewards.items():
            await db.players.update_player(
                user_id,
                coins=reward_data['coins']
            )
            
            combat_skills = await db.skills.get_skills(user_id)
            combat_skill = next((s for s in combat_skills if s['skill_name'] == 'combat'), None)
            
            if combat_skill:
                await db.skills.update_skill(
                    user_id,
                    'combat',
                    xp=combat_skill['xp'] + reward_data['xp']
                )
        
        return session
    
    @staticmethod
    def get_mvp(session: Dict[str, Any]) -> Optional[int]:
        if not session['member_damage']:
            return None
        
        return max(session['member_damage'].items(), key=lambda x: x[1])[0]
    
    @staticmethod
    async def distribute_loot(db, session: Dict[str, Any], loot_items: List[tuple]) -> Dict[int, List[tuple]]:
        member_loot = {uid: [] for uid in session['member_ids']}
        
        for item_id, amount in loot_items:
            recipient = random.choice(session['member_ids'])
            member_loot[recipient].append((item_id, amount))
        
        for user_id, items in member_loot.items():
            for item_id, amount in items:
                await db.inventory.add_item_to_inventory(user_id, item_id, amount)
        
        return member_loot
