import discord
from components.buttons.achievements_buttons import (
    AchievementsMainButton,
    AchievementsCategoryButton,
    AchievementsLeaderboardButton,
    AchievementsPreviousButton,
    AchievementsNextButton
)

class AchievementsMenuView(discord.ui.View):
    def __init__(self, bot, user_id, target_user):
        super().__init__(timeout=180)
        self.bot = bot
        self.user_id = user_id
        self.target_user = target_user
        self.current_view = 'main'
        self.current_category = None
        self.page = 0
        self.items_per_page = 10
        self.all_achievements = []
        self.player_achievements = []
        self.categories = {}
        self.unlocked_ids = set()
        
        self.main_button = AchievementsMainButton(self)
        self.category_button = AchievementsCategoryButton(self)
        self.leaderboard_button = AchievementsLeaderboardButton(self)
        self.prev_button = AchievementsPreviousButton(self)
        self.next_button = AchievementsNextButton(self)
        
        self._update_buttons()
    
    async def load_data(self):
        self.all_achievements = await self.bot.db.achievements.get_all_achievements()
        self.player_achievements = await self.bot.db.achievements.get_player_achievements(self.target_user.id)
        
        self.categories = {}
        for achievement in self.all_achievements:
            category = achievement['category']
            if category not in self.categories:
                self.categories[category] = {
                    'total': 0,
                    'unlocked': 0,
                    'achievements': []
                }
            self.categories[category]['total'] += 1
            self.categories[category]['achievements'].append(achievement)
        
        self.unlocked_ids = {a['achievement_id'] for a in self.player_achievements}
        for category_data in self.categories.values():
            for achievement in category_data['achievements']:
                if achievement['achievement_id'] in self.unlocked_ids:
                    category_data['unlocked'] += 1
    
    async def get_embed(self):
        if self.current_view == 'main':
            return await self.get_main_embed()
        elif self.current_view == 'category':
            return await self.get_category_embed()
        elif self.current_view == 'leaderboard':
            return await self.get_leaderboard_embed()
        else:
            return await self.get_main_embed()
    
    async def get_main_embed(self):
        total_unlocked = len(self.player_achievements)
        total_achievements = len(self.all_achievements)
        progress_percentage = (total_unlocked / total_achievements * 100) if total_achievements > 0 else 0
        
        embed = discord.Embed(
            title=f"🏆 {self.target_user.display_name}'s Achievements",
            description=f"**Progress:** {total_unlocked}/{total_achievements} ({progress_percentage:.1f}%)\n\n",
            color=discord.Color.gold()
        )
        
        for category, data in sorted(self.categories.items()):
            category_progress = f"{data['unlocked']}/{data['total']}"
            progress_bar = self._create_progress_bar(data['unlocked'], data['total'])
            embed.add_field(
                name=f"{category} {progress_bar}",
                value=f"{category_progress} achievements",
                inline=True
            )
        
        if self.player_achievements:
            recent = self.player_achievements[:5]
            recent_text = "\n".join([
                f"{a['icon']} **{a['name']}** - {a['description']}"
                for a in recent
            ])
            embed.add_field(
                name="🆕 Recently Unlocked",
                value=recent_text,
                inline=False
            )
        
        embed.set_footer(text="Use buttons below to explore achievements")
        return embed
    
    async def get_category_embed(self):
        if not self.current_category:
            return await self.get_main_embed()
        
        category_achievements = await self.bot.db.achievements.get_achievements_by_category(self.current_category)
        
        if not category_achievements:
            return await self.get_main_embed()
        
        unlocked_count = sum(1 for a in category_achievements if a['achievement_id'] in self.unlocked_ids)
        total_count = len(category_achievements)
        
        embed = discord.Embed(
            title=f"🏆 {self.current_category} Achievements",
            description=f"**Progress:** {unlocked_count}/{total_count}\n\n",
            color=discord.Color.gold()
        )
        
        start = self.page * self.items_per_page
        end = min(start + self.items_per_page, len(category_achievements))
        page_achievements = category_achievements[start:end]
        
        for achievement in page_achievements:
            is_unlocked = achievement['achievement_id'] in self.unlocked_ids
            status = "✅" if is_unlocked else "🔒"
            
            embed.add_field(
                name=f"{status} {achievement['icon']} {achievement['name']}",
                value=achievement['description'],
                inline=False
            )
        
        total_pages = (len(category_achievements) + self.items_per_page - 1) // self.items_per_page if category_achievements else 1
        embed.set_footer(text=f"Page {self.page + 1}/{total_pages}")
        return embed
    
    async def get_leaderboard_embed(self):
        leaderboard = await self.bot.db.achievements.get_achievement_leaderboard(limit=10)
        
        if not leaderboard:
            embed = discord.Embed(
                title="🏆 Achievement Leaderboard",
                description="No achievements unlocked yet!",
                color=discord.Color.gold()
            )
            return embed
        
        total_achievements = len(self.all_achievements)
        
        embed = discord.Embed(
            title="🏆 Achievement Leaderboard",
            description="Top players by achievements unlocked\n\n",
            color=discord.Color.gold()
        )
        
        for i, entry in enumerate(leaderboard, 1):
            try:
                user = await self.bot.fetch_user(entry['user_id'])
                username = user.display_name
            except:
                username = f"User {entry['user_id']}"
            
            count = entry['achievement_count']
            percentage = (count / total_achievements * 100) if total_achievements > 0 else 0
            
            medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"#{i}"
            
            embed.add_field(
                name=f"{medal} {username}",
                value=f"{count}/{total_achievements} ({percentage:.1f}%)",
                inline=False
            )
        
        return embed
    
    def _create_progress_bar(self, current: int, total: int, length: int = 10) -> str:
        if total == 0:
            return "▱" * length
        
        filled = int((current / total) * length)
        bar = "▰" * filled + "▱" * (length - filled)
        return bar
    
    def _update_buttons(self):
        self.clear_items()
        
        self.add_item(self.main_button)
        self.add_item(self.category_button)
        self.add_item(self.leaderboard_button)
        
        if self.current_view == 'category' and self.current_category:
            category_achievements = []
            if self.current_category in [cat['category'] for cat in self.all_achievements]:
                for achievement in self.all_achievements:
                    if achievement['category'] == self.current_category:
                        category_achievements.append(achievement)
            
            if category_achievements:
                total_pages = (len(category_achievements) + self.items_per_page - 1) // self.items_per_page
                if total_pages > 1:
                    self.add_item(self.prev_button)
                    self.add_item(self.next_button)
