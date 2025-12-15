import discord
from utils.systems.party_system import PartySystem
from components.modals.party_invite_modal import PartyInviteModal
from components.modals.party_kick_modal import PartyKickModal

class PartyCreateButton(discord.ui.Button):
    def __init__(self, view):
        super().__init__(label="Create Party", style=discord.ButtonStyle.green, custom_id="party_create", row=0)
        self.parent_view = view
    
    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.parent_view.user_id:
            await interaction.response.send_message("This isn't your menu!", ephemeral=True)
            return
        
        result = PartySystem.create_party(self.parent_view.user_id, self.parent_view.username)
        
        if result['success']:
            stats = await self.parent_view.bot.db.get_player_stats(interaction.user.id)
            if stats:
                total_parties_hosted = stats.get('total_parties_hosted', 0) + 1
                await self.parent_view.bot.db.update_player_stats(interaction.user.id, total_parties_hosted=total_parties_hosted)
                
                from utils.systems.achievement_system import AchievementSystem
                await AchievementSystem.check_parties_hosted_achievements(self.parent_view.bot.db, interaction, interaction.user.id, total_parties_hosted)
                await AchievementSystem.unlock_action_achievement(self.parent_view.bot.db, interaction, interaction.user.id, 'coop_member')
            
            await interaction.response.send_message("✅ Party created!", ephemeral=True)
        else:
            await interaction.response.send_message(f"❌ {result['error']}", ephemeral=True)

class PartyLeaveButton(discord.ui.Button):
    def __init__(self, view):
        super().__init__(label="Leave Party", style=discord.ButtonStyle.red, custom_id="party_leave", row=0)
        self.parent_view = view
    
    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.parent_view.user_id:
            await interaction.response.send_message("This isn't your menu!", ephemeral=True)
            return
        
        result = PartySystem.leave_party(self.parent_view.user_id)
        
        if result['success']:
            if result.get('disbanded'):
                await interaction.response.send_message("👋 You left and the party was disbanded.", ephemeral=True)
            else:
                await interaction.response.send_message("👋 You left the party.", ephemeral=True)
        else:
            await interaction.response.send_message(f"❌ {result['error']}", ephemeral=True)

class PartyRefreshButton(discord.ui.Button):
    def __init__(self, view):
        super().__init__(label="Refresh", style=discord.ButtonStyle.gray, custom_id="party_refresh", row=0)
        self.parent_view = view
    
    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.parent_view.user_id:
            await interaction.response.send_message("This isn't your menu!", ephemeral=True)
            return
        
        await interaction.response.edit_message(embed=await self.parent_view.get_embed(), view=self.parent_view)

class PartyInviteButton(discord.ui.Button):
    def __init__(self, view):
        super().__init__(label="👥 Invite", style=discord.ButtonStyle.blurple, custom_id="party_invite", row=1)
        self.parent_view = view
    
    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.parent_view.user_id:
            await interaction.response.send_message("This isn't your menu!", ephemeral=True)
            return
        
        await interaction.response.send_modal(PartyInviteModal(self.parent_view.bot))

class PartyKickButton(discord.ui.Button):
    def __init__(self, view):
        super().__init__(label="🚫 Kick", style=discord.ButtonStyle.red, custom_id="party_kick", row=1)
        self.parent_view = view
    
    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.parent_view.user_id:
            await interaction.response.send_message("This isn't your menu!", ephemeral=True)
            return
        
        await interaction.response.send_modal(PartyKickModal(self.parent_view.bot))

class PartyDisbandButton(discord.ui.Button):
    def __init__(self, view):
        super().__init__(label="💥 Disband", style=discord.ButtonStyle.red, custom_id="party_disband", row=1)
        self.parent_view = view
    
    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.parent_view.user_id:
            await interaction.response.send_message("This isn't your menu!", ephemeral=True)
            return
        
        result = PartySystem.disband_party(interaction.user.id)
        
        if result['success']:
            embed = discord.Embed(
                title="💥 Party Disbanded",
                description="Your party has been disbanded.",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
        else:
            await interaction.response.send_message(f"❌ {result['error']}", ephemeral=True)

class PartyAcceptButton(discord.ui.Button):
    def __init__(self, view):
        super().__init__(label="Accept", style=discord.ButtonStyle.green, custom_id="party_accept")
        self.parent_view = view
    
    async def callback(self, interaction: discord.Interaction):
        from discord.ui import Button
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
                if isinstance(child, Button):
                    child.disabled = True
            
            await interaction.response.edit_message(embed=embed, view=self.parent_view)
        else:
            await interaction.response.send_message(f"❌ {result['error']}", ephemeral=True)

class PartyDeclineButton(discord.ui.Button):
    def __init__(self, view):
        super().__init__(label="Decline", style=discord.ButtonStyle.red, custom_id="party_decline")
        self.parent_view = view
    
    async def callback(self, interaction: discord.Interaction):
        from discord.ui import Button
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
            if isinstance(child, Button):
                child.disabled = True
        
        await interaction.response.edit_message(embed=embed, view=self.parent_view)
