import discord
from discord.ext import commands
from discord import app_commands
import math

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
    
    async def load_data(self):
        if self.current_category == 'coins':
            if self.bot.db.conn:
                async with self.bot.db.conn.execute('''
                    SELECT user_id, username, coins FROM players ORDER BY coins DESC LIMIT 100
                ''') as cursor:
                    rows = await cursor.fetchall()
                    self.data = [{'user_id': r[0], 'username': r[1], 'coins': r[2]} for r in rows]
        elif self.current_category == 'networth':
            if self.bot.db.conn:
                async with self.bot.db.conn.execute('''
                    SELECT user_id, username, (coins + bank) as networth FROM players ORDER BY networth DESC LIMIT 100
                ''') as cursor:
                    rows = await cursor.fetchall()
                    self.data = [{'user_id': r[0], 'username': r[1], 'networth': r[2]} for r in rows]
        elif self.current_category == 'skill_avg':
            if self.bot.db.conn:
                async with self.bot.db.conn.execute('''
                    SELECT s.user_id, p.username, AVG(s.level) as skill_avg
                    FROM player_skills s
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
    
    @discord.ui.button(label="💰 Coins", style=discord.ButtonStyle.blurple, row=0)
    async def coins_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("This isn't your menu!", ephemeral=True)
            return
        
        self.current_category = 'coins'
        self.page = 0
        await self.load_data()
        await interaction.response.edit_message(embed=await self.get_embed(), view=self)
    
    @discord.ui.button(label="💎 Net Worth", style=discord.ButtonStyle.green, row=0)
    async def networth_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("This isn't your menu!", ephemeral=True)
            return
        
        self.current_category = 'networth'
        self.page = 0
        await self.load_data()
        await interaction.response.edit_message(embed=await self.get_embed(), view=self)
    
    @discord.ui.button(label="📚 Skills", style=discord.ButtonStyle.gray, row=0)
    async def skills_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("This isn't your menu!", ephemeral=True)
            return
        
        self.current_category = 'skill_avg'
        self.page = 0
        await self.load_data()
        await interaction.response.edit_message(embed=await self.get_embed(), view=self)
    
    @discord.ui.button(label="Previous", style=discord.ButtonStyle.primary, row=1)
    async def prev_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("This isn't your menu!", ephemeral=True)
            return
        
        if self.page > 0:
            self.page -= 1
            await interaction.response.edit_message(embed=await self.get_embed(), view=self)
        else:
            await interaction.response.defer()
    
    @discord.ui.button(label="Next", style=discord.ButtonStyle.primary, row=1)
    async def next_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("This isn't your menu!", ephemeral=True)
            return
        
        total_pages = math.ceil(len(self.data) / self.items_per_page) if self.data else 1
        if self.page < total_pages - 1:
            self.page += 1
            await interaction.response.edit_message(embed=await self.get_embed(), view=self)
        else:
            await interaction.response.defer()

class LeaderboardCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="leaderboard", description="View server leaderboards")
    async def leaderboard(self, interaction: discord.Interaction):
        await interaction.response.defer()
        
        view = LeaderboardMenuView(self.bot, interaction.user.id)
        await view.load_data()
        embed = await view.get_embed()
        
        await interaction.followup.send(embed=embed, view=view)

async def setup(bot):
    await bot.add_cog(LeaderboardCommands(bot))
