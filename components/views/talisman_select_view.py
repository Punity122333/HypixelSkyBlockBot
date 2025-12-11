import discord
from components.modals.talisman_select_modal import TalismanSelectModal

class TalismanSelectView(discord.ui.View):
    def __init__(self, bot, user_id, talismans):
        super().__init__(timeout=60)
        self.bot = bot
        self.user_id = user_id
        self.talismans = talismans
        
        choose_button = discord.ui.Button(
            label="🔍 Choose Talisman",
            style=discord.ButtonStyle.primary,
            custom_id="choose_talisman"
        )
        choose_button.callback = self.choose_callback
        self.add_item(choose_button)
    
    async def choose_callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("This isn't your menu!", ephemeral=True)
            return
        
        modal = TalismanSelectModal(self.bot, self.user_id, self.talismans)
        await interaction.response.send_modal(modal)
