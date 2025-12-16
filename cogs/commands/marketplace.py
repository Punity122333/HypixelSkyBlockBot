import discord
from discord.ext import commands
from discord import app_commands
from components.views.marketplace_view import MarketplaceView


class MarketplaceInteractive(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @property
    def player_manager(self):
        return getattr(self.bot, "player_manager", None)

    @property
    def db(self):
        return getattr(self.bot, "db", None)

    @app_commands.command(name="marketplace", description="Access the marketplace and trade with players")
    async def marketplace(self, interaction: discord.Interaction):
        await interaction.response.defer()
        
        if not self.player_manager:
            await interaction.followup.send("❌ Player manager not configured.", ephemeral=True)
            return
        
        if not self.db or not hasattr(self.db, "trading"):
            await interaction.followup.send("❌ Database trading manager not configured.", ephemeral=True)
            return
        
        await self.player_manager.get_or_create_player(
            interaction.user.id, interaction.user.name
        )
        
        view = MarketplaceView(self.bot, interaction.user.id)
        embed = await view.get_embed()
        
        await interaction.followup.send(embed=embed, view=view)


async def setup(bot: commands.Bot):
    await bot.add_cog(MarketplaceInteractive(bot))

