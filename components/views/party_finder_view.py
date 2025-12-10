import discord
from components.buttons.party_finder_buttons import (
    PartyFinderListButton,
    PartyFinderJoinButton,
    PartyFinderLeaveButton,
    PartyFinderCreateButton,
    PartyFinderStartButton,
    PartyFinderRefreshButton,
    PartyFinderPreviousButton,
    PartyFinderNextButton
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
        self.start_button = PartyFinderStartButton(self)
        self.refresh_button = PartyFinderRefreshButton(self)
        self.prev_button = PartyFinderPreviousButton(self)
        self.next_button = PartyFinderNextButton(self)
        
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
            member_list.append(f"**{member['username']}** - {member['dungeon_class'].title()}")
        
        embed.add_field(name="Party Members", value='\n'.join(member_list) if member_list else "No members", inline=False)
        
        if party.get('description'):
            embed.add_field(name="Description", value=party['description'], inline=False)
        
        return embed
    
    def _update_buttons(self):
        self.clear_items()
        
        if self.current_view == 'list':
            self.add_item(self.create_button)
            self.add_item(self.refresh_button)
            if self.parties_list:
                self.add_item(self.prev_button)
                self.add_item(self.next_button)
                self.add_item(self.join_button)
            if self.current_party_id:
                self.add_item(self.leave_button)
        elif self.current_view == 'party':
            self.add_item(self.list_button)
            self.add_item(self.start_button)
            self.add_item(self.leave_button)
