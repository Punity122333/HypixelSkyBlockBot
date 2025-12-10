import discord
from discord.ext import commands
from discord import app_commands
from discord.ui import View, Button
from typing import Dict

class TradeView(View):
    def __init__(self, bot: commands.Bot, user1_id: int, user2_id: int):
        super().__init__(timeout=180)
        self.bot = bot
        self.user1_id = user1_id
        self.user2_id = user2_id
        self.user1_offer: Dict[str, int] = {}
        self.user2_offer: Dict[str, int] = {}
        self.user1_ready = False
        self.user2_ready = False
        
    @discord.ui.button(label="✅ Accept Trade", style=discord.ButtonStyle.green)
    async def accept_button(self, interaction: discord.Interaction, button: Button):
        if interaction.user.id == self.user1_id:
            self.user1_ready = True
        elif interaction.user.id == self.user2_id:
            self.user2_ready = True
        else:
            await interaction.response.send_message("This isn't your trade!", ephemeral=True)
            return
        
        if self.user1_ready and self.user2_ready:
            embed = discord.Embed(
                title="✅ Trade Complete!",
                description="Both players accepted the trade!",
                color=discord.Color.green()
            )
            self.stop()
            for child in self.children:
                if hasattr(child, 'disabled'):
                    child.disabled = True  # type: ignore
            await interaction.response.edit_message(embed=embed, view=self)
        else:
            await interaction.response.send_message("✅ You accepted the trade! Waiting for the other player...", ephemeral=True)
    
    @discord.ui.button(label="❌ Cancel Trade", style=discord.ButtonStyle.red)
    async def cancel_button(self, interaction: discord.Interaction, button: Button):
        embed = discord.Embed(
            title="❌ Trade Cancelled",
            description="The trade was cancelled.",
            color=discord.Color.red()
        )
        self.stop()
        for child in self.children:
            if hasattr(child, 'disabled'):
                child.disabled = True  # type: ignore
        await interaction.response.edit_message(embed=embed, view=self)

class MarketplaceInteractive(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot


    @app_commands.command(name="trade", description="Trade with another player!")
    @app_commands.describe(user="The player to trade with")
    async def trade_interactive(self, interaction: discord.Interaction, user: discord.User):
        if user.id == interaction.user.id:
            await interaction.response.send_message("❌ You can't trade with yourself!", ephemeral=True)
            return
        
        if user.bot:
            await interaction.response.send_message("❌ You can't trade with bots!", ephemeral=True)
            return
        
        await self.bot.player_manager.get_or_create_player(  # type: ignore
            interaction.user.id, interaction.user.name
        )
        await self.bot.player_manager.get_or_create_player(  # type: ignore
            user.id, user.name
        )
        
        view = TradeView(self.bot, interaction.user.id, user.id)
        
        embed = discord.Embed(
            title="🤝 Trade",
            description=f"**{interaction.user.name}** is trading with **{user.name}**",
            color=discord.Color.green()
        )
        embed.add_field(
            name=f"{interaction.user.name}'s Offer",
            value="Empty",
            inline=True
        )
        embed.add_field(
            name=f"{user.name}'s Offer",
            value="Empty",
            inline=True
        )
        embed.set_footer(text="Both players must accept to complete the trade")
        
        await interaction.response.send_message(f"{user.mention}", embed=embed, view=view)

async def setup(bot: commands.Bot):
    await bot.add_cog(MarketplaceInteractive(bot))
