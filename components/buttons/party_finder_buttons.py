import discord
from components.modals.party_finder_modals import PartyFinderCreateModal, PartyFinderJoinModal
from utils.systems.party_system import PartySystem

class PartyFinderListButton(discord.ui.Button):
    def __init__(self, view):
        super().__init__(label="Party List", style=discord.ButtonStyle.primary, emoji="📋")
        self.parent_view = view
    
    async def callback(self, interaction: discord.Interaction):
        self.parent_view.current_view = 'list'
        self.parent_view.page = 0
        await self.parent_view.load_parties()
        self.parent_view._update_buttons()
        embed = await self.parent_view.get_embed()
        await interaction.response.edit_message(embed=embed, view=self.parent_view)

class PartyFinderCreateButton(discord.ui.Button):
    def __init__(self, view):
        super().__init__(label="Create Party", style=discord.ButtonStyle.success, emoji="➕")
        self.parent_view = view
    
    async def callback(self, interaction: discord.Interaction):
        modal = PartyFinderCreateModal(self.parent_view)
        await interaction.response.send_modal(modal)

class PartyFinderJoinButton(discord.ui.Button):
    def __init__(self, view):
        super().__init__(label="Join Party", style=discord.ButtonStyle.primary, emoji="👥")
        self.parent_view = view
    
    async def callback(self, interaction: discord.Interaction):
        modal = PartyFinderJoinModal(self.parent_view)
        await interaction.response.send_modal(modal)

class PartyFinderLeaveButton(discord.ui.Button):
    def __init__(self, view):
        super().__init__(label="Leave Party", style=discord.ButtonStyle.danger, emoji="🚪")
        self.parent_view = view
    
    async def callback(self, interaction: discord.Interaction):
        from utils.systems.party_system import PartySystem
        
        if not self.parent_view.current_party_id:
            await interaction.response.send_message("❌ You're not in a party", ephemeral=True)
            return
        
        result = PartySystem.leave_party(self.parent_view.user_id)
        
        if result['success']:
            self.parent_view.current_party_id = None
            await self.parent_view.load_parties()
            self.parent_view._update_buttons()
            embed = await self.parent_view.get_embed()
            await interaction.response.edit_message(embed=embed, view=self.parent_view)
        else:
            await interaction.response.send_message(f"❌ {result['error']}", ephemeral=True)

class PartyFinderStartButton(discord.ui.Button):
    def __init__(self, view):
        super().__init__(label="Start Dungeon", style=discord.ButtonStyle.success, emoji="🏃")
        self.parent_view = view
    
    async def callback(self, interaction: discord.Interaction):
        from utils.systems.party_system import PartySystem
        
        if not self.parent_view.current_party_id:
            await interaction.response.send_message("❌ You're not in a party", ephemeral=True)
            return
        
        result = await PartySystem.start_dungeon(
            self.parent_view.bot.db,
            self.parent_view.user_id
        )
        
        if result['success']:
            await interaction.response.send_message("✅ Dungeon started! Good luck!", ephemeral=False)
        else:
            await interaction.response.send_message(f"❌ {result['error']}", ephemeral=True)

class PartyFinderRefreshButton(discord.ui.Button):
    def __init__(self, view):
        super().__init__(label="Refresh", style=discord.ButtonStyle.secondary, emoji="🔄")
        self.parent_view = view
    
    async def callback(self, interaction: discord.Interaction):
        await self.parent_view.load_parties()
        self.parent_view._update_buttons()
        embed = await self.parent_view.get_embed()
        await interaction.response.edit_message(embed=embed, view=self.parent_view)

class PartyFinderPreviousButton(discord.ui.Button):
    def __init__(self, view):
        super().__init__(label="Previous", style=discord.ButtonStyle.secondary, emoji="◀️")
        self.parent_view = view
    
    async def callback(self, interaction: discord.Interaction):
        if self.parent_view.page > 0:
            self.parent_view.page -= 1
            embed = await self.parent_view.get_embed()
            await interaction.response.edit_message(embed=embed, view=self.parent_view)
        else:
            await interaction.response.defer()

class PartyFinderNextButton(discord.ui.Button):
    def __init__(self, view):
        super().__init__(label="Next", style=discord.ButtonStyle.secondary, emoji="▶️")
        self.parent_view = view
    
    async def callback(self, interaction: discord.Interaction):
        total_pages = (len(self.parent_view.parties_list) + self.parent_view.items_per_page - 1) // self.parent_view.items_per_page
        if self.parent_view.page < total_pages - 1:
            self.parent_view.page += 1
            embed = await self.parent_view.get_embed()
            await interaction.response.edit_message(embed=embed, view=self.parent_view)
        else:
            await interaction.response.defer()
