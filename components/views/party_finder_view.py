import discord
from components.buttons.party_finder_buttons import (
    PartyFinderListButton,
    PartyFinderJoinButton,
    PartyFinderLeaveButton,
    PartyFinderCreateButton,
    PartyFinderRefreshButton,
    PartyFinderPreviousButton,
    PartyFinderNextButton,
    PartyFinderMyPartyButton,
    PartyFinderInviteButton,
    PartyFinderKickButton,
    PartyFinderDisbandButton
)

class PartyFinderView(discord.ui.View):
    def __init__(self, bot, user_id):
        super().__init__(timeout=180)
        self.bot = bot
        self.user_id = user_id
        self.current_view = 'list'
        self.page = 0
        self.items_per_page = 5
        self.parties_list = []
        self.current_party_id = None
        
        self.list_button = PartyFinderListButton(self)
        self.create_button = PartyFinderCreateButton(self)
        self.join_button = PartyFinderJoinButton(self)
        self.leave_button = PartyFinderLeaveButton(self)
        self.refresh_button = PartyFinderRefreshButton(self)
        self.prev_button = PartyFinderPreviousButton(self)
        self.next_button = PartyFinderNextButton(self)
        self.my_party_button = PartyFinderMyPartyButton(self)
        self.invite_button = PartyFinderInviteButton(self)
        self.kick_button = PartyFinderKickButton(self)
        self.disband_button = PartyFinderDisbandButton(self)
        
        self._update_buttons()
    
    async def load_parties(self, floor=None):
        from utils.systems.party_system import PartySystem
        self.parties_list = PartySystem.get_open_parties(floor)
        player_party = PartySystem.get_party(self.user_id)
        if player_party:
            self.current_party_id = player_party['party_id']
    
    async def get_embed(self):
        if self.current_view == 'list':
            return await self.get_list_embed()
        elif self.current_view == 'party':
            return await self.get_party_embed()
        elif self.current_view == 'my_party':
            return await self.get_my_party_embed()
        else:
            return await self.get_list_embed()
    
    async def get_list_embed(self):
        from utils.systems.party_system import PartySystem
        
        embed = discord.Embed(
            title="⚔️ Dungeon Party Finder",
            description="Browse and join dungeon parties",
            color=discord.Color.blue()
        )
        
        if not self.parties_list:
            embed.add_field(name="No Open Parties", value="Create one to get started!", inline=False)
        else:
            start = self.page * self.items_per_page
            end = min(start + self.items_per_page, len(self.parties_list))
            page_parties = self.parties_list[start:end]
            
            for party in page_parties:
                floor_info = PartySystem.DUNGEON_FLOORS.get(party['dungeon_floor'], {})
                recommended = PartySystem.recommend_class(party['party_id'])
                
                party_info = [
                    f"**Leader:** {party['leader_name']}",
                    f"**Members:** {len(party['members'])}/5",
                    f"**Min Level:** Catacombs {party.get('min_catacombs_level', 0)}",
                    f"**Recommended:** {recommended.title()}"
                ]
                
                if party.get('description'):
                    party_info.append(f"*{party['description']}*")
                
                embed.add_field(
                    name=f"#{party['party_id']} - {floor_info.get('name', f'Floor {party['dungeon_floor']}')}",
                    value='\n'.join(party_info),
                    inline=False
                )
            
            total_pages = (len(self.parties_list) + self.items_per_page - 1) // self.items_per_page
            embed.set_footer(text=f"Page {self.page + 1}/{total_pages}")
        
        return embed
    
    async def get_party_embed(self):
        from utils.systems.party_system import PartySystem
        
        if not self.current_party_id:
            return await self.get_list_embed()
        
        party = PartySystem.get_party_by_id(self.current_party_id)
        if not party:
            return await self.get_list_embed()
        
        members = party['members']
        floor_info = PartySystem.DUNGEON_FLOORS.get(party['dungeon_floor'], {})
        
        embed = discord.Embed(
            title=f"⚔️ Party #{self.current_party_id}",
            description=floor_info.get('name', f"Floor {party['dungeon_floor']}"),
            color=discord.Color.green()
        )
        
        embed.add_field(name="Leader", value=party['leader_name'], inline=True)
        embed.add_field(name="Status", value=party['status'].title(), inline=True)
        embed.add_field(name="Members", value=f"{len(members)}/5", inline=True)
        
        member_list = []
        for member in members:
            dungeon_class = member['dungeon_class'].title() if member['dungeon_class'] else 'No Class'
            member_list.append(f"**{member['username']}** - {dungeon_class}")
        
        embed.add_field(name="Party Members", value='\n'.join(member_list) if member_list else "No members", inline=False)
        
        if party.get('description'):
            embed.add_field(name="Description", value=party['description'], inline=False)
        
        return embed
    
    async def get_my_party_embed(self):
        from utils.systems.party_system import PartySystem
        
        party = PartySystem.get_party(self.user_id)
        
        if not party:
            embed = discord.Embed(
                title="👥 My Party",
                description="You are not in a party. Create or join one!",
                color=discord.Color.blue()
            )
        else:
            embed = discord.Embed(
                title=f"👥 {party['leader_name']}'s Party",
                description=f"**Party ID:** {party['party_id']}",
                color=discord.Color.blue()
            )
            
            members_text = ""
            for member in party['members']:
                leader_badge = "👑 " if member['user_id'] == party['leader_id'] else ""
                dungeon_class = member['dungeon_class'].title() if member['dungeon_class'] else 'No Class'
                members_text += f"{leader_badge}**{member['username']}** - {dungeon_class}\n"
            
            embed.add_field(name=f"Members ({len(party['members'])}/{party['max_members']})", value=members_text, inline=False)
            
            if party['in_dungeon']:
                floor_info = PartySystem.DUNGEON_FLOORS.get(party['dungeon_floor'], {})
                floor_name = floor_info.get('name', f"Floor {party['dungeon_floor']}")
                embed.add_field(name="Status", value=f"🏰 In Dungeon: {floor_name}", inline=False)
            else:
                embed.add_field(name="Status", value="⏳ Waiting in lobby", inline=False)
        
        return embed
    
    def _update_buttons(self):
        self.clear_items()
        
        if self.current_view == 'list':
            self.add_item(self.create_button)
            self.add_item(self.refresh_button)
            self.add_item(self.join_button)
            
            if self.parties_list:
                total_pages = (len(self.parties_list) + self.items_per_page - 1) // self.items_per_page
                if total_pages > 1:
                    self.add_item(self.prev_button)
                    self.add_item(self.next_button)
                
            if self.current_party_id:
                self.add_item(self.my_party_button)
                self.add_item(self.leave_button)
        elif self.current_view == 'party':
            self.add_item(self.list_button)
            self.add_item(self.leave_button)
        elif self.current_view == 'my_party':
            from utils.systems.party_system import PartySystem
            party = PartySystem.get_party(self.user_id)
            
            self.add_item(self.list_button)
            self.add_item(self.refresh_button)
            
            if party:
                self.add_item(self.leave_button)
                
                if party['leader_id'] == self.user_id:
                    self.add_item(self.invite_button)
                    if len(party['members']) > 1:
                        self.add_item(self.kick_button)
                    self.add_item(self.disband_button)
            else:
                self.add_item(self.create_button)
