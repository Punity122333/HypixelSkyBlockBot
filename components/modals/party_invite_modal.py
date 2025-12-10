import discord
from utils.systems.party_system import PartySystem
from components.views.party_invite_view import PartyInviteView

class PartyInviteModal(discord.ui.Modal, title="Invite to Party"):
    user_id = discord.ui.TextInput(label="User ID", placeholder="Enter user ID to invite", required=True)
    
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
        
        if target_user_id == interaction.user.id:
            await interaction.followup.send("❌ You cannot invite yourself!", ephemeral=True)
            return
        
        try:
            user = await self.bot.fetch_user(target_user_id)
        except:
            await interaction.followup.send("❌ User not found!", ephemeral=True)
            return
        
        if user.bot:
            await interaction.followup.send("❌ You cannot invite bots!", ephemeral=True)
            return
        
        result = PartySystem.invite_to_party(interaction.user.id, user.id, user.name)
        
        if result['success']:
            invite = result['invite']
            embed = discord.Embed(
                title="🎊 Party Invite",
                description=f"{user.mention}, you've been invited to join **{invite['inviter_name']}'s** party!",
                color=discord.Color.gold()
            )
            embed.set_footer(text="Invite expires in 5 minutes")
            
            view = PartyInviteView(user.id, invite['party_id'])
            
            await interaction.followup.send(embed=embed, view=view, ephemeral=True)
        else:
            await interaction.followup.send(f"❌ {result['error']}", ephemeral=True)
