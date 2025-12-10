import discord
from components.modals.merchant_deal_modal import MerchantDealModal

class MerchantPreviousButton(discord.ui.Button):
    def __init__(self, view):
        super().__init__(label="Previous", style=discord.ButtonStyle.primary, custom_id="merchant_previous", row=0)
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

class MerchantNextButton(discord.ui.Button):
    def __init__(self, view):
        super().__init__(label="Next", style=discord.ButtonStyle.primary, custom_id="merchant_next", row=0)
        self.parent_view = view
    
    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.parent_view.user_id:
            await interaction.response.send_message("This isn't your menu!", ephemeral=True)
            return
        
        per_page = 3
        total_pages = (len(self.parent_view.deals) + per_page - 1) // per_page
        if self.parent_view.page < total_pages - 1:
            self.parent_view.page += 1
            await interaction.response.edit_message(embed=await self.parent_view.get_embed(), view=self.parent_view)
        else:
            await interaction.response.defer()

class MerchantRefreshButton(discord.ui.Button):
    def __init__(self, view):
        super().__init__(label="🔄 Refresh", style=discord.ButtonStyle.blurple, custom_id="merchant_refresh", row=0)
        self.parent_view = view
    
    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.parent_view.user_id:
            await interaction.response.send_message("This isn't your menu!", ephemeral=True)
            return
        
        await self.parent_view.load_deals()
        await interaction.response.edit_message(embed=await self.parent_view.get_embed(), view=self.parent_view)

class MerchantAcceptButton(discord.ui.Button):
    def __init__(self, view):
        super().__init__(label="✅ Accept Deal", style=discord.ButtonStyle.green, custom_id="merchant_accept", row=1)
        self.parent_view = view
    
    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.parent_view.user_id:
            await interaction.response.send_message("This isn't your menu!", ephemeral=True)
            return
        
        await interaction.response.send_modal(MerchantDealModal(self.parent_view.bot))
