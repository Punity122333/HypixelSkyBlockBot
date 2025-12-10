import discord
import random
from components.buttons.island_buttons import (
    IslandSearchButton,
    IslandProgressButton,
    IslandRefreshButton
)

class IslandMenuView(discord.ui.View):
    def __init__(self, bot, user_id, username):
        super().__init__(timeout=180)
        self.bot = bot
        self.user_id = user_id
        self.username = username
        
        self.add_item(IslandSearchButton(self))
        self.add_item(IslandProgressButton(self))
        self.add_item(IslandRefreshButton(self))
    
    async def get_embed(self):
        souls = await self.bot.db.get_fairy_souls(self.user_id)
        
        embed = discord.Embed(
            title=f"🏝️ {self.username}'s Island",
            description="Your personal island in SkyBlock!",
            color=discord.Color.green()
        )
        
        embed.add_field(name="📊 Island Level", value="15", inline=True)
        embed.add_field(name="👥 Visitors", value="Enabled", inline=True)
        embed.add_field(name="✨ Fairy Souls", value=f"{souls}/242", inline=True)
        
        embed.add_field(
            name="🤖 Active Minions",
            value="Wheat Minion XI x2\nCobblestone Minion X x3\nSnow Minion IX x1",
            inline=False
        )
        
        embed.set_footer(text="Use buttons below to interact with your island")
        return embed