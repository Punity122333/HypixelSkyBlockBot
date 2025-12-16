import discord
from components.modals.achievements_category_modal import AchievementsCategoryModal

class AchievementsMainButton(discord.ui.Button):
    def __init__(self, view):
        super().__init__(label="Main", style=discord.ButtonStyle.primary, emoji="🏠", row=0)
        self.parent_view = view
    
    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.parent_view.user_id:
            await interaction.response.send_message("This isn't your menu!", ephemeral=True)
            return
        
        self.parent_view.current_view = 'main'
        self.parent_view.page = 0
        self.parent_view._update_buttons()
        embed = await self.parent_view.get_embed()
        await interaction.response.edit_message(embed=embed, view=self.parent_view)

class AchievementsCategoryButton(discord.ui.Button):
    def __init__(self, view):
        super().__init__(label="Category", style=discord.ButtonStyle.green, emoji="📂", row=0)
        self.parent_view = view
    
    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.parent_view.user_id:
            await interaction.response.send_message("This isn't your menu!", ephemeral=True)
            return
        
        modal = AchievementsCategoryModal(self.parent_view)
        await interaction.response.send_modal(modal)

class AchievementsLeaderboardButton(discord.ui.Button):
    def __init__(self, view):
        super().__init__(label="Leaderboard", style=discord.ButtonStyle.blurple, emoji="🏆", row=0)
        self.parent_view = view
    
    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.parent_view.user_id:
            await interaction.response.send_message("This isn't your menu!", ephemeral=True)
            return
        
        self.parent_view.current_view = 'leaderboard'
        self.parent_view.page = 0
        self.parent_view._update_buttons()
        embed = await self.parent_view.get_embed()
        await interaction.response.edit_message(embed=embed, view=self.parent_view)

class AchievementsPreviousButton(discord.ui.Button):
    def __init__(self, view):
        super().__init__(label="◀️ Previous", style=discord.ButtonStyle.gray, row=1)
        self.parent_view = view
    
    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.parent_view.user_id:
            await interaction.response.send_message("This isn't your menu!", ephemeral=True)
            return
        
        if self.parent_view.page > 0:
            self.parent_view.page -= 1
        self.parent_view._update_buttons()
        embed = await self.parent_view.get_embed()
        await interaction.response.edit_message(embed=embed, view=self.parent_view)

class AchievementsNextButton(discord.ui.Button):
    def __init__(self, view):
        super().__init__(label="Next ▶️", style=discord.ButtonStyle.gray, row=1)
        self.parent_view = view
    
    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.parent_view.user_id:
            await interaction.response.send_message("This isn't your menu!", ephemeral=True)
            return
        
        self.parent_view.page += 1
        self.parent_view._update_buttons()
        embed = await self.parent_view.get_embed()
        await interaction.response.edit_message(embed=embed, view=self.parent_view)
