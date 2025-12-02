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

class StockMenuView(discord.ui.View):
    def __init__(self, bot, user_id):
        super().__init__(timeout=180)
        self.bot = bot
        self.user_id = user_id
        self.current_page = 0
        self.stocks = []
    
    async def load_stocks(self):
        self.stocks = await self.bot.db.get_all_stocks()
    
    async def get_embed(self):
        embed = discord.Embed(
            title="📈 SkyBlock Stock Exchange",
            description="View and trade stocks",
            color=discord.Color.blue()
        )
        
        per_page = 4
        start = self.current_page * per_page
        end = start + per_page
        page_stocks = self.stocks[start:end]
        
        if not page_stocks:
            embed.description = "No stocks available at the moment."
        else:
            for stock in page_stocks:
                change = ((stock['current_price'] - stock['opening_price']) / stock['opening_price']) * 100
                emoji = "📈" if change > 0 else "📉" if change < 0 else "➡️"
                value = f"**${stock['current_price']:.2f}** {emoji}\nChange: {change:+.2f}%\nVol: {stock['volume']:,}\nHigh: ${stock['daily_high']:.2f} | Low: ${stock['daily_low']:.2f}"
                embed.add_field(name=f"{stock['symbol']} - {stock['company_name']}", value=value, inline=True)
        
        total_pages = math.ceil(len(self.stocks) / per_page) if len(self.stocks) > 0 else 1
        embed.set_footer(text=f"Page {self.current_page + 1}/{total_pages}")
        return embed
    
    @discord.ui.button(label="Previous", style=discord.ButtonStyle.primary, row=0)
    async def previous_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("This isn't your menu!", ephemeral=True)
            return
        
        if self.current_page > 0:
            self.current_page -= 1
            await interaction.response.edit_message(embed=await self.get_embed(), view=self)
        else:
            await interaction.response.defer()
    
    @discord.ui.button(label="Next", style=discord.ButtonStyle.primary, row=0)
    async def next_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("This isn't your menu!", ephemeral=True)
            return
        
        per_page = 4
        total_pages = math.ceil(len(self.stocks) / per_page)
        if self.current_page < total_pages - 1:
            self.current_page += 1
            await interaction.response.edit_message(embed=await self.get_embed(), view=self)
        else:
            await interaction.response.defer()
    
    @discord.ui.button(label="My Portfolio", style=discord.ButtonStyle.green, row=0)
    async def portfolio_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("This isn't your menu!", ephemeral=True)
            return
        
        stocks = await self.bot.db.get_player_stocks(self.user_id)
        
        embed = discord.Embed(
            title=f"📊 {interaction.user.name}'s Portfolio",
            description="Your stock holdings and performance",
            color=discord.Color.gold()
        )
        
        if not stocks:
            embed.description = "You don't own any stocks yet!"
        else:
            total_value = 0
            total_invested = 0
            for stock in stocks[:5]:
                current_value = stock['shares'] * stock['current_price']
                invested_value = stock['shares'] * stock['avg_buy_price']
                profit = current_value - invested_value
                profit_percent = (profit / invested_value) * 100 if invested_value > 0 else 0
                total_value += current_value
                total_invested += invested_value
                emoji = "🟢" if profit > 0 else "🔴" if profit < 0 else "⚪"
                value = f"Shares: {stock['shares']}\nAvg Buy: ${stock['avg_buy_price']:.2f}\nCurrent: ${stock['current_price']:.2f}\nValue: {int(current_value):,} coins\nP/L: {int(profit):,} ({profit_percent:+.2f}%) {emoji}"
                embed.add_field(name=f"{stock['stock_symbol']}", value=value, inline=True)
            
            total_profit = total_value - total_invested
            total_profit_percent = (total_profit / total_invested) * 100 if total_invested > 0 else 0
            summary = f"**Total Value:** {int(total_value):,} coins\n**Total Invested:** {int(total_invested):,} coins\n**Total P/L:** {int(total_profit):,} coins ({total_profit_percent:+.2f}%)"
            embed.add_field(name="Portfolio Summary", value=summary, inline=False)
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @discord.ui.button(label="Refresh", style=discord.ButtonStyle.blurple, row=0)
    async def refresh_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("This isn't your menu!", ephemeral=True)
            return
        
        await self.load_stocks()
        await interaction.response.edit_message(embed=await self.get_embed(), view=self)
    
    @discord.ui.button(label="💰 Buy", style=discord.ButtonStyle.green, row=1)
    async def buy_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("This isn't your menu!", ephemeral=True)
            return
        
        await interaction.response.send_modal(StockBuyModal(self.bot))
    
    @discord.ui.button(label="💸 Sell", style=discord.ButtonStyle.red, row=1)
    async def sell_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("This isn't your menu!", ephemeral=True)
            return
        
        await interaction.response.send_modal(StockSellModal(self.bot))
    
    @discord.ui.button(label="ℹ️ Info", style=discord.ButtonStyle.blurple, row=1)
    async def info_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("This isn't your menu!", ephemeral=True)
            return
        
        await interaction.response.send_modal(StockInfoModal(self.bot))

class StockMarketCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="stocks", description="Access the Stock Exchange")
    async def stocks_menu(self, interaction: discord.Interaction):
        await interaction.response.defer()
        
        await self.bot.player_manager.get_or_create_player(
            interaction.user.id, interaction.user.name
        )
        
        view = StockMenuView(self.bot, interaction.user.id)
        await view.load_stocks()
        embed = await view.get_embed()
        
        await interaction.followup.send(embed=embed, view=view)


async def setup(bot):
    await bot.add_cog(StockMarketCommands(bot))
