import discord
from utils.systems.party_system import PartySystem

class PartyInviteAcceptButton(discord.ui.Button):
    def __init__(self, view):
        super().__init__(label="Accept", style=discord.ButtonStyle.green, custom_id="party_invite_accept")
        self.parent_view = view
    
    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.parent_view.user_id:
            await interaction.response.send_message("This invite is not for you!", ephemeral=True)
            return
        
        result = PartySystem.accept_invite(interaction.user.id, self.parent_view.party_id)
        
        if result['success']:
            party = result['party']
            embed = discord.Embed(
                title="✅ Joined Party!",
                description=f"You joined {party['leader_name']}'s party!",
                color=discord.Color.green()
            )
            embed.add_field(name="Party Members", value=f"{len(party['members'])}/{party['max_members']}", inline=True)
            
            for child in self.parent_view.children:
                if isinstance(child, discord.ui.Button):
                    child.disabled = True
            
            await interaction.response.edit_message(embed=embed, view=self.parent_view)
        else:
            await interaction.response.send_message(f"❌ {result['error']}", ephemeral=True)

class PartyInviteDeclineButton(discord.ui.Button):
    def __init__(self, view):
        super().__init__(label="Decline", style=discord.ButtonStyle.red, custom_id="party_invite_decline")
        self.parent_view = view
    
    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.parent_view.user_id:
            await interaction.response.send_message("This invite is not for you!", ephemeral=True)
            return
        
        result = PartySystem.decline_invite(interaction.user.id, self.parent_view.party_id)
        
        embed = discord.Embed(
            title="❌ Invite Declined",
            description="You declined the party invite.",
            color=discord.Color.red()
        )
        
        for child in self.parent_view.children:
            if isinstance(child, discord.ui.Button):
                child.disabled = True
        
        await interaction.response.edit_message(embed=embed, view=self.parent_view)
