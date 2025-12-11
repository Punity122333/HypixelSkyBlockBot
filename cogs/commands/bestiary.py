import discord
from discord.ext import commands
from discord import app_commands
from typing import Optional


class BestiaryCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="bestiary", description="View your bestiary progress")
    @app_commands.describe(
        category="Filter by location category",
        mob="View specific mob details"
    )
    @app_commands.choices(category=[
        app_commands.Choice(name="All", value="all"),
        app_commands.Choice(name="Hub", value="hub"),
        app_commands.Choice(name="Spider's Den", value="spiders_den"),
        app_commands.Choice(name="Crimson Isle", value="crimson_isle"),
        app_commands.Choice(name="The End", value="end"),
        app_commands.Choice(name="Nether", value="nether"),
        app_commands.Choice(name="Deep Caverns", value="deep_caverns"),
    ])
    async def bestiary(
        self, 
        interaction: discord.Interaction, 
        category: Optional[str] = "all",
        mob: Optional[str] = None
    ):
        await interaction.response.defer()
        
        await self.bot.player_manager.get_or_create_player(
            interaction.user.id, interaction.user.name
        )
        
        if mob:
            await self._show_mob_details(interaction, mob)
        else:
            await self._show_bestiary_overview(interaction, category or "all")
    
    async def _show_mob_details(self, interaction: discord.Interaction, mob_id: str):
        progress = await self.bot.db.bestiary.get_bestiary_progress(interaction.user.id, mob_id)
        level_info = await self.bot.db.bestiary.get_bestiary_level_requirements(mob_id)
        
        if not level_info:
            await interaction.followup.send("❌ Mob not found in bestiary!", ephemeral=True)
            return
        
        mob_name = level_info['mob_name']
        current_level = progress['level']
        kills = progress['kills']
        deaths = progress['deaths']
        next_level_kills = progress['next_level_kills']
        progress_percent = progress['progress']
        
        embed = discord.Embed(
            title=f"📖 Bestiary: {mob_name}",
            description=f"**Level:** {current_level}/{level_info['max_level']}\n**Category:** {level_info['category'].replace('_', ' ').title()}",
            color=discord.Color.blue()
        )
        
        stats_text = f"**Kills:** {kills}\n**Deaths:** {deaths}"
        if kills > 0 and deaths > 0:
            kd_ratio = kills / deaths
            stats_text += f"\n**K/D Ratio:** {kd_ratio:.2f}"
        embed.add_field(name="📊 Statistics", value=stats_text, inline=True)
        
        if current_level < level_info['max_level']:
            progress_bar = self._create_progress_bar(progress_percent)
            progress_text = f"{progress_bar}\n{kills}/{next_level_kills} kills ({progress_percent:.1f}%)"
            embed.add_field(name="🎯 Progress to Next Level", value=progress_text, inline=False)
        else:
            embed.add_field(name="✅ Max Level", value="You've reached the maximum level!", inline=False)
        
        rewards = await self.bot.db.bestiary.get_all_bestiary_rewards_for_mob(mob_id)
        if rewards:
            rewards_text = ""
            for reward in rewards:
                level = reward['level']
                reward_type = reward['reward_type'].replace('_', ' ').title()
                reward_value = reward['reward_value']
                
                if level <= current_level:
                    rewards_text += f"✅ Lv{level}: +{reward_value} {reward_type}\n"
                else:
                    rewards_text += f"🔒 Lv{level}: +{reward_value} {reward_type}\n"
            
            if len(rewards_text) > 1024:
                rewards_text = rewards_text[:1021] + "..."
            
            embed.add_field(name="🎁 Rewards", value=rewards_text or "No rewards", inline=False)
        
        await interaction.followup.send(embed=embed)
    
    async def _show_bestiary_overview(self, interaction: discord.Interaction, category: str):
        if category == "all":
            bestiary_entries = await self.bot.db.bestiary.get_player_bestiary(interaction.user.id)
        else:
            all_mobs = await self.bot.db.bestiary.get_all_mobs_in_category(category)
            mob_ids = [mob['mob_id'] for mob in all_mobs]
            all_entries = await self.bot.db.bestiary.get_player_bestiary(interaction.user.id)
            
            if isinstance(all_entries, list):
                bestiary_entries = [e for e in all_entries if e['mob_id'] in mob_ids]
            else:
                bestiary_entries = []
        
        total_stats = await self.bot.db.bestiary.get_total_bestiary_stats(interaction.user.id)
        
        embed = discord.Embed(
            title=f"📖 Bestiary - {category.replace('_', ' ').title()}",
            description="Track your kills and unlock permanent stat bonuses!",
            color=discord.Color.green()
        )
        
        if total_stats:
            stats_text = ""
            for stat, value in sorted(total_stats.items()):
                stat_name = stat.replace('_', ' ').title()
                stats_text += f"**{stat_name}:** +{value}\n"
            
            if stats_text:
                embed.add_field(name="📊 Total Bonuses", value=stats_text, inline=False)
        
        if isinstance(bestiary_entries, list) and bestiary_entries:
            entries_text = ""
            for entry in sorted(bestiary_entries, key=lambda x: x['kills'], reverse=True)[:15]:
                mob_id = entry['mob_id']
                level_info = await self.bot.db.bestiary.get_bestiary_level_requirements(mob_id)
                
                if level_info:
                    mob_name = level_info['mob_name']
                    level = entry['bestiary_level']
                    kills = entry['kills']
                    max_level = level_info['max_level']
                    
                    level_display = f"Lv{level}/{max_level}"
                    if level >= max_level:
                        level_display = f"✅ {level_display}"
                    
                    entries_text += f"**{mob_name}** - {level_display} ({kills} kills)\n"
            
            if entries_text:
                embed.add_field(name="🎯 Your Progress", value=entries_text, inline=False)
        else:
            embed.add_field(
                name="🎯 Your Progress", 
                value="No entries yet! Start fighting mobs to fill your bestiary.",
                inline=False
            )
        
        embed.set_footer(text="Use /bestiary mob:<mob_name> for detailed information")
        
        await interaction.followup.send(embed=embed)
    
    def _create_progress_bar(self, percentage: float) -> str:
        filled = int(percentage / 5)
        bar = "█" * filled + "░" * (20 - filled)
        return f"[{bar}]"


async def setup(bot):
    await bot.add_cog(BestiaryCommands(bot))
