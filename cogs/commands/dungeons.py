import discord
from discord.ext import commands
from discord import app_commands
from discord.ui import View, Button
import random
import asyncio
from typing import Optional, TYPE_CHECKING, Dict, Any
from utils.stat_calculator import StatCalculator
from utils.compat import roll_loot as compat_roll_loot, get_coins_reward as compat_get_coins
from utils.decorators import auto_defer
from utils.data.loot_tables import default_loot
from utils.systems.party_system import PartySystem
from utils.systems.puzzle_system import PuzzleSystem, Puzzle, PuzzleType
from utils.systems.combat_system import CombatSystem
from utils.systems.dungeon_system import DungeonSystem
from utils.systems.economy_system import EconomySystem

if TYPE_CHECKING:
    from main import SkyblockBot

class DungeonView(View):
    def __init__(self, bot: "SkyblockBot", user_id: int, floor_name: str, floor_data: dict, party_id: Optional[int] = None):
        super().__init__(timeout=300)
        self.bot = bot
        self.user_id = user_id
        self.floor_name = floor_name
        self.floor_data = floor_data
        self.party_id = party_id
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
        self.coins_gained_in_run = 0
        self.current_puzzle: Optional[Puzzle] = None
        self.party_size = 1
        
        if self.party_id:
            party = PartySystem.get_party_by_id(self.party_id)
            if party:
                self.party_size = len(party['members'])
        
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
            player_stats = await StatCalculator.calculate_player_stats(self.bot.db, self.bot.game_data, self.user_id)
            self.current_health = int(player_stats['max_health'])
            self.max_health = int(player_stats['max_health'])
        
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
                self.coins_gained_in_run += coins
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
                self.coins_gained_in_run += coins
                result = f"⚰️ **Crypt!** You opened a crypt and found {coins} coins!"
            else:
                damage_taken = random.randint(15, 35)
                self.current_health = (self.current_health or 0) - damage_taken
                self.total_damage += damage_taken
                result = f"⚰️ **Crypt!** Undead burst out and dealt {damage_taken} damage!"
        elif room_type == 'mob':
            mob_difficulty = random.choice(['easy', 'medium', 'hard', 'miniboss'])
            
            mob_configs = {
                'easy': {'defense': 10, 'damage_range': (5, 15), 'coins': (20, 50)},
                'medium': {'defense': 25, 'damage_range': (15, 30), 'coins': (50, 100)},
                'hard': {'defense': 50, 'damage_range': (25, 45), 'coins': (100, 200)},
                'miniboss': {'defense': 100, 'damage_range': (40, 80), 'coins': (150, 400)}
            }
            
            config = mob_configs[mob_difficulty]
            
            damage_result = await CombatSystem.calculate_player_damage(
                self.bot.db, self.user_id, config['defense']
            )
            
            mob_base_hp = config['damage_range'][1] * 3
            player_damage = damage_result['damage']
            
            if player_damage >= mob_base_hp:
                damage_taken = config['damage_range'][0]
            else:
                damage_taken = random.randint(*config['damage_range'])
            
            coins = random.randint(*config['coins'])
            self.coins_gained_in_run += coins
            
            if mob_difficulty == 'miniboss':
                result = f"👑 **Miniboss Room!** You defeated a mini-boss! Took {damage_taken} damage but gained {coins} coins!"
            elif mob_difficulty == 'hard':
                result = f"⚔️ **Mob Room (Hard)!** Tough enemies dealt {damage_taken} damage! ({int(player_damage)} damage dealt)"
            elif mob_difficulty == 'medium':
                result = f"⚔️ **Mob Room (Medium)!** You took {damage_taken} damage clearing the room! ({int(player_damage)} damage dealt)"
            else:
                result = f"⚔️ **Mob Room (Easy)!** You took {damage_taken} damage clearing the room! ({int(player_damage)} damage dealt)"
            
            self.current_health = (self.current_health or 0) - damage_taken
            self.total_damage += damage_taken
            
            if random.random() > 0.6:
                secret_count = random.randint(1, 2)
                self.secrets_found += secret_count
                result += f"\n✨ Found {secret_count} secret(s) while fighting!"
        elif room_type == 'puzzle':
            floor_id = self.floor_name.lower().replace(' ', '')
            puzzle_difficulty = min(10, max(1, (self.rooms_cleared // 2) + 1))
            
            self.current_puzzle = PuzzleSystem.create_puzzle(puzzle_difficulty, self.party_size)
            
            embed = discord.Embed(
                title=f"🧩 Puzzle Room - {self.current_puzzle.data['name']}",
                description=f"**Difficulty:** {puzzle_difficulty}/10\n**Attempts:** {self.current_puzzle.max_attempts}\n\n{self.current_puzzle.data['description']}",
                color=discord.Color.purple()
            )
            embed.add_field(name="Question", value=self.current_puzzle.data['question'], inline=False)
            embed.add_field(name="❤️ Health", value=f"{self.current_health or 0}/{self.max_health or 0}", inline=True)
            embed.add_field(name="🗝️ Keys", value=str(self.keys), inline=True)
            embed.add_field(name="✨ Secrets", value=f"{self.secrets_found}/{self.max_secrets}", inline=True)
            embed.set_footer(text="Type your answer in chat or use the 'Get Hint' button")
            
            await interaction.response.edit_message(embed=embed, view=self)
            return
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
            self.coins_gained_in_run += coins
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
            self.coins_gained_in_run += coins
            
            secret_types = ['Chest', 'Lever', 'Wither Essence', 'Bat', 'Item Frame', 'Redstone Key']
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
        embed.add_field(name=" Deaths", value=str(self.death_count), inline=True)
        embed.add_field(name="🚪 Doors Unlocked", value=f"W:{self.wither_doors_unlocked} B:{self.blood_doors_unlocked}", inline=True)
        embed.add_field(name="⚰️ Crypts", value=str(self.crypts_opened), inline=True)
        
        await interaction.response.edit_message(embed=embed, view=self)
    
    @discord.ui.button(label="🚪 Exit Dungeon", style=discord.ButtonStyle.gray, row=1)
    async def exit_dungeon(self, interaction: discord.Interaction, button: Button):
        floor_id = self.floor_name.lower().replace(' ', '')
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
        
        drops = await compat_roll_loot(self.bot.game_data, loot_table, magic_find)
        items_obtained = []
        
        if self.party_id:
            party = PartySystem.get_party_by_id(self.party_id)
            if party:
                member_ids = [m['user_id'] for m in party['members']]
                member_data = [{'user_id': mid} for mid in member_ids]
                
                items_per_member = max(1, len(drops) // len(member_ids))
                
                for member_id in member_ids:
                    for item_id, amount in drops[:items_per_member]:
                        await self.bot.db.add_item_to_inventory(member_id, item_id, amount)
                        if member_id == self.user_id:
                            items_obtained.append(f"{item_id} x{amount}")
        else:
            for item_id, amount in drops:
                await self.bot.db.add_item_to_inventory(self.user_id, item_id, amount)
                items_obtained.append(f"{item_id} x{amount}")
        
        dungeon_loot = await self._roll_dungeon_loot(floor_key, score, magic_find)
        for item_id, amount in dungeon_loot:
            await self.bot.db.add_item_to_inventory(self.user_id, item_id, amount)
            items_obtained.append(f"✨ {item_id.replace('_', ' ').title()} x{amount}")
        
        if 'keys' in loot_table:
            min_keys, max_keys = loot_table['keys']
            bonus_keys = random.randint(min_keys, max_keys)
            self.keys += bonus_keys
        
        coin_rewards = (self.rooms_cleared * 100) + (self.secrets_found * 50) - (self.death_count * 50)
        xp_rewards = (self.rooms_cleared * 20) + (self.secrets_found * 10)
        
        total_rewards = coin_rewards + self.coins_gained_in_run
        
        if self.party_id:
            party = PartySystem.get_party_by_id(self.party_id)
            if party:
                member_data = party['members']
                
                coins_per_member = total_rewards // len(member_data)
                
                for member in member_data:
                    member_id = member['user_id']
                    await self.bot.player_manager.add_coins(member_id, coins_per_member)
                    player_data = await self.bot.db.get_player(member_id)
                    if player_data:
                        await self.bot.db.update_player(
                            member_id,
                            total_earned=player_data.get('total_earned', 0) + coins_per_member,
                            coins=player_data.get('coins', 0) + coins_per_member
                        )
        else:
            await self.bot.player_manager.add_coins(self.user_id, total_rewards)
            player_data = await self.bot.db.get_player(self.user_id)
            if player_data:
                await self.bot.db.update_player(
                    interaction.user.id,
                    total_earned=player_data.get('total_earned', 0) + total_rewards,
                    coins=player_data.get('coins', 0) + total_rewards
                )
        
        if items_obtained:
            embed.add_field(name="🎁 Items Found", value="\n".join(items_obtained[:15]), inline=False)
        embed.add_field(name="🗝️ Keys Obtained", value=str(self.keys), inline=True)
        embed.add_field(name="💰 Reward", value=f"{total_rewards} coins", inline=True)
        embed.add_field(name="⭐ XP Gained", value=f"{xp_rewards} XP", inline=True)
        
        if self.party_id:
            PartySystem.end_dungeon(self.party_id)
            embed.set_footer(text=f"Party rewards distributed to {self.party_size} members")
        
        self.stop()
        for child in self.children:
            if isinstance(child, Button):
                child.disabled = True 
        await interaction.response.edit_message(embed=embed, view=self)
    
    @discord.ui.button(label="💡 Get Hint", style=discord.ButtonStyle.blurple, row=1)
    async def get_puzzle_hint(self, interaction: discord.Interaction, button: Button):
        if not self.current_puzzle:
            await interaction.response.send_message("❌ No active puzzle!", ephemeral=True)
            return
        
        hint = self.current_puzzle.get_hint()
        
        if hint:
            attempts_remaining = self.current_puzzle.max_attempts - self.current_puzzle.attempts
            embed = discord.Embed(
                title=f"💡 Puzzle Hint",
                description=hint,
                color=discord.Color.blue()
            )
            embed.set_footer(text=f"Attempts remaining: {attempts_remaining}/{self.current_puzzle.max_attempts}")
            await interaction.response.send_message(embed=embed, ephemeral=True)
        else:
            await interaction.response.send_message("❌ No hints available for this puzzle!", ephemeral=True)
    
    async def check_puzzle_answer(self, message_content: str) -> bool:
        if not self.current_puzzle:
            return False
        
        is_correct, message = self.current_puzzle.attempt_solve(message_content)
        
        if is_correct:
            floor_difficulty = min(10, max(1, (self.rooms_cleared // 2) + 1))
            
            rewards = PuzzleSystem.calculate_puzzle_rewards(
                self.current_puzzle,
                floor_difficulty
            )
            
            self.coins_gained_in_run += rewards['coins']
            
            self.current_puzzle = None
            return True
        else:
            attempts_remaining = self.current_puzzle.max_attempts - self.current_puzzle.attempts
            if attempts_remaining <= 0:
                self.puzzles_failed += 1
                
                player_stats = await StatCalculator.calculate_full_stats(self.bot.db, self.user_id)
                
                damage = PuzzleSystem.calculate_damage_on_failure(
                    self.current_puzzle.difficulty,
                    player_stats
                )
                
                self.current_health = (self.current_health or 0) - damage
                self.total_damage += damage
                
                self.current_puzzle = None
                return False
            return False
    
    async def _roll_dungeon_loot(self, floor_id: str, score: int, magic_find: float):
        dungeon_loot = await self.bot.db.get_dungeon_loot(floor_id, score)
        items = []

        if not dungeon_loot:
            dungeon_loot = self._get_default_dungeon_loot(floor_id)

        valid_loot = []
        for loot in dungeon_loot:
            req = loot.get('score_requirement') if isinstance(loot, dict) else loot['score_requirement']
            if req is None or score >= req:
                valid_loot.append(loot)

        for loot in valid_loot:
            if isinstance(loot, dict):
                drop_chance = loot.get('drop_chance', 0.1)
                item_id = loot.get('item_id')
                min_amount = loot.get('min_amount', 1)
                max_amount = loot.get('max_amount', 1)
            else:
                drop_chance = loot['drop_chance']
                item_id = loot['item_id']
                min_amount = loot['min_amount']
                max_amount = loot['max_amount']

            adjusted_chance = drop_chance * (1 + magic_find / 100)
            if random.random() < adjusted_chance:
                amount = random.randint(min_amount, max_amount)
                items.append((item_id, amount))

        return items

    def _get_default_dungeon_loot(self, floor_id: str):
        
        return default_loot.get(floor_id, default_loot.get('entrance', []))
    
    def _calculate_score(self) -> int:
        base_score = (self.rooms_cleared * 20)
        secret_bonus = (self.secrets_found * 5)
        death_penalty = (self.death_count * 25)
        door_bonus = (self.wither_doors_unlocked * 3) + (self.blood_doors_unlocked * 2)
        crypt_bonus = (self.crypts_opened * 5)
        puzzle_penalty = (self.puzzles_failed * 10)
        
        score = base_score + secret_bonus + door_bonus + crypt_bonus - death_penalty - puzzle_penalty
        
        return max(0, score)

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
        
        can_enter, reason = await DungeonSystem.can_enter_floor(self.bot.db, interaction.user.id, floor)
        if not can_enter:
            await interaction.followup.send(f"❌ Cannot enter this floor: {reason}", ephemeral=True)
            return
        
        gear_score = await DungeonSystem.calculate_gear_score(self.bot.db, interaction.user.id)
        
        party = PartySystem.get_party(interaction.user.id)
        party_id = None
        
        if party:
            if party['leader_id'] != interaction.user.id:
                await interaction.followup.send("❌ Only the party leader can start a dungeon!", ephemeral=True)
                return
            
            if party['in_dungeon']:
                await interaction.followup.send("❌ Your party is already in a dungeon!", ephemeral=True)
                return
            
            result = PartySystem.start_dungeon(interaction.user.id, floor)
            if not result['success']:
                await interaction.followup.send(f"❌ {result['error']}", ephemeral=True)
                return
            
            party_id = party['party_id']
        
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
        
        view = DungeonView(self.bot, interaction.user.id, floor_info['name'], floor_info, party_id)
        
        embed = discord.Embed(
            title=f"🏰 Entering {floor_info['name']}",
            description="Your dungeon run has started!\n\nNavigate through rooms, find secrets, and survive to get rewards!",
            color=discord.Color.dark_purple()
        )
        embed.add_field(name="Expected Time", value=f"~{floor_info['time']//60}m {floor_info['time']%60}s", inline=True)
        embed.add_field(name="Base Rewards", value=f"{floor_info['rewards']:,} coins", inline=True)
        embed.add_field(name="Gear Score", value=f"{gear_score}", inline=True)
        
        if party_id:
            party = PartySystem.get_party_by_id(party_id)
            if party:
                embed.add_field(name="Party Size", value=f"{len(party['members'])}/{party['max_members']}", inline=True)
                embed.set_footer(text="Party dungeon run - rewards will be distributed")
        else:
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

async def setup(bot):
    await bot.add_cog(DungeonCommands(bot))