import discord
from utils.systems.coop_system import CoopSystem
from utils.systems.badge_system import BadgeSystem

class CoopCreateModal(discord.ui.Modal, title="Create Co-op"):
    coop_name = discord.ui.TextInput(
        label="Co-op Name",
        placeholder="Enter a name for your co-op",
        required=True,
        max_length=50
    )
    
    def __init__(self, view):
        super().__init__()
        self.parent_view = view
    
    async def on_submit(self, interaction: discord.Interaction):
        try:
            coop_id = await CoopSystem.create_coop(
                self.parent_view.bot.db,
                interaction.user.id,
                self.coop_name.value
            )
            
            await BadgeSystem.unlock_badge(self.parent_view.bot.db, interaction.user.id, 'coop_founder')
            
            await self.parent_view.load_coop_data()
            self.parent_view._update_buttons()
            embed = await self.parent_view.get_embed()
            await interaction.response.edit_message(embed=embed, view=self.parent_view)
            
        except Exception as e:
            await interaction.response.send_message(f"❌ Failed to create co-op: {str(e)}", ephemeral=True)
