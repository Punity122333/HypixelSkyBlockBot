import discord
from discord.ext import commands
from discord import app_commands
import time

class BeginCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="begin", description="Start your SkyBlock journey from scratch")
    async def begin(self, interaction: discord.Interaction):
        await interaction.response.defer()
        
        player = await self.bot.player_manager.get_or_create_player(
            interaction.user.id, interaction.user.name
        )
        
        progression = await self.bot.db.get_player_progression(interaction.user.id)
        
        if progression and progression.get('tutorial_completed'):
            await interaction.followup.send("❌ You've already started your journey! Use `/profile` to view your progress.", ephemeral=True)
            return
        
        if player['coins'] > 0 or player['bank'] > 0:
            await interaction.followup.send("❌ You already have coins! This command is only for new players starting from nothing.", ephemeral=True)
            return
        
        inventory = await self.bot.db.get_inventory(interaction.user.id)
        if inventory:
            await interaction.followup.send("❌ You already have items! This command is only for new players.", ephemeral=True)
            return
        
        await self.bot.db.add_item_to_inventory(interaction.user.id, 'wooden_sword', 1)
        await self.bot.db.add_item_to_inventory(interaction.user.id, 'wooden_pickaxe', 1)
        await self.bot.db.add_item_to_inventory(interaction.user.id, 'wooden_hoe', 1)
        await self.bot.db.add_item_to_inventory(interaction.user.id, 'wooden_axe', 1)
        await self.bot.db.add_item_to_inventory(interaction.user.id, 'wooden_fishing_rod', 1)
        
        await self.bot.db.update_progression(
            interaction.user.id,
            tutorial_completed=1,
            first_mine_date=int(time.time())
        )
        
        embed = discord.Embed(
            title="🌱 Welcome to SkyBlock!",
            description="You're starting with absolutely nothing. Time to build an empire from scratch!",
            color=discord.Color.green()
        )
        
        embed.add_field(
            name="Starting Equipment",
            value="• Wooden Sword (for basic combat)\n• Wooden Pickaxe (for mining)\n• Wooden Hoe (for farming)\n• Wooden Axe (for chopping wood)\n• Wooden Fishing Rod (for fishing)",
            inline=False
        )
        
        embed.add_field(
            name="📖 Your First Steps",
            value="1. Use `/mine` to gather basic ores (cobblestone, coal)\n"
                  "2. Collect at least 50 cobblestone and 10 coal\n"
                  "3. Use `/craft stone_pickaxe` to upgrade your tool\n"
                  "4. Better tools = more resources = more coins!",
            inline=False
        )
        
        embed.add_field(
            name="💡 Pro Tip",
            value="Don't sell everything! Save materials to craft better equipment.\n"
                  "Better pickaxe → Mine faster → More resources → More profit!",
            inline=False
        )
        
        embed.add_field(
            name="Next Commands",
            value="`/mine` - Start gathering resources\n"
                  "`/inventory` - Check your items\n"
                  "`/craft` - View craftable upgrades\n"
                  "`/progression_path` - See your upgrade path",
            inline=False
        )
        
        await interaction.followup.send(embed=embed)

async def setup(bot):
    await bot.add_cog(BeginCommands(bot))
