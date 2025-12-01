import discord
from discord.ext import commands
from discord import app_commands
from utils.systems.progression_system import ProgressionSystem

class ProgressionCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="guide", description="View the beginner's guide")
    async def guide(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="📖 SkyBlock Progression Guide",
            description="Your path from nothing to riches!",
            color=discord.Color.blue()
        )
        
        embed.add_field(
            name="🎯 Stage 1: Getting Started (0-10k coins)",
            value="1. Claim `/starter_pack` for free items and 500 coins\n"
                  "2. Use `/mine` or `/farm` to gather basic resources\n"
                  "3. Sell gathered items with `/bz_sell` for quick coins\n"
                  "4. Build up to 10,000 coins through gathering",
            inline=False
        )
        
        embed.add_field(
            name="💼 Stage 2: Early Trading (10k-100k coins)",
            value="1. Check `/bz_prices` to find profitable items\n"
                  "2. Buy low, sell high using bazaar\n"
                  "3. Use `/market_trends` to identify rising items\n"
                  "4. Start flipping common items for small profits\n"
                  "5. Check `/merchants` for special deals",
            inline=False
        )
        
        embed.add_field(
            name="🏪 Stage 3: Advanced Trading (100k-1M coins)",
            value="1. Use `/bz_order_buy` and `/bz_order_sell` for better margins\n"
                  "2. Browse `/ah_browse` for underpriced auctions\n"
                  "3. Start investing in `/stocks` for passive gains\n"
                  "4. Track your progress with `/flip_stats`\n"
                  "5. Compete with bot traders for the best deals",
            inline=False
        )
        
        embed.add_field(
            name="📈 Stage 4: Wealth Building (1M+ coins)",
            value="1. Diversify with stock market investments\n"
                  "2. Create auctions with `/ah_create` for rare items\n"
                  "3. Use `/auction_insights` to understand bot behavior\n"
                  "4. Build a balanced portfolio of stocks\n"
                  "5. Reinvest profits to compound your wealth",
            inline=False
        )
        
        embed.add_field(
            name="💡 Pro Tips",
            value="• Bot traders actively compete in auctions and bazaar\n"
                  "• Supply and demand affects all prices dynamically\n"
                  "• Merchant deals expire - act fast!\n"
                  "• Stock market has real volatility\n"
                  "• Check `/economy_overview` to see the full picture",
            inline=False
        )
        
        embed.set_footer(text="Remember: This is a REAL economy. Work hard, trade smart, get rich!")
        
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="tips", description="Get trading and economy tips")
    async def tips(self, interaction: discord.Interaction):
        import random
        
        tips = [
            "💡 Bot traders use different strategies - learn their patterns to compete!",
            "📊 Rising trends mean increased demand - buy early, sell at the peak!",
            "🔍 Check auction house for BIN snipes - bots are hunting too!",
            "💰 Diversify your portfolio - don't put all coins in one investment!",
            "⏰ Merchant deals are time-limited - grab good deals quickly!",
            "📈 Stock volatility creates opportunities - buy dips, sell highs!",
            "🤖 8 different bot trading strategies compete with you!",
            "💹 Track your flips with /flip_stats to improve your strategy!",
            "🏪 Bazaar prices change based on actual supply and demand!",
            "🎯 Start small, reinvest profits, compound your wealth!",
            "📉 Falling markets = buying opportunities for patient traders!",
            "⚡ Quick flips are safer than long-term holds in volatile markets!",
            "🔔 Watch market trends to predict bot behavior!",
            "💎 Rare items on auction house attract aggressive bot bidding!",
            "🎲 Risk tolerance matters - conservative or aggressive trading?",
        ]
        
        tip = random.choice(tips)
        
        embed = discord.Embed(
            title="💡 Trading Tip",
            description=tip,
            color=discord.Color.gold()
        )
        
        embed.set_footer(text="Use /guide for comprehensive progression info!")
        
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="progression", description="View your progression and milestones")
    async def progression(self, interaction: discord.Interaction):
        await interaction.response.defer()
        
        player = await self.bot.player_manager.get_or_create_player(
            interaction.user.id, interaction.user.name
        )
        
        progression = await self.bot.db.get_player_progression(interaction.user.id)
        
        embed = discord.Embed(
            title=f"🎯 {interaction.user.name}'s Progression",
            description="Your journey through SkyBlock",
            color=discord.Color.purple()
        )
        
        wealth = player['coins'] + player['bank']
        
        milestones = [
            (0, "🌱 Newcomer"),
            (10000, "💼 Trader"),
            (50000, "🏪 Merchant"),
            (100000, "💰 Wealthy"),
            (500000, "📈 Investor"),
            (1000000, "💎 Millionaire"),
            (5000000, "🏆 Tycoon"),
            (10000000, "👑 Mogul"),
        ]
        
        current_rank = "🌱 Newcomer"
        next_milestone = 10000
        
        for threshold, rank in milestones:
            if wealth >= threshold:
                current_rank = rank
            else:
                next_milestone = threshold
                break
        
        embed.add_field(
            name="Current Rank",
            value=current_rank,
            inline=True
        )
        
        embed.add_field(
            name="Total Wealth",
            value=f"{wealth:,} coins",
            inline=True
        )
        
        if wealth < 10000000:
            remaining = next_milestone - wealth
            embed.add_field(
                name="Next Milestone",
                value=f"{remaining:,} coins away",
                inline=True
            )
        
        if progression:
            status = ""
            if progression.get('tutorial_completed'):
                status += "✅ Tutorial Complete\n"
            else:
                status += "❌ Tutorial Pending (use `/begin`)\n"
            
            if progression.get('first_mine_date'):
                status += "✅ First Mining Session\n"
            else:
                status += "⛏️ Start mining (use `/mine`)\n"
            
            if progression.get('first_farm_date'):
                status += "✅ First Farming Session\n"
            else:
                status += "🌾 Start farming (use `/farm`)\n"
            
            if progression.get('first_auction_date'):
                status += "✅ First Auction Created\n"
            else:
                status += "📦 Create your first auction\n"
            
            if progression.get('first_trade_date'):
                status += "✅ First Trade Completed\n"
            else:
                status += "🤝 Complete your first trade\n"
            
            embed.add_field(name="Progress", value=status, inline=False)
        
        total_earned = player.get('total_earned', 0)
        total_spent = player.get('total_spent', 0)
        net_profit = total_earned - total_spent
        
        embed.add_field(
            name="Trading Stats",
            value=f"Earned: {total_earned:,}\nSpent: {total_spent:,}\nProfit: {net_profit:,}",
            inline=True
        )
        
        embed.set_footer(text="Keep progressing to unlock achievements and rank up!")
        
        await interaction.followup.send(embed=embed)

async def setup(bot):
    await bot.add_cog(ProgressionCommands(bot))
