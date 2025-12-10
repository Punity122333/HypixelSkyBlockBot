import discord

class SlayerMainButton(discord.ui.Button):
    def __init__(self, view):
        super().__init__(label="🏠 Main", style=discord.ButtonStyle.blurple, custom_id="slayer_main", row=0)
        self.parent_view = view
    
    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.parent_view.user_id:
            await interaction.response.send_message("This isn't your menu!", ephemeral=True)
            return
        
        self.parent_view.current_view = 'main'
        await interaction.response.edit_message(embed=await self.parent_view.get_embed(), view=self.parent_view)

class SlayerStatsButton(discord.ui.Button):
    def __init__(self, view):
        super().__init__(label="📊 Stats", style=discord.ButtonStyle.green, custom_id="slayer_stats", row=0)
        self.parent_view = view
    
    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.parent_view.user_id:
            await interaction.response.send_message("This isn't your menu!", ephemeral=True)
            return
        
        self.parent_view.current_view = 'stats'
        await interaction.response.edit_message(embed=await self.parent_view.get_embed(), view=self.parent_view)

class SlayerInfoButton(discord.ui.Button):
    def __init__(self, view):
        super().__init__(label="ℹ️ Info", style=discord.ButtonStyle.gray, custom_id="slayer_info", row=0)
        self.parent_view = view
    
    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.parent_view.user_id:
            await interaction.response.send_message("This isn't your menu!", ephemeral=True)
            return
        
        self.parent_view.current_view = 'info'
        await interaction.response.edit_message(embed=await self.parent_view.get_embed(), view=self.parent_view)
