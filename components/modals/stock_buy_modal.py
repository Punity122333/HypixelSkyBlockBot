import discord

class StockBuyModal(discord.ui.Modal, title="Buy Stock"):
    symbol = discord.ui.TextInput(label="Stock Symbol", placeholder="e.g., ENCH", required=True)
    shares = discord.ui.TextInput(label="Shares", placeholder="Number of shares", required=True)
    
    def __init__(self, bot):
        super().__init__()
        self.bot = bot
    
    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer()
        symbol = self.symbol.value.upper()
        try:
            shares = int(self.shares.value)
        except ValueError:
            await interaction.followup.send("❌ Invalid number of shares!", ephemeral=True)
            return
        
        player = await self.bot.player_manager.get_or_create_player(interaction.user.id, interaction.user.name)
        stock = await self.bot.db.get_stock(symbol)
        if not stock:
            await interaction.followup.send("❌ Invalid stock symbol!", ephemeral=True)
            return
        total_cost = int(stock['current_price'] * shares)
        if player['coins'] < total_cost:
            await interaction.followup.send(f"❌ Not enough coins! Need {total_cost:,} coins.", ephemeral=True)
            return
        success = await self.bot.db.buy_stock(interaction.user.id, symbol, shares, stock['current_price'])
        if success:
            embed = discord.Embed(
                title="✅ Stock Purchase Complete!",
                color=discord.Color.green()
            )
            embed.add_field(name=f"Bought {shares} shares of {symbol}", value="\u200b", inline=False)
            embed.add_field(name="Price per Share", value=f"${stock['current_price']:.2f}", inline=True)
            embed.add_field(name="Total Cost", value=f"{total_cost:,} coins", inline=True)
            await interaction.followup.send(embed=embed, ephemeral=True)
        else:
            await interaction.followup.send("❌ Purchase failed!", ephemeral=True)