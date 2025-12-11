import discord
from utils.systems.talisman_pouch_system import TalismanPouchSystem

class TalismanRemoveModal(discord.ui.Modal, title="Remove Talisman from Pouch"):
    slot_number = discord.ui.TextInput(
        label="Slot Number",
        placeholder="Enter slot number to remove...",
        required=True
    )
    
    def __init__(self, parent_view):
        super().__init__()
        self.parent_view = parent_view
    
    async def on_submit(self, interaction: discord.Interaction):
        try:
            slot = int(self.slot_number.value) - 1
        except ValueError:
            await interaction.response.send_message("❌ Invalid slot number!", ephemeral=True)
            return
        
        result = await TalismanPouchSystem.remove_talisman_from_pouch(
            self.parent_view.bot.db,
            self.parent_view.user_id,
            slot
        )
        
        if result['success']:
            await self.parent_view.load_talismans()
            self.parent_view.current_view = 'manage'
            self.parent_view._update_buttons()
            talisman_id = result['talisman_id']
            item = await self.parent_view.bot.game_data.get_item(talisman_id)
            item_name = item.name if item else talisman_id
            await interaction.response.edit_message(
                embed=await self.parent_view.get_embed(),
                view=self.parent_view
            )
        else:
            await interaction.response.send_message(f"❌ {result['message']}", ephemeral=True)
