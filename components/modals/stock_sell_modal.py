import discord

class StockSellModal(discord.ui.Modal, title="Sell Stock"):
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
        success = await self.bot.db.sell_stock(interaction.user.id, symbol, shares, stock['current_price'])
        if success:
            total_gain = int(stock['current_price'] * shares)
            embed = discord.Embed(
                title="✅ Stock Sale Complete!",
                color=discord.Color.green()
            )
            embed.add_field(name=f"Sold {shares} shares of {symbol}", value="\u200b", inline=False)
            embed.add_field(name="Price per Share", value=f"${stock['current_price']:.2f}", inline=True)
            embed.add_field(name="Total Gained", value=f"{total_gain:,} coins", inline=True)
            await interaction.followup.send(embed=embed, ephemeral=True)
        else:
            await interaction.followup.send("❌ Sale failed! You don't have enough shares.", ephemeral=True)