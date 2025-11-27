import discord
from discord.ext import commands
from discord import app_commands
from discord.ui import View, Button
import math

class LeaderboardView(View):
    def __init__(self, category: str, data: list, user_id: int, user_rank: int, user_value: int):
        super().__init__(timeout=180)
        self.category = category
        self.data = data
        self.user_id = user_id
        self.user_rank = user_rank
        self.user_value = user_value
        self.page = 0
        self.items_per_page = 10
        
        self.add_buttons()
    
    def add_buttons(self):
        self.clear_items()
        
        if self.page > 0:
            prev_button = Button(label="◀️ Previous", style=discord.ButtonStyle.gray)
            prev_button.callback = self.previous_page
            self.add_item(prev_button)
        
        total_pages = math.ceil(len(self.data) / self.items_per_page)
        if self.page < total_pages - 1:
            next_button = Button(label="Next ▶️", style=discord.ButtonStyle.gray)
            next_button.callback = self.next_page
            self.add_item(next_button)
    
    async def previous_page(self, interaction: discord.Interaction):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("This isn't your menu!", ephemeral=True)
            return
        
        self.page -= 1
        self.add_buttons()
        embed = self.create_embed()
        await interaction.response.edit_message(embed=embed, view=self)
    
    async def next_page(self, interaction: discord.Interaction):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("This isn't your menu!", ephemeral=True)
            return
        
        self.page += 1
        self.add_buttons()
        embed = self.create_embed()
        await interaction.response.edit_message(embed=embed, view=self)
    
    def create_embed(self):
        category_names = {
            'coins': '💰 Richest Players',
            'networth': '💎 Net Worth',
            'skill_avg': '📚 Skill Average',
            'catacombs': '🏰 Catacombs Level',
            'slayer': '⚔️ Total Slayer XP'
        }
        
        embed = discord.Embed(
            title=f"🏆 Leaderboard - {category_names.get(self.category, self.category.title())}",
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
            
            if self.category == 'coins':
                value = f"{entry.get('coins', 0):,} coins"
            elif self.category == 'networth':
                value = f"{entry.get('networth', 0):,} coins"
            elif self.category == 'skill_avg':
                value = f"{entry.get('skill_avg', 0):.2f} avg"
            elif self.category == 'catacombs':
                value = f"Level {entry.get('catacombs_level', 0)}"
            elif self.category == 'slayer':
                value = f"{entry.get('total_slayer', 0):,} XP"
            else:
                value = str(entry.get('value', 0))
            
            leaderboard_text += f"{medal} **{username}** - {value}\n"
        
        embed.description = leaderboard_text if leaderboard_text else "No data available"
        
        total_pages = math.ceil(len(self.data) / self.items_per_page)
        embed.set_footer(text=f"Page {self.page + 1}/{total_pages} • Your rank: #{self.user_rank} ({self.user_value:,})")
        
        return embed

class LeaderboardCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="leaderboard", description="View leaderboards")
    @app_commands.describe(category="Leaderboard category")
    @app_commands.choices(category=[
        app_commands.Choice(name="💰 Richest Players", value="coins"),
        app_commands.Choice(name="💎 Net Worth", value="networth"),
        app_commands.Choice(name="📚 Skill Average", value="skill_avg"),
        app_commands.Choice(name="🏰 Catacombs Level", value="catacombs"),
        app_commands.Choice(name="⚔️ Total Slayer XP", value="slayer"),
    ])
    async def leaderboard(self, interaction: discord.Interaction, category: str = "coins"):
        await interaction.response.defer()
        
        await self.bot.player_manager.get_or_create_player(
            interaction.user.id, interaction.user.name
        )
        
        leaderboard_data = await self.bot.db.get_leaderboard(category, limit=100)
        
        if not leaderboard_data:
            embed = discord.Embed(
                title="🏆 Leaderboard",
                description="No data available yet!",
                color=discord.Color.gold()
            )
            await interaction.followup.send(embed=embed)
            return
        
        user_rank = 0
        user_value = 0
        
        for i, entry in enumerate(leaderboard_data):
            if entry['user_id'] == interaction.user.id:
                user_rank = i + 1
                
                if category == 'coins':
                    user_value = entry.get('coins', 0)
                elif category == 'networth':
                    user_value = entry.get('networth', 0)
                elif category == 'skill_avg':
                    user_value = int(entry.get('skill_avg', 0) * 100)
                elif category == 'catacombs':
                    user_value = entry.get('catacombs_level', 0)
                elif category == 'slayer':
                    user_value = entry.get('total_slayer', 0)
                break
        
        if user_rank == 0:
            player = await self.bot.db.get_player(interaction.user.id)
            if player:
                if category == 'coins':
                    user_value = player.get('coins', 0)
                elif category == 'networth':
                    user_value = player.get('coins', 0) + player.get('bank', 0)
                user_rank = len(leaderboard_data) + 1
        
        view = LeaderboardView(category, leaderboard_data, interaction.user.id, user_rank, user_value)
        embed = view.create_embed()
        
        await interaction.followup.send(embed=embed, view=view)

async def setup(bot):
    await bot.add_cog(LeaderboardCommands(bot))

