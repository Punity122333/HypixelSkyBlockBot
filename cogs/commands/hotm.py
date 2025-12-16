import discord
from discord.ext import commands
from discord import app_commands
from components.views.hotm_menu_view import HotmMenuView

class HotMCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @app_commands.command(name="hotm", description="View your Heart of the Mountain progress")
    async def hotm(self, interaction: discord.Interaction):
        await interaction.response.defer()
        
        await self.bot.player_manager.get_or_create_player(
            interaction.user.id, interaction.user.name
        )
        
        skills = await self.bot.db.get_skills(interaction.user.id)
        mining_skill = next((s for s in skills if s['skill_name'] == 'mining'), None)
        mining_level = mining_skill['level'] if mining_skill else 0
        
        if mining_level < 12:
            await interaction.followup.send(
                f"❌ You need Mining Level 12+ to access Heart of the Mountain! (Current: {mining_level})",
                ephemeral=True
            )
            return
        
        view = HotmMenuView(self.bot, interaction.user.id)
        await view.refresh_data()
        embed = await view.get_embed()
        
        message = await interaction.followup.send(embed=embed, view=view)
        view.message = message


async def setup(bot):
    await bot.add_cog(HotMCommands(bot))
