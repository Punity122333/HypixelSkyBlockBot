import discord
from utils.systems.party_system import PartySystem
from components.modals.party_invite_modal import PartyInviteModal
from components.modals.party_kick_modal import PartyKickModal
from components.buttons.party_buttons import (
    PartyCreateButton,
    PartyLeaveButton,
    PartyRefreshButton,
    PartyInviteButton,
    PartyKickButton,
    PartyDisbandButton
)

class PartyMenuView(discord.ui.View):
    def __init__(self, bot, user_id, username):
        super().__init__(timeout=180)
        self.bot = bot
        self.user_id = user_id
        self.username = username
        
        self.add_item(PartyCreateButton(self))
        self.add_item(PartyLeaveButton(self))
        self.add_item(PartyRefreshButton(self))
        self.add_item(PartyInviteButton(self))
        self.add_item(PartyKickButton(self))
        self.add_item(PartyDisbandButton(self))
    
    async def get_embed(self):
        party = PartySystem.get_party(self.user_id)
        
        if not party:
            embed = discord.Embed(
                title="👥 Party System",
                description="You are not in a party. Create or join one!",
                color=discord.Color.blue()
            )
        else:
            embed = discord.Embed(
                title=f"👥 {party['leader_name']}'s Party",
                description=f"**Party ID:** {party['party_id']}\n**Created:** <t:{int(party['created_at'])}:R>",
                color=discord.Color.blue()
            )
            
            members_text = ""
            for member in party['members']:
                leader_badge = "👑 " if member['user_id'] == party['leader_id'] else ""
                members_text += f"{leader_badge}**{member['username']}** (joined <t:{int(member['joined_at'])}:R>)\n"
            
            embed.add_field(name=f"Members ({len(party['members'])}/{party['max_members']})", value=members_text, inline=False)
            
            if party['in_dungeon']:
                embed.add_field(name="Status", value=f"🏰 In Dungeon: {party['dungeon_floor']}", inline=False)
            else:
                embed.add_field(name="Status", value="⏳ Waiting in lobby", inline=False)
        
        return embed