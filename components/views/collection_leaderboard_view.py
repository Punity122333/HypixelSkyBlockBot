import discord
from components.buttons.collection_leaderboard_buttons import (
    CollectionLeaderboardPreviousButton,
    CollectionLeaderboardNextButton
)

class CollectionLeaderboardView(discord.ui.View):
    def __init__(self, bot, user_id, item_id, item_name, top_players, cog):
        super().__init__(timeout=180)
        self.bot = bot
        self.user_id = user_id
        self.item_id = item_id
        self.item_name = item_name
        self.top_players = top_players
        self.cog = cog
        self.page = 0
        self.items_per_page = 10
        
        self.add_item(CollectionLeaderboardPreviousButton(self))
        self.add_item(CollectionLeaderboardNextButton(self))
    
    async def get_embed(self):
        embed = discord.Embed(
            title=f"🏆 {self.item_name} Collection Leaderboard",
            description="Top collectors",
            color=discord.Color.gold()
        )
        
        start = self.page * self.items_per_page
        end = start + self.items_per_page
        page_players = self.top_players[start:end]
        
        leaderboard_text = ""
        for i, player_data in enumerate(page_players, start=start + 1):
            try:
                user = await self.bot.fetch_user(player_data['user_id'])
                username = user.name if user else f"User {player_data['user_id']}"
            except:
                username = f"User {player_data['user_id']}"
            
            tier = await self.cog.get_tier_for_amount(self.item_id, player_data['amount'])
            
            medal = {1: '🥇', 2: '🥈', 3: '🥉'}.get(i, f'{i}.')
            leaderboard_text += f"{medal} **{username}**: {player_data['amount']:,} (Tier {tier})\n"
        
        embed.add_field(name="Top Collectors", value=leaderboard_text or "No data yet!", inline=False)
        
        total_pages = (len(self.top_players) + self.items_per_page - 1) // self.items_per_page if self.top_players else 1
        embed.set_footer(text=f"Page {self.page + 1}/{total_pages}")
        return embed