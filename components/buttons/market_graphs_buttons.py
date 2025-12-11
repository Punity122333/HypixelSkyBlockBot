import discord

class MarketGraphsPriceButton(discord.ui.Button):
    def __init__(self, view):
        super().__init__(label="Price History", style=discord.ButtonStyle.primary, emoji="📈")
        self.parent_view = view
    
    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer()
        self.parent_view.current_view = 'price'
        self.parent_view._update_buttons()
        embed, file = await self.parent_view.get_embed()
        if file:
            await interaction.edit_original_response(embed=embed, attachments=[file], view=self.parent_view)
        else:
            await interaction.edit_original_response(embed=embed, attachments=[], view=self.parent_view)

class MarketGraphsNetworthButton(discord.ui.Button):
    def __init__(self, view):
        super().__init__(label="Networth", style=discord.ButtonStyle.success, emoji="💰")
        self.parent_view = view
    
    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer()
        self.parent_view.current_view = 'networth'
        self.parent_view._update_buttons()
        embed, file = await self.parent_view.get_embed()
        if file:
            await interaction.edit_original_response(embed=embed, attachments=[file], view=self.parent_view)
        else:
            await interaction.edit_original_response(embed=embed, attachments=[], view=self.parent_view)

class MarketGraphsFlipsButton(discord.ui.Button):
    def __init__(self, view):
        super().__init__(label="Best Flips", style=discord.ButtonStyle.success, emoji="💹")
        self.parent_view = view
    
    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer()
        self.parent_view.current_view = 'flips'
        self.parent_view._update_buttons()
        embed, file = await self.parent_view.get_embed()
        if file:
            await interaction.edit_original_response(embed=embed, attachments=[file], view=self.parent_view)
        else:
            await interaction.edit_original_response(embed=embed, attachments=[], view=self.parent_view)

class MarketGraphsRefreshButton(discord.ui.Button):
    def __init__(self, view):
        super().__init__(label="Back", style=discord.ButtonStyle.secondary, emoji="◀️")
        self.parent_view = view
    
    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer()
        self.parent_view.current_view = 'main'
        self.parent_view._update_buttons()
        embed, file = await self.parent_view.get_embed()
        await interaction.edit_original_response(embed=embed, attachments=[], view=self.parent_view)
