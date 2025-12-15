import discord
from discord.ext import commands
from discord import app_commands
from typing import Optional


class AchievementsCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @app_commands.command(name="achievements", description="View your achievements")
    @app_commands.describe(
        user="The user whose achievements you want to view (defaults to yourself)"
    )
    async def achievements(self, interaction: discord.Interaction, user: Optional[discord.User] = None):
        await interaction.response.defer()
        
        target_user = user or interaction.user
        user_id = target_user.id
        
        all_achievements = await self.bot.db.achievements.get_all_achievements()
        player_achievements = await self.bot.db.achievements.get_player_achievements(user_id)
        
        categories = {}
        for achievement in all_achievements:
            category = achievement['category']
            if category not in categories:
                categories[category] = {
                    'total': 0,
                    'unlocked': 0,
                    'achievements': []
                }
            categories[category]['total'] += 1
            categories[category]['achievements'].append(achievement)
        
        unlocked_ids = {a['achievement_id'] for a in player_achievements}
        for category_data in categories.values():
            for achievement in category_data['achievements']:
                if achievement['achievement_id'] in unlocked_ids:
                    category_data['unlocked'] += 1
        
        total_unlocked = len(player_achievements)
        total_achievements = len(all_achievements)
        progress_percentage = (total_unlocked / total_achievements * 100) if total_achievements > 0 else 0
        
        embed = discord.Embed(
            title=f"🏆 {target_user.display_name}'s Achievements",
            description=f"**Progress:** {total_unlocked}/{total_achievements} ({progress_percentage:.1f}%)\n\n",
            color=discord.Color.gold()
        )
        
        for category, data in sorted(categories.items()):
            category_progress = f"{data['unlocked']}/{data['total']}"
            progress_bar = self._create_progress_bar(data['unlocked'], data['total'])
            embed.add_field(
                name=f"{category} {progress_bar}",
                value=f"{category_progress} achievements",
                inline=True
            )
        
        if player_achievements:
            recent = player_achievements[:5]
            recent_text = "\n".join([
                f"{a['icon']} **{a['name']}** - {a['description']}"
                for a in recent
            ])
            embed.add_field(
                name="🆕 Recently Unlocked",
                value=recent_text,
                inline=False
            )
        
        embed.set_footer(text="Use /achievements_category to view achievements by category")
        await interaction.followup.send(embed=embed)
    
    @app_commands.command(name="achievements_category", description="View achievements in a specific category")
    @app_commands.describe(
        category="The category to view",
        user="The user whose achievements you want to view"
    )
    async def achievements_category(
        self, 
        interaction: discord.Interaction, 
        category: str,
        user: Optional[discord.User] = None
    ):
        await interaction.response.defer()
        
        target_user = user or interaction.user
        user_id = target_user.id
        
        category_achievements = await self.bot.db.achievements.get_achievements_by_category(category)
        
        if not category_achievements:
            embed = discord.Embed(
                title="❌ Invalid Category",
                description=f"Category '{category}' not found.",
                color=discord.Color.red()
            )
            await interaction.followup.send(embed=embed)
            return
        
        player_achievements = await self.bot.db.achievements.get_player_achievements(user_id)
        unlocked_ids = {a['achievement_id'] for a in player_achievements}
        
        unlocked_count = sum(1 for a in category_achievements if a['achievement_id'] in unlocked_ids)
        total_count = len(category_achievements)
        
        embed = discord.Embed(
            title=f"🏆 {category} Achievements",
            description=f"**Progress:** {unlocked_count}/{total_count}\n\n",
            color=discord.Color.gold()
        )
        
        for achievement in category_achievements[:25]:
            is_unlocked = achievement['achievement_id'] in unlocked_ids
            status = "✅" if is_unlocked else "🔒"
            
            embed.add_field(
                name=f"{status} {achievement['icon']} {achievement['name']}",
                value=achievement['description'],
                inline=False
            )
        
        if len(category_achievements) > 25:
            embed.set_footer(text=f"Showing 25 of {total_count} achievements")
        
        await interaction.followup.send(embed=embed)
    
    @app_commands.command(name="achievements_leaderboard", description="View top achievement earners")
    async def achievements_leaderboard(self, interaction: discord.Interaction):
        await interaction.response.defer()
        
        leaderboard = await self.bot.db.achievements.get_achievement_leaderboard(limit=10)
        
        if not leaderboard:
            embed = discord.Embed(
                title="🏆 Achievement Leaderboard",
                description="No achievements unlocked yet!",
                color=discord.Color.gold()
            )
            await interaction.followup.send(embed=embed)
            return
        
        all_achievements = await self.bot.db.achievements.get_all_achievements()
        total_achievements = len(all_achievements)
        
        embed = discord.Embed(
            title="🏆 Achievement Leaderboard",
            description="Top players by achievements unlocked\n\n",
            color=discord.Color.gold()
        )
        
        for i, entry in enumerate(leaderboard, 1):
            try:
                user = await self.bot.fetch_user(entry['user_id'])
                username = user.display_name
            except:
                username = f"User {entry['user_id']}"
            
            count = entry['achievement_count']
            percentage = (count / total_achievements * 100) if total_achievements > 0 else 0
            
            medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"#{i}"
            
            embed.add_field(
                name=f"{medal} {username}",
                value=f"{count}/{total_achievements} ({percentage:.1f}%)",
                inline=False
            )
        
        await interaction.followup.send(embed=embed)
    
    @achievements_category.autocomplete('category')
    async def category_autocomplete(
        self,
        interaction: discord.Interaction,
        current: str,
    ) -> list[app_commands.Choice[str]]:
        all_achievements = await self.bot.db.achievements.get_all_achievements()
        categories = list(set(a['category'] for a in all_achievements))
        
        return [
            app_commands.Choice(name=category, value=category)
            for category in categories
            if current.lower() in category.lower()
        ][:25]
    
    def _create_progress_bar(self, current: int, total: int, length: int = 10) -> str:
        if total == 0:
            return "▱" * length
        
        filled = int((current / total) * length)
        bar = "▰" * filled + "▱" * (length - filled)
        return bar

async def setup(bot):
    await bot.add_cog(AchievementsCommands(bot))
