import discord

class WithdrawModal(discord.ui.Modal, title="Withdraw Coins"):
    amount = discord.ui.TextInput(label="Amount", placeholder="Enter amount to withdraw", required=True)
    
    def __init__(self, bot, view):
        super().__init__()
        self.bot = bot
        self.view = view
    
    async def on_submit(self, interaction: discord.Interaction):
        try:
            amount = int(self.amount.value)
        except ValueError:
            await interaction.response.send_message("❌ Invalid amount!", ephemeral=True)
            return
        
        player = await self.bot.player_manager.get_or_create_player(interaction.user.id, interaction.user.name)
        
        if amount <= 0:
            await interaction.response.send_message("❌ Amount must be positive!", ephemeral=True)
            return
        if player['bank'] < amount:
            await interaction.response.send_message("❌ You don't have enough coins in your bank!", ephemeral=True)
            return
        
        await self.bot.db.players.update_player(
            interaction.user.id,
            coins=player['coins'] + amount,
            bank=player['bank'] - amount
        )
        
        # Clear cache to ensure fresh data
        self.bot.player_manager.clear_cache(interaction.user.id)
        
        # Update the embed with fresh data
        embed = await self.view.get_embed()
        
        # Send confirmation message
        await interaction.response.send_message(f"✅ Withdrew {amount:,} coins from your bank!", ephemeral=True)
        
        # Update the original bank message if available
        if self.view.message:
            await self.view.message.edit(embed=embed, view=self.view)