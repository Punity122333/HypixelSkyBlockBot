import discord
from discord.ext import commands
from discord import app_commands
from typing import List
import math
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import io
from datetime import datetime

class StockMarketCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def paginate_embed(self, interaction: discord.Interaction, embeds: List[discord.Embed]):
        current = 0
        total = len(embeds)

        class Paginator(discord.ui.View):
            def __init__(self):
                super().__init__(timeout=180)

            @discord.ui.button(label="Previous", style=discord.ButtonStyle.primary)
            async def previous(self, interaction_inner: discord.Interaction, button: discord.ui.Button):
                nonlocal current
                current = (current - 1) % total
                await interaction_inner.response.edit_message(embed=embeds[current], view=self)

            @discord.ui.button(label="Next", style=discord.ButtonStyle.primary)
            async def next(self, interaction_inner: discord.Interaction, button: discord.ui.Button):
                nonlocal current
                current = (current + 1) % total
                await interaction_inner.response.edit_message(embed=embeds[current], view=self)

        # Use followup if interaction has been deferred, otherwise use response
        if interaction.response.is_done():
            await interaction.followup.send(embed=embeds[current], view=Paginator())
        else:
            await interaction.response.send_message(embed=embeds[current], view=Paginator())

    @app_commands.command(name="stocks", description="View the stock market")
    async def stocks(self, interaction: discord.Interaction):
        await interaction.response.defer()
        stocks = await self.bot.db.get_all_stocks()
        
        if not stocks:
            embed = discord.Embed(
                title="📈 SkyBlock Stock Exchange",
                description="No stocks available at the moment.",
                color=discord.Color.blue()
            )
            await interaction.followup.send(embed=embed)
            return
        
        embeds: List[discord.Embed] = []
        per_page = 4
        pages = math.ceil(len(stocks) / per_page)

        for i in range(pages):
            embed = discord.Embed(
                title="📈 SkyBlock Stock Exchange",
                description="Live stock prices and market data",
                color=discord.Color.blue()
            )
            for stock in stocks[i * per_page:(i + 1) * per_page]:
                change = ((stock['current_price'] - stock['opening_price']) / stock['opening_price']) * 100
                emoji = "📈" if change > 0 else "📉" if change < 0 else "➡️"
                value = f"**${stock['current_price']:.2f}** {emoji}\nChange: {change:+.2f}%\nVol: {stock['volume']:,}\nHigh: ${stock['daily_high']:.2f} | Low: ${stock['daily_low']:.2f}"
                embed.add_field(name=f"{stock['symbol']} - {stock['company_name']}", value=value, inline=True)
            embed.set_footer(text="Use /stock_buy or /stock_sell to trade stocks")
            embeds.append(embed)

        await self.paginate_embed(interaction, embeds)

    @app_commands.command(name="portfolio", description="View your stock portfolio")
    async def portfolio(self, interaction: discord.Interaction):
        await interaction.response.defer()
        await self.bot.player_manager.get_or_create_player(interaction.user.id, interaction.user.name)
        stocks = await self.bot.db.get_player_stocks(interaction.user.id)
        embeds: List[discord.Embed] = []
        per_page = 4

        if not stocks:
            embed = discord.Embed(
                title=f"📊 {interaction.user.name}'s Portfolio",
                description="You don't own any stocks yet! Use `/stock_buy` to get started.",
                color=discord.Color.gold()
            )
            embeds.append(embed)
        else:
            pages = math.ceil(len(stocks) / per_page)
            for i in range(pages):
                embed = discord.Embed(
                    title=f"📊 {interaction.user.name}'s Portfolio",
                    description="Your stock holdings and performance",
                    color=discord.Color.gold()
                )
                total_value = 0
                total_invested = 0
                for stock in stocks[i * per_page:(i + 1) * per_page]:
                    current_value = stock['shares'] * stock['current_price']
                    invested_value = stock['shares'] * stock['avg_buy_price']
                    profit = current_value - invested_value
                    profit_percent = (profit / invested_value) * 100 if invested_value > 0 else 0
                    total_value += current_value
                    total_invested += invested_value
                    emoji = "🟢" if profit > 0 else "🔴" if profit < 0 else "⚪"
                    value = f"Shares: {stock['shares']}\nAvg Buy: ${stock['avg_buy_price']:.2f}\nCurrent: ${stock['current_price']:.2f}\nValue: {int(current_value):,} coins\nP/L: {int(profit):,} ({profit_percent:+.2f}%) {emoji}"
                    embed.add_field(name=f"{stock['stock_symbol']} - {stock['company_name']}", value=value, inline=True)
                total_profit = total_value - total_invested
                total_profit_percent = (total_profit / total_invested) * 100 if total_invested > 0 else 0
                summary = f"**Total Value:** {int(total_value):,} coins\n**Total Invested:** {int(total_invested):,} coins\n**Total P/L:** {int(total_profit):,} coins ({total_profit_percent:+.2f}%)"
                embed.add_field(name="Portfolio Summary", value=summary, inline=False)
                embeds.append(embed)

        await self.paginate_embed(interaction, embeds)

    @app_commands.command(name="stock_info", description="Get detailed information about a stock")
    @app_commands.describe(symbol="Stock symbol")
    async def stock_info(self, interaction: discord.Interaction, symbol: str):
        await interaction.response.defer()
        symbol = symbol.upper()
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
                
                await interaction.followup.send(embed=embed, file=file)
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

        await interaction.followup.send(embed=embed)

    @app_commands.command(name="stock_buy", description="Buy stocks")
    @app_commands.describe(symbol="Stock symbol", shares="Number of shares")
    async def stock_buy(self, interaction: discord.Interaction, symbol: str, shares: int):
        await interaction.response.defer()
        symbol = symbol.upper()
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
            await interaction.followup.send(embed=embed)
        else:
            await interaction.followup.send("❌ Purchase failed!", ephemeral=True)

    @app_commands.command(name="stock_sell", description="Sell stocks")
    @app_commands.describe(symbol="Stock symbol", shares="Number of shares")
    async def stock_sell(self, interaction: discord.Interaction, symbol: str, shares: int):
        await interaction.response.defer()
        symbol = symbol.upper()
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
            await interaction.followup.send(embed=embed)
        else:
            await interaction.followup.send("❌ Sale failed! You don't have enough shares.", ephemeral=True)


async def setup(bot):
    await bot.add_cog(StockMarketCommands(bot))
