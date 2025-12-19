from typing import Dict, List, Optional, Any
import time
import random
from .dungeon_system import DungeonSystem
from ..stat_calculator import StatCalculator

class PartySystem:
    
    _parties: Dict[int, Dict[str, Any]] = {}
    _invites: Dict[int, List[Dict[str, Any]]] = {}
    _party_by_member: Dict[int, int] = {}
    
    DUNGEON_CLASSES = {}
    DUNGEON_FLOORS = {}

    @classmethod
    async def _load_constants(cls, db):
        cls.DUNGEON_CLASSES = await db.game_constants.get_dungeon_classes()
        cls.DUNGEON_FLOORS = await db.game_constants.get_party_dungeon_floors()
    
    @classmethod
    def create_party(cls, leader_id: int, leader_name: str, floor: Optional[int] = None, 
                     requirements: Optional[Dict] = None, description: str = '') -> Dict[str, Any]:
        if leader_id in cls._party_by_member:
            return {'success': False, 'error': 'You are already in a party'}
        
        party_id = int(time.time() * 1000)
        
        party = {
            'party_id': party_id,
            'leader_id': leader_id,
            'leader_name': leader_name,
            'members': [{'user_id': leader_id, 'username': leader_name, 'joined_at': time.time(), 'dungeon_class': None}],
            'created_at': time.time(),
            'max_members': 5,
            'in_dungeon': False,
            'dungeon_floor': floor,
            'min_catacombs_level': requirements.get('min_catacombs_level', 0) if requirements else 0,
            'description': description,
            'status': 'open',
            'dungeon_data': None
        }
        
        cls._parties[party_id] = party
        cls._party_by_member[leader_id] = party_id
        
        return {'success': True, 'party_id': party_id, 'party': party}
    
    @classmethod
    def get_party(cls, user_id: int) -> Optional[Dict[str, Any]]:
        party_id = cls._party_by_member.get(user_id)
        if party_id:
            return cls._parties.get(party_id)
        return None
    
    @classmethod
    def get_party_by_id(cls, party_id: int) -> Optional[Dict[str, Any]]:
        return cls._parties.get(party_id)
    
    @classmethod
    def get_open_parties(cls, floor: Optional[int] = None) -> List[Dict[str, Any]]:
        open_parties = [p for p in cls._parties.values() if not p['in_dungeon']]
        
        if floor is not None:
            open_parties = [p for p in open_parties if p['dungeon_floor'] == floor]
        
        return open_parties
    
    @classmethod
    def invite_to_party(cls, inviter_id: int, invitee_id: int, invitee_name: str) -> Dict[str, Any]:
        party = cls.get_party(inviter_id)
        
        if not party:
            return {'success': False, 'error': 'You are not in a party'}
        
        if party['leader_id'] != inviter_id:
            return {'success': False, 'error': 'Only the party leader can invite members'}
        
        if invitee_id in cls._party_by_member:
            return {'success': False, 'error': 'This player is already in a party'}
        
        if len(party['members']) >= party['max_members']:
            return {'success': False, 'error': f'Party is full ({party["max_members"]}/{party["max_members"]})'}
        
        if invitee_id in [m['user_id'] for m in party['members']]:
            return {'success': False, 'error': 'This player is already in the party'}
        
        if invitee_id not in cls._invites:
            cls._invites[invitee_id] = []
        
        existing_invite = next((inv for inv in cls._invites[invitee_id] if inv['party_id'] == party['party_id']), None)
        if existing_invite:
            return {'success': False, 'error': 'Already invited this player'}
        
        invite = {
            'party_id': party['party_id'],
            'inviter_id': inviter_id,
            'inviter_name': party['leader_name'],
            'invitee_id': invitee_id,
            'invitee_name': invitee_name,
            'created_at': time.time(),
            'expires_at': time.time() + 300
        }
        
        cls._invites[invitee_id].append(invite)
        
        return {'success': True, 'invite': invite}
    
    @classmethod
    def join_party(cls, party_id: int, user_id: int, username: str, dungeon_class: Optional[str] = None) -> Dict[str, Any]:
        if user_id in cls._party_by_member:
            return {'success': False, 'error': 'You are already in a party'}
        
        party = cls._parties.get(party_id)
        
        if not party:
            return {'success': False, 'error': 'Party not found'}
        
        if party['status'] != 'open':
            return {'success': False, 'error': 'Party is not accepting members'}
        
        if len(party['members']) >= party['max_members']:
            return {'success': False, 'error': 'Party is full'}
        
        if dungeon_class and dungeon_class not in DungeonSystem.DUNGEON_CLASSES:
            return {'success': False, 'error': 'Invalid dungeon class'}
        
        party['members'].append({
            'user_id': user_id,
            'username': username,
            'joined_at': time.time(),
            'dungeon_class': dungeon_class
        })
        
        cls._party_by_member[user_id] = party_id
        
        if len(party['members']) >= party['max_members']:
            party['status'] = 'full'
        
        return {'success': True, 'party': party}
    
    @classmethod
    def accept_invite(cls, user_id: int, party_id: int) -> Dict[str, Any]:
        if user_id in cls._party_by_member:
            return {'success': False, 'error': 'You are already in a party'}
        
        if user_id not in cls._invites:
            return {'success': False, 'error': 'No pending invites'}
        
        invite = next((inv for inv in cls._invites[user_id] if inv['party_id'] == party_id), None)
        
        if not invite:
            return {'success': False, 'error': 'Invite not found'}
        
        if time.time() > invite['expires_at']:
            cls._invites[user_id].remove(invite)
            return {'success': False, 'error': 'Invite has expired'}
        
        party = cls._parties.get(party_id)
        
        if not party:
            cls._invites[user_id].remove(invite)
            return {'success': False, 'error': 'Party no longer exists'}
        
        if len(party['members']) >= party['max_members']:
            return {'success': False, 'error': 'Party is full'}
        
        party['members'].append({
            'user_id': user_id,
            'username': invite['invitee_name'],
            'joined_at': time.time(),
            'dungeon_class': None
        })
        
        cls._party_by_member[user_id] = party_id
        cls._invites[user_id].remove(invite)
        
        if len(party['members']) >= party['max_members']:
            party['status'] = 'full'
        
        return {'success': True, 'party': party}
    
    @classmethod
    def decline_invite(cls, user_id: int, party_id: int) -> Dict[str, Any]:
        if user_id not in cls._invites:
            return {'success': False, 'error': 'No pending invites'}
        
        invite = next((inv for inv in cls._invites[user_id] if inv['party_id'] == party_id), None)
        
        if not invite:
            return {'success': False, 'error': 'Invite not found'}
        
        cls._invites[user_id].remove(invite)
        
        return {'success': True}
    
    @classmethod
    def get_pending_invites(cls, user_id: int) -> List[Dict[str, Any]]:
        if user_id not in cls._invites:
            return []
        
        current_time = time.time()
        cls._invites[user_id] = [inv for inv in cls._invites[user_id] if inv['expires_at'] > current_time]
        
        return cls._invites[user_id]
    
    @classmethod
    def leave_party(cls, user_id: int) -> Dict[str, Any]:
        party_id = cls._party_by_member.get(user_id)
        
        if not party_id:
            return {'success': False, 'error': 'You are not in a party'}
        
        party = cls._parties.get(party_id)
        
        if not party:
            del cls._party_by_member[user_id]
            return {'success': False, 'error': 'Party not found'}
        
        if party['in_dungeon']:
            return {'success': False, 'error': 'Cannot leave party during a dungeon run'}
        
        party['members'] = [m for m in party['members'] if m['user_id'] != user_id]
        del cls._party_by_member[user_id]
        
        if len(party['members']) == 0:
            del cls._parties[party_id]
            return {'success': True, 'disbanded': True}
        
        if len(party['members']) < party['max_members'] and party['status'] == 'full':
            party['status'] = 'open'
        
        if party['leader_id'] == user_id:
            new_leader = party['members'][0]
            party['leader_id'] = new_leader['user_id']
            party['leader_name'] = new_leader['username']
            return {'success': True, 'disbanded': False, 'new_leader': new_leader}
        
        return {'success': True, 'disbanded': False}
    
    @classmethod
    def kick_member(cls, kicker_id: int, member_id: int) -> Dict[str, Any]:
        party = cls.get_party(kicker_id)
        
        if not party:
            return {'success': False, 'error': 'You are not in a party'}
        
        if party['leader_id'] != kicker_id:
            return {'success': False, 'error': 'Only the party leader can kick members'}
        
        if member_id == kicker_id:
            return {'success': False, 'error': 'Cannot kick yourself'}
        
        if member_id not in [m['user_id'] for m in party['members']]:
            return {'success': False, 'error': 'This player is not in your party'}
        
        if party['in_dungeon']:
            return {'success': False, 'error': 'Cannot kick members during a dungeon run'}
        
        party['members'] = [m for m in party['members'] if m['user_id'] != member_id]
        
        if member_id in cls._party_by_member:
            del cls._party_by_member[member_id]
        
        if len(party['members']) < party['max_members'] and party['status'] == 'full':
            party['status'] = 'open'
        
        return {'success': True}
    
    @classmethod
    def disband_party(cls, leader_id: int) -> Dict[str, Any]:
        party = cls.get_party(leader_id)
        
        if not party:
            return {'success': False, 'error': 'You are not in a party'}
        
        if party['leader_id'] != leader_id:
            return {'success': False, 'error': 'Only the party leader can disband the party'}
        
        if party['in_dungeon']:
            return {'success': False, 'error': 'Cannot disband party during a dungeon run'}
        
        party_id = party['party_id']
        
        for member in party['members']:
            if member['user_id'] in cls._party_by_member:
                del cls._party_by_member[member['user_id']]
        
        del cls._parties[party_id]
        
        return {'success': True}
    
    @classmethod
    async def start_dungeon(cls, db, leader_id: int, floor_id: str) -> Dict[str, Any]:
        party = cls.get_party(leader_id)
        
        if not party:
            return {'success': False, 'error': 'You are not in a party'}
        
        if party['leader_id'] != leader_id:
            return {'success': False, 'error': 'Only the party leader can start a dungeon'}
        
        if party['in_dungeon']:
            return {'success': False, 'error': 'Party is already in a dungeon'}
        
        for member in party['members']:
            can_enter, reason = await DungeonSystem.can_enter_floor(db, member['user_id'], floor_id)
            if not can_enter:
                return {'success': False, 'error': f"{member['username']}: {reason}"}
        
        rooms = DungeonSystem._generate_dungeon_rooms(floor_id)
        
        party['in_dungeon'] = True
        party['dungeon_floor'] = floor_id
        party['dungeon_started_at'] = time.time()
        party['status'] = 'in_progress'
        party['dungeon_data'] = {
            'rooms': rooms,
            'current_room': 0,
            'rooms_cleared': 0,
            'secrets_found': 0,
            'deaths': 0,
            'score': 0,
            'damage_taken': 0
        }
        
        return {'success': True, 'party': party, 'dungeon_data': party['dungeon_data']}
    
    @classmethod
    async def end_dungeon(cls, db, party_id: int, completed: bool = True) -> Dict[str, Any]:
        party = cls._parties.get(party_id)
        
        if not party:
            return {'success': False, 'error': 'Party not found'}
        
        if not party['in_dungeon']:
            return {'success': False, 'error': 'Party is not in a dungeon'}
        
        dungeon_data = party.get('dungeon_data', {})
        rewards = {}
        
        if completed:
            floor_id = party['dungeon_floor']
            score = dungeon_data.get('score', 0)
            time_taken = int(time.time() - party['dungeon_started_at'])
            
            if not db.conn:
                return {'success': False, 'error': 'Database not connected'}
            
            cursor = await db.conn.execute('''
                SELECT * FROM dungeon_floors WHERE floor_id = ?
            ''', (floor_id,))
            floor_data = await cursor.fetchone()
            
            if floor_data:
                base_rewards = floor_data['rewards']
                score_multiplier = 1.0 + (score / 1000)
                time_multiplier = 1.0 if time_taken < floor_data['time'] else 0.8
                
                total_coins = int(base_rewards * score_multiplier * time_multiplier)
                coins_per_member = total_coins // len(party['members'])
                
                for member in party['members']:
                    await db.conn.execute(
                        'UPDATE players SET coins = coins + ? WHERE user_id = ?',
                        (coins_per_member, member['user_id'])
                    )
                    rewards[member['user_id']] = coins_per_member
                
                await db.conn.commit()
        
        party['in_dungeon'] = False
        party['dungeon_floor'] = None
        party['dungeon_started_at'] = None
        party['status'] = 'open'
        party['dungeon_data'] = None
        
        return {'success': True, 'completed': completed, 'rewards': rewards, 'score': dungeon_data.get('score', 0)}
    
    @classmethod
    async def clear_room(cls, db, party_id: int, room_index: int) -> Dict[str, Any]:
        party = cls._parties.get(party_id)
        
        if not party or not party['in_dungeon']:
            return {'success': False, 'error': 'Party not in dungeon'}
        
        dungeon_data = party['dungeon_data']
        
        if room_index >= len(dungeon_data['rooms']):
            return {'success': False, 'error': 'Invalid room'}
        
        room = dungeon_data['rooms'][room_index]
        
        if room['cleared']:
            return {'success': False, 'error': 'Room already cleared'}
        
        room_type = room['type']
        
        for member in party['members']:
            player = await db.get_player(member['user_id'])
            current_health = player.get('current_health', player.get('health', 100))
            max_health = player.get('max_health', player.get('health', 100))
            
            from .combat_system import CombatSystem
            regenerated_health = await CombatSystem.apply_health_regeneration(
                db, member['user_id'], current_health, max_health
            )
            
            await db.conn.execute(
                'UPDATE players SET current_health = ? WHERE user_id = ?',
                (regenerated_health, member['user_id'])
            )
            await db.conn.commit()
        
        if room_type in ['mob', 'miniboss', 'boss']:
            result = await cls._clear_combat_room_party(db, party, room)
        elif room_type == 'puzzle':
            result = await DungeonSystem._clear_puzzle_room(db, party['leader_id'], room)
        elif room_type == 'trap':
            result = await cls._clear_trap_room_party(db, party, room)
        else:
            result = {'success': True}
        
        if result['success']:
            room['cleared'] = True
            dungeon_data['rooms_cleared'] += 1
            dungeon_data['current_room'] = room_index + 1
            dungeon_data['score'] += 100 * room['difficulty']
        
        return result
    
    @classmethod
    async def _clear_combat_room_party(cls, db, party: Dict, room: Dict) -> Dict[str, Any]:
        total_party_damage = 0
        
        for member in party['members']:
            player_stats = await StatCalculator.calculate_full_stats(db, member['user_id'], context='dungeon')
            member_damage = player_stats.get('strength', 100)
            
            dungeon_class = member.get('dungeon_class', 'berserk')
            if dungeon_class == 'berserk':
                member_damage *= 1.5
            elif dungeon_class == 'mage':
                member_damage *= 1.3
            elif dungeon_class == 'archer':
                member_damage *= 1.2
            elif dungeon_class == 'healer':
                member_damage *= 0.8
            elif dungeon_class == 'tank':
                member_damage *= 1.0
            
            total_party_damage += member_damage
        
        total_mob_health = sum(mob['health'] for mob in room['mobs'] if mob['alive'])
        
        if total_party_damage >= total_mob_health:
            for mob in room['mobs']:
                mob['alive'] = False
            
            return {'success': True, 'reward': f'Defeated all enemies! +{room["difficulty"] * 50} score'}
        else:
            return {'success': False, 'error': 'Party wiped!'}
    
    @classmethod
    async def _clear_trap_room_party(cls, db, party: Dict, room: Dict) -> Dict[str, Any]:
        damage_taken = room['difficulty'] * 20
        
        for member in party['members']:
            player = await db.get_player(member['user_id'])
            current_health = player.get('current_health', player.get('health', 100))
            new_health = max(0, current_health - damage_taken)
            
            await db.conn.execute(
                'UPDATE players SET current_health = ? WHERE user_id = ?',
                (new_health, member['user_id'])
            )
            await db.conn.commit()
        
        return {'success': True, 'reward': f'Survived the trap! Took {damage_taken} damage'}
    
    @classmethod
    def get_party_member_ids(cls, user_id: int) -> List[int]:
        party = cls.get_party(user_id)
        if party:
            return [m['user_id'] for m in party['members']]
        return [user_id]
    
    @classmethod
    def is_in_party(cls, user_id: int) -> bool:
        return user_id in cls._party_by_member
    
    @classmethod
    def get_party_size(cls, user_id: int) -> int:
        party = cls.get_party(user_id)
        return len(party['members']) if party else 1
    
    @classmethod
    def recommend_class(cls, party_id: int) -> str:
        party = cls._parties.get(party_id)
        if not party:
            return 'berserk'
        
        current_classes = [m.get('dungeon_class') for m in party['members'] if m.get('dungeon_class')]
        
        class_priority = ['healer', 'tank', 'mage', 'archer', 'berserk']
        
        for cls_name in class_priority:
            if cls_name not in current_classes:
                return cls_name
        
        return 'berserk'
