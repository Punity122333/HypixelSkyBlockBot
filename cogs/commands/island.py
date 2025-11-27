import discord
from discord.ext import commands
from discord import app_commands
import random

class IslandCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="island", description="Visit your private island")
    async def island(self, interaction: discord.Interaction):
        await self.bot.player_manager.get_or_create_player(
            interaction.user.id, interaction.user.name
        )
        
        embed = discord.Embed(
            title=f"🏝️ {interaction.user.name}'s Island",
            description="Your personal island in SkyBlock!",
            color=discord.Color.green()
        )
        
        embed.add_field(name="📊 Island Level", value="15", inline=True)
        embed.add_field(name="👥 Visitors", value="Enabled", inline=True)
        embed.add_field(name="🏗️ Build Limit", value="192 blocks", inline=True)
        
        embed.add_field(
            name="🤖 Active Minions",
            value="Wheat Minion XI x2\nCobblestone Minion X x3\nSnow Minion IX x1",
            inline=False
        )
        
        embed.set_footer(text="Use /minion to manage your minions")
        
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="minion", description="Manage your minions")
    @app_commands.describe(action="What to do with minions")
    @app_commands.choices(action=[
        app_commands.Choice(name="View All", value="view"),
        app_commands.Choice(name="Place Minion", value="place"),
        app_commands.Choice(name="Collect Items", value="collect"),
        app_commands.Choice(name="Upgrade", value="upgrade"),
    ])
    async def minion(self, interaction: discord.Interaction, action: str):
        await self.bot.player_manager.get_or_create_player(
            interaction.user.id, interaction.user.name
        )
        
        if action == "view":
            embed = discord.Embed(
                title="🤖 Your Minions",
                description="All minions on your island",
                color=discord.Color.blue()
            )
            
            embed.add_field(
                name="Slot 1: Wheat Minion XI",
                value="Storage: 1,245/1,920 wheat\nFuel: 48% Catalyst",
                inline=False
            )
            embed.add_field(
                name="Slot 2: Cobblestone Minion X",
                value="Storage: 892/1,536 cobblestone\nFuel: None",
                inline=False
            )
            
            await interaction.response.send_message(embed=embed)
        
        elif action == "collect":
            minion_items = [
                ('wheat', 50, 150),
                ('cobblestone', 100, 300),
                ('coal', 20, 80),
                ('oak_wood', 30, 120),
            ]
            
            items_collected = []
            for item_id, min_amt, max_amt in minion_items:
                amount = random.randint(min_amt, max_amt)
                await self.bot.db.add_item_to_inventory(interaction.user.id, item_id, amount)
                items_collected.append(f"{item_id} x{amount}")
            
            coins = random.randint(1000, 5000)
            await self.bot.player_manager.add_coins(interaction.user.id, coins)
            
            player_data = await self.bot.db.get_player(interaction.user.id)
            if player_data:
                await self.bot.db.update_player(interaction.user.id, total_earned=player_data.get('total_earned', 0) + coins)
            
            embed = discord.Embed(
                title="💰 Minion Collection",
                description="You collected items from all minions!",
                color=discord.Color.gold()
            )
            embed.add_field(name="🎁 Items Collected", value="\n".join(items_collected), inline=False)
            embed.add_field(name="Coins Earned", value=f"+{coins:,} coins", inline=False)
            
            await interaction.response.send_message(embed=embed)
        
        else:
            await interaction.response.send_message(
                f"🤖 Minion {action} system coming soon!",
                ephemeral=True
            )

    @app_commands.command(name="fairy_souls", description="Check your fairy soul progress")
    async def fairy_souls(self, interaction: discord.Interaction):
        await self.bot.player_manager.get_or_create_player(
            interaction.user.id, interaction.user.name
        )
        
        embed = discord.Embed(
            title="✨ Fairy Souls",
            description="Collect fairy souls for permanent stat bonuses!",
            color=discord.Color.purple()
        )
        
        embed.add_field(name="Collected", value="127 / 242", inline=True)
        embed.add_field(name="Next Milestone", value="150 souls", inline=True)
        embed.add_field(name="Progress", value="52.5%", inline=True)
        
        embed.add_field(
            name="Bonuses Unlocked",
            value="+25 Health\n+12 Defense\n+8 Strength\n+10 Speed",
            inline=False
        )
        
        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(IslandCommands(bot))
