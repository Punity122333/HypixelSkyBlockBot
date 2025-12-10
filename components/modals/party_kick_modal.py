import discord
from utils.systems.party_system import PartySystem

class PartyKickModal(discord.ui.Modal, title="Kick Member"):
    user_id = discord.ui.TextInput(label="User ID", placeholder="Enter user ID to kick", required=True)
    
    def __init__(self, bot):
        super().__init__()
        self.bot = bot
    
    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer()
        try:
            target_user_id = int(self.user_id.value)
        except ValueError:
            await interaction.followup.send("❌ Invalid user ID!", ephemeral=True)
            return
        
        result = PartySystem.kick_member(interaction.user.id, target_user_id)
        
        if result['success']:
            embed = discord.Embed(
                title="🚫 Member Kicked",
                description=f"Member has been removed from the party.",
                color=discord.Color.orange()
            )
            await interaction.followup.send(embed=embed, ephemeral=True)
        else:
            await interaction.followup.send(f"❌ {result['error']}", ephemeral=True)