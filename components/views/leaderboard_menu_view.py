import discord
import math
from components.buttons.leaderboard_buttons import (
    LeaderboardCoinsButton,
    LeaderboardNetworthButton,
    LeaderboardSkillsButton,
    LeaderboardPreviousButton,
    LeaderboardNextButton
)

class LeaderboardMenuView(discord.ui.View):
    def __init__(self, bot, user_id):
        super().__init__(timeout=180)
        self.bot = bot
        self.user_id = user_id
        self.current_category = 'coins'
        self.page = 0
        self.items_per_page = 10
        self.data = []
        self.user_rank = 0
        self.user_value = 0
        
        self.add_item(LeaderboardCoinsButton(self))
        self.add_item(LeaderboardNetworthButton(self))
        self.add_item(LeaderboardSkillsButton(self))
        self.add_item(LeaderboardPreviousButton(self))
        self.add_item(LeaderboardNextButton(self))
    
    async def load_data(self):
        if self.current_category == 'coins':
            if self.bot.db.conn:
                async with self.bot.db.conn.execute('''
                    SELECT p.user_id, p.username, e.coins 
                    FROM players p
                    JOIN player_economy e ON p.user_id = e.user_id
                    ORDER BY e.coins DESC LIMIT 100
                ''') as cursor:
                    rows = await cursor.fetchall()
                    self.data = [{'user_id': r[0], 'username': r[1], 'coins': r[2]} for r in rows]
        elif self.current_category == 'networth':
            if self.bot.db.conn:
                async with self.bot.db.conn.execute('''
                    SELECT p.user_id, p.username, (e.coins + e.bank) as networth 
                    FROM players p
                    JOIN player_economy e ON p.user_id = e.user_id
                    ORDER BY networth DESC LIMIT 100
                ''') as cursor:
                    rows = await cursor.fetchall()
                    self.data = [{'user_id': r[0], 'username': r[1], 'networth': r[2]} for r in rows]
        elif self.current_category == 'skill_avg':
            if self.bot.db.conn:
                async with self.bot.db.conn.execute('''
                    SELECT s.user_id, p.username, AVG(s.level) as skill_avg
                    FROM skills s
                    JOIN players p ON s.user_id = p.user_id
                    GROUP BY s.user_id
                    ORDER BY skill_avg DESC
                    LIMIT 100
                ''') as cursor:
                    rows = await cursor.fetchall()
                    self.data = [{'user_id': r[0], 'username': r[1], 'skill_avg': r[2]} for r in rows]
    
    async def get_embed(self):
        category_names = {
            'coins': '💰 Richest Players',
            'networth': '💎 Net Worth',
            'skill_avg': '📚 Skill Average'
        }
        
        embed = discord.Embed(
            title=f"🏆 Leaderboard - {category_names.get(self.current_category, self.current_category.title())}",
            color=discord.Color.gold()
        )
        
        start_idx = self.page * self.items_per_page
        end_idx = min(start_idx + self.items_per_page, len(self.data))
        
        leaderboard_text = ""
        for i in range(start_idx, end_idx):
            entry = self.data[i]
            rank = i + 1
            
            medal = ""
            if rank == 1:
                medal = "🥇"
            elif rank == 2:
                medal = "🥈"
            elif rank == 3:
                medal = "🥉"
            else:
                medal = f"#{rank}"
            
            username = entry.get('username', 'Unknown')
            
            if self.current_category == 'coins':
                value = f"{entry.get('coins', 0):,} coins"
            elif self.current_category == 'networth':
                value = f"{entry.get('networth', 0):,} coins"
            elif self.current_category == 'skill_avg':
                value = f"{entry.get('skill_avg', 0):.2f} avg"
            else:
                value = str(entry.get('value', 0))
            
            leaderboard_text += f"{medal} **{username}** - {value}\n"
        
        if leaderboard_text:
            embed.description = leaderboard_text
        else:
            embed.description = "No leaderboard data available."
        
        total_pages = math.ceil(len(self.data) / self.items_per_page) if self.data else 1
        embed.set_footer(text=f"Page {self.page + 1}/{total_pages} • Use buttons to view different categories")
        return embed