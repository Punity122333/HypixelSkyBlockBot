import discord
from components.modals.quest_claim_modal import QuestClaimModal

class QuestActiveButton(discord.ui.Button):
    def __init__(self, view):
        style = discord.ButtonStyle.primary if view.current_view == 'active' else discord.ButtonStyle.secondary
        super().__init__(label="Active", style=style, custom_id="quest_active", row=0)
        self.parent_view = view
    
    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.parent_view.user_id:
            await interaction.response.send_message("This is not your quest menu!", ephemeral=True)
            return
        
        self.parent_view.current_view = 'active'
        self.parent_view.page = 0
        self.parent_view._update_buttons()
        embed = await self.parent_view.get_embed()
        await interaction.response.edit_message(embed=embed, view=self.parent_view)

class QuestCompletedButton(discord.ui.Button):
    def __init__(self, view):
        style = discord.ButtonStyle.primary if view.current_view == 'completed' else discord.ButtonStyle.secondary
        super().__init__(label="Completed", style=style, custom_id="quest_completed", row=0)
        self.parent_view = view
    
    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.parent_view.user_id:
            await interaction.response.send_message("This is not your quest menu!", ephemeral=True)
            return
        
        self.parent_view.current_view = 'completed'
        self.parent_view.page = 0
        self.parent_view._update_buttons()
        embed = await self.parent_view.get_embed()
        await interaction.response.edit_message(embed=embed, view=self.parent_view)

class QuestPreviousButton(discord.ui.Button):
    def __init__(self, view):
        super().__init__(label="Previous", style=discord.ButtonStyle.secondary, custom_id="quest_prev", row=1, disabled=view.page == 0)
        self.parent_view = view
    
    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.parent_view.user_id:
            await interaction.response.send_message("This is not your quest menu!", ephemeral=True)
            return
        
        self.parent_view.page = max(0, self.parent_view.page - 1)
        self.parent_view._update_buttons()
        embed = await self.parent_view.get_embed()
        await interaction.response.edit_message(embed=embed, view=self.parent_view)

class QuestNextButton(discord.ui.Button):
    def __init__(self, view):
        data_list = view.active_quests if view.current_view == 'active' else view.completed_quests
        total_pages = (len(data_list) + view.items_per_page - 1) // view.items_per_page if data_list else 1
        super().__init__(label="Next", style=discord.ButtonStyle.secondary, custom_id="quest_next", row=1, disabled=view.page >= total_pages - 1)
        self.parent_view = view
    
    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.parent_view.user_id:
            await interaction.response.send_message("This is not your quest menu!", ephemeral=True)
            return
        
        data_list = self.parent_view.active_quests if self.parent_view.current_view == 'active' else self.parent_view.completed_quests
        total_pages = (len(data_list) + self.parent_view.items_per_page - 1) // self.parent_view.items_per_page if data_list else 1
        self.parent_view.page = min(total_pages - 1, self.parent_view.page + 1)
        self.parent_view._update_buttons()
        embed = await self.parent_view.get_embed()
        await interaction.response.edit_message(embed=embed, view=self.parent_view)

class QuestClaimButton(discord.ui.Button):
    def __init__(self, view):
        super().__init__(label="Claim Quest", style=discord.ButtonStyle.success, custom_id="quest_claim", row=2)
        self.parent_view = view
    
    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.parent_view.user_id:
            await interaction.response.send_message("This is not your quest menu!", ephemeral=True)
            return
        
        await interaction.response.send_modal(QuestClaimModal(self.parent_view))
