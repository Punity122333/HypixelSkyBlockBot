import discord
import matplotlib.pyplot as plt
import io

class StockInfoModal(discord.ui.Modal, title="Stock Information"):
    symbol = discord.ui.TextInput(label="Stock Symbol", placeholder="e.g., ENCH", required=True)
    
    def __init__(self, bot):
        super().__init__()
        self.bot = bot
    
    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer()
        symbol = self.symbol.value.upper()
        stock = await self.bot.db.get_stock(symbol)
        if not stock:
            await interaction.followup.send("❌ Invalid stock symbol!", ephemeral=True)
            return

        change = ((stock['current_price'] - stock['opening_price']) / stock['opening_price']) * 100
        emoji = "📈" if change > 0 else "📉" if change < 0 else "➡️"

        embed = discord.Embed(
            title=f"{stock['stock_symbol']} - {stock['company_name']}",
            description=f"Current Price: **${stock['current_price']:.2f}** {emoji}",
            color=discord.Color.blue() if change >= 0 else discord.Color.red()
        )

        fields = {
            "Opening Price": f"${stock['opening_price']:.2f}",
            "Change": f"{change:+.2f}%",
            "Volume": f"{stock['volume']:,}",
            "Daily High": f"${stock['daily_high']:.2f}",
            "Daily Low": f"${stock['daily_low']:.2f}",
            "Market Cap": f"{stock['market_cap']:,} coins",
            "Volatility": f"{stock['volatility']*100:.1f}%"
        }

        for name, value in fields.items():
            embed.add_field(name=name, value=value, inline=True)

        history = await self.bot.db.get_market_history(symbol, 50)
        
        if history and len(history) > 1:
            try:
                plt.style.use('dark_background')
                fig, ax = plt.subplots(figsize=(10, 5))
                
                prices = [h['price'] for h in reversed(history)]
                timestamps = list(range(len(prices)))
                
                ax.plot(timestamps, prices, color='#00ff00' if change >= 0 else '#ff0000', linewidth=2)
                ax.fill_between(timestamps, prices, alpha=0.3, color='#00ff00' if change >= 0 else '#ff0000')
                
                ax.set_title(f"{symbol} Price History", fontsize=14, fontweight='bold')
                ax.set_xlabel("Time", fontsize=10)
                ax.set_ylabel("Price ($)", fontsize=10)
                ax.grid(True, alpha=0.2)
                
                plt.tight_layout()
                
                buffer = io.BytesIO()
                plt.savefig(buffer, format='png', dpi=100, facecolor='#2f3136')
                buffer.seek(0)
                plt.close()
                
                file = discord.File(buffer, filename=f"{symbol}_chart.png")
                embed.set_image(url=f"attachment://{symbol}_chart.png")
                
                await interaction.followup.send(embed=embed, file=file, ephemeral=True)
                return
            except Exception as e:
                print(f"Chart generation error: {e}")
        
        if history:
            history_text = ""
            for h in history[:5]:
                import time
                minutes_ago = (int(time.time()) - h['timestamp']) // 60
                history_text += f"${h['price']:.2f} ({minutes_ago}m ago)\n"
            embed.add_field(name="Recent Prices", value=history_text, inline=False)

        await interaction.followup.send(embed=embed, ephemeral=True)
