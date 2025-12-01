import discord
from discord.ext import commands
from discord import app_commands
from utils.stat_calculator import StatCalculator

class ProfileCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="profile", description="View your SkyBlock profile")
    async def profile(self, interaction: discord.Interaction):
        await interaction.response.defer()
        
        player = await self.bot.player_manager.get_or_create_player(
            interaction.user.id, interaction.user.name
        )
        
        stats = await StatCalculator.calculate_full_stats(self.bot.db, interaction.user.id)
        skills = await self.bot.db.get_skills(interaction.user.id)
        
        embed = discord.Embed(
            title=f"📊 {interaction.user.name}'s Profile",
            color=discord.Color.gold()
        )
        
        embed.add_field(name="💰 Purse", value=f"{player['coins']:,} coins", inline=True)
        embed.add_field(name="🏦 Bank", value=f"{player['bank']:,} coins", inline=True)
        embed.add_field(name="❤️ Health", value=f"{int(stats['health'])}/{int(stats['max_health'])}", inline=True)
        
        embed.add_field(name="💙 Mana", value=f"{int(stats['max_mana'])}", inline=True)
        embed.add_field(name="🛡️ Defense", value=str(int(stats['defense'])), inline=True)
        embed.add_field(name="⚔️ Strength", value=str(int(stats['strength'])), inline=True)
        
        skill_avg = sum(s['level'] for s in skills) / len(skills) if skills else 0
        embed.add_field(name="📚 Skill Average", value=f"{skill_avg:.2f}", inline=True)
        
        embed.add_field(name="📊 Trading Rep", value=f"{player.get('trading_reputation', 0)}", inline=True)
        embed.add_field(name="🏪 Merchant Lvl", value=f"{player.get('merchant_level', 0)}", inline=True)
        
        total_wealth = player['coins'] + player['bank']
        embed.add_field(name="💎 Total Wealth", value=f"{total_wealth:,} coins", inline=False)
        
        progression = await self.bot.db.get_player_progression(interaction.user.id)
        if progression:
            import json
            achievements = len(json.loads(progression.get('achievements', '[]')))
            embed.add_field(name="🏆 Achievements", value=f"{achievements} unlocked", inline=True)
        
        stocks = await self.bot.db.get_player_stocks(interaction.user.id)
        if stocks:
            portfolio_value = sum(s['shares'] * s['current_price'] for s in stocks)
            embed.add_field(name="📈 Portfolio Value", value=f"{int(portfolio_value):,} coins", inline=True)
        
        embed.set_footer(text="Keep playing to increase your stats and wealth!")
        
        await interaction.followup.send(embed=embed)

    @app_commands.command(name="stats", description="View your detailed stats")
    async def stats(self, interaction: discord.Interaction):
        await interaction.response.defer()
        
        stats = await StatCalculator.calculate_full_stats(self.bot.db, interaction.user.id)

        embed = discord.Embed(
            title=f"📈 {interaction.user.name}'s Stats",
            color=discord.Color.blue()
        )
        
        embed.add_field(name="❤️ Health", value=f"{int(stats['max_health'])}", inline=True)
        embed.add_field(name="🛡️ Defense", value=str(int(stats['defense'])), inline=True)
        embed.add_field(name="⚔️ Strength", value=str(int(stats['strength'])), inline=True)
        
        embed.add_field(name="☠️ Crit Chance", value=f"{stats.get('crit_chance', 0)}%", inline=True)
        embed.add_field(name="💥 Crit Damage", value=f"{stats.get('crit_damage', 0)}%", inline=True)
        embed.add_field(name="✨ Intelligence", value=str(int(stats.get('intelligence', 0))), inline=True)
        
        embed.add_field(name="⚡ Speed", value=str(int(stats.get('speed', 0))), inline=True)
        embed.add_field(name="🐟 Sea Creature Chance", value=f"{stats.get('sea_creature_chance', 0)}%", inline=True)
        embed.add_field(name="🔮 Magic Find", value=str(int(stats.get('magic_find', 0))), inline=True)
        
        embed.add_field(name="🍀 Pet Luck", value=str(int(stats.get('pet_luck', 0))), inline=True)
        embed.add_field(name="💢 Ferocity", value=str(int(stats.get('ferocity', 0))), inline=True)
        embed.add_field(name="⚡ Ability Damage", value=str(int(stats.get('ability_damage', 0))), inline=True)
        
        await interaction.followup.send(embed=embed)

async def setup(bot):
    await bot.add_cog(ProfileCommands(bot))
