import discord
from components.modals.talisman_equip_modal import TalismanEquipModal

class EquipTalismanButton(discord.ui.Button):
    def __init__(self):
        super().__init__(label="📿 Equip Talisman", style=discord.ButtonStyle.green, custom_id="equip_talisman", row=1)
    
    async def callback(self, interaction: discord.Interaction):
        bot = interaction.client
        await interaction.response.send_modal(TalismanEquipModal(bot, interaction.user.id))
