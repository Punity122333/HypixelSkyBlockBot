import discord
from discord.ext import commands
from discord import app_commands
from utils.systems.progression_system import ProgressionSystem

class ProgressionCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

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
