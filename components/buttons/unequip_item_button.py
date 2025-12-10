import discord
from components.modals.unequip_item_modal import UnequipItemModal

class UnequipItemButton(discord.ui.Button):
    def __init__(self):
        super().__init__(label="✖️ Unequip Item", style=discord.ButtonStyle.red, custom_id="unequip_item", row=1)
    
    async def callback(self, interaction: discord.Interaction):
        bot = interaction.client
        await interaction.response.send_modal(UnequipItemModal(bot, interaction.user.id))
