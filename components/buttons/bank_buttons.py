import discord
from components.modals.deposit_modal import DepositModal
from components.modals.withdraw_modal import WithdrawModal

class BankDepositButton(discord.ui.Button):
    def __init__(self, view):
        super().__init__(label="Deposit", style=discord.ButtonStyle.green, custom_id="bank_deposit", row=0)
        self.parent_view = view
    
    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.parent_view.user_id:
            await interaction.response.send_message("This isn't your menu!", ephemeral=True)
            return
        
        await interaction.response.send_modal(DepositModal(self.parent_view.bot, self.parent_view))

class BankWithdrawButton(discord.ui.Button):
    def __init__(self, view):
        super().__init__(label="Withdraw", style=discord.ButtonStyle.blurple, custom_id="bank_withdraw", row=0)
        self.parent_view = view
    
    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.parent_view.user_id:
            await interaction.response.send_message("This isn't your menu!", ephemeral=True)
            return
        
        await interaction.response.send_modal(WithdrawModal(self.parent_view.bot, self.parent_view))

class BankRefreshButton(discord.ui.Button):
    def __init__(self, view):
        super().__init__(label="Refresh", style=discord.ButtonStyle.gray, custom_id="bank_refresh", row=0)
        self.parent_view = view
    
    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.parent_view.user_id:
            await interaction.response.send_message("This isn't your menu!", ephemeral=True)
            return
        
        await interaction.response.edit_message(embed=await self.parent_view.get_embed(), view=self.parent_view)
