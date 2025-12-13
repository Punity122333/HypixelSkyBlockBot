import discord
from components.modals.potion_select_modal import PotionSelectModal

class PotionSelectView(discord.ui.View):
    def __init__(self, bot, user_id, potions, parent_view):
        super().__init__(timeout=60)
        self.bot = bot
        self.user_id = user_id
        self.potions = potions
        self.parent_view = parent_view
        
        choose_button = discord.ui.Button(
            label="🧪 Choose Potion",
            style=discord.ButtonStyle.primary,
            custom_id="choose_potion"
        )
        choose_button.callback = self.choose_callback
        self.add_item(choose_button)
    
    async def choose_callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("This isn't your menu!", ephemeral=True)
            return
        
        modal = PotionSelectModal(self.bot, self.user_id, self.potions, self.parent_view)
        await interaction.response.send_modal(modal)
