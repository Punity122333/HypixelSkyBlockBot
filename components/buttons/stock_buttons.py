import discord
import math
from components.modals.stock_buy_modal import StockBuyModal
from components.modals.stock_sell_modal import StockSellModal
from components.modals.stock_info_modal import StockInfoModal

class StockPreviousButton(discord.ui.Button):
    def __init__(self, view):
        super().__init__(label="Previous", style=discord.ButtonStyle.primary, custom_id="stock_previous", row=0)
        self.parent_view = view
    
    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.parent_view.user_id:
            await interaction.response.send_message("This isn't your menu!", ephemeral=True)
            return
        
        if self.parent_view.current_page > 0:
            self.parent_view.current_page -= 1
            await interaction.response.edit_message(embed=await self.parent_view.get_embed(), view=self.parent_view)
        else:
            await interaction.response.defer()

class StockNextButton(discord.ui.Button):
    def __init__(self, view):
        super().__init__(label="Next", style=discord.ButtonStyle.primary, custom_id="stock_next", row=0)
        self.parent_view = view
    
    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.parent_view.user_id:
            await interaction.response.send_message("This isn't your menu!", ephemeral=True)
            return
        
        per_page = 4
        total_pages = math.ceil(len(self.parent_view.stocks) / per_page)
        if self.parent_view.current_page < total_pages - 1:
            self.parent_view.current_page += 1
            await interaction.response.edit_message(embed=await self.parent_view.get_embed(), view=self.parent_view)
        else:
            await interaction.response.defer()

class StockPortfolioButton(discord.ui.Button):
    def __init__(self, view):
        super().__init__(label="My Portfolio", style=discord.ButtonStyle.green, custom_id="stock_portfolio", row=0)
        self.parent_view = view
    
    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.parent_view.user_id:
            await interaction.response.send_message("This isn't your menu!", ephemeral=True)
            return
        
        stocks = await self.parent_view.bot.db.get_player_stocks(self.parent_view.user_id)
        
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

class StockRefreshButton(discord.ui.Button):
    def __init__(self, view):
        super().__init__(label="Refresh", style=discord.ButtonStyle.blurple, custom_id="stock_refresh", row=0)
        self.parent_view = view
    
    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.parent_view.user_id:
            await interaction.response.send_message("This isn't your menu!", ephemeral=True)
            return
        
        await self.parent_view.load_stocks()
        await interaction.response.edit_message(embed=await self.parent_view.get_embed(), view=self.parent_view)

class StockBuyButton(discord.ui.Button):
    def __init__(self, view):
        super().__init__(label="💰 Buy", style=discord.ButtonStyle.green, custom_id="stock_buy", row=1)
        self.parent_view = view
    
    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.parent_view.user_id:
            await interaction.response.send_message("This isn't your menu!", ephemeral=True)
            return
        
        await interaction.response.send_modal(StockBuyModal(self.parent_view.bot))

class StockSellButton(discord.ui.Button):
    def __init__(self, view):
        super().__init__(label="💸 Sell", style=discord.ButtonStyle.red, custom_id="stock_sell", row=1)
        self.parent_view = view
    
    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.parent_view.user_id:
            await interaction.response.send_message("This isn't your menu!", ephemeral=True)
            return
        
        await interaction.response.send_modal(StockSellModal(self.parent_view.bot))

class StockInfoButton(discord.ui.Button):
    def __init__(self, view):
        super().__init__(label="ℹ️ Info", style=discord.ButtonStyle.blurple, custom_id="stock_info", row=1)
        self.parent_view = view
    
    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.parent_view.user_id:
            await interaction.response.send_message("This isn't your menu!", ephemeral=True)
            return
        
        await interaction.response.send_modal(StockInfoModal(self.parent_view.bot))
