import discord
from discord.ext import commands
from discord import app_commands
from typing import Optional
from utils.systems.badge_system import BadgeSystem
from utils.decorators import auto_defer

class BadgesCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="badges", description="View your badges")
    @auto_defer
    async def badges(self, interaction: discord.Interaction, user: Optional[discord.User] = None):
        target_user = user or interaction.user
        await self.bot.player_manager.get_or_create_player(target_user.id, target_user.name)
        
        badges = await BadgeSystem.get_player_badges(self.bot.db, target_user.id)
        all_badges = await BadgeSystem.get_all_badges(self.bot.db)
        
        embed = discord.Embed(
            title=f"🏅 {target_user.name}'s Badges",
            description=f"Total badges: {len(badges)}/{len(all_badges)}",
            color=discord.Color.gold()
        )
        
        if not badges:
            embed.add_field(
                name="No Badges Yet",
                value="Play the game to unlock badges!",
                inline=False
            )
        else:
            badge_text = []
            for badge in badges[:25]:
                badge_text.append(f"{badge['name']}\n*{badge['description']}*")
            
            if len(badges) > 25:
                badge_text.append(f"*...and {len(badges) - 25} more!*")
            
            embed.add_field(name="Unlocked Badges", value='\n\n'.join(badge_text), inline=False)
        
        embed.set_footer(text=f"Keep playing to unlock more badges!")
        
        await interaction.followup.send(embed=embed)

    @app_commands.command(name="badge_list", description="View all available badges")
    @auto_defer
    async def badge_list(self, interaction: discord.Interaction):
        await self.bot.player_manager.get_or_create_player(interaction.user.id, interaction.user.name)
        
        all_badges = await BadgeSystem.get_all_badges(self.bot.db)
        player_badges = await BadgeSystem.get_player_badges(self.bot.db, interaction.user.id)
        unlocked_ids = {b['badge_id'] for b in player_badges}
        
        embed = discord.Embed(
            title="🏅 All Available Badges",
            description=f"You've unlocked {len(unlocked_ids)}/{len(all_badges)} badges",
            color=discord.Color.purple()
        )
        
        categories = {}
        for badge in all_badges:
            category = badge['category']
            if category not in categories:
                categories[category] = []
            status = "✅" if badge['badge_id'] in unlocked_ids else "🔒"
            categories[category].append(f"{status} {badge['name']}")
        
        for category, badge_list in categories.items():
            embed.add_field(name=category, value='\n'.join(badge_list), inline=True)
        
        await interaction.followup.send(embed=embed)


async def setup(bot):
    await bot.add_cog(BadgesCommands(bot))
