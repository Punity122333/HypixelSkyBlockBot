import discord
from components.buttons.equip_item_button import EquipItemButton
from components.buttons.unequip_item_button import UnequipItemButton

class ProfileButton(discord.ui.Button):
    def __init__(self, view):
        super().__init__(label="📊 Profile", style=discord.ButtonStyle.blurple, custom_id="profile_view", row=0)
        self.parent_view = view
    
    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.parent_view.user_id:
            await interaction.response.send_message("This isn't your menu!", ephemeral=True)
            return
        
        self.parent_view.current_view = 'profile'
        await interaction.response.edit_message(embed=await self.parent_view.get_embed(), view=self.parent_view)

class DetailedStatsButton(discord.ui.Button):
    def __init__(self, view):
        super().__init__(label="📈 Detailed Stats", style=discord.ButtonStyle.green, custom_id="stats_view", row=0)
        self.parent_view = view
    
    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.parent_view.user_id:
            await interaction.response.send_message("This isn't your menu!", ephemeral=True)
            return
        
        self.parent_view.current_view = 'stats'
        await interaction.response.edit_message(embed=await self.parent_view.get_embed(), view=self.parent_view)

class ProfileWardrobeButton(discord.ui.Button):
    def __init__(self, view):
        super().__init__(label="👔 Wardrobe", style=discord.ButtonStyle.blurple, custom_id="profile_wardrobe", row=0)
        self.parent_view = view
    
    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.parent_view.user_id:
            await interaction.response.send_message("This isn't your menu!", ephemeral=True)
            return
        
        self.parent_view.current_view = 'wardrobe'
        self.parent_view.wardrobe_page = 1
        
        for item in self.parent_view.children[:]:
            if hasattr(item, 'custom_id') and getattr(item, 'custom_id', None) and getattr(item, 'custom_id', '').startswith(('equip_', 'unequip_')):
                self.parent_view.remove_item(item)
        
        if self.parent_view.current_view == 'wardrobe':
            self.parent_view.add_item(EquipItemButton())
            self.parent_view.add_item(UnequipItemButton())
        
        await interaction.response.edit_message(embed=await self.parent_view.get_embed(), view=self.parent_view)

class ProfileTalismanPouchButton(discord.ui.Button):
    def __init__(self, view):
        super().__init__(label="📿 Talismans", style=discord.ButtonStyle.green, custom_id="profile_talisman_pouch", row=1)
        self.parent_view = view
    
    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.parent_view.user_id:
            await interaction.response.send_message("This isn't your menu!", ephemeral=True)
            return
        
        self.parent_view.current_view = 'talisman_pouch'
        await interaction.response.edit_message(embed=await self.parent_view.get_embed(), view=self.parent_view)

