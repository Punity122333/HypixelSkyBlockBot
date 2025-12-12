import discord
from typing import TYPE_CHECKING
from components.buttons.boss_rotation_buttons import (
    BossRotationMainButton,
    BossRotationFightButton,
    BossRotationScheduleButton,
    BossRotationLeaderboardButton,
    BossRotationRefreshButton
)

if TYPE_CHECKING:
    from main import SkyblockBot


class BossRotationView(discord.ui.View):
    def __init__(self, bot: "SkyblockBot", user_id: int, username: str):
        super().__init__(timeout=180)
        self.bot = bot
        self.user_id = user_id
        self.username = username
        self.current_view = 'main'
        self.boss_data = None
        self.time_remaining = 0
        self.next_boss = None
        self.player_stats = None
        self.leaderboard = []
        
        self.main_button = BossRotationMainButton(self)
        self.fight_button = BossRotationFightButton(self)
        self.schedule_button = BossRotationScheduleButton(self)
        self.leaderboard_button = BossRotationLeaderboardButton(self)
        self.refresh_button = BossRotationRefreshButton(self)
        
        self._update_buttons()
    
    async def load_data(self):
        self.boss_data = await self.bot.db.boss_rotation.get_current_boss()
        self.time_remaining = self.bot.db.boss_rotation.get_time_until_next_boss()
        self.next_boss = await self.bot.db.boss_rotation.get_next_boss()
        
        self.player_stats = await self.bot.db.boss_rotation.get_player_boss_stats(
            self.user_id, self.boss_data['boss_id']
        )
        
        if self.current_view == 'leaderboard':
            self.leaderboard = await self.bot.db.boss_rotation.get_boss_leaderboard(
                self.boss_data['boss_id'], 10
            )
    
    async def get_embed(self):
        if self.current_view == 'main':
            return await self.get_main_embed()
        elif self.current_view == 'schedule':
            return await self.get_schedule_embed()
        elif self.current_view == 'leaderboard':
            return await self.get_leaderboard_embed()
        else:
            return await self.get_main_embed()
    
    async def get_main_embed(self):
        if not self.boss_data:
            await self.load_data()
        
        if not self.boss_data or not self.next_boss:
            return discord.Embed(
                title="Error",
                description="Failed to load boss data",
                color=discord.Color.red()
            )
        
        hours = self.time_remaining // 3600
        minutes = (self.time_remaining % 3600) // 60
        
        embed = discord.Embed(
            title=f"{self.boss_data['emoji']} Daily Boss: {self.boss_data['name']}",
            description=f"**The current daily boss has spawned!**\n\nThis boss rotates every 6 hours. Defeat it with your party for amazing rewards!",
            color=discord.Color.dark_gold()
        )
        
        embed.add_field(
            name="💪 Boss Stats",
            value=f"Health: {self.boss_data['health']:,} HP\nDamage: ~{self.boss_data['damage']:,}\nRewards: {self.boss_data['rewards_coins']:,} coins, {self.boss_data['rewards_xp']:,} XP",
            inline=False
        )
        
        embed.add_field(
            name="⏰ Rotation Info",
            value=f"Current Boss: **{self.boss_data['name']}**\nNext Boss: **{self.next_boss['name']}** in {hours}h {minutes}m",
            inline=False
        )
        
        if self.player_stats and self.player_stats.get('total_kills', 0) > 0:
            embed.add_field(
                name="📊 Your Stats",
                value=f"Kills: {self.player_stats['total_kills']}\nBest Time: {self.player_stats.get('best_time', 0)}s",
                inline=True
            )
        
        from utils.systems.party_system import PartySystem
        party_id = PartySystem._party_by_member.get(self.user_id)
        if party_id:
            party = PartySystem.get_party(party_id)
            if party:
                member_names = []
                for member in party['members']:
                    member_names.append(f"<@{member['user_id']}>")
                embed.add_field(
                    name="👥 Party Members",
                    value=", ".join(member_names),
                    inline=False
                )
                embed.set_footer(text="Fighting with your party! Rewards will be shared based on contribution.")
        else:
            embed.set_footer(text="Click 'Fight Boss' to start the battle! Join a party for cooperative fights.")
        
        return embed
    
    async def get_schedule_embed(self):
        if not self.boss_data:
            await self.load_data()
        
        if not self.boss_data:
            return discord.Embed(
                title="Error",
                description="Failed to load boss data",
                color=discord.Color.red()
            )
        
        hours = self.time_remaining // 3600
        minutes = (self.time_remaining % 3600) // 60
        
        embed = discord.Embed(
            title="🗓️ Daily Boss Rotation Schedule",
            description="Bosses rotate every 6 hours. Defeat them for rare loot!",
            color=discord.Color.blue()
        )
        
        embed.add_field(
            name=f"⏰ Currently Active",
            value=f"{self.boss_data['emoji']} **{self.boss_data['name']}**\nTime Remaining: {hours}h {minutes}m",
            inline=False
        )
        
        all_bosses_text = ""
        all_bosses = await self.bot.db.boss_rotation.get_boss_rotation_data()
        for boss in all_bosses:
            is_current = boss['boss_id'] == self.boss_data['boss_id']
            marker = "🔴" if is_current else "⚪"
            all_bosses_text += f"{marker} {boss['emoji']} **{boss['name']}**\n"
            all_bosses_text += f"   HP: {boss['health']:,} | Damage: {boss['damage']:,}\n"
            all_bosses_text += f"   Rewards: {boss['rewards_coins']:,} coins\n\n"
        
        embed.add_field(name="📋 Full Rotation", value=all_bosses_text, inline=False)
        embed.set_footer(text="Use 'Fight Boss' button to fight the current boss!")
        
        return embed
    
    async def get_leaderboard_embed(self):
        if not self.boss_data:
            await self.load_data()
        
        if not self.leaderboard:
            await self.load_data()
        
        if not self.boss_data:
            return discord.Embed(
                title="Error",
                description="Failed to load boss data",
                color=discord.Color.red()
            )
        
        embed = discord.Embed(
            title=f"🏆 {self.boss_data['name']} Leaderboard",
            description=f"{self.boss_data['emoji']} Top fighters of the {self.boss_data['name']}!",
            color=discord.Color.gold()
        )
        
        if not self.leaderboard:
            embed.add_field(name="No Data", value="Be the first to defeat this boss!", inline=False)
        else:
            leaderboard_text = ""
            for i, entry in enumerate(self.leaderboard):
                medal = ["🥇", "🥈", "🥉"][i] if i < 3 else f"**{i+1}.**"
                player = await self.bot.db.players.get_player(entry['user_id'])
                username = player['username'] if player else "Unknown"
                
                leaderboard_text += f"{medal} {username}\n"
                leaderboard_text += f"   Kills: {entry['kills']} | Best Time: {entry['best_time']}s\n"
                leaderboard_text += f"   Max Damage: {entry['max_damage']:,}\n\n"
            
            embed.add_field(name="Top Players", value=leaderboard_text, inline=False)
        
        embed.set_footer(text="Compete for the #1 spot!")
        
        return embed
    
    def _update_buttons(self):
        self.clear_items()
        
        if self.current_view == 'main':
            self.add_item(self.fight_button)
            self.add_item(self.schedule_button)
            self.add_item(self.leaderboard_button)
            self.add_item(self.refresh_button)
        elif self.current_view == 'schedule':
            self.add_item(self.main_button)
            self.add_item(self.fight_button)
            self.add_item(self.leaderboard_button)
            self.add_item(self.refresh_button)
        elif self.current_view == 'leaderboard':
            self.add_item(self.main_button)
            self.add_item(self.fight_button)
            self.add_item(self.schedule_button)
            self.add_item(self.refresh_button)
