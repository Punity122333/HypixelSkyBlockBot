import discord
from discord.ext import commands
from discord import app_commands
import time
from utils.systems.economy_system import EconomySystem
from utils.normalize import normalize_item_id
from components.views.auction_menu_view import AuctionMenuView

class AuctionCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="auction", description="Access the Auction House")
    async def auction(self, interaction: discord.Interaction):
        await interaction.response.defer()
        
        await self.bot.player_manager.get_or_create_player(
            interaction.user.id, interaction.user.name
        )
        
        view = AuctionMenuView(self.bot, interaction.user.id)
        await view.load_auctions()
        embed = await view.get_embed()
        
        await interaction.followup.send(embed=embed, view=view)

async def setup(bot):
    await bot.add_cog(AuctionCommands(bot))
