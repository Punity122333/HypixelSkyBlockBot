import discord
from utils.systems.economy_system import EconomySystem

class AuctionBINModal(discord.ui.Modal, title="Buy Instantly"):
    auction_id = discord.ui.TextInput(label="Auction ID", placeholder="Enter auction ID", required=True)
    
    def __init__(self, bot):
        super().__init__()
        self.bot = bot
    
    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer()
        try:
            auction_id = int(self.auction_id.value)
        except ValueError:
            await interaction.followup.send("❌ Invalid auction ID!", ephemeral=True)
            return
        
        result = await EconomySystem.buy_bin(self.bot.db, interaction.user.id, auction_id)
        
        if result['success']:
            embed = discord.Embed(title="✅ Purchase Successful!", color=discord.Color.green())
            embed.add_field(name="Item", value=f"{result['amount']}x {result['item_id'].replace('_', ' ').title()}", inline=True)
            embed.add_field(name="Price", value=f"{result['price']:,} coins", inline=True)
            await interaction.followup.send(embed=embed, ephemeral=True)
        else:
            await interaction.followup.send(f"❌ {result.get('error', 'Purchase failed')}", ephemeral=True)