import discord
import math

class LeaderboardCoinsButton(discord.ui.Button):
    def __init__(self, view):
        super().__init__(label="💰 Coins", style=discord.ButtonStyle.blurple, custom_id="leaderboard_coins", row=0)
        self.parent_view = view
    
    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.parent_view.user_id:
            await interaction.response.send_message("This isn't your menu!", ephemeral=True)
            return
        
        self.parent_view.current_category = 'coins'
        self.parent_view.page = 0
        await self.parent_view.load_data()
        await interaction.response.edit_message(embed=await self.parent_view.get_embed(), view=self.parent_view)

class LeaderboardNetworthButton(discord.ui.Button):
    def __init__(self, view):
        super().__init__(label="💎 Net Worth", style=discord.ButtonStyle.green, custom_id="leaderboard_networth", row=0)
        self.parent_view = view
    
    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.parent_view.user_id:
            await interaction.response.send_message("This isn't your menu!", ephemeral=True)
            return
        
        self.parent_view.current_category = 'networth'
        self.parent_view.page = 0
        await self.parent_view.load_data()
        await interaction.response.edit_message(embed=await self.parent_view.get_embed(), view=self.parent_view)

class LeaderboardSkillsButton(discord.ui.Button):
    def __init__(self, view):
        super().__init__(label="📚 Skills", style=discord.ButtonStyle.gray, custom_id="leaderboard_skills", row=0)
        self.parent_view = view
    
    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.parent_view.user_id:
            await interaction.response.send_message("This isn't your menu!", ephemeral=True)
            return
        
        self.parent_view.current_category = 'skill_avg'
        self.parent_view.page = 0
        await self.parent_view.load_data()
        await interaction.response.edit_message(embed=await self.parent_view.get_embed(), view=self.parent_view)

class LeaderboardPreviousButton(discord.ui.Button):
    def __init__(self, view):
        super().__init__(label="Previous", style=discord.ButtonStyle.primary, custom_id="leaderboard_previous", row=1)
        self.parent_view = view
    
    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.parent_view.user_id:
            await interaction.response.send_message("This isn't your menu!", ephemeral=True)
            return
        
        if self.parent_view.page > 0:
            self.parent_view.page -= 1
            await interaction.response.edit_message(embed=await self.parent_view.get_embed(), view=self.parent_view)
        else:
            await interaction.response.defer()

class LeaderboardNextButton(discord.ui.Button):
    def __init__(self, view):
        super().__init__(label="Next", style=discord.ButtonStyle.primary, custom_id="leaderboard_next", row=1)
        self.parent_view = view
    
    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.parent_view.user_id:
            await interaction.response.send_message("This isn't your menu!", ephemeral=True)
            return
        
        total_pages = math.ceil(len(self.parent_view.data) / self.parent_view.items_per_page) if self.parent_view.data else 1
        if self.parent_view.page < total_pages - 1:
            self.parent_view.page += 1
            await interaction.response.edit_message(embed=await self.parent_view.get_embed(), view=self.parent_view)
        else:
            await interaction.response.defer()
