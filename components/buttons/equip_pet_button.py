import discord
from components.modals.equip_pet_modal import EquipPetModal

class EquipPetButton(discord.ui.Button):
    def __init__(self):
        super().__init__(label="🐾 Equip Pet", style=discord.ButtonStyle.green, custom_id="equip_pet", row=1)
    
    async def callback(self, interaction: discord.Interaction):
        bot = interaction.client
        await interaction.response.send_modal(EquipPetModal(bot, interaction.user.id))
