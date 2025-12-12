import discord

class EconomyMainButton(discord.ui.Button):
    def __init__(self, view):
        super().__init__(label="🏠 Main", style=discord.ButtonStyle.blurple, custom_id="economy_main", row=0)
        self.parent_view = view
    
    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.parent_view.user_id:
            await interaction.response.send_message("This menu is not for you!", ephemeral=True)
            return
        
        self.parent_view.current_view = 'main'
        self.parent_view.page = 0
        self.parent_view._update_buttons()
        await interaction.response.edit_message(embed=await self.parent_view.get_embed(), view=self.parent_view)

class EconomyFlipsButton(discord.ui.Button):
    def __init__(self, view):
        super().__init__(label="💹 Flips", style=discord.ButtonStyle.green, custom_id="economy_flips", row=0)
        self.parent_view = view
    
    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.parent_view.user_id:
            await interaction.response.send_message("This menu is not for you!", ephemeral=True)
            return
        
        self.parent_view.current_view = 'flips'
        self.parent_view.page = 0
        self.parent_view._update_buttons()
        await interaction.response.edit_message(embed=await self.parent_view.get_embed(), view=self.parent_view)

class EconomyTrendsButton(discord.ui.Button):
    def __init__(self, view):
        super().__init__(label="📊 Trends", style=discord.ButtonStyle.gray, custom_id="economy_trends", row=0)
        self.parent_view = view
    
    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.parent_view.user_id:
            await interaction.response.send_message("This menu is not for you!", ephemeral=True)
            return
        
        self.parent_view.current_view = 'trends'
        self.parent_view.page = 0
        self.parent_view._update_buttons()
        await interaction.response.edit_message(embed=await self.parent_view.get_embed(), view=self.parent_view)

class EconomyAuctionsButton(discord.ui.Button):
    def __init__(self, view):
        super().__init__(label="🔨 Auctions", style=discord.ButtonStyle.gray, custom_id="economy_auctions", row=0)
        self.parent_view = view
    
    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.parent_view.user_id:
            await interaction.response.send_message("This menu is not for you!", ephemeral=True)
            return
        
        self.parent_view.current_view = 'auctions'
        self.parent_view.page = 0
        self.parent_view._update_buttons()
        await interaction.response.edit_message(embed=await self.parent_view.get_embed(), view=self.parent_view)

class EconomyStocksButton(discord.ui.Button):
    def __init__(self, view):
        super().__init__(label="📈 Stocks", style=discord.ButtonStyle.gray, custom_id="economy_stocks", row=0)
        self.parent_view = view
    
    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.parent_view.user_id:
            await interaction.response.send_message("This menu is not for you!", ephemeral=True)
            return
        
        self.parent_view.current_view = 'stocks'
        self.parent_view.page = 0
        self.parent_view._update_buttons()
        await interaction.response.edit_message(embed=await self.parent_view.get_embed(), view=self.parent_view)

class EconomyPreviousButton(discord.ui.Button):
    def __init__(self, view):
        super().__init__(label="◀ Previous", style=discord.ButtonStyle.primary, custom_id="economy_previous", row=1)
        self.parent_view = view
    
    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.parent_view.user_id:
            await interaction.response.send_message("This menu is not for you!", ephemeral=True)
            return
        
        if self.parent_view.page > 0:
            self.parent_view.page -= 1
            await interaction.response.edit_message(embed=await self.parent_view.get_embed(), view=self.parent_view)
        else:
            await interaction.response.defer()

class EconomyNextButton(discord.ui.Button):
    def __init__(self, view):
        super().__init__(label="Next ▶", style=discord.ButtonStyle.primary, custom_id="economy_next", row=1)
        self.parent_view = view
    
    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.parent_view.user_id:
            await interaction.response.send_message("This menu is not for you!", ephemeral=True)
            return
        
        self.parent_view.page += 1
        await interaction.response.edit_message(embed=await self.parent_view.get_embed(), view=self.parent_view)
