import discord
from components.buttons.bank_buttons import (
    BankDepositButton,
    BankWithdrawButton,
    BankRefreshButton
)

class BankView(discord.ui.View):
    def __init__(self, bot, user_id, username):
        super().__init__(timeout=180)
        self.bot = bot
        self.user_id = user_id
        self.username = username
        
        self.add_item(BankDepositButton(self))
        self.add_item(BankWithdrawButton(self))
        self.add_item(BankRefreshButton(self))
    
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
