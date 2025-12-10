import discord
from utils.normalize import normalize_item_id
from components.views.collection_leaderboard_view import CollectionLeaderboardView

class CollectionLeaderboardModal(discord.ui.Modal, title="Collection Leaderboard"):
    item = discord.ui.TextInput(label="Item Name (optional)", placeholder="e.g., wheat", required=False)
    
    def __init__(self, bot, user_id, cog):
        super().__init__()
        self.bot = bot
        self.user_id = user_id
        self.cog = cog
    
    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer()
        
        if self.item.value:
            item_id = normalize_item_id(self.item.value)
            tiers = await self.bot.game_data.get_collection_tier_requirements(item_id)
            if not tiers:
                await interaction.followup.send(f"❌ Collection not found for '{self.item.value}'!", ephemeral=True)
                return
            
            top_players = await self.bot.db.get_top_collections(item_id, 100)
            
            view = CollectionLeaderboardView(self.bot, self.user_id, item_id, self.item.value.title(), top_players, self.cog)
            embed = await view.get_embed()
            await interaction.followup.send(embed=embed, view=view, ephemeral=True)
        else:
            all_categories = await self.bot.game_data.get_collection_categories()
            categories_data = {}
            for category in all_categories.keys():
                top_player = await self.bot.db.get_top_category_collectors(category, 1)
                if top_player:
                    categories_data[category] = top_player[0]
            
            embed = discord.Embed(
                title="🏆 Collection Category Leaders",
                description="Top collectors in each category",
                color=discord.Color.gold()
            )
            
            for category, player_data in categories_data.items():
                user = await self.bot.fetch_user(player_data['user_id'])
                username = user.name if user else f"User {player_data['user_id']}"
                level = player_data.get('total_tiers', 0)
                
                cat_emoji = {'farming': '🌾', 'mining': '⛏️', 'foraging': '🪓', 'combat': '⚔️'}
                embed.add_field(
                    name=f"{cat_emoji.get(category, '📦')} {category.title()}",
                    value=f"**{username}**\nLevel: {level}",
                    inline=True
                )
        
            await interaction.followup.send(embed=embed, ephemeral=True)