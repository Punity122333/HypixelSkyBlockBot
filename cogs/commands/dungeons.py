import discord
from discord.ext import commands
from discord import app_commands
from discord.ui import View, Button
import random
import asyncio
from typing import Optional, TYPE_CHECKING
from utils.stat_calculator import StatCalculator
from utils.compat import roll_loot as compat_roll_loot, get_coins_reward as compat_get_coins
from utils.decorators import auto_defer

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
        self.wither_doors_unlocked = 0
        self.blood_doors_unlocked = 0
        self.total_damage = 0
        self.secrets_found = 0
        self.max_secrets = 25
        self.crypts_opened = 0
        self.puzzles_failed = 0
        self.death_count = 0
        self.room_history = []
        
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
        
        room_types = ['mob', 'puzzle', 'trap', 'treasure', 'blood_door', 'wither_door', 'crypt']
        weights = [35, 20, 15, 15, 5, 5, 5]
        room_type = random.choices(room_types, weights=weights)[0]
        result = ""
        
        if room_type == 'wither_door' and self.keys > 0:
            self.keys -= 1
            self.wither_doors_unlocked += 1
            result = f"🚪 **Wither Door!** You used a key to unlock it! (-1 🗝️)\nSecrets may be behind here..."
            if random.random() > 0.4:
                secret_count = random.randint(1, 3)
                self.secrets_found += secret_count
                coins = random.randint(50, 150)
                await self.bot.player_manager.add_coins(self.user_id, coins)
                result += f"\n✨ Found {secret_count} secret(s) and {coins} coins!"
        elif room_type == 'blood_door':
            cost = random.randint(5, 15)
            if self.current_health and self.current_health > cost:
                self.current_health -= cost
                self.blood_doors_unlocked += 1
                result = f"🩸 **Blood Door!** You sacrificed {cost} HP to open it!\nRisk brings reward..."
                if random.random() > 0.5:
                    secret_count = random.randint(2, 4)
                    self.secrets_found += secret_count
                    result += f"\n✨ Found {secret_count} secret(s)!"
            else:
                result = f"🩸 **Blood Door!** Not enough HP to open (need {cost} HP)"
                room_type = 'blocked'
        elif room_type == 'crypt':
            self.crypts_opened += 1
            loot_roll = random.random()
            if loot_roll > 0.7:
                coins = random.randint(100, 300)
                await self.bot.player_manager.add_coins(self.user_id, coins)
                result = f"⚰️ **Crypt!** You opened a crypt and found {coins} coins!"
            else:
                damage_taken = random.randint(15, 35)
                self.current_health = (self.current_health or 0) - damage_taken
                self.total_damage += damage_taken
                result = f"⚰️ **Crypt!** Undead burst out and dealt {damage_taken} damage!"
        elif room_type == 'mob':
            mob_difficulty = random.choice(['easy', 'medium', 'hard', 'miniboss'])
            if mob_difficulty == 'miniboss':
                damage_taken = random.randint(40, 80)
                coins = random.randint(150, 400)
                await self.bot.player_manager.add_coins(self.user_id, coins)
                result = f"👑 **Miniboss Room!** You defeated a mini-boss! Took {damage_taken} damage but gained {coins} coins!"
            elif mob_difficulty == 'hard':
                damage_taken = random.randint(25, 45)
                result = f"⚔️ **Mob Room (Hard)!** Tough enemies dealt {damage_taken} damage!"
            elif mob_difficulty == 'medium':
                damage_taken = random.randint(15, 30)
                result = f"⚔️ **Mob Room (Medium)!** You took {damage_taken} damage clearing the room!"
            else:
                damage_taken = random.randint(5, 15)
                result = f"⚔️ **Mob Room (Easy)!** You took {damage_taken} damage clearing the room!"
            
            self.current_health = (self.current_health or 0) - damage_taken
            self.total_damage += damage_taken
            
            if random.random() > 0.6:
                secret_count = random.randint(1, 2)
                self.secrets_found += secret_count
                result += f"\n✨ Found {secret_count} secret(s) while fighting!"
        elif room_type == 'puzzle':
            puzzle_types = ['Teleport Maze', 'Ice Path', 'Three Weirdos', 'Blaze Puzzle', 'Water Board']
            puzzle_name = random.choice(puzzle_types)
            success_chance = 0.65
            
            if random.random() < success_chance:
                self.keys += 1
                reward = random.choice(['key', 'coins', 'secrets'])
                if reward == 'coins':
                    coins = random.randint(80, 200)
                    await self.bot.player_manager.add_coins(self.user_id, coins)
                    result = f"🧩 **Puzzle Room ({puzzle_name})!** Solved! Got a key and {coins} coins! 🗝️"
                elif reward == 'secrets':
                    secret_count = random.randint(2, 3)
                    self.secrets_found += secret_count
                    result = f"🧩 **Puzzle Room ({puzzle_name})!** Solved! Got a key and found {secret_count} secrets! 🗝️"
                else:
                    result = f"🧩 **Puzzle Room ({puzzle_name})!** You solved it and got a key! 🗝️"
            else:
                self.puzzles_failed += 1
                damage_taken = random.randint(10, 25)
                self.current_health = (self.current_health or 0) - damage_taken
                self.total_damage += damage_taken
                result = f"🧩 **Puzzle Room ({puzzle_name})!** Failed! Took {damage_taken} damage from traps!"
        elif room_type == 'trap':
            trap_types = ['Arrow Trap', 'Lava Pit', 'TNT Trap', 'Poison Darts', 'Falling Blocks']
            trap_name = random.choice(trap_types)
            damage_taken = random.randint(20, 50)
            self.current_health = (self.current_health or 0) - damage_taken
            self.total_damage += damage_taken
            result = f"🪤 **Trap Room ({trap_name})!** You triggered traps and took {damage_taken} damage!"
            
            if random.random() > 0.7:
                secret_count = 1
                self.secrets_found += secret_count
                result += f"\n✨ Found a secret while dodging traps!"
        elif room_type != 'blocked':
            coins = random.randint(30, 150)
            await self.bot.player_manager.add_coins(self.user_id, coins)   
            result = f"💎 **Treasure Room!** You found {coins} coins!"
            if random.random() > 0.5:
                secret_count = random.randint(1, 3)
                self.secrets_found += secret_count
                result += f"\n✨ Also found {secret_count} secret(s)!"
        
        if not result:
            result = "🚪 Nothing happened."
        
        if room_type != 'blocked' and random.random() > 0.85:
            self.secrets_found += 1
            result += f"\n🔍 You spotted a hidden secret! (+{self.secrets_found}/{self.max_secrets})"
        
        self.room_history.append(room_type)
        
        if self.current_health is not None and self.current_health <= 0:
            self.death_count += 1
            self.current_health = self.max_health // 2 if self.max_health else 50
            result += f"\n💀 **You died!** Respawning with half health... (Deaths: {self.death_count})"
        
        if self.rooms_cleared >= self.total_rooms:
            embed = discord.Embed(
                title=f"🏆 Blood Room Complete!",
                description="All rooms cleared! Time to face the boss!",
                color=discord.Color.gold()
            )
            embed.add_field(name="Secrets Found", value=f"{self.secrets_found}/{self.max_secrets}", inline=True)
            embed.add_field(name="Deaths", value=str(self.death_count), inline=True)
            
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
        embed.add_field(name="❤️ Health", value=f"{self.current_health or 0}/{self.max_health or 0}", inline=True)
        embed.add_field(name="🗝️ Keys", value=str(self.keys), inline=True)
        embed.add_field(name="✨ Secrets", value=f"{self.secrets_found}/{self.max_secrets}", inline=True)
        embed.add_field(name="💀 Deaths", value=str(self.death_count), inline=True)
        embed.add_field(name="🚪 Doors Unlocked", value=f"W:{self.wither_doors_unlocked} B:{self.blood_doors_unlocked}", inline=True)
        embed.add_field(name="⚰️ Crypts", value=str(self.crypts_opened), inline=True)
        
        await interaction.response.edit_message(embed=embed, view=self)
    
    @discord.ui.button(label="🔍 Search for Secrets", style=discord.ButtonStyle.blurple, row=0)
    async def search_secrets(self, interaction: discord.Interaction, button: Button):
        if self.secrets_found >= self.max_secrets:
            embed = discord.Embed(
                title=f"🏰 {self.floor_name} - Room {self.rooms_cleared}/{self.total_rooms}",
                description=f"✨ All Secrets Found!\nYou've already found all {self.max_secrets} secrets in this dungeon!",
                color=discord.Color.gold()
            )
            embed.add_field(name="❤️ Health", value=f"{self.current_health or 0}/{self.max_health or 0}", inline=True)
            embed.add_field(name="🗝️ Keys", value=str(self.keys), inline=True)
            embed.add_field(name="✨ Secrets", value=f"{self.secrets_found}/{self.max_secrets}", inline=True)
            embed.add_field(name="💀 Deaths", value=str(self.death_count), inline=True)
            embed.add_field(name="🚪 Doors Unlocked", value=f"W:{self.wither_doors_unlocked} B:{self.blood_doors_unlocked}", inline=True)
            embed.add_field(name="⚰️ Crypts", value=str(self.crypts_opened), inline=True)
            await interaction.response.edit_message(embed=embed, view=self)
            return
        
        result = ""
        if random.random() > 0.4:
            self.secrets_found += 1
            coins = random.randint(30, 120)
            await self.bot.player_manager.add_coins(self.user_id, coins)   
            
            secret_types = ['Chest', 'Lever', 'Fairy Soul', 'Wither Essence', 'Bat', 'Item Frame']
            secret_type = random.choice(secret_types)
            
            result = f"✨ **Secret Found - {secret_type}!**\nYou found a secret and gained {coins} coins!"
        else:
            result = "🔍 **No Secret Here**\nYou searched but found nothing..."
        
        embed = discord.Embed(
            title=f"🏰 {self.floor_name} - Room {self.rooms_cleared}/{self.total_rooms}",
            description=result,
            color=discord.Color.gold() if self.secrets_found > 0 else discord.Color.greyple()
        )
        embed.add_field(name="❤️ Health", value=f"{self.current_health or 0}/{self.max_health or 0}", inline=True)
        embed.add_field(name="🗝️ Keys", value=str(self.keys), inline=True)
        embed.add_field(name="✨ Secrets", value=f"{self.secrets_found}/{self.max_secrets}", inline=True)
        embed.add_field(name="� Deaths", value=str(self.death_count), inline=True)
        embed.add_field(name="🚪 Doors Unlocked", value=f"W:{self.wither_doors_unlocked} B:{self.blood_doors_unlocked}", inline=True)
        embed.add_field(name="⚰️ Crypts", value=str(self.crypts_opened), inline=True)
        
        await interaction.response.edit_message(embed=embed, view=self)
    
    @discord.ui.button(label="🚪 Exit Dungeon", style=discord.ButtonStyle.gray, row=1)
    async def exit_dungeon(self, interaction: discord.Interaction, button: Button):
        score = self._calculate_score()
        
        embed = discord.Embed(
            title=f"🏰 {self.floor_name} Run Complete!",
            description=f"**Score: {score}**",
            color=discord.Color.green()
        )
        embed.add_field(name="Rooms Cleared", value=f"{self.rooms_cleared}/{self.total_rooms}")
        embed.add_field(name="Secrets Found", value=f"{self.secrets_found}/{self.max_secrets}")
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
            await self.bot.db.update_player(
                interaction.user.id,
                total_earned=player_data.get('total_earned', 0) + rewards,
                coins=player_data.get('coins', 0) + rewards
            )
        
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
        secret_score = self.secrets_found * 5
        secret_percentage = (self.secrets_found / self.max_secrets) * 100
        
        health_bonus = max(0, 100 - self.total_damage // 10)
        death_penalty = self.death_count * 25
        puzzle_bonus = max(0, 50 - (self.puzzles_failed * 10))
        door_bonus = (self.wither_doors_unlocked * 10) + (self.blood_doors_unlocked * 8)
        crypt_bonus = self.crypts_opened * 5
        
        total_score = (base_score + room_score + secret_score + health_bonus + 
                      puzzle_bonus + door_bonus + crypt_bonus - death_penalty)
        
        if secret_percentage >= 100:
            total_score += 100
        elif secret_percentage >= 80:
            total_score += 50
        
        return max(0, total_score)

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
    @auto_defer
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
                'name': floor_info_from_db['name'] if 'name' in floor_info_from_db.keys() else 'Unknown Floor',
                'rewards': int(floor_info_from_db['rewards']) if 'rewards' in floor_info_from_db.keys() else 5000,
                'time': int(floor_info_from_db['time']) if 'time' in floor_info_from_db.keys() else 300
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
        
        await interaction.followup.send(embed=embed, view=view)

    @app_commands.command(name="dungeon_stats", description="View your dungeon statistics")
    @auto_defer
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
        
        await interaction.followup.send(embed=embed)

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
