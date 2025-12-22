import discord
class DepositModal(discord.ui.Modal, title="Deposit Coins"):
    amount = discord.ui.TextInput(label="Amount", placeholder="Enter amount to deposit", required=True)
    
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
        if player['coins'] < amount:
            await interaction.response.send_message("❌ You don't have enough coins!", ephemeral=True)
            return
        
        await self.bot.db.players.update_player(
            interaction.user.id,
            coins=player['coins'] - amount,
            bank=player['bank'] + amount
        )
        
        from utils.systems.badge_system import BadgeSystem
        new_bank = player['bank'] + amount
        if new_bank >= 1000000:
            await BadgeSystem.unlock_badge(self.bot.db, interaction.user.id, 'bank_1m')
        
        from utils.systems.achievement_system import AchievementSystem
        await AchievementSystem.check_bank_balance_achievements(self.bot.db, interaction, interaction.user.id, new_bank)
        
        embed = await self.view.get_embed()
        await interaction.response.send_message(f"✅ Deposited {amount:,} coins to your bank!", ephemeral=True)
