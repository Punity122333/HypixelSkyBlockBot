from typing import Dict, List, Optional, Any, Tuple
import time
from datetime import datetime, timedelta


class PartySystem:
    
    _parties: Dict[int, Dict[str, Any]] = {}
    _invites: Dict[int, List[Dict[str, Any]]] = {}
    _party_by_member: Dict[int, int] = {}
    
    @classmethod
    def create_party(cls, leader_id: int, leader_name: str) -> Dict[str, Any]:
        if leader_id in cls._party_by_member:
            return {'success': False, 'error': 'You are already in a party'}
        
        party_id = int(time.time() * 1000)
        
        party = {
            'party_id': party_id,
            'leader_id': leader_id,
            'leader_name': leader_name,
            'members': [{'user_id': leader_id, 'username': leader_name, 'joined_at': time.time()}],
            'created_at': time.time(),
            'max_members': 5,
            'in_dungeon': False,
            'dungeon_floor': None
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
            'joined_at': time.time()
        })
        
        cls._party_by_member[user_id] = party_id
        cls._invites[user_id].remove(invite)
        
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
    def start_dungeon(cls, leader_id: int, floor_id: str) -> Dict[str, Any]:
        party = cls.get_party(leader_id)
        
        if not party:
            return {'success': False, 'error': 'You are not in a party'}
        
        if party['leader_id'] != leader_id:
            return {'success': False, 'error': 'Only the party leader can start a dungeon'}
        
        if party['in_dungeon']:
            return {'success': False, 'error': 'Party is already in a dungeon'}
        
        party['in_dungeon'] = True
        party['dungeon_floor'] = floor_id
        party['dungeon_started_at'] = time.time()
        
        return {'success': True, 'party': party}
    
    @classmethod
    def end_dungeon(cls, party_id: int) -> Dict[str, Any]:
        party = cls._parties.get(party_id)
        
        if not party:
            return {'success': False, 'error': 'Party not found'}
        
        party['in_dungeon'] = False
        party['dungeon_floor'] = None
        party['dungeon_started_at'] = None
        
        return {'success': True}
    
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
