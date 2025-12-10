import discord
from discord.ext import commands
from discord import app_commands
from typing import Optional
import os
import pathlib

AUTHORIZED_USER_ID = 702136500334100604

class AdminCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="reload_cog", description="Reload a specific cog")
    @app_commands.describe(cog="Select the cog to reload")
    async def reload_cog(self, interaction: discord.Interaction, cog: str):
        if interaction.user.id != AUTHORIZED_USER_ID:
            await interaction.response.send_message("❌ You are not authorized to use this command!", ephemeral=True)
            return
        
        await interaction.response.defer(ephemeral=True)
        
        try:
            await self.bot.reload_extension(cog)
            embed = discord.Embed(
                title="✅ Cog Reloaded",
                description=f"Successfully reloaded `{cog}`",
                color=discord.Color.green()
            )
            await interaction.followup.send(embed=embed, ephemeral=True)
        except Exception as e:
            embed = discord.Embed(
                title="❌ Reload Failed",
                description=f"Failed to reload `{cog}`\nError: {str(e)}",
                color=discord.Color.red()
            )
            await interaction.followup.send(embed=embed, ephemeral=True)

    @reload_cog.autocomplete('cog')
    async def cog_autocomplete(self, interaction: discord.Interaction, current: str):
        cogs = []
        cogs_dir = pathlib.Path("cogs")
        
        for category_dir in cogs_dir.iterdir():
            if not category_dir.is_dir() or category_dir.name.startswith('__'):
                continue
            
            for file_path in category_dir.rglob("*.py"):
                if file_path.name.startswith('__'):
                    continue
                
                relative_path = file_path.relative_to(pathlib.Path("."))
                cog_path = str(relative_path).replace(os.sep, '.')[:-3]
                cogs.append(cog_path)
        
        filtered_cogs = [
            app_commands.Choice(name=cog.replace('cogs.', '').replace('.', ' > '), value=cog)
            for cog in cogs
            if current.lower() in cog.lower()
        ]
        
        return filtered_cogs[:25]

    @app_commands.command(name="sync_commands", description="Force sync commands to Discord")
    @app_commands.describe(force="Force sync even if no changes detected")
    async def sync_commands(self, interaction: discord.Interaction, force: bool = False):
        if interaction.user.id != AUTHORIZED_USER_ID:
            await interaction.response.send_message("❌ You are not authorized to use this command!", ephemeral=True)
            return
        
        await interaction.response.defer(ephemeral=True)
        
        try:
            if interaction.guild:
                guild = discord.Object(id=interaction.guild.id)
                synced_count = await self.bot.sync_manager.safe_sync(guild=guild, force=force)
                location = f"guild {interaction.guild.name}"
            else:
                synced_count = await self.bot.sync_manager.safe_sync(guild=None, force=force)
                location = "globally"
            
            if synced_count > 0:
                embed = discord.Embed(
                    title="✅ Commands Synced",
                    description=f"Successfully synced {synced_count} commands {location}",
                    color=discord.Color.green()
                )
            else:
                embed = discord.Embed(
                    title="✨ No Changes",
                    description=f"No command changes detected {location}",
                    color=discord.Color.blue()
                )
            await interaction.followup.send(embed=embed, ephemeral=True)
        except Exception as e:
            embed = discord.Embed(
                title="❌ Sync Failed",
                description=f"Failed to sync commands\nError: {str(e)}",
                color=discord.Color.red()
            )
            await interaction.followup.send(embed=embed, ephemeral=True)

    @app_commands.command(name="clear_sync_cache", description="Clear command sync cache")
    @app_commands.describe(guild_id="Guild ID to clear cache for (leave empty for all)")
    async def clear_sync_cache(self, interaction: discord.Interaction, guild_id: Optional[str] = None):
        if interaction.user.id != AUTHORIZED_USER_ID:
            await interaction.response.send_message("❌ You are not authorized to use this command!", ephemeral=True)
            return
        
        self.bot.sync_manager.clear_cache(guild_id)
        
        location = f"guild {guild_id}" if guild_id else "all guilds"
        embed = discord.Embed(
            title="🗑️ Cache Cleared",
            description=f"Cleared command sync cache for {location}",
            color=discord.Color.green()
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)

async def setup(bot):
    await bot.add_cog(AdminCommands(bot))
