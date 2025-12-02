import discord
from discord.ext import commands
from discord import app_commands

class BankView(discord.ui.View):
    def __init__(self, bot, user_id, username):
        super().__init__(timeout=180)
        self.bot = bot
        self.user_id = user_id
        self.username = username
    
    async def get_embed(self):
        player = await self.bot.player_manager.get_player_fresh(self.user_id)
        if not player:
            await self.bot.player_manager.get_or_create_player(self.user_id, self.username)
            player = await self.bot.player_manager.get_player_fresh(self.user_id)
        
        embed = discord.Embed(
            title=f"🏦 {self.username}'s Bank",
            description="Manage your coins and transactions",
            color=discord.Color.blue()
        )
        embed.add_field(name="💰 Purse", value=f"{player['coins']:,} coins", inline=True)
        embed.add_field(name="🏦 Bank", value=f"{player['bank']:,} coins", inline=True)
        embed.add_field(name="💎 Total Wealth", value=f"{player['coins'] + player['bank']:,} coins", inline=True)
        embed.set_footer(text="Use the buttons below to manage your coins")
        return embed
    
    @discord.ui.button(label="Deposit", style=discord.ButtonStyle.green, row=0)
    async def deposit_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("This isn't your menu!", ephemeral=True)
            return
        
        await interaction.response.send_modal(DepositModal(self.bot, self))
    
    @discord.ui.button(label="Withdraw", style=discord.ButtonStyle.blurple, row=0)
    async def withdraw_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("This isn't your menu!", ephemeral=True)
            return
        
        await interaction.response.send_modal(WithdrawModal(self.bot, self))
    
    @discord.ui.button(label="Refresh", style=discord.ButtonStyle.gray, row=0)
    async def refresh_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("This isn't your menu!", ephemeral=True)
            return
        
        await interaction.response.edit_message(embed=await self.get_embed(), view=self)

class DepositModal(discord.ui.Modal, title="Deposit Coins"):
    amount = discord.ui.TextInput(label="Amount", placeholder="Enter amount to deposit", required=True)
    
    def __init__(self, bot, view):
        super().__init__()
        self.bot = bot
        self.view = view
    
    async def on_submit(self, interaction: discord.Interaction):
        try:
            amount = int(self.amount.value)
        except ValueError:
            await interaction.response.send_message("❌ Invalid amount!", ephemeral=True)
            return
        
        player = await self.bot.player_manager.get_or_create_player(interaction.user.id, interaction.user.name)
        
        if amount <= 0:
            await interaction.response.send_message("❌ Amount must be positive!", ephemeral=True)
            return
        if player['coins'] < amount:
            await interaction.response.send_message("❌ You don't have enough coins!", ephemeral=True)
            return
        
        await self.bot.db.update_player(
            interaction.user.id,
            coins=player['coins'] - amount,
            bank=player['bank'] + amount
        )
        
        embed = await self.view.get_embed()
        await interaction.response.send_message(f"✅ Deposited {amount:,} coins to your bank!", ephemeral=True)

class WithdrawModal(discord.ui.Modal, title="Withdraw Coins"):
    amount = discord.ui.TextInput(label="Amount", placeholder="Enter amount to withdraw", required=True)
    
    def __init__(self, bot, view):
        super().__init__()
        self.bot = bot
        self.view = view
    
    async def on_submit(self, interaction: discord.Interaction):
        try:
            amount = int(self.amount.value)
        except ValueError:
            await interaction.response.send_message("❌ Invalid amount!", ephemeral=True)
            return
        
        player = await self.bot.player_manager.get_or_create_player(interaction.user.id, interaction.user.name)
        
        if amount <= 0:
            await interaction.response.send_message("❌ Amount must be positive!", ephemeral=True)
            return
        if player['bank'] < amount:
            await interaction.response.send_message("❌ You don't have enough coins in your bank!", ephemeral=True)
            return
        
        await self.bot.db.update_player(
            interaction.user.id,
            coins=player['coins'] + amount,
            bank=player['bank'] - amount
        )
        
        embed = await self.view.get_embed()
        await interaction.response.send_message(f"✅ Withdrew {amount:,} coins from your bank!", ephemeral=True)

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
