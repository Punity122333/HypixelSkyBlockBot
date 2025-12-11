import discord

class TalismanEquipModal(discord.ui.Modal, title="Equip Talismans"):
    def __init__(self, bot, user_id):
        super().__init__()
        self.bot = bot
        self.user_id = user_id
    
    async def on_submit(self, interaction: discord.Interaction):
        from utils.helper import show_talisman_select
        await show_talisman_select(interaction)
