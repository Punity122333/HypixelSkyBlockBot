import discord
from discord.ui import Button

class WikiFirstButton(discord.ui.Button):
    def __init__(self, view):
        super().__init__(label="First Page", style=discord.ButtonStyle.secondary, custom_id="wiki_first")
        self.parent_view = view
    
    async def callback(self, interaction: discord.Interaction):
        self.parent_view.current_page = 0
        self.parent_view.update_buttons()
        await interaction.response.edit_message(embed=self.parent_view.get_embed(), view=self.parent_view)

class WikiPreviousButton(discord.ui.Button):
    def __init__(self, view):
        super().__init__(label="Previous", style=discord.ButtonStyle.primary, custom_id="wiki_previous")
        self.parent_view = view
    
    async def callback(self, interaction: discord.Interaction):
        self.parent_view.current_page -= 1
        self.parent_view.update_buttons()
        await interaction.response.edit_message(embed=self.parent_view.get_embed(), view=self.parent_view)

class WikiNextButton(discord.ui.Button):
    def __init__(self, view):
        super().__init__(label="Next", style=discord.ButtonStyle.primary, custom_id="wiki_next")
        self.parent_view = view
    
    async def callback(self, interaction: discord.Interaction):
        self.parent_view.current_page += 1
        self.parent_view.update_buttons()
        await interaction.response.edit_message(embed=self.parent_view.get_embed(), view=self.parent_view)

class WikiLastButton(discord.ui.Button):
    def __init__(self, view):
        super().__init__(label="Last Page", style=discord.ButtonStyle.secondary, custom_id="wiki_last")
        self.parent_view = view
    
    async def callback(self, interaction: discord.Interaction):
        self.parent_view.current_page = len(self.parent_view.pages) - 1
        self.parent_view.update_buttons()
        await interaction.response.edit_message(embed=self.parent_view.get_embed(), view=self.parent_view)

