import discord
from utils.systems.economy_system import EconomySystem
from utils.normalize import normalize_item_id
from utils.helper import is_item_bazaar_tradeable

class BazaarOrderModal(discord.ui.Modal, title="Place Bazaar Order"):
    order_type = discord.ui.TextInput(label="Order Type (BUY or SELL)", placeholder="BUY or SELL", required=True)
    item_id = discord.ui.TextInput(label="Item ID", placeholder="Enter item ID", required=True)
    price = discord.ui.TextInput(label="Price per item", placeholder="Enter price", required=True)
    amount = discord.ui.TextInput(label="Amount", placeholder="Enter amount", required=True)
    
    def __init__(self, bot):
        super().__init__()
        self.bot = bot
    
    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer()
        try:
            amount = int(self.amount.value)
            price = float(self.price.value)
        except ValueError:
            await interaction.followup.send("❌ Invalid amount or price!", ephemeral=True)
            return
        
        order_type = self.order_type.value.upper()
        if order_type not in ['BUY', 'SELL']:
            await interaction.followup.send("❌ Order type must be BUY or SELL!", ephemeral=True)
            return
        
        item_id_normalized = normalize_item_id(self.item_id.value)
        
        can_trade, reason = await is_item_bazaar_tradeable(self.bot.db, item_id_normalized)
        if not can_trade:
            await interaction.followup.send(f"❌ {reason}", ephemeral=True)
            return
        
        result = await EconomySystem.create_bazaar_order(self.bot.db, interaction.user.id, item_id_normalized, order_type, amount, price)
        
        if result['success']:
            stats = await self.bot.db.get_player_stats(interaction.user.id)
            if stats:
                total_bazaar_orders = stats.get('total_bazaar_orders', 0) + 1
                await self.bot.db.update_player_stats(interaction.user.id, total_bazaar_orders=total_bazaar_orders)
                
                from utils.systems.achievement_system import AchievementSystem
                await AchievementSystem.check_bazaar_order_achievements(self.bot.db, interaction, interaction.user.id, total_bazaar_orders)
            
            embed = discord.Embed(title="✅ Order Placed!", color=discord.Color.green())
            embed.add_field(name="Type", value=order_type, inline=True)
            embed.add_field(name="Item", value=f"{amount}x {item_id_normalized.replace('_', ' ').title()}", inline=True)
            embed.add_field(name="Price", value=f"{price:.1f} coins each", inline=True)
            await interaction.followup.send(embed=embed, ephemeral=True)
        else:
            await interaction.followup.send(f"❌ {result.get('error', 'Order failed')}", ephemeral=True)
