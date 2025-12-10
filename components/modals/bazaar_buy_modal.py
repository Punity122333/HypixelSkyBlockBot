import discord
from utils.systems.economy_system import EconomySystem
from utils.normalize import normalize_item_id

class BazaarBuyModal(discord.ui.Modal, title="Buy from Bazaar"):
    item_id = discord.ui.TextInput(label="Item ID", placeholder="Enter item ID", required=True)
    amount = discord.ui.TextInput(label="Amount", placeholder="Enter amount to buy", required=True)
    
    def __init__(self, bot):
        super().__init__()
        self.bot = bot
    
    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer()
        try:
            amount = int(self.amount.value)
        except ValueError:
            await interaction.followup.send("❌ Invalid amount!", ephemeral=True)
            return
        
        item_id_normalized = normalize_item_id(self.item_id.value)
        result = await EconomySystem.instant_buy_bazaar(self.bot.db, interaction.user.id, item_id_normalized, amount)
        
        if result['success']:
            from utils.systems.badge_system import BadgeSystem
            profit_check = await self.bot.db.fetchone(
                'SELECT SUM(profit) as total_profit FROM bazaar_flips WHERE user_id = ?',
                (interaction.user.id,)
            )
            if profit_check and profit_check['total_profit'] >= 1000000:
                await BadgeSystem.unlock_badge(self.bot.db, interaction.user.id, 'bazaar_1m_profit')
            
            embed = discord.Embed(title="✅ Purchase Successful!", color=discord.Color.green())
            embed.add_field(name="Item", value=f"{amount}x {item_id_normalized.replace('_', ' ').title()}", inline=True)
            embed.add_field(name="Total Cost", value=f"{result['total_cost']:,} coins", inline=True)
            await interaction.followup.send(embed=embed, ephemeral=True)
        else:
            await interaction.followup.send(f"❌ {result.get('error', 'Transaction failed')}", ephemeral=True)
