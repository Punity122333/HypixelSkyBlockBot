import discord
from components.modals.pet_select_modal import PetSelectModal

class PetSelectView(discord.ui.View):
    def __init__(self, bot, user_id, pets):
        super().__init__(timeout=60)
        self.bot = bot
        self.user_id = user_id
        self.pets = pets

        choose_button = discord.ui.Button(
            label="🐾 Choose Pet",
            style=discord.ButtonStyle.primary,
            custom_id="choose_pet"
        )
        choose_button.callback = self.choose_callback
        self.add_item(choose_button)
    
    async def choose_callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("This isn't your menu!", ephemeral=True)
            return
        
        modal = PetSelectModal(self.bot, self.user_id, self.pets)
        await interaction.response.send_modal(modal)
