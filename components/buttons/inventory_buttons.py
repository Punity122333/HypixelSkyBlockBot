import discord
from components.buttons.equip_item_button import EquipItemButton
from components.buttons.unequip_item_button import UnequipItemButton
from components.buttons.equip_pet_button import EquipPetButton
from components.buttons.unequip_pet_button import UnequipPetButton

class InventoryButton(discord.ui.Button):
    def __init__(self, view):
        super().__init__(label="🎒 Inventory", style=discord.ButtonStyle.blurple, custom_id="inventory_view", row=0)
        self.parent_view = view
    
    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.parent_view.user_id:
            await interaction.response.send_message("This isn't your menu!", ephemeral=True)
            return
        
        self.parent_view.current_view = 'inventory'
        self.parent_view.page = 0
        self.parent_view._update_buttons()
        await interaction.response.edit_message(embed=await self.parent_view.get_embed(), view=self.parent_view)

class EnderchestButton(discord.ui.Button):
    def __init__(self, view):
        super().__init__(label="📦 Ender Chest", style=discord.ButtonStyle.gray, custom_id="enderchest_view", row=0)
        self.parent_view = view
    
    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.parent_view.user_id:
            await interaction.response.send_message("This isn't your menu!", ephemeral=True)
            return
        
        self.parent_view.current_view = 'enderchest'
        self.parent_view.page = 0
        self.parent_view._update_buttons()
        await interaction.response.edit_message(embed=await self.parent_view.get_embed(), view=self.parent_view)

class WardrobeButton(discord.ui.Button):
    def __init__(self, view):
        super().__init__(label="👔 Wardrobe", style=discord.ButtonStyle.green, custom_id="wardrobe_view", row=0)
        self.parent_view = view
    
    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.parent_view.user_id:
            await interaction.response.send_message("This isn't your menu!", ephemeral=True)
            return
        
        self.parent_view.current_view = 'wardrobe'
        self.parent_view.page = 0
        self.parent_view.wardrobe_page = 1
        
        for item in self.parent_view.children[:]:
            if hasattr(item, 'custom_id') and getattr(item, 'custom_id', None) and getattr(item, 'custom_id', '').startswith(('equip_', 'unequip_')):
                self.parent_view.remove_item(item)
        
        self.parent_view._update_buttons()
        
        if self.parent_view.current_view == 'wardrobe':
            self.parent_view.add_item(EquipItemButton())
            self.parent_view.add_item(UnequipItemButton())
            self.parent_view.add_item(EquipPetButton())
            self.parent_view.add_item(UnequipPetButton())
        
        await interaction.response.edit_message(embed=await self.parent_view.get_embed(), view=self.parent_view)

class AccessoriesButton(discord.ui.Button):
    def __init__(self, view):
        super().__init__(label="💎 Accessories", style=discord.ButtonStyle.gray, custom_id="accessories_view", row=0)
        self.parent_view = view
    
    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.parent_view.user_id:
            await interaction.response.send_message("This isn't your menu!", ephemeral=True)
            return
        
        self.parent_view.current_view = 'accessories'
        self.parent_view.page = 0
        self.parent_view._update_buttons()
        await interaction.response.edit_message(embed=await self.parent_view.get_embed(), view=self.parent_view)

class InventoryPreviousButton(discord.ui.Button):
    def __init__(self, view):
        super().__init__(label="Previous", style=discord.ButtonStyle.primary, custom_id="inventory_previous", row=1)
        self.parent_view = view
    
    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.parent_view.user_id:
            await interaction.response.send_message("This isn't your menu!", ephemeral=True)
            return
        
        if self.parent_view.page > 0:
            self.parent_view.page -= 1
            embed = await self.parent_view.get_embed()
            self.parent_view._update_buttons()
            await interaction.response.edit_message(embed=embed, view=self.parent_view)
        else:
            await interaction.response.defer()

class InventoryNextButton(discord.ui.Button):
    def __init__(self, view):
        super().__init__(label="Next", style=discord.ButtonStyle.primary, custom_id="inventory_next", row=1)
        self.parent_view = view
    
    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.parent_view.user_id:
            await interaction.response.send_message("This isn't your menu!", ephemeral=True)
            return
        
        if self.parent_view.page < self.parent_view.total_pages - 1:
            self.parent_view.page += 1
            embed = await self.parent_view.get_embed()
            self.parent_view._update_buttons()
            await interaction.response.edit_message(embed=embed, view=self.parent_view)
        else:
            await interaction.response.defer()
