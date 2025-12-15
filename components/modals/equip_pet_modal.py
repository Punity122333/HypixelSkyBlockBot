import discord

class EquipPetModal(discord.ui.Modal, title="Equip Pet"):
    def __init__(self, bot, user_id):
        super().__init__()
        self.bot = bot
        self.user_id = user_id
    
    async def on_submit(self, interaction: discord.Interaction):
        from utils.helper import show_pet_select
        await show_pet_select(interaction)
