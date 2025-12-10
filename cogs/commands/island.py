import discord
from discord.ext import commands
from discord import app_commands
import random
from components.views.island_menu_view import IslandMenuView

class IslandCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="island", description="Visit and manage your private island")
    async def island_menu(self, interaction: discord.Interaction):
        await interaction.response.defer()
        
        await self.bot.player_manager.get_or_create_player(
            interaction.user.id, interaction.user.name
        )
        
        view = IslandMenuView(self.bot, interaction.user.id, interaction.user.name)
        embed = await view.get_embed()
        
        await interaction.followup.send(embed=embed, view=view)


        
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="search_fairy_soul", description="Search for a fairy soul!")
    async def search_fairy_soul(self, interaction: discord.Interaction):
        await interaction.response.defer()
        
        await self.bot.player_manager.get_or_create_player(
            interaction.user.id, interaction.user.name
        )
        
        collected_locations_data = await self.bot.db.get_fairy_soul_locations(interaction.user.id)
        
        collected_locations = []
        if collected_locations_data:
            if isinstance(collected_locations_data, list):
                collected_locations = [loc if isinstance(loc, str) else loc.get('location', '') for loc in collected_locations_data if loc]
            
        all_locations_data = await self.bot.game_data.get_all_fairy_soul_locations()
        all_locations = []
        if all_locations_data:
            if isinstance(all_locations_data, list):
                all_locations = [loc if isinstance(loc, str) else loc.get('location', '') for loc in all_locations_data if loc]
        
        uncollected = [loc for loc in all_locations if loc and loc not in collected_locations]
        
        if not uncollected:
            embed = discord.Embed(
                title="✨ All Fairy Souls Collected!",
                description="You've collected all available fairy souls!",
                color=discord.Color.gold()
            )
            await interaction.followup.send(embed=embed)
            return
        
        found_chance = random.random()
        
        if found_chance < 0.3:
            location = random.choice(uncollected)
            success = await self.bot.db.collect_fairy_soul(interaction.user.id, location)
            
            if success:
                from utils.systems.badge_system import BadgeSystem
                
                total_souls = await self.bot.db.get_fairy_souls(interaction.user.id)
                
                if total_souls >= 1:
                    await BadgeSystem.unlock_badge(self.bot.db, interaction.user.id, 'first_fairy_soul')
                if total_souls >= 50:
                    await BadgeSystem.unlock_badge(self.bot.db, interaction.user.id, 'fairy_souls_50')
                
                health_bonus = total_souls * 3
                mana_bonus = total_souls * 2
                
                player = await self.bot.db.get_player(interaction.user.id)
                base_health = 100
                base_mana = 20
                
                await self.bot.db.update_player(
                    interaction.user.id,
                    max_health=base_health + health_bonus,
                    max_mana=base_mana + mana_bonus
                )
                
                embed = discord.Embed(
                    title="✨ Fairy Soul Found!",
                    description=f"You found a fairy soul at **{location.replace('_', ' ').title()}**!",
                    color=discord.Color.purple()
                )
                embed.add_field(name="Total Souls", value=f"{total_souls}/{len(all_locations)}", inline=True)
                embed.add_field(name="Health Bonus", value=f"+{health_bonus} ❤️", inline=True)
                embed.add_field(name="Mana Bonus", value=f"+{mana_bonus} ✨", inline=True)
                
                await interaction.followup.send(embed=embed)
            else:
                embed = discord.Embed(
                    title="✨ Already Collected",
                    description="You've already collected this fairy soul!",
                    color=discord.Color.orange()
                )
                await interaction.followup.send(embed=embed)
        else:
            embed = discord.Embed(
                title="🔍 Still Searching...",
                description="You searched but didn't find a fairy soul this time. Keep searching!",
                color=discord.Color.blue()
            )
            embed.set_footer(text="Try again to keep searching!")
            await interaction.followup.send(embed=embed)

    @app_commands.command(name="fairy_souls", description="Check your fairy soul progress")
    async def fairy_souls(self, interaction: discord.Interaction):
        await interaction.response.defer()
        
        await self.bot.player_manager.get_or_create_player(
            interaction.user.id, interaction.user.name
        )
        
        souls = await self.bot.db.get_fairy_souls(interaction.user.id)
        collected_locations = await self.bot.db.get_fairy_soul_locations(interaction.user.id)
        
        health_bonus = souls * 3
        mana_bonus = souls * 2
        
        progress_pct = (souls / 242) * 100
        
        embed = discord.Embed(
            title="✨ Fairy Souls",
            description="Collect fairy souls for permanent stat bonuses!",
            color=discord.Color.purple()
        )
        
        embed.add_field(name="Collected", value=f"{souls} / 242", inline=True)
        embed.add_field(name="Progress", value=f"{progress_pct:.1f}%", inline=True)
        embed.add_field(name="Remaining", value=f"{242 - souls}", inline=True)
        
        embed.add_field(
            name="Current Bonuses",
            value=f"+{health_bonus} ❤️ Health\n+{mana_bonus} ✨ Mana",
            inline=False
        )
        
        embed.set_footer(text="Use /search_fairy_soul to find more fairy souls!")
        
        await interaction.followup.send(embed=embed)

async def setup(bot):
    await bot.add_cog(IslandCommands(bot))
