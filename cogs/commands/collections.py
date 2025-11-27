import discord
from discord.ext import commands
from discord import app_commands

class CollectionCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="view_collections", description="View your collections")
    async def collections(self, interaction: discord.Interaction):
        await interaction.response.defer()
        
        await self.bot.player_manager.get_or_create_player(
            interaction.user.id, interaction.user.name
        )
        
        embed = discord.Embed(
            title=f"📦 {interaction.user.name}'s Collections",
            description="Track your progress across all collections!",
            color=discord.Color.gold()
        )
        
        farming_items = await self.bot.game_data.get_collection_items_by_category('farming')
        mining_items = await self.bot.game_data.get_collection_items_by_category('mining')
        combat_items = await self.bot.game_data.get_collection_items_by_category('combat')
        foraging_items = await self.bot.game_data.get_collection_items_by_category('foraging')
        
        farming_text = ""
        for item_data in farming_items[:5]:
            item_id = item_data['item_id']
            amount = await self.bot.db.get_collection(interaction.user.id, item_id)
            if amount > 0:
                farming_text += f"{item_data['display_name']}: {amount:,}\n"
        
        mining_text = ""
        for item_data in mining_items[:5]:
            item_id = item_data['item_id']
            amount = await self.bot.db.get_collection(interaction.user.id, item_id)
            if amount > 0:
                mining_text += f"{item_data['display_name']}: {amount:,}\n"
        
        combat_text = ""
        for item_data in combat_items[:5]:
            item_id = item_data['item_id']
            amount = await self.bot.db.get_collection(interaction.user.id, item_id)
            if amount > 0:
                combat_text += f"{item_data['display_name']}: {amount:,}\n"
        
        foraging_text = ""
        for item_data in foraging_items:
            item_id = item_data['item_id']
            amount = await self.bot.db.get_collection(interaction.user.id, item_id)
            if amount > 0:
                foraging_text += f"{item_data['display_name']}: {amount:,}\n"
        
        if farming_text:
            embed.add_field(name="🌾 Farming", value=farming_text or "No items", inline=False)
        if mining_text:
            embed.add_field(name="⛏️ Mining", value=mining_text or "No items", inline=False)
        if combat_text:
            embed.add_field(name="⚔️ Combat", value=combat_text or "No items", inline=False)
        if foraging_text:
            embed.add_field(name="🪓 Foraging", value=foraging_text or "No items", inline=False)
        
        if not (farming_text or mining_text or combat_text or foraging_text):
            embed.description = "No collections yet! Use gathering commands to start collecting."
        
        await interaction.followup.send(embed=embed)

async def setup(bot):
    await bot.add_cog(CollectionCommands(bot))
