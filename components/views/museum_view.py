import discord
from discord.ui import View
from components.buttons.museum_buttons import (
    MuseumMainButton,
    MuseumCollectionButton,
    MuseumDonateButton,
    MuseumMilestonesButton,
    MuseumLeaderboardButton,
    MuseumRefreshButton
)


class MuseumView(View):
    def __init__(self, bot, user_id, username):
        super().__init__(timeout=180)
        self.bot = bot
        self.user_id = user_id
        self.username = username
        self.current_view = 'main'
        self.museum_items = []
        self.total_donations = 0
        self.total_points = 0
        self.rarity_breakdown = {}
        self.claimed_milestones = []
        self.leaderboard = []
        
        self.main_button = MuseumMainButton(self)
        self.collection_button = MuseumCollectionButton(self)
        self.donate_button = MuseumDonateButton(self)
        self.milestones_button = MuseumMilestonesButton(self)
        self.leaderboard_button = MuseumLeaderboardButton(self)
        self.refresh_button = MuseumRefreshButton(self)
        
        self._update_buttons()
    
    async def load_data(self):
        self.museum_items = await self.bot.db.museum.get_museum_items(self.user_id)
        self.total_donations = await self.bot.db.museum.get_total_donations(self.user_id)
        self.total_points = await self.bot.db.museum.get_total_points(self.user_id)
        self.rarity_breakdown = await self.bot.db.museum.get_rarity_breakdown(self.user_id)
        self.claimed_milestones = await self.bot.db.museum.get_claimed_milestones(self.user_id)
        
        if self.current_view == 'leaderboard':
            self.leaderboard = await self.bot.db.museum.get_museum_leaderboard(10)
    
    async def get_embed(self):
        if self.current_view == 'main':
            return await self.get_main_embed()
        elif self.current_view == 'collection':
            return await self.get_collection_embed()
        elif self.current_view == 'milestones':
            return await self.get_milestones_embed()
        elif self.current_view == 'leaderboard':
            return await self.get_leaderboard_embed()
        else:
            return await self.get_main_embed()
    
    async def get_main_embed(self):
        embed = discord.Embed(
            title=f"🏛️ {self.username}'s Museum",
            description="Donate rare items to your personal museum for permanent display and rewards!",
            color=discord.Color.purple()
        )
        
        embed.add_field(name="📦 Total Items", value=str(self.total_donations), inline=True)
        embed.add_field(name="⭐ Total Points", value=f"{self.total_points:,}", inline=True)
        embed.add_field(name="🏆 Milestones", value=f"{len(self.claimed_milestones)}", inline=True)
        
        if self.rarity_breakdown:
            rarity_text = ""
            rarity_emoji = {
                'COMMON': '⬜', 'UNCOMMON': '🟩', 'RARE': '🟦',
                'EPIC': '🟪', 'LEGENDARY': '🟧', 'MYTHIC': '🟥'
            }
            for rarity in ['COMMON', 'UNCOMMON', 'RARE', 'EPIC', 'LEGENDARY', 'MYTHIC']:
                count = self.rarity_breakdown.get(rarity, 0)
                if count > 0:
                    rarity_text += f"{rarity_emoji.get(rarity, '⬜')} {rarity}: {count}\n"
            
            embed.add_field(name="📊 Rarity Breakdown", value=rarity_text or "No items yet", inline=False)
        
        next_milestone = await self.bot.db.museum.get_next_milestone(self.user_id)
        if next_milestone:
            progress = next_milestone['progress']
            required = next_milestone['required']
            reward = next_milestone['reward']
            progress_bar = self._create_progress_bar(progress, required)
            
            embed.add_field(
                name="🎯 Next Milestone",
                value=f"{progress_bar}\n{progress}/{required} items\n**Reward:** {reward['coins']:,} coins, {reward['title']}",
                inline=False
            )
        else:
            embed.add_field(name="🏆 Congratulations!", value="All milestones completed!", inline=False)
        
        return embed
    
    async def get_collection_embed(self):
        embed = discord.Embed(
            title=f"🏛️ Museum Collection",
            description=f"{self.username}'s donated items",
            color=discord.Color.blue()
        )
        
        if not self.museum_items:
            embed.add_field(name="Empty Museum", value="Donate items to start your collection!", inline=False)
        else:
            items_per_page = 15
            items_text = ""
            
            for i, item in enumerate(self.museum_items[:items_per_page]):
                item_id = item['item_id']
                rarity = item['rarity']
                points = item['points']
                
                game_item = await self.bot.game_data.get_item(item_id)
                item_name = game_item.name if game_item else item_id.replace('_', ' ').title()
                
                rarity_emoji = {
                    'COMMON': '⬜', 'UNCOMMON': '🟩', 'RARE': '🟦',
                    'EPIC': '🟪', 'LEGENDARY': '🟧', 'MYTHIC': '🟥'
                }
                
                items_text += f"{rarity_emoji.get(rarity, '⬜')} **{item_name}** ({points} pts)\n"
            
            embed.add_field(name=f"Items ({len(self.museum_items)})", value=items_text, inline=False)
            
            if len(self.museum_items) > items_per_page:
                embed.set_footer(text=f"Showing {items_per_page}/{len(self.museum_items)} items")
        
        return embed
    
    async def get_milestones_embed(self):
        embed = discord.Embed(
            title="🏆 Museum Milestones",
            description="Complete milestones to earn rewards!",
            color=discord.Color.gold()
        )
        
        milestones = await self.bot.db.museum.get_milestone_rewards()
        milestones_text = ""
        
        for milestone, reward in sorted(milestones.items()):
            status = "✅" if milestone in self.claimed_milestones else "🔒" if self.total_donations < milestone else "🎁"
            milestones_text += f"{status} **{milestone} items** - {reward['coins']:,} coins, {reward['title']}\n"
        
        embed.add_field(name="Milestones", value=milestones_text, inline=False)
        embed.add_field(name="Your Progress", value=f"{self.total_donations} items donated", inline=False)
        
        return embed
    
    async def get_leaderboard_embed(self):
        if not self.leaderboard:
            await self.load_data()
        
        embed = discord.Embed(
            title="🏆 Museum Leaderboard",
            description="Top collectors across all museums!",
            color=discord.Color.gold()
        )
        
        if not self.leaderboard:
            embed.add_field(name="No Data", value="Be the first to start a museum collection!", inline=False)
        else:
            leaderboard_text = ""
            for i, entry in enumerate(self.leaderboard):
                medal = ["🥇", "🥈", "🥉"][i] if i < 3 else f"**{i+1}.**"
                player = await self.bot.db.players.get_player(entry['user_id'])
                username = player['username'] if player else "Unknown"
                
                leaderboard_text += f"{medal} {username}\n"
                leaderboard_text += f"   Items: {entry['total_items']} | Points: {entry['total_points']}\n\n"
            
            embed.add_field(name="Top Collectors", value=leaderboard_text, inline=False)
        
        embed.set_footer(text="Donate rare items to climb the leaderboard!")
        
        return embed
    
    def _create_progress_bar(self, current, total, length=10):
        filled = int((current / total) * length) if total > 0 else 0
        bar = "█" * filled + "░" * (length - filled)
        percentage = int((current / total) * 100) if total > 0 else 0
        return f"[{bar}] {percentage}%"
    
    def _update_buttons(self):
        self.clear_items()
        
        if self.current_view == 'main':
            self.add_item(self.collection_button)
            self.add_item(self.donate_button)
            self.add_item(self.milestones_button)
            self.add_item(self.leaderboard_button)
            self.add_item(self.refresh_button)
        elif self.current_view == 'collection':
            self.add_item(self.main_button)
            self.add_item(self.donate_button)
            self.add_item(self.milestones_button)
            self.add_item(self.leaderboard_button)
            self.add_item(self.refresh_button)
        elif self.current_view == 'milestones':
            self.add_item(self.main_button)
            self.add_item(self.collection_button)
            self.add_item(self.leaderboard_button)
            self.add_item(self.refresh_button)
        elif self.current_view == 'leaderboard':
            self.add_item(self.main_button)
            self.add_item(self.collection_button)
            self.add_item(self.milestones_button)
            self.add_item(self.refresh_button)
