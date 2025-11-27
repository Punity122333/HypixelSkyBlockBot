import discord
from discord.ext import commands
from discord import app_commands
import time

class EconomyStatsCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="flip_stats", description="View your bazaar flipping statistics")
    async def flip_stats(self, interaction: discord.Interaction):
        await interaction.response.defer()
        
        await self.bot.player_manager.get_or_create_player(
            interaction.user.id, interaction.user.name
        )
        
        embed = discord.Embed(
            title=f"💹 {interaction.user.name}'s Flip Statistics",
            description="Your bazaar flipping performance",
            color=discord.Color.gold()
        )
        
        player = await self.bot.db.get_player(interaction.user.id)
        if player:
            embed.add_field(name="Total Earned", value=f"{player.get('total_earned', 0):,} coins", inline=True)
            embed.add_field(name="Total Spent", value=f"{player.get('total_spent', 0):,} coins", inline=True)
            net = player.get('total_earned', 0) - player.get('total_spent', 0)
            embed.add_field(name="Net Profit", value=f"{net:,} coins", inline=True)
        
        top_flippers = await self.bot.db.get_top_flippers(10)
        
        if top_flippers:
            leaderboard_text = ""
            for idx, flipper in enumerate(top_flippers, 1):
                if flipper['user_id'] == interaction.user.id:
                    leaderboard_text += f"**{idx}. You - {flipper['total_profit']:,} coins ({flipper['flip_count']} flips)**\n"
                else:
                    user = await self.bot.fetch_user(flipper['user_id'])
                    name = user.name if user else f"User {flipper['user_id']}"
                    leaderboard_text += f"{idx}. {name} - {flipper['total_profit']:,} coins ({flipper['flip_count']} flips)\n"
            
            embed.add_field(name="Top Flippers (Last 7 Days)", value=leaderboard_text, inline=False)
        
        embed.set_footer(text="Keep flipping to climb the leaderboard!")
        await interaction.followup.send(embed=embed)

    @app_commands.command(name="market_trends", description="View current market trends")
    async def market_trends(self, interaction: discord.Interaction):
        await interaction.response.defer()
        
        embed = discord.Embed(
            title="📊 Market Trends Analysis",
            description="Current supply and demand trends",
            color=discord.Color.blue()
        )
        
        rising_items = []
        falling_items = []
        stable_items = []
        
        for item_id, sd in self.bot.market_system.supply_demand.items():
            if sd['trend'] == 'rising':
                rising_items.append((item_id, sd['demand'] / sd['supply']))
            elif sd['trend'] == 'falling':
                falling_items.append((item_id, sd['demand'] / sd['supply']))
            else:
                stable_items.append(item_id)
        
        rising_items.sort(key=lambda x: x[1], reverse=True)
        falling_items.sort(key=lambda x: x[1])
        
        if rising_items:
            rising_text = ""
            for item_id, ratio in rising_items[:5]:
                item = await self.bot.game_data.get_item(item_id)
                if item:
                    rising_text += f"📈 {item.name} (Demand: {ratio:.2f}x)\n"
            embed.add_field(name="🔥 Trending UP", value=rising_text or "None", inline=False)
        
        if falling_items:
            falling_text = ""
            for item_id, ratio in falling_items[:5]:
                item = await self.bot.game_data.get_item(item_id)
                if item:
                    falling_text += f"📉 {item.name} (Demand: {ratio:.2f}x)\n"
            embed.add_field(name="❄️ Trending DOWN", value=falling_text or "None", inline=False)
        
        embed.set_footer(text="Buy low, sell high! Use trends to maximize profits.")
        await interaction.followup.send(embed=embed)

    @app_commands.command(name="auction_insights", description="View auction house insights and bot activity")
    async def auction_insights(self, interaction: discord.Interaction):
        await interaction.response.defer()
        
        embed = discord.Embed(
            title="🔨 Auction House Insights",
            description="Real-time auction market analysis",
            color=discord.Color.purple()
        )
        
        auctions = await self.bot.db.get_active_auctions(100)
        
        total_volume = sum(a['current_bid'] for a in auctions)
        avg_price = total_volume / len(auctions) if auctions else 0
        
        embed.add_field(name="Active Auctions", value=str(len(auctions)), inline=True)
        embed.add_field(name="Total Volume", value=f"{total_volume:,} coins", inline=True)
        embed.add_field(name="Avg Price", value=f"{int(avg_price):,} coins", inline=True)
        
        bin_auctions = [a for a in auctions if a['bin']]
        embed.add_field(name="BIN Listings", value=str(len(bin_auctions)), inline=True)
        
        auction_bots = await self.bot.db.get_auction_bots()
        embed.add_field(name="Active Bot Traders", value=str(len(auction_bots)), inline=True)
        
        bot_info = "**Trading Bots:**\n"
        for bot in auction_bots[:5]:
            bot_info += f"• {bot['bot_name']} ({bot['trading_strategy']}) - {bot['coins']:,} coins\n"
        
        embed.add_field(name="Bot Activity", value=bot_info, inline=False)
        
        embed.set_footer(text="Bot traders compete in the market just like players!")
        await interaction.followup.send(embed=embed)

    @app_commands.command(name="economy_overview", description="View complete economy overview")
    async def economy_overview(self, interaction: discord.Interaction):
        await interaction.response.defer()
        
        player = await self.bot.player_manager.get_or_create_player(
            interaction.user.id, interaction.user.name
        )
        
        embed = discord.Embed(
            title="🌐 SkyBlock Economy Overview",
            description="Complete economic statistics",
            color=discord.Color.gold()
        )
        
        embed.add_field(
            name="💰 Your Balance",
            value=f"{player['coins']:,} coins\nBank: {player['bank']:,} coins",
            inline=True
        )
        
        stocks = await self.bot.db.get_all_stocks()
        total_market_cap = sum(s['market_cap'] for s in stocks)
        embed.add_field(
            name="📈 Stock Market",
            value=f"Total Market Cap: {total_market_cap:,} coins\n{len(stocks)} listed companies",
            inline=True
        )
        
        auctions = await self.bot.db.get_active_auctions(1000)
        total_auction_volume = sum(a['current_bid'] for a in auctions)
        embed.add_field(
            name="🔨 Auction House",
            value=f"{len(auctions)} active auctions\n{total_auction_volume:,} coins in bids",
            inline=True
        )
        
        deals = await self.bot.db.get_active_merchant_deals()
        embed.add_field(
            name="🏪 Merchants",
            value=f"{len(deals)} active deals",
            inline=True
        )
        
        trading_rep = player.get('trading_reputation', 0)
        merchant_level = player.get('merchant_level', 0)
        embed.add_field(
            name="📊 Your Trading Stats",
            value=f"Rep: {trading_rep}\nMerchant Level: {merchant_level}",
            inline=True
        )
        
        progression = await self.bot.db.get_player_progression(interaction.user.id)
        if progression:
            achievements = len(eval(progression.get('achievements', '[]')))
            embed.add_field(
                name="🏆 Progression",
                value=f"Achievements: {achievements}\nTutorial: {'✅' if progression.get('tutorial_completed') else '❌'}",
                inline=True
            )
        
        embed.set_footer(text="Use various commands to participate in the economy!")
        await interaction.followup.send(embed=embed)

async def setup(bot):
    await bot.add_cog(EconomyStatsCommands(bot))
