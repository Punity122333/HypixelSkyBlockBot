import discord
from discord.ext import commands
from discord import app_commands
from discord.ui import View, Button
import random
import asyncio
from typing import Optional, TYPE_CHECKING
from utils.stat_calculator import StatCalculator
from utils.compat import roll_loot as compat_roll_loot, get_coins_reward as compat_get_coins

if TYPE_CHECKING:
    from main import SkyblockBot

class DungeonView(View):
    def __init__(self, bot: "SkyblockBot", user_id: int, floor_name: str, floor_data: dict):
        super().__init__(timeout=300)
        self.bot = bot
        self.user_id = user_id
        self.floor_name = floor_name
        self.floor_data = floor_data
        self.rooms_cleared = 0
        self.total_rooms = 7
        self.current_health: Optional[int] = None
        self.max_health: Optional[int] = None
        self.keys = 0
        self.wither_doors = 0
        self.blood_doors = 0
        self.total_damage = 0
        self.secrets_found = 0
        
    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("This isn't your dungeon run!", ephemeral=True)
            return False
        return True
    
    @discord.ui.button(label="🗝️ Open Door", style=discord.ButtonStyle.green, row=0)
    async def open_door(self, interaction: discord.Interaction, button: Button):
        player = await self.bot.db.get_player(self.user_id)   
        if not player:
            return
        
        if self.current_health is None:
            self.current_health = player['health']
            self.max_health = player['max_health']
        
        self.rooms_cleared += 1
        
        room_types = ['mob', 'puzzle', 'trap', 'treasure']
        room_type = random.choice(room_types)
        
        if room_type == 'mob':
            damage_taken = random.randint(10, 30)
            self.current_health = (self.current_health or 0) - damage_taken
            self.total_damage += damage_taken
            result = f"⚔️ **Mob Room!** You took {damage_taken} damage clearing the room!"
        elif room_type == 'puzzle':
            if random.random() > 0.5:
                self.keys += 1
                result = f"🧩 **Puzzle Room!** You solved it and got a key! 🗝️"
            else:
                result = f"🧩 **Puzzle Room!** You solved it!"
        elif room_type == 'trap':
            damage_taken = random.randint(20, 50)
            self.current_health = (self.current_health or 0) - damage_taken
            self.total_damage += damage_taken
            result = f"🪤 **Trap Room!** You triggered traps and took {damage_taken} damage!"
        else:
            coins = random.randint(30, 150)
            await self.bot.player_manager.add_coins(self.user_id, coins)   
            result = f"💎 **Treasure Room!** You found {coins} coins!"
        
        if random.random() > 0.7:
            self.secrets_found += 1
            result += f"\n✨ You found a secret! (+{self.secrets_found}/5)"
        
        if self.current_health is not None and self.current_health <= 0:
            embed = discord.Embed(
                title=f"💀 You died in {self.floor_name}!",
                description="Your run has ended.",
                color=discord.Color.red()
            )
            embed.add_field(name="Rooms Cleared", value=str(self.rooms_cleared))
            embed.add_field(name="Secrets Found", value=f"{self.secrets_found}/5")
            self.stop()
            for child in self.children:
                if isinstance(child, Button):
                    child.disabled = True   
            await interaction.response.edit_message(embed=embed, view=self)
            return
        
        if self.rooms_cleared >= self.total_rooms:
            embed = discord.Embed(
                title=f"🏆 Blood Room Complete!",
                description="Time to face the boss!",
                color=discord.Color.gold()
            )
            self.remove_item(button)
            if len(self.children) > 0 and isinstance(self.children[0], Button):
                self.children[0].label = "🐲 Fight Boss"   
                self.children[0].style = discord.ButtonStyle.red   
            await interaction.response.edit_message(embed=embed, view=self)
            return
        
        embed = discord.Embed(
            title=f"🏰 {self.floor_name} - Room {self.rooms_cleared}/{self.total_rooms}",
            description=result,
            color=discord.Color.blue()
        )
        embed.add_field(name="❤️ Health", value=f"{self.current_health or 0}/{self.max_health or 0}")
        embed.add_field(name="🗝️ Keys", value=str(self.keys))
        embed.add_field(name="✨ Secrets", value=f"{self.secrets_found}/5")
        
        await interaction.response.edit_message(embed=embed, view=self)
    
    @discord.ui.button(label="🔍 Search for Secrets", style=discord.ButtonStyle.blurple, row=0)
    async def search_secrets(self, interaction: discord.Interaction, button: Button):
        if random.random() > 0.3:
            self.secrets_found += 1
            coins = random.randint(20, 80)
            await self.bot.player_manager.add_coins(self.user_id, coins)   
            
            embed = discord.Embed(
                title="✨ Secret Found!",
                description=f"You found a secret and gained {coins} coins!",
                color=discord.Color.gold()
            )
            embed.add_field(name="Total Secrets", value=f"{self.secrets_found}/5")
        else:
            embed = discord.Embed(
                title="🔍 No Secret Here",
                description="You searched but found nothing...",
                color=discord.Color.greyple()
            )
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @discord.ui.button(label="🚪 Exit Dungeon", style=discord.ButtonStyle.gray, row=1)
    async def exit_dungeon(self, interaction: discord.Interaction, button: Button):
        score = self._calculate_score()
        
        embed = discord.Embed(
            title=f"🏰 {self.floor_name} Run Complete!",
            description=f"**Score: {score}**",
            color=discord.Color.green()
        )
        embed.add_field(name="Rooms Cleared", value=f"{self.rooms_cleared}/{self.total_rooms}")
        embed.add_field(name="Secrets Found", value=f"{self.secrets_found}/5")
        embed.add_field(name="Damage Taken", value=str(self.total_damage))
        
        floor_key = self.floor_name.lower().replace(' ', '_')
        loot_table = await self.bot.game_data.get_loot_table(floor_key, 'dungeon')
        if not loot_table:
            loot_table = {}
        
        player_stats = await StatCalculator.calculate_player_stats(self.bot.db, self.bot.game_data, self.user_id)
        magic_find = player_stats.get('magic_find', 0)
        magic_find += self.secrets_found * 2
        
        drops = await compat_roll_loot(self.bot.game_data, loot_table, magic_find)
        items_obtained = []
        for item_id, amount in drops:
            await self.bot.db.add_item_to_inventory(self.user_id, item_id, amount)
            items_obtained.append(f"{item_id} x{amount}")
        
        if 'keys' in loot_table:
            min_keys, max_keys = loot_table['keys']
            bonus_keys = random.randint(min_keys, max_keys)
            self.keys += bonus_keys
        
        score = self._calculate_score()
        rewards = compat_get_coins(loot_table)
        rewards = int(rewards * (score / 300))
        await self.bot.player_manager.add_coins(self.user_id, rewards)   
        
        player_data = await self.bot.db.get_player(self.user_id)
        if player_data:
            await self.bot.db.update_player(self.user_id, total_earned=player_data.get('total_earned', 0) + rewards)
        
        if items_obtained:
            embed.add_field(name="🎁 Items Found", value="\n".join(items_obtained[:15]), inline=False)
        embed.add_field(name="🗝️ Keys Obtained", value=str(self.keys), inline=True)
        embed.add_field(name="💰 Reward", value=f"{rewards} coins", inline=True)
        
        self.stop()
        for child in self.children:
            if isinstance(child, Button):
                child.disabled = True 
        await interaction.response.edit_message(embed=embed, view=self)
    
    def _calculate_score(self) -> int:
        base_score = 100
        room_score = self.rooms_cleared * 20
        secret_score = self.secrets_found * 10
        health_score = max(0, 100 - self.total_damage // 10)
        
        return base_score + room_score + secret_score + health_score

class DungeonCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="dungeon", description="Start an interactive dungeon run!")
    @app_commands.describe(floor="Choose a dungeon floor")
    @app_commands.choices(floor=[
        app_commands.Choice(name="Entrance", value="entrance"),
        app_commands.Choice(name="Floor 1", value="floor1"),
        app_commands.Choice(name="Floor 2", value="floor2"),
        app_commands.Choice(name="Floor 3", value="floor3"),
        app_commands.Choice(name="Floor 4", value="floor4"),
        app_commands.Choice(name="Floor 5", value="floor5"),
        app_commands.Choice(name="Floor 6", value="floor6"),
        app_commands.Choice(name="Floor 7", value="floor7"),
        app_commands.Choice(name="Master Mode 1", value="m1"),
        app_commands.Choice(name="Master Mode 2", value="m2"),
        app_commands.Choice(name="Master Mode 3", value="m3"),
        app_commands.Choice(name="Master Mode 4", value="m4"),
        app_commands.Choice(name="Master Mode 5", value="m5"),
        app_commands.Choice(name="Master Mode 6", value="m6"),
        app_commands.Choice(name="Master Mode 7", value="m7"),
    ])
    async def dungeon(self, interaction: discord.Interaction, floor: str):
        await self.bot.player_manager.get_or_create_player( 
            interaction.user.id, interaction.user.name
        )
        
        floor_info_from_db = await self.bot.game_data.get_dungeon_floor(floor)
        
        if not floor_info_from_db:
            floor_data = {
                'entrance': {'name': 'Entrance', 'rewards': 500, 'time': 180},
                'floor1': {'name': 'Floor 1', 'rewards': 1000, 'time': 240},
                'floor2': {'name': 'Floor 2', 'rewards': 2000, 'time': 300},
                'floor3': {'name': 'Floor 3', 'rewards': 4000, 'time': 360},
                'floor4': {'name': 'Floor 4', 'rewards': 8000, 'time': 420},
                'floor5': {'name': 'Floor 5', 'rewards': 15000, 'time': 480},
                'floor6': {'name': 'Floor 6', 'rewards': 30000, 'time': 540},
                'floor7': {'name': 'Floor 7', 'rewards': 60000, 'time': 600},
                'm1': {'name': 'Master Mode 1', 'rewards': 100000, 'time': 300},
                'm2': {'name': 'Master Mode 2', 'rewards': 150000, 'time': 360},
                'm3': {'name': 'Master Mode 3', 'rewards': 250000, 'time': 420},
                'm4': {'name': 'Master Mode 4', 'rewards': 400000, 'time': 480},
                'm5': {'name': 'Master Mode 5', 'rewards': 600000, 'time': 540},
                'm6': {'name': 'Master Mode 6', 'rewards': 900000, 'time': 600},
                'm7': {'name': 'Master Mode 7', 'rewards': 1500000, 'time': 660},
            }
            floor_info = floor_data.get(floor, floor_data['entrance'])
        else:
            floor_info = {
                'name': floor_info_from_db['name'],
                'rewards': int(floor_info_from_db['reward_multiplier'] * 1000),
                'time': 300
            }
        
        view = DungeonView(self.bot, interaction.user.id, floor_info['name'], floor_info)
        
        embed = discord.Embed(
            title=f"🏰 Entering {floor_info['name']}",
            description="Your dungeon run has started!\n\nNavigate through rooms, find secrets, and survive to get rewards!",
            color=discord.Color.dark_purple()
        )
        embed.add_field(name="Expected Time", value=f"~{floor_info['time']//60}m {floor_info['time']%60}s", inline=True)
        embed.add_field(name="Base Rewards", value=f"{floor_info['rewards']:,} coins", inline=True)
        embed.set_footer(text="Use buttons to navigate the dungeon")
        
        await interaction.response.send_message(embed=embed, view=view)

    @app_commands.command(name="dungeon_stats", description="View your dungeon statistics")
    async def dungeon_stats(self, interaction: discord.Interaction):
        await self.bot.player_manager.get_or_create_player(  
            interaction.user.id, interaction.user.name
        )
        
        embed = discord.Embed(
            title=f"🏰 {interaction.user.name}'s Dungeon Stats",
            color=discord.Color.purple()
        )
        
        embed.add_field(name="Catacombs Level", value="15", inline=True)
        embed.add_field(name="Total Runs", value="247", inline=True)
        embed.add_field(name="Secrets Found", value="4,521", inline=True)
        
        embed.add_field(name="Best Score", value="300 (S+)", inline=True)
        embed.add_field(name="Fastest Run", value="3m 42s", inline=True)
        embed.add_field(name="Deaths", value="89", inline=True)
        
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="party", description="Create or join a dungeon party")
    async def party(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="👥 Party System",
            description="Create or join a party to run dungeons together!",
            color=discord.Color.blue()
        )
        
        embed.add_field(
            name="Commands",
            value="`/party_create` - Create a new party\n`/party_invite @user` - Invite someone\n`/party_join @user` - Join a party\n`/party_leave` - Leave party",
            inline=False
        )
        
        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(DungeonCommands(bot))
