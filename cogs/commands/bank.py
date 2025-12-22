import discord
from discord.ext import commands
from discord import app_commands
from components.views.bank_view import BankView

class BankCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def fetch_player(self, user_id: int, username: str, fresh: bool = False):
        if fresh:
            player = await self.bot.player_manager.get_player_fresh(user_id)
            if not player:
                await self.bot.player_manager.get_or_create_player(user_id, username)
                player = await self.bot.player_manager.get_player_fresh(user_id)
            return player
        return await self.bot.player_manager.get_or_create_player(user_id, username)

    @app_commands.command(name="bank", description="Access your bank")
    async def bank_command(self, interaction: discord.Interaction):
        await interaction.response.defer()
        
        await self.bot.player_manager.get_or_create_player(
            interaction.user.id, interaction.user.name
        )
        
        view = BankView(self.bot, interaction.user.id, interaction.user.name)
        embed = await view.get_embed()
        
        await interaction.followup.send(embed=embed, view=view)

    @app_commands.command(name="pay", description="Pay coins to another player")
    @app_commands.describe(user="The player to pay", amount="Amount to pay")
    async def pay(self, interaction: discord.Interaction, user: discord.User, amount: int):
        await interaction.response.defer()
        if user.id == interaction.user.id:
            return await interaction.followup.send("❌ You can't pay yourself!", ephemeral=True)
        if amount <= 0:
            return await interaction.followup.send("❌ Amount must be positive!", ephemeral=True)

        payer = await self.fetch_player(interaction.user.id, interaction.user.name)
        if payer['coins'] < amount:
            return await interaction.followup.send("❌ You don't have enough coins!", ephemeral=True)

        recipient = await self.fetch_player(user.id, user.name)

        await self.bot.db.players.update_player(interaction.user.id, coins=payer['coins'] - amount, total_spent=payer.get('total_spent', 0) + amount)
        await self.bot.db.players.update_player(user.id, coins=recipient['coins'] + amount, total_earned=recipient.get('total_earned', 0) + amount)

        payer = await self.fetch_player(interaction.user.id, interaction.user.name, fresh=True)

        embed = discord.Embed(
            title="💸 Payment Sent",
            description=f"You paid {amount:,} coins to {user.mention}!",
            color=discord.Color.green()
        )
        embed.add_field(name="Your Purse", value=f"{payer['coins']:,} coins", inline=True)
        await interaction.followup.send(embed=embed)


async def setup(bot):
    await bot.add_cog(BankCommands(bot))
