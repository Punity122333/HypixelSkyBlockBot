import discord
from components.modals.equipment_select_modal import EquipmentSelectModal

class EquipmentSelectView(discord.ui.View):
    def __init__(self, bot, user_id, equipment_slot, items):
        super().__init__(timeout=60)
        self.bot = bot
        self.user_id = user_id
        self.equipment_slot = equipment_slot
        self.items = items

        choose_button = discord.ui.Button(
            label="🔍 Choose Item",
            style=discord.ButtonStyle.primary,
            custom_id="choose_item"
        )
        choose_button.callback = self.choose_callback
        self.add_item(choose_button)
    
    async def choose_callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("This isn't your menu!", ephemeral=True)
            return
        
        modal = EquipmentSelectModal(self.bot, self.user_id, self.equipment_slot, self.items)
        await interaction.response.send_modal(modal)