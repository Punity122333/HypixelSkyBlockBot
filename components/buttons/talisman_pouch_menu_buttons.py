import discord
from components.modals.talisman_add_modal import TalismanAddModal
from components.modals.talisman_remove_modal import TalismanRemoveModal

class TalismanMainButton(discord.ui.Button):
    def __init__(self, view):
        super().__init__(label="🏠 Main", style=discord.ButtonStyle.blurple, custom_id="talisman_main", row=0)
        self.parent_view = view
    
    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.parent_view.user_id:
            await interaction.response.send_message("This isn't your menu!", ephemeral=True)
            return
        
        self.parent_view.current_view = 'main'
        self.parent_view.page = 0
        self.parent_view._update_buttons()
        await interaction.response.edit_message(embed=await self.parent_view.get_embed(), view=self.parent_view)

class TalismanAddButton(discord.ui.Button):
    def __init__(self, view):
        super().__init__(label="➕ Add", style=discord.ButtonStyle.green, custom_id="talisman_add", row=0)
        self.parent_view = view
    
    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.parent_view.user_id:
            await interaction.response.send_message("This isn't your menu!", ephemeral=True)
            return
        
        from utils.helper import show_talisman_select
        await show_talisman_select(interaction)

class TalismanRemoveButton(discord.ui.Button):
    def __init__(self, view):
        super().__init__(label="➖ Remove", style=discord.ButtonStyle.red, custom_id="talisman_remove", row=0)
        self.parent_view = view
    
    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.parent_view.user_id:
            await interaction.response.send_message("This isn't your menu!", ephemeral=True)
            return
        
        modal = TalismanRemoveModal(self.parent_view)
        await interaction.response.send_modal(modal)

class TalismanPreviousButton(discord.ui.Button):
    def __init__(self, view):
        super().__init__(label="◀️ Previous", style=discord.ButtonStyle.gray, custom_id="talisman_prev", row=1)
        self.parent_view = view
    
    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.parent_view.user_id:
            await interaction.response.send_message("This isn't your menu!", ephemeral=True)
            return
        
        if self.parent_view.page > 0:
            self.parent_view.page -= 1
        await interaction.response.edit_message(embed=await self.parent_view.get_embed(), view=self.parent_view)

class TalismanNextButton(discord.ui.Button):
    def __init__(self, view):
        super().__init__(label="Next ▶️", style=discord.ButtonStyle.gray, custom_id="talisman_next", row=1)
        self.parent_view = view
    
    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.parent_view.user_id:
            await interaction.response.send_message("This isn't your menu!", ephemeral=True)
            return
        
        if self.parent_view.current_view == 'manage':
            total_pages = (len(self.parent_view.talisman_list) + self.parent_view.items_per_page - 1) // self.parent_view.items_per_page
            if self.parent_view.page < total_pages - 1:
                self.parent_view.page += 1
        
        await interaction.response.edit_message(embed=await self.parent_view.get_embed(), view=self.parent_view)
