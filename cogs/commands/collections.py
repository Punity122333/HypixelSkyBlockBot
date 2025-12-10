import discord
from discord.ext import commands
from discord import app_commands
from typing import Optional
from components.views.collection_menu_view import CollectionMenuView

class CollectionCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="collections", description="View and manage your collections")
    async def collections_menu(self, interaction: discord.Interaction):
        await interaction.response.defer()
        
        await self.bot.player_manager.get_or_create_player(
            interaction.user.id, interaction.user.name
        )
        
        view = CollectionMenuView(self.bot, interaction.user.id, interaction.user.name, self)
        embed = await view.get_embed()
        
        await interaction.followup.send(embed=embed, view=view)

    async def get_tier_for_amount(self, item_id: str, amount: int) -> int:
        tiers = await self.bot.game_data.get_collection_tier_requirements(item_id)
        if not tiers:
            return 0
        tier = 0
        for i, req in enumerate(tiers):
            if amount >= req:
                tier = i + 1
            else:
                break
        return tier
    
    async def get_category_for_item(self, item_id: str) -> Optional[str]:
        return await self.bot.game_data.get_item_category(item_id)
    
    async def get_category_level(self, user_id: int, category: str) -> int:
        items = await self.bot.game_data.get_category_items(category)
        if not items:
            return 0
        total_tiers = 0
        for item_id in items:
            amount = await self.bot.db.get_collection(user_id, item_id)
            tier = await self.get_tier_for_amount(item_id, amount)
            total_tiers += tier
        return total_tiers



async def setup(bot):
    await bot.add_cog(CollectionCommands(bot))
