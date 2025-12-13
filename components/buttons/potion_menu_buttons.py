import discord
from utils.systems.potion_system import PotionSystem
from components.modals.potion_select_modal import PotionSelectModal

class PotionMainButton(discord.ui.Button):
    def __init__(self, view):
        super().__init__(label="🏠 Main", style=discord.ButtonStyle.blurple, custom_id="potion_main", row=0)
        self.parent_view = view
    
    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.parent_view.user_id:
            await interaction.response.send_message("This isn't your menu!", ephemeral=True)
            return
        
        self.parent_view.current_view = 'main'
        self.parent_view.page = 0
        self.parent_view._update_buttons()
        await interaction.response.edit_message(embed=await self.parent_view.get_embed(), view=self.parent_view)

class PotionActiveButton(discord.ui.Button):
    def __init__(self, view):
        super().__init__(label="✨ Active Effects", style=discord.ButtonStyle.green, custom_id="potion_active", row=0)
        self.parent_view = view
    
    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.parent_view.user_id:
            await interaction.response.send_message("This isn't your menu!", ephemeral=True)
            return
        
        await interaction.response.defer()
        
        await self.parent_view.load_active_potions()
        self.parent_view.current_view = 'active'
        self.parent_view.page = 0
        
        self.parent_view._update_buttons()
        await interaction.edit_original_response(embed=await self.parent_view.get_embed(), view=self.parent_view)

class PotionInventoryButton(discord.ui.Button):
    def __init__(self, view):
        super().__init__(label="🧪 My Potions", style=discord.ButtonStyle.gray, custom_id="potion_inventory", row=0)
        self.parent_view = view
    
    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.parent_view.user_id:
            await interaction.response.send_message("This isn't your menu!", ephemeral=True)
            return
        
        await interaction.response.defer()
        
        await self.parent_view.load_potions()
        self.parent_view.current_view = 'inventory'
        self.parent_view.page = 0
        
        self.parent_view._update_buttons()
        await interaction.edit_original_response(embed=await self.parent_view.get_embed(), view=self.parent_view)

class PotionPreviousButton(discord.ui.Button):
    def __init__(self, view):
        super().__init__(label="Previous", style=discord.ButtonStyle.primary, custom_id="potion_previous", row=1)
        self.parent_view = view
    
    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.parent_view.user_id:
            await interaction.response.send_message("This isn't your menu!", ephemeral=True)
            return
        
        if self.parent_view.page > 0:
            self.parent_view.page -= 1
            self.parent_view._update_buttons()
            await interaction.response.edit_message(embed=await self.parent_view.get_embed(), view=self.parent_view)
        else:
            await interaction.response.defer()

class PotionNextButton(discord.ui.Button):
    def __init__(self, view):
        super().__init__(label="Next", style=discord.ButtonStyle.primary, custom_id="potion_next", row=1)
        self.parent_view = view
    
    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.parent_view.user_id:
            await interaction.response.send_message("This isn't your menu!", ephemeral=True)
            return
        
        data_list = []
        if self.parent_view.current_view == 'inventory':
            data_list = self.parent_view.potions_list
        elif self.parent_view.current_view == 'active':
            data_list = self.parent_view.active_list
        
        if data_list:
            total_pages = (len(data_list) + self.parent_view.items_per_page - 1) // self.parent_view.items_per_page
            if self.parent_view.page < total_pages - 1:
                self.parent_view.page += 1
        
        self.parent_view._update_buttons()
        await interaction.response.edit_message(embed=await self.parent_view.get_embed(), view=self.parent_view)

class PotionUseButton(discord.ui.Button):
    def __init__(self, view):
        super().__init__(label="🧪 Use Potion", style=discord.ButtonStyle.green, custom_id="potion_use", row=2)
        self.parent_view = view
    
    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.parent_view.user_id:
            await interaction.response.send_message("This isn't your menu!", ephemeral=True)
            return
        
        if not self.parent_view.potions_list:
            await self.parent_view.load_potions()
        
        if not self.parent_view.potions_list:
            await interaction.response.send_message("❌ You don't have any potions!", ephemeral=True)
            return
        
        modal = PotionSelectModal(self.parent_view.bot, self.parent_view.user_id, self.parent_view.potions_list, self.parent_view)
        await interaction.response.send_modal(modal)
