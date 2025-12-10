import discord
from components.modals.pet_equip_modal import PetEquipModal
import math

class PetListButton(discord.ui.Button):
    def __init__(self, view):
        super().__init__(label="📜 List", style=discord.ButtonStyle.blurple, custom_id="pet_list", row=0)
        self.parent_view = view
    
    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.parent_view.user_id:
            await interaction.response.send_message("This isn't your menu!", ephemeral=True)
            return
        
        self.parent_view.current_view = 'list'
        self.parent_view.page = 0
        await interaction.response.edit_message(embed=await self.parent_view.get_embed(), view=self.parent_view)

class PetPreviousButton(discord.ui.Button):
    def __init__(self, view):
        super().__init__(label="Previous", style=discord.ButtonStyle.gray, custom_id="pet_previous", row=1)
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

class PetNextButton(discord.ui.Button):
    def __init__(self, view):
        super().__init__(label="Next", style=discord.ButtonStyle.gray, custom_id="pet_next", row=1)
        self.parent_view = view
    
    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.parent_view.user_id:
            await interaction.response.send_message("This isn't your menu!", ephemeral=True)
            return
        
        total_pages = max(1, math.ceil(len(self.parent_view.pets) / self.parent_view.items_per_page))
        if self.parent_view.page < total_pages - 1:
            self.parent_view.page += 1
            await interaction.response.edit_message(embed=await self.parent_view.get_embed(), view=self.parent_view)
        else:
            await interaction.response.defer()

class PetEquipButton(discord.ui.Button):
    def __init__(self, view):
        super().__init__(label="🔧 Equip", style=discord.ButtonStyle.green, custom_id="pet_equip", row=2)
        self.parent_view = view
    
    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.parent_view.user_id:
            await interaction.response.send_message("This isn't your menu!", ephemeral=True)
            return
        
        await interaction.response.send_modal(PetEquipModal(self.parent_view.bot))

class PetUnequipButton(discord.ui.Button):
    def __init__(self, view):
        super().__init__(label="❌ Unequip", style=discord.ButtonStyle.red, custom_id="pet_unequip", row=2)
        self.parent_view = view
    
    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.parent_view.user_id:
            await interaction.response.send_message("This isn't your menu!", ephemeral=True)
            return
        
        active_pet = await self.parent_view.bot.db.get_active_pet(interaction.user.id)
        
        if not active_pet:
            await interaction.response.send_message("❌ You don't have any pet equipped!", ephemeral=True)
            return
        
        await self.parent_view.bot.db.unequip_pet(interaction.user.id)
        
        embed = discord.Embed(
            title="🐾 Pet Unequipped",
            description=f"You unequipped your **{active_pet['rarity']} {active_pet['pet_type'].title()}**!",
            color=discord.Color.greyple()
        )
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
