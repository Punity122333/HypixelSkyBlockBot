import discord
from components.modals.museum_donate_modal import MuseumDonateModal


class MuseumMainButton(discord.ui.Button):
    def __init__(self, view):
        super().__init__(label="Main", style=discord.ButtonStyle.primary, emoji="🏛️")
        self.parent_view = view
    
    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.parent_view.user_id:
            await interaction.response.send_message("This isn't your museum!", ephemeral=True)
            return
        
        self.parent_view.current_view = 'main'
        self.parent_view._update_buttons()
        embed = await self.parent_view.get_embed()
        await interaction.response.edit_message(embed=embed, view=self.parent_view)


class MuseumCollectionButton(discord.ui.Button):
    def __init__(self, view):
        super().__init__(label="Collection", style=discord.ButtonStyle.secondary, emoji="📦")
        self.parent_view = view
    
    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.parent_view.user_id:
            await interaction.response.send_message("This isn't your museum!", ephemeral=True)
            return
        
        self.parent_view.current_view = 'collection'
        self.parent_view._update_buttons()
        embed = await self.parent_view.get_embed()
        await interaction.response.edit_message(embed=embed, view=self.parent_view)


class MuseumDonateButton(discord.ui.Button):
    def __init__(self, view):
        super().__init__(label="Donate", style=discord.ButtonStyle.success, emoji="🎁")
        self.parent_view = view
    
    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.parent_view.user_id:
            await interaction.response.send_message("This isn't your museum!", ephemeral=True)
            return
        
        modal = MuseumDonateModal(self.parent_view.bot, self.parent_view)
        await interaction.response.send_modal(modal)


class MuseumMilestonesButton(discord.ui.Button):
    def __init__(self, view):
        super().__init__(label="Milestones", style=discord.ButtonStyle.secondary, emoji="🏆")
        self.parent_view = view
    
    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.parent_view.user_id:
            await interaction.response.send_message("This isn't your museum!", ephemeral=True)
            return
        
        self.parent_view.current_view = 'milestones'
        self.parent_view._update_buttons()
        embed = await self.parent_view.get_embed()
        await interaction.response.edit_message(embed=embed, view=self.parent_view)


class MuseumLeaderboardButton(discord.ui.Button):
    def __init__(self, view):
        super().__init__(label="Leaderboard", style=discord.ButtonStyle.secondary, emoji="🥇")
        self.parent_view = view
    
    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.parent_view.user_id:
            await interaction.response.send_message("This isn't your museum!", ephemeral=True)
            return
        
        self.parent_view.current_view = 'leaderboard'
        await self.parent_view.load_data()
        self.parent_view._update_buttons()
        embed = await self.parent_view.get_embed()
        await interaction.response.edit_message(embed=embed, view=self.parent_view)


class MuseumRefreshButton(discord.ui.Button):
    def __init__(self, view):
        super().__init__(label="Refresh", style=discord.ButtonStyle.gray, emoji="🔄")
        self.parent_view = view
    
    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.parent_view.user_id:
            await interaction.response.send_message("This isn't your museum!", ephemeral=True)
            return
        
        await self.parent_view.load_data()
        self.parent_view._update_buttons()
        embed = await self.parent_view.get_embed()
        await interaction.response.edit_message(embed=embed, view=self.parent_view)
