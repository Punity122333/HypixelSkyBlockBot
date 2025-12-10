import discord
from components.modals.coop_modals import CoopInviteModal, CoopDepositModal, CoopWithdrawModal
from components.modals.coop_create_modal import CoopCreateModal

class CoopCreateButton(discord.ui.Button):
    def __init__(self, view):
        super().__init__(label="Create Co-op", style=discord.ButtonStyle.green, emoji="🤝")
        self.parent_view = view
    
    async def callback(self, interaction: discord.Interaction):
        modal = CoopCreateModal(self.parent_view)
        await interaction.response.send_modal(modal)

class CoopMainButton(discord.ui.Button):
    def __init__(self, view):
        super().__init__(label="Main", style=discord.ButtonStyle.primary, emoji="🏠")
        self.parent_view = view
    
    async def callback(self, interaction: discord.Interaction):
        self.parent_view.current_view = 'main'
        self.parent_view._update_buttons()
        embed = await self.parent_view.get_embed()
        await interaction.response.edit_message(embed=embed, view=self.parent_view)

class CoopMembersButton(discord.ui.Button):
    def __init__(self, view):
        super().__init__(label="Members", style=discord.ButtonStyle.primary, emoji="👥")
        self.parent_view = view
    
    async def callback(self, interaction: discord.Interaction):
        self.parent_view.current_view = 'members'
        self.parent_view._update_buttons()
        embed = await self.parent_view.get_embed()
        await interaction.response.edit_message(embed=embed, view=self.parent_view)

class CoopBankButton(discord.ui.Button):
    def __init__(self, view):
        super().__init__(label="Bank", style=discord.ButtonStyle.primary, emoji="💰")
        self.parent_view = view
    
    async def callback(self, interaction: discord.Interaction):
        self.parent_view.current_view = 'bank'
        self.parent_view._update_buttons()
        embed = await self.parent_view.get_embed()
        await interaction.response.edit_message(embed=embed, view=self.parent_view)

class CoopMinionsButton(discord.ui.Button):
    def __init__(self, view):
        super().__init__(label="Minions", style=discord.ButtonStyle.primary, emoji="⚒️")
        self.parent_view = view
    
    async def callback(self, interaction: discord.Interaction):
        self.parent_view.current_view = 'minions'
        self.parent_view._update_buttons()
        embed = await self.parent_view.get_embed()
        await interaction.response.edit_message(embed=embed, view=self.parent_view)

class CoopInviteButton(discord.ui.Button):
    def __init__(self, view):
        super().__init__(label="Invite Member", style=discord.ButtonStyle.success, emoji="➕")
        self.parent_view = view
    
    async def callback(self, interaction: discord.Interaction):
        modal = CoopInviteModal(self.parent_view)
        await interaction.response.send_modal(modal)

class CoopLeaveButton(discord.ui.Button):
    def __init__(self, view):
        super().__init__(label="Leave Co-op", style=discord.ButtonStyle.danger, emoji="🚪")
        self.parent_view = view
    
    async def callback(self, interaction: discord.Interaction):
        from utils.systems.coop_system import CoopSystem
        
        if not self.parent_view.coop_data:
            await interaction.response.send_message("❌ You're not in a co-op", ephemeral=True)
            return
        
        success = await CoopSystem.leave_coop(
            self.parent_view.bot.db,
            self.parent_view.coop_data['id'],
            self.parent_view.user_id
        )
        
        if success:
            self.parent_view.coop_data = None
            await self.parent_view.load_coop_data()
            self.parent_view._update_buttons()
            embed = await self.parent_view.get_embed()
            await interaction.response.edit_message(embed=embed, view=self.parent_view)
        else:
            await interaction.response.send_message("❌ Cannot leave (owner must transfer or disband)", ephemeral=True)

class CoopDepositButton(discord.ui.Button):
    def __init__(self, view):
        super().__init__(label="Deposit", style=discord.ButtonStyle.success, emoji="💵")
        self.parent_view = view
    
    async def callback(self, interaction: discord.Interaction):
        modal = CoopDepositModal(self.parent_view)
        await interaction.response.send_modal(modal)

class CoopWithdrawButton(discord.ui.Button):
    def __init__(self, view):
        super().__init__(label="Withdraw", style=discord.ButtonStyle.danger, emoji="💸")
        self.parent_view = view
    
    async def callback(self, interaction: discord.Interaction):
        modal = CoopWithdrawModal(self.parent_view)
        await interaction.response.send_modal(modal)

class CoopRefreshButton(discord.ui.Button):
    def __init__(self, view):
        super().__init__(label="Refresh", style=discord.ButtonStyle.secondary, emoji="🔄")
        self.parent_view = view
    
    async def callback(self, interaction: discord.Interaction):
        await self.parent_view.load_coop_data()
        self.parent_view._update_buttons()
        embed = await self.parent_view.get_embed()
        await interaction.response.edit_message(embed=embed, view=self.parent_view)
