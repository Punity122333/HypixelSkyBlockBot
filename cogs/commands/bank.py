import discord
from discord.ext import commands
from discord import app_commands

class BankCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def fetch_player(self, user_id: int, username: str, fresh: bool = False):
        """Helper to always get the latest player data from DB if fresh=True."""
        if fresh:
            player = await self.bot.player_manager.get_player_fresh(user_id)
            if not player:
                await self.bot.player_manager.get_or_create_player(user_id, username)
                player = await self.bot.player_manager.get_player_fresh(user_id)
            return player
        return await self.bot.player_manager.get_or_create_player(user_id, username)

    @app_commands.command(name="bank", description="View your bank balance")
    async def bank(self, interaction: discord.Interaction):
        await interaction.response.defer()
        player = await self.fetch_player(interaction.user.id, interaction.user.name, fresh=True)
        embed = discord.Embed(
            title=f"🏦 {interaction.user.name}'s Bank",
            color=discord.Color.blue()
        )
        embed.add_field(name="💰 Purse", value=f"{player['coins']:,} coins", inline=True)
        embed.add_field(name="🏦 Bank", value=f"{player['bank']:,} coins", inline=True)
        embed.add_field(name="💎 Total Wealth", value=f"{player['coins'] + player['bank']:,} coins", inline=True)
        await interaction.followup.send(embed=embed)

    @app_commands.command(name="deposit", description="Deposit coins to your bank")
    @app_commands.describe(amount="Amount of coins to deposit")
    async def deposit(self, interaction: discord.Interaction, amount: int):
        await interaction.response.defer()
        player = await self.fetch_player(interaction.user.id, interaction.user.name)

        if amount <= 0:
            return await interaction.followup.send("❌ Amount must be positive!", ephemeral=True)
        if player['coins'] < amount:
            return await interaction.followup.send("❌ You don't have enough coins!", ephemeral=True)

        await self.bot.db.update_player(
            interaction.user.id,
            coins=player['coins'] - amount,
            bank=player['bank'] + amount
        )

        # Refetch fresh player data
        player = await self.fetch_player(interaction.user.id, interaction.user.name, fresh=True)

        embed = discord.Embed(
            title="🏦 Deposit Successful",
            description=f"Deposited {amount:,} coins to your bank!",
            color=discord.Color.green()
        )
        embed.add_field(name="Purse", value=f"{player['coins']:,} coins", inline=True)
        embed.add_field(name="Bank", value=f"{player['bank']:,} coins", inline=True)
        await interaction.followup.send(embed=embed)

    @app_commands.command(name="withdraw", description="Withdraw coins from your bank")
    @app_commands.describe(amount="Amount of coins to withdraw")
    async def withdraw(self, interaction: discord.Interaction, amount: int):
        await interaction.response.defer()
        player = await self.fetch_player(interaction.user.id, interaction.user.name)

        if amount <= 0:
            return await interaction.followup.send("❌ Amount must be positive!", ephemeral=True)
        if player['bank'] < amount:
            return await interaction.followup.send("❌ You don't have enough coins in your bank!", ephemeral=True)

        await self.bot.db.update_player(
            interaction.user.id,
            coins=player['coins'] + amount,
            bank=player['bank'] - amount
        )

        # Refetch fresh player data
        player = await self.fetch_player(interaction.user.id, interaction.user.name, fresh=True)

        embed = discord.Embed(
            title="🏦 Withdrawal Successful",
            description=f"Withdrew {amount:,} coins from your bank!",
            color=discord.Color.green()
        )
        embed.add_field(name="Purse", value=f"{player['coins']:,} coins", inline=True)
        embed.add_field(name="Bank", value=f"{player['bank']:,} coins", inline=True)
        await interaction.followup.send(embed=embed)

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

        # Update both users
        await self.bot.db.update_player(interaction.user.id, coins=payer['coins'] - amount)
        await self.bot.db.update_player(user.id, coins=recipient['coins'] + amount)

        # Refetch payer to show updated coins
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
