import discord
from utils.systems.economy_system import EconomySystem

class AuctionBidModal(discord.ui.Modal, title="Place Bid"):
    auction_id = discord.ui.TextInput(label="Auction ID", placeholder="Enter auction ID", required=True)
    bid_amount = discord.ui.TextInput(label="Bid Amount", placeholder="Enter your bid", required=True)
    
    def __init__(self, bot):
        super().__init__()
        self.bot = bot
    
    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer()
        try:
            auction_id = int(self.auction_id.value)
            bid_amount = int(self.bid_amount.value)
        except ValueError:
            await interaction.followup.send("❌ Invalid input values!", ephemeral=True)
            return
        
        result = await EconomySystem.place_bid(self.bot.db, interaction.user.id, auction_id, bid_amount)
        
        if result['success']:
            embed = discord.Embed(title="✅ Bid Placed!", color=discord.Color.green())
            embed.add_field(name="Auction", value=f"#{auction_id}", inline=True)
            embed.add_field(name="Bid Amount", value=f"{bid_amount:,} coins", inline=True)
            await interaction.followup.send(embed=embed, ephemeral=True)
        else:
            await interaction.followup.send(f"❌ {result.get('error', 'Bid failed')}", ephemeral=True)