import discord
from components.modals.equip_item_modal import EquipItemModal

class EquipItemButton(discord.ui.Button):
    def __init__(self):
        super().__init__(label="⚔️ Equip Item", style=discord.ButtonStyle.green, custom_id="equip_item", row=1)
    
    async def callback(self, interaction: discord.Interaction):
        bot = interaction.client
        await interaction.response.send_modal(EquipItemModal(bot, interaction.user.id))