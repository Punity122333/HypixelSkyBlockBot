import discord

class ProgressionMainButton(discord.ui.Button):
    def __init__(self, view):
        super().__init__(label="🏠 Overview", style=discord.ButtonStyle.blurple, custom_id="progression_main", row=0)
        self.parent_view = view
    
    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.parent_view.user_id:
            await interaction.response.send_message("This menu is not for you!", ephemeral=True)
            return
        
        self.parent_view.current_view = 'main'
        self.parent_view._update_buttons()
        await interaction.response.edit_message(embed=await self.parent_view.get_embed(), view=self.parent_view)

class ProgressionMilestonesButton(discord.ui.Button):
    def __init__(self, view):
        super().__init__(label="🏆 Milestones", style=discord.ButtonStyle.green, custom_id="progression_milestones", row=0)
        self.parent_view = view
    
    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.parent_view.user_id:
            await interaction.response.send_message("This menu is not for you!", ephemeral=True)
            return
        
        self.parent_view.current_view = 'milestones'
        self.parent_view._update_buttons()
        await interaction.response.edit_message(embed=await self.parent_view.get_embed(), view=self.parent_view)

class ProgressionToolsButton(discord.ui.Button):
    def __init__(self, view):
        super().__init__(label="🛠️ Tools", style=discord.ButtonStyle.gray, custom_id="progression_tools", row=0)
        self.parent_view = view
    
    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.parent_view.user_id:
            await interaction.response.send_message("This menu is not for you!", ephemeral=True)
            return
        
        self.parent_view.current_view = 'tools'
        self.parent_view._update_buttons()
        await interaction.response.edit_message(embed=await self.parent_view.get_embed(), view=self.parent_view)

class ProgressionStatsButton(discord.ui.Button):
    def __init__(self, view):
        super().__init__(label="📊 Stats", style=discord.ButtonStyle.gray, custom_id="progression_stats", row=0)
        self.parent_view = view
    
    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.parent_view.user_id:
            await interaction.response.send_message("This menu is not for you!", ephemeral=True)
            return
        
        self.parent_view.current_view = 'stats'
        self.parent_view._update_buttons()
        await interaction.response.edit_message(embed=await self.parent_view.get_embed(), view=self.parent_view)
