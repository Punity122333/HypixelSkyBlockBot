import discord
from discord import app_commands
from discord.ext import commands
from typing import TYPE_CHECKING
from utils.systems.potion_system import PotionSystem

if TYPE_CHECKING:
    from main import SkyblockBot

class PotionCommands(commands.Cog):
    def __init__(self, bot: "SkyblockBot"):
        self.bot = bot
    
    @app_commands.command(name="use_potion", description="Use a potion to gain temporary stat boosts")
    @app_commands.describe(potion="The name of the potion to use")
    async def use_potion(self, interaction: discord.Interaction, potion: str):
        await self.bot.player_manager.get_or_create_player(
            interaction.user.id, interaction.user.name
        )
        
        from utils.normalize import normalize_item_id
        potion_id = normalize_item_id(potion)
        
        result = await PotionSystem.use_potion(self.bot.db, interaction.user.id, potion_id)
        
        if result['success']:
            if result.get('type') == 'instant_heal':
                embed = discord.Embed(
                    title="❤️ Health Potion Used!",
                    description=f"You consumed a health potion!",
                    color=discord.Color.red()
                )
                embed.add_field(name="Effect", value=f"Restores {result['amount']} HP", inline=True)
                embed.set_footer(text="Use health potions in combat for instant healing!")
                await interaction.response.send_message(embed=embed)
            elif result.get('type') == 'god':
                duration_min = result['duration'] // 60
                embed = discord.Embed(
                    title="✨ God Potion Activated!",
                    description=f"You consumed a God Potion and gained ALL stat bonuses!",
                    color=discord.Color.gold()
                )
                god_effects = PotionSystem.POTION_EFFECTS['god_potion']['effects']
                effects_text = "\n".join([f"+{amt} {stat.replace('_', ' ').title()}" for stat, amt in list(god_effects.items())[:10]])
                embed.add_field(name="Effects (showing 10)", value=effects_text, inline=False)
                embed.add_field(name="Duration", value=f"{duration_min} minutes", inline=True)
                embed.set_footer(text=f"Total: {len(god_effects)} stat bonuses active!")
                await interaction.response.send_message(embed=embed)
            else:
                stat_name = result['stat'].replace('_', ' ').title()
                duration_min = result['duration'] // 60
                embed = discord.Embed(
                    title="🧪 Potion Used!",
                    description=f"You consumed a potion and gained a temporary buff!",
                    color=discord.Color.green()
                )
                embed.add_field(name="Effect", value=f"+{result['amount']} {stat_name}", inline=True)
                embed.add_field(name="Duration", value=f"{duration_min} minutes", inline=True)
                await interaction.response.send_message(embed=embed)
        else:
            await interaction.response.send_message(f"❌ {result['message']}", ephemeral=True)
    
    @app_commands.command(name="active_potions", description="View your active potion effects")
    async def active_potions(self, interaction: discord.Interaction):
        await self.bot.player_manager.get_or_create_player(
            interaction.user.id, interaction.user.name
        )
        
        active_potions = await PotionSystem.get_active_potions(self.bot.db, interaction.user.id)
        
        embed = discord.Embed(
            title=f"🧪 {interaction.user.name}'s Active Potions",
            description=f"You have {len(active_potions)} active potion effect(s)",
            color=discord.Color.blue()
        )
        
        if active_potions:
            import time
            current_time = int(time.time())
            
            for potion_data in active_potions:
                potion_id = potion_data['potion_id']
                expires_at = potion_data['expires_at']
                time_left = expires_at - current_time
                minutes_left = time_left // 60
                seconds_left = time_left % 60
                
                if potion_id in PotionSystem.POTION_EFFECTS:
                    effect = PotionSystem.POTION_EFFECTS[potion_id]
                    stat_name = effect['stat'].replace('_', ' ').title()
                    potion_name = potion_id.replace('_', ' ').title()
                    
                    embed.add_field(
                        name=f"🧪 {potion_name}",
                        value=f"+{effect['amount']} {stat_name}\nTime left: {minutes_left}m {seconds_left}s",
                        inline=False
                    )
        else:
            embed.description = "You have no active potion effects"
        
        await interaction.response.send_message(embed=embed)

async def setup(bot: "SkyblockBot"):
    await bot.add_cog(PotionCommands(bot))
