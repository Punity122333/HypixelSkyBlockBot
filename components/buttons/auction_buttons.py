import discord
from components.modals.auction_bid_modal import AuctionBidModal
from components.modals.auction_bin_modal import AuctionBINModal
from components.modals.auction_create_modal import AuctionCreateModal

class AuctionBrowseButton(discord.ui.Button):
    def __init__(self, view):
        super().__init__(label="🔨 Browse", style=discord.ButtonStyle.blurple, custom_id="auction_browse", row=0)
        self.parent_view = view
    
    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.parent_view.user_id:
            await interaction.response.send_message("This isn't your menu!", ephemeral=True)
            return
        
        self.parent_view.current_view = 'browse'
        self.parent_view.current_page = 0
        await interaction.response.edit_message(embed=await self.parent_view.get_embed(), view=self.parent_view)

class AuctionMyAuctionsButton(discord.ui.Button):
    def __init__(self, view):
        super().__init__(label="📜 My Auctions", style=discord.ButtonStyle.green, custom_id="auction_my_auctions", row=0)
        self.parent_view = view
    
    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.parent_view.user_id:
            await interaction.response.send_message("This isn't your menu!", ephemeral=True)
            return
        
        self.parent_view.current_view = 'my_auctions'
        self.parent_view.current_page = 0
        await interaction.response.edit_message(embed=await self.parent_view.get_embed(), view=self.parent_view)

class AuctionPreviousButton(discord.ui.Button):
    def __init__(self, view):
        super().__init__(label="Previous", style=discord.ButtonStyle.primary, custom_id="auction_previous", row=1)
        self.parent_view = view
    
    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.parent_view.user_id:
            await interaction.response.send_message("This isn't your menu!", ephemeral=True)
            return
        
        if self.parent_view.current_page > 0:
            self.parent_view.current_page -= 1
            await interaction.response.edit_message(embed=await self.parent_view.get_embed(), view=self.parent_view)
        else:
            await interaction.response.defer()

class AuctionNextButton(discord.ui.Button):
    def __init__(self, view):
        super().__init__(label="Next", style=discord.ButtonStyle.primary, custom_id="auction_next", row=1)
        self.parent_view = view
    
    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.parent_view.user_id:
            await interaction.response.send_message("This isn't your menu!", ephemeral=True)
            return
        
        total_pages = (len(self.parent_view.auctions) + 4) // 5
        if self.parent_view.current_page < total_pages - 1:
            self.parent_view.current_page += 1
            await interaction.response.edit_message(embed=await self.parent_view.get_embed(), view=self.parent_view)
        else:
            await interaction.response.defer()

class AuctionCreateButton(discord.ui.Button):
    def __init__(self, view):
        super().__init__(label="➕ Create", style=discord.ButtonStyle.green, custom_id="auction_create", row=2)
        self.parent_view = view
    
    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.parent_view.user_id:
            await interaction.response.send_message("This isn't your menu!", ephemeral=True)
            return
        
        await interaction.response.send_modal(AuctionCreateModal(self.parent_view.bot))

class AuctionBidButton(discord.ui.Button):
    def __init__(self, view):
        super().__init__(label="💰 Bid", style=discord.ButtonStyle.blurple, custom_id="auction_bid", row=2)
        self.parent_view = view
    
    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.parent_view.user_id:
            await interaction.response.send_message("This isn't your menu!", ephemeral=True)
            return
        
        await interaction.response.send_modal(AuctionBidModal(self.parent_view.bot))

class AuctionBINButton(discord.ui.Button):
    def __init__(self, view):
        super().__init__(label="⚡ Buy Now", style=discord.ButtonStyle.red, custom_id="auction_bin", row=2)
        self.parent_view = view
    
    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.parent_view.user_id:
            await interaction.response.send_message("This isn't your menu!", ephemeral=True)
            return
        
        await interaction.response.send_modal(AuctionBINModal(self.parent_view.bot))
