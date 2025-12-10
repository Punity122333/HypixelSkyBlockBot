import discord
from components.modals.bazaar_buy_modal import BazaarBuyModal
from components.modals.bazaar_sell_modal import BazaarSellModal
from components.modals.bazaar_order_modal import BazaarOrderModal
from components.modals.bazaar_cancel_modal import BazaarCancelModal
from components.modals.bazaar_search_modal import BazaarSearchModal

class BazaarMainButton(discord.ui.Button):
    def __init__(self, view):
        super().__init__(label="🏠 Main", style=discord.ButtonStyle.blurple, custom_id="bazaar_main", row=0)
        self.parent_view = view
    
    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.parent_view.user_id:
            await interaction.response.send_message("This isn't your menu!", ephemeral=True)
            return
        
        self.parent_view.current_view = 'main'
        self.parent_view.page = 0
        self.parent_view.orders_list = []
        self.parent_view.items_list = []
        self.parent_view._update_buttons()
        await interaction.response.edit_message(embed=await self.parent_view.get_embed(), view=self.parent_view)

class BazaarBrowseButton(discord.ui.Button):
    def __init__(self, view):
        super().__init__(label="📋 Browse", style=discord.ButtonStyle.green, custom_id="bazaar_browse", row=0)
        self.parent_view = view
    
    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.parent_view.user_id:
            await interaction.response.send_message("This isn't your menu!", ephemeral=True)
            return
        
        await interaction.response.defer()
        
        if not self.parent_view.items_list:
            await self.parent_view.load_items()
            
        self.parent_view.current_view = 'browse'
        self.parent_view.page = 0
        self.parent_view.orders_list = []
        
        self.parent_view._update_buttons()
        
        await interaction.edit_original_response(embed=await self.parent_view.get_embed(), view=self.parent_view)

class BazaarOrdersButton(discord.ui.Button):
    def __init__(self, view):
        super().__init__(label="📊 My Orders", style=discord.ButtonStyle.gray, custom_id="bazaar_orders", row=0)
        self.parent_view = view
    
    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.parent_view.user_id:
            await interaction.response.send_message("This isn't your menu!", ephemeral=True)
            return
        
        await interaction.response.defer()
        
        if not self.parent_view.orders_list:
            await self.parent_view.load_orders()
            
        self.parent_view.current_view = 'orders'
        self.parent_view.page = 0
        self.parent_view.items_list = []
        self.parent_view._update_buttons()
        await interaction.edit_original_response(embed=await self.parent_view.get_embed(), view=self.parent_view)

class BazaarPreviousButton(discord.ui.Button):
    def __init__(self, view):
        super().__init__(label="Previous", style=discord.ButtonStyle.primary, custom_id="bazaar_previous", row=1)
        self.parent_view = view
    
    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.parent_view.user_id:
            await interaction.response.send_message("This isn't your menu!", ephemeral=True)
            return
        
        data_list = []
        if self.parent_view.current_view == 'browse':
            data_list = self.parent_view.items_list
        elif self.parent_view.current_view == 'orders':
            data_list = self.parent_view.orders_list
        
        if self.parent_view.page > 0 and data_list:
            self.parent_view.page -= 1
            self.parent_view._update_buttons()
            await interaction.response.edit_message(embed=await self.parent_view.get_embed(), view=self.parent_view)
        else:
            await interaction.response.defer()

class BazaarNextButton(discord.ui.Button):
    def __init__(self, view):
        super().__init__(label="Next", style=discord.ButtonStyle.primary, custom_id="bazaar_next", row=1)
        self.parent_view = view
    
    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.parent_view.user_id:
            await interaction.response.send_message("This isn't your menu!", ephemeral=True)
            return
        
        data_list = []
        if self.parent_view.current_view == 'browse':
            data_list = self.parent_view.items_list
        elif self.parent_view.current_view == 'orders':
            data_list = self.parent_view.orders_list
            
        if data_list:
            total_pages = (len(data_list) + self.parent_view.items_per_page - 1) // self.parent_view.items_per_page
            if self.parent_view.page < total_pages - 1:
                self.parent_view.page += 1
                self.parent_view._update_buttons()
                await interaction.response.edit_message(embed=await self.parent_view.get_embed(), view=self.parent_view)
                return
        
        await interaction.response.defer()

class BazaarBuyButton(discord.ui.Button):
    def __init__(self, view):
        super().__init__(label="💰 Buy", style=discord.ButtonStyle.green, custom_id="bazaar_buy", row=2)
        self.parent_view = view
    
    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.parent_view.user_id:
            await interaction.response.send_message("This isn't your menu!", ephemeral=True)
            return
        
        await interaction.response.send_modal(BazaarBuyModal(self.parent_view.bot))

class BazaarSellButton(discord.ui.Button):
    def __init__(self, view):
        super().__init__(label="💸 Sell", style=discord.ButtonStyle.red, custom_id="bazaar_sell", row=2)
        self.parent_view = view
    
    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.parent_view.user_id:
            await interaction.response.send_message("This isn't your menu!", ephemeral=True)
            return
        
        await interaction.response.send_modal(BazaarSellModal(self.parent_view.bot))

class BazaarOrderButton(discord.ui.Button):
    def __init__(self, view):
        super().__init__(label="📝 Order", style=discord.ButtonStyle.blurple, custom_id="bazaar_order", row=2)
        self.parent_view = view
    
    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.parent_view.user_id:
            await interaction.response.send_message("This isn't your menu!", ephemeral=True)
            return
        
        await interaction.response.send_modal(BazaarOrderModal(self.parent_view.bot))

class BazaarCancelButton(discord.ui.Button):
    def __init__(self, view):
        super().__init__(label="❌ Cancel Order", style=discord.ButtonStyle.gray, custom_id="bazaar_cancel", row=2)
        self.parent_view = view
    
    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.parent_view.user_id:
            await interaction.response.send_message("This isn't your menu!", ephemeral=True)
            return
        
        await interaction.response.send_modal(BazaarCancelModal(self.parent_view.bot))

class BazaarSearchButton(discord.ui.Button):
    def __init__(self, view):
        super().__init__(label="🔍 Search", style=discord.ButtonStyle.gray, custom_id="bazaar_search", row=2)
        self.parent_view = view
    
    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.parent_view.user_id:
            await interaction.response.send_message("This isn't your menu!", ephemeral=True)
            return
        
        await interaction.response.send_modal(BazaarSearchModal(self.parent_view.bot, self.parent_view))
