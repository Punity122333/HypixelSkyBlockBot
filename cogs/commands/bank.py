import discord
from discord.ext import commands
from discord import app_commands

class BankCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="bank", description="View your bank balance")
    async def bank(self, interaction: discord.Interaction):
        await interaction.response.defer()
        
        player = await self.bot.player_manager.get_or_create_player(
            interaction.user.id, interaction.user.name
        )
        
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
        
        player = await self.bot.player_manager.get_or_create_player(
            interaction.user.id, interaction.user.name
        )
        
        if amount <= 0:
            await interaction.followup.send("❌ Amount must be positive!", ephemeral=True)
            return
        
        if player['coins'] < amount:
            await interaction.followup.send("❌ You don't have enough coins!", ephemeral=True)
            return
        
        new_purse = player['coins'] - amount
        new_bank = player['bank'] + amount
        
        await self.bot.db.update_player(interaction.user.id, coins=new_purse, bank=new_bank)
        
        embed = discord.Embed(
            title="🏦 Deposit Successful",
            description=f"Deposited {amount:,} coins to your bank!",
            color=discord.Color.green()
        )
        embed.add_field(name="Purse", value=f"{new_purse:,} coins", inline=True)
        embed.add_field(name="Bank", value=f"{new_bank:,} coins", inline=True)
        
        await interaction.followup.send(embed=embed)

    @app_commands.command(name="withdraw", description="Withdraw coins from your bank")
    @app_commands.describe(amount="Amount of coins to withdraw")
    async def withdraw(self, interaction: discord.Interaction, amount: int):
        await interaction.response.defer()
        
        player = await self.bot.player_manager.get_or_create_player(
            interaction.user.id, interaction.user.name
        )
        
        if amount <= 0:
            await interaction.followup.send("❌ Amount must be positive!", ephemeral=True)
            return
        
        if player['bank'] < amount:
            await interaction.followup.send("❌ You don't have enough coins in your bank!", ephemeral=True)
            return
        
        new_purse = player['coins'] + amount
        new_bank = player['bank'] - amount
        
        await self.bot.db.update_player(interaction.user.id, coins=new_purse, bank=new_bank)
        
        embed = discord.Embed(
            title="🏦 Withdrawal Successful",
            description=f"Withdrew {amount:,} coins from your bank!",
            color=discord.Color.green()
        )
        embed.add_field(name="Purse", value=f"{new_purse:,} coins", inline=True)
        embed.add_field(name="Bank", value=f"{new_bank:,} coins", inline=True)
        
        await interaction.followup.send(embed=embed)

    @app_commands.command(name="pay", description="Pay coins to another player")
    @app_commands.describe(user="The player to pay", amount="Amount to pay")
    async def pay(self, interaction: discord.Interaction, user: discord.User, amount: int):
        await interaction.response.defer()
        
        if user.id == interaction.user.id:
            await interaction.followup.send("❌ You can't pay yourself!", ephemeral=True)
            return
        
        if amount <= 0:
            await interaction.followup.send("❌ Amount must be positive!", ephemeral=True)
            return
        
        player = await self.bot.player_manager.get_or_create_player(
            interaction.user.id, interaction.user.name
        )
        
        if player['coins'] < amount:
            await interaction.followup.send("❌ You don't have enough coins!", ephemeral=True)
            return
        
        await self.bot.player_manager.get_or_create_player(user.id, user.name)
        
        await self.bot.player_manager.remove_coins(interaction.user.id, amount)
        await self.bot.player_manager.add_coins(user.id, amount)
        
        embed = discord.Embed(
            title="💸 Payment Sent",
            description=f"You paid {amount:,} coins to {user.mention}!",
            color=discord.Color.green()
        )
        
        await interaction.followup.send(embed=embed)

async def setup(bot):
    await bot.add_cog(BankCommands(bot))
