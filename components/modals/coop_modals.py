import discord
from utils.systems.coop_system import CoopSystem

class CoopInviteModal(discord.ui.Modal, title="Invite Member"):
    user_id_input = discord.ui.TextInput(
        label="User ID",
        placeholder="Enter user ID to invite",
        required=True,
        max_length=20
    )
    
    def __init__(self, view):
        super().__init__()
        self.parent_view = view
    
    async def on_submit(self, interaction: discord.Interaction):
        try:
            invitee_id = int(self.user_id_input.value)
            
            if not self.parent_view.coop_data:
                await interaction.response.send_message("❌ You're not in a co-op", ephemeral=True)
                return
            
            success = await CoopSystem.invite_member(
                self.parent_view.bot.db,
                self.parent_view.coop_data['id'],
                interaction.user.id,
                invitee_id
            )
            
            if success:
                await self.parent_view.load_coop_data()
                self.parent_view._update_buttons()
                embed = await self.parent_view.get_embed()
                await interaction.response.edit_message(embed=embed, view=self.parent_view)
            else:
                await interaction.response.send_message(
                    "❌ Cannot invite (already in co-op or no permission)",
                    ephemeral=True
                )
                
        except ValueError:
            await interaction.response.send_message("❌ Invalid user ID", ephemeral=True)

class CoopDepositModal(discord.ui.Modal, title="Deposit to Bank"):
    amount_input = discord.ui.TextInput(
        label="Amount",
        placeholder="Enter amount to deposit",
        required=True,
        max_length=15
    )
    
    def __init__(self, view):
        super().__init__()
        self.parent_view = view
    
    async def on_submit(self, interaction: discord.Interaction):
        try:
            amount = int(self.amount_input.value)
            
            if amount <= 0:
                await interaction.response.send_message("❌ Amount must be positive", ephemeral=True)
                return
            
            if not self.parent_view.coop_data:
                await interaction.response.send_message("❌ You're not in a co-op", ephemeral=True)
                return
            
            success = await CoopSystem.deposit_to_bank(
                self.parent_view.bot.db,
                interaction.user.id,
                self.parent_view.coop_data['id'],
                amount
            )
            
            if success:
                await self.parent_view.load_coop_data()
                embed = await self.parent_view.get_embed()
                await interaction.response.edit_message(embed=embed, view=self.parent_view)
            else:
                await interaction.response.send_message("❌ Insufficient funds or bank full", ephemeral=True)
                
        except ValueError:
            await interaction.response.send_message("❌ Invalid amount", ephemeral=True)

class CoopWithdrawModal(discord.ui.Modal, title="Withdraw from Bank"):
    amount_input = discord.ui.TextInput(
        label="Amount",
        placeholder="Enter amount to withdraw",
        required=True,
        max_length=15
    )
    
    def __init__(self, view):
        super().__init__()
        self.parent_view = view
    
    async def on_submit(self, interaction: discord.Interaction):
        try:
            amount = int(self.amount_input.value)
            
            if amount <= 0:
                await interaction.response.send_message("❌ Amount must be positive", ephemeral=True)
                return
            
            if not self.parent_view.coop_data:
                await interaction.response.send_message("❌ You're not in a co-op", ephemeral=True)
                return
            
            success = await CoopSystem.withdraw_from_bank(
                self.parent_view.bot.db,
                interaction.user.id,
                self.parent_view.coop_data['id'],
                amount
            )
            
            if success:
                await self.parent_view.load_coop_data()
                embed = await self.parent_view.get_embed()
                await interaction.response.edit_message(embed=embed, view=self.parent_view)
            else:
                await interaction.response.send_message("❌ Insufficient funds in bank or no permission", ephemeral=True)
                
        except ValueError:
            await interaction.response.send_message("❌ Invalid amount", ephemeral=True)
