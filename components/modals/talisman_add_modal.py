import discord
from utils.systems.talisman_pouch_system import TalismanPouchSystem
from utils.normalize import normalize_item_id

class TalismanAddModal(discord.ui.Modal, title="Add Talisman to Pouch"):
    talisman_name = discord.ui.TextInput(
        label="Talisman Name",
        placeholder="Enter talisman name...",
        required=True
    )
    
    def __init__(self, parent_view):
        super().__init__()
        self.parent_view = parent_view
    
    async def on_submit(self, interaction: discord.Interaction):
        talisman_id = normalize_item_id(self.talisman_name.value)
        
        result = await TalismanPouchSystem.add_talisman_to_pouch(
            self.parent_view.bot.db,
            self.parent_view.user_id,
            talisman_id
        )
        
        if result['success']:
            await self.parent_view.load_talismans()
            self.parent_view.current_view = 'manage'
            self.parent_view._update_buttons()
            await interaction.response.edit_message(
                embed=await self.parent_view.get_embed(),
                view=self.parent_view
            )
        else:
            await interaction.response.send_message(f"❌ {result['message']}", ephemeral=True)
