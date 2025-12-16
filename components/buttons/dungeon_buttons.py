import discord
from discord.ui import Button
import random
from utils.stat_calculator import StatCalculator
from utils.systems.puzzle_system import PuzzleSystem
from utils.systems.combat_system import CombatSystem
from components.views.puzzle_view import PuzzleView

class DungeonOpenDoorButton(discord.ui.Button):
    def __init__(self, view):
        super().__init__(label="🗝️ Open Door", style=discord.ButtonStyle.green, custom_id="dungeon_open_door", row=0)
        self.parent_view = view
    
    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.parent_view.user_id:
            await interaction.response.send_message("This isn't your dungeon run!", ephemeral=True)
            return
        
        player = await self.parent_view.bot.db.get_player(self.parent_view.user_id)   
        if not player:
            return
        
        if self.parent_view.current_health is None:
            player_stats = await StatCalculator.calculate_player_stats(self.parent_view.bot.db, self.parent_view.bot.game_data, self.parent_view.user_id)
            self.parent_view.current_health = int(player_stats['max_health'])
            self.parent_view.max_health = int(player_stats['max_health'])
        
        if self.parent_view.rooms_cleared >= self.parent_view.total_rooms:
            from components.views.dungeon_combat_view import DungeonCombatView
            
            floor_difficulty = {
                'entrance': 1, 'floor1': 2, 'floor2': 3, 'floor3': 5,
                'floor4': 7, 'floor5': 10, 'floor6': 15, 'floor7': 20
            }
            floor_id = self.parent_view.floor_name.lower().replace(' ', '')
            difficulty = floor_difficulty.get(floor_id, 1)
            
            boss_health = 2000 * difficulty
            boss_damage = 100 * difficulty
            boss_defense = 150 * difficulty
            
            boss_names = ['Necromancer', 'Watcher', 'Shadow Lord', 'Crypt Master', 'Ancient Guardian']
            boss_name = random.choice(boss_names)
            
            combat_view = DungeonCombatView(
                self.parent_view.bot,
                self.parent_view.user_id,
                boss_name,
                boss_health,
                boss_damage,
                boss_defense,
                self.parent_view,
                self.parent_view.party_id
            )
            
            embed = discord.Embed(
                title=f"👹 BOSS - {boss_name}!",
                description=f"The final boss has appeared!\n\nDefeat it to complete the dungeon!",
                color=discord.Color.dark_red()
            )
            embed.add_field(name="Boss Health", value=f"❤️ {boss_health:,} HP", inline=True)
            embed.add_field(name="Boss Defense", value=f"🛡️ {boss_defense:,}", inline=True)
            embed.add_field(name="Boss Damage", value=f"⚔️ ~{boss_damage} damage", inline=True)
            embed.set_footer(text="This is the final battle!")
            
            await interaction.response.edit_message(embed=embed, view=combat_view)
            return
        
        self.parent_view.rooms_cleared += 1
        
        if self.parent_view.current_health and self.parent_view.max_health:
            self.parent_view.current_health = await CombatSystem.apply_health_regeneration(
                self.parent_view.bot.db, self.parent_view.user_id, 
                int(self.parent_view.current_health), int(self.parent_view.max_health)
            )
        
        room_types = ['mob', 'puzzle', 'trap', 'treasure', 'blood_door', 'wither_door', 'crypt']
        weights = [35, 20, 15, 15, 5, 5, 5]
        room_type = random.choices(room_types, weights=weights)[0]
        result = ""
        
        if room_type == 'wither_door' and self.parent_view.keys > 0:
            self.parent_view.keys -= 1
            self.parent_view.wither_doors_unlocked += 1
            result = f"🚪 **Wither Door!** You used a key to unlock it! (-1 🗝️)\nSecrets may be behind here..."
            if random.random() > 0.4:
                secret_count = random.randint(1, 3)
                self.parent_view.secrets_found += secret_count
                coins = random.randint(50, 150)
                self.parent_view.coins_gained_in_run += coins
                result += f"\n✨ Found {secret_count} secret(s) and {coins} coins!"
        elif room_type == 'blood_door':
            cost = random.randint(5, 15)
            if self.parent_view.current_health and self.parent_view.current_health > cost:
                self.parent_view.current_health -= cost
                self.parent_view.blood_doors_unlocked += 1
                result = f"🩸 **Blood Door!** You sacrificed {cost} HP to open it!\nRisk brings reward..."
                if random.random() > 0.5:
                    secret_count = random.randint(2, 4)
                    self.parent_view.secrets_found += secret_count
                    result += f"\n✨ Found {secret_count} secret(s)!"
            else:
                result = f"🩸 **Blood Door!** Not enough HP to open (need {cost} HP)"
                room_type = 'blocked'
        elif room_type == 'crypt':
            self.parent_view.crypts_opened += 1
            loot_roll = random.random()
            if loot_roll > 0.7:
                coins = random.randint(100, 300)
                self.parent_view.coins_gained_in_run += coins
                result = f"⚰️ **Crypt!** You opened a crypt and found {coins} coins!"
            else:
                damage_taken = random.randint(15, 35)
                self.parent_view.current_health = (self.parent_view.current_health or 0) - damage_taken
                self.parent_view.total_damage += damage_taken
                result = f"⚰️ **Crypt!** Undead burst out and dealt {damage_taken} damage!"
        elif room_type == 'mob':
            from components.views.dungeon_combat_view import DungeonCombatView
            
            mob_difficulty = random.choice(['easy', 'medium', 'hard', 'miniboss'])
            
            mob_configs = {
                'easy': {'health': 150, 'damage': 10, 'defense': 10},
                'medium': {'health': 300, 'damage': 20, 'defense': 25},
                'hard': {'health': 500, 'damage': 35, 'defense': 50},
                'miniboss': {'health': 1000, 'damage': 60, 'defense': 100}
            }
            
            config = mob_configs[mob_difficulty]
            
            mob_names = {
                'easy': ['Zombie', 'Skeleton', 'Spider'],
                'medium': ['Crypt Ghoul', 'Lost Adventurer', 'Dungeon Zombie'],
                'hard': ['Dungeon Knight', 'Crypt Lurker', 'Shadow Assassin'],
                'miniboss': ['Super Archer', 'Super Tank', 'Lonely Spider']
            }
            
            mob_name = random.choice(mob_names[mob_difficulty])
            
            combat_view = DungeonCombatView(
                self.parent_view.bot,
                self.parent_view.user_id,
                mob_name,
                config['health'],
                config['damage'],
                config['defense'],
                self.parent_view,
                self.parent_view.party_id
            )
            
            level_color = discord.Color.green()
            if mob_difficulty == 'medium':
                level_color = discord.Color.gold()
            elif mob_difficulty == 'hard':
                level_color = discord.Color.red()
            elif mob_difficulty == 'miniboss':
                level_color = discord.Color.purple()
            
            embed = discord.Embed(
                title=f"⚔️ Mob Room - {mob_name} appeared!",
                description=f"Prepare for battle!",
                color=level_color
            )
            embed.add_field(name="Enemy Health", value=f"❤️ {config['health']} HP", inline=True)
            embed.add_field(name="Enemy Defense", value=f"🛡️ {config['defense']}", inline=True)
            embed.add_field(name="Enemy Damage", value=f"⚔️ ~{config['damage']} damage", inline=True)
            embed.set_footer(text="Use the buttons below to fight!")
            
            await interaction.response.edit_message(embed=embed, view=combat_view)
            return
        elif room_type == 'puzzle':
            floor_id = self.parent_view.floor_name.lower().replace(' ', '')
            puzzle_difficulty = min(10, max(1, (self.parent_view.rooms_cleared // 2) + 1))
            
            self.parent_view.current_puzzle = PuzzleSystem.create_puzzle(puzzle_difficulty, self.parent_view.party_size)
            
            embed = discord.Embed(
                title=f"🧩 Puzzle Room - {self.parent_view.current_puzzle.data['name']}",
                description=f"**Difficulty:** {puzzle_difficulty}/10\n**Attempts:** {self.parent_view.current_puzzle.max_attempts}\n\n{self.parent_view.current_puzzle.data['description']}",
                color=discord.Color.purple()
            )
            
            puzzle_display = self.parent_view._format_puzzle_display(self.parent_view.current_puzzle)
            if puzzle_display:
                embed.add_field(name="Puzzle", value=puzzle_display, inline=False)
            
            embed.add_field(name="Question", value=self.parent_view.current_puzzle.data['question'], inline=False)
            
            embed.add_field(name="❤️ Health", value=f"{self.parent_view.current_health or 0}/{self.parent_view.max_health or 0}", inline=True)
            embed.add_field(name="🗝️ Keys", value=str(self.parent_view.keys), inline=True)
            embed.add_field(name="✨ Secrets", value=f"{self.parent_view.secrets_found}/{self.parent_view.max_secrets}", inline=True)
            
            puzzle_view = PuzzleView(self.parent_view.bot, self.parent_view.user_id, self.parent_view.current_puzzle, self.parent_view)
            await interaction.response.edit_message(embed=embed, view=puzzle_view)
            return
        elif room_type == 'trap':
            trap_types = ['Arrow Trap', 'Lava Pit', 'TNT Trap', 'Poison Darts', 'Falling Blocks']
            trap_name = random.choice(trap_types)
            base_damage = random.randint(10, 25)
            
            player_stats = await StatCalculator.calculate_full_stats(self.parent_view.bot.db, self.parent_view.user_id)
            player_defense = player_stats.get('defense', 0)
            
            damage_taken = int(CombatSystem._calculate_mob_damage(base_damage, player_defense))
            
            self.parent_view.current_health = (self.parent_view.current_health or 0) - damage_taken
            self.parent_view.total_damage += damage_taken
            result = f"🪤 **Trap Room ({trap_name})!** You triggered traps and took {damage_taken} damage!"
            
            if random.random() > 0.7:
                secret_count = 1
                self.parent_view.secrets_found += secret_count
                result += f"\n✨ Found a secret while dodging traps!"
        elif room_type != 'blocked':
            coins = random.randint(30, 150)
            self.parent_view.coins_gained_in_run += coins
            result = f"💎 **Treasure Room!** You found {coins} coins!"
            if random.random() > 0.5:
                secret_count = random.randint(1, 3)
                self.parent_view.secrets_found += secret_count
                result += f"\n✨ Also found {secret_count} secret(s)!"
        
        if not result:
            result = "🚪 Nothing happened."
        
        if room_type != 'blocked' and random.random() > 0.85:
            self.parent_view.secrets_found += 1
            result += f"\n🔍 You spotted a hidden secret! (+{self.parent_view.secrets_found}/{self.parent_view.max_secrets})"
        
        self.parent_view.room_history.append(room_type)
        
        if self.parent_view.current_health is not None and self.parent_view.current_health <= 0:
            self.parent_view.death_count += 1
            self.parent_view.current_health = self.parent_view.max_health // 2 if self.parent_view.max_health else 50
            result += f"\n💀 **You died!** Respawning with half health... (Deaths: {self.parent_view.death_count})"
        
        embed = discord.Embed(
            title=f"🏰 {self.parent_view.floor_name} - Room {self.parent_view.rooms_cleared}/{self.parent_view.total_rooms}",
            description=result,
            color=discord.Color.blue()
        )
        embed.add_field(name="❤️ Health", value=f"{self.parent_view.current_health or 0}/{self.parent_view.max_health or 0}", inline=True)
        embed.add_field(name="🗝️ Keys", value=str(self.parent_view.keys), inline=True)
        embed.add_field(name="✨ Secrets", value=f"{self.parent_view.secrets_found}/{self.parent_view.max_secrets}", inline=True)
        embed.add_field(name="💀 Deaths", value=str(self.parent_view.death_count), inline=True)
        embed.add_field(name="🚪 Doors Unlocked", value=f"W:{self.parent_view.wither_doors_unlocked} B:{self.parent_view.blood_doors_unlocked}", inline=True)
        embed.add_field(name="⚰️ Crypts", value=str(self.parent_view.crypts_opened), inline=True)
        
        await interaction.response.edit_message(embed=embed, view=self.parent_view)

class DungeonSearchSecretsButton(discord.ui.Button):
    def __init__(self, view):
        super().__init__(label="🔍 Search for Secrets", style=discord.ButtonStyle.blurple, custom_id="dungeon_search_secrets", row=0)
        self.parent_view = view
    
    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.parent_view.user_id:
            await interaction.response.send_message("This isn't your dungeon run!", ephemeral=True)
            return
        
        if self.parent_view.secrets_found >= self.parent_view.max_secrets:
            embed = discord.Embed(
                title=f"🏰 {self.parent_view.floor_name} - Room {self.parent_view.rooms_cleared}/{self.parent_view.total_rooms}",
                description=f"✨ All Secrets Found!\nYou've already found all {self.parent_view.max_secrets} secrets in this dungeon!",
                color=discord.Color.gold()
            )
            embed.add_field(name="❤️ Health", value=f"{self.parent_view.current_health or 0}/{self.parent_view.max_health or 0}", inline=True)
            embed.add_field(name="🗝️ Keys", value=str(self.parent_view.keys), inline=True)
            embed.add_field(name="✨ Secrets", value=f"{self.parent_view.secrets_found}/{self.parent_view.max_secrets}", inline=True)
            embed.add_field(name="💀 Deaths", value=str(self.parent_view.death_count), inline=True)
            embed.add_field(name="🚪 Doors Unlocked", value=f"W:{self.parent_view.wither_doors_unlocked} B:{self.parent_view.blood_doors_unlocked}", inline=True)
            embed.add_field(name="⚰️ Crypts", value=str(self.parent_view.crypts_opened), inline=True)
            await interaction.response.edit_message(embed=embed, view=self.parent_view)
            return
        
        result = ""
        if random.random() > 0.4:
            self.parent_view.secrets_found += 1
            coins = random.randint(30, 120)
            self.parent_view.coins_gained_in_run += coins
            
            secret_types = ['Chest', 'Lever', 'Wither Essence', 'Bat', 'Item Frame', 'Redstone Key']
            secret_type = random.choice(secret_types)
            
            result = f"✨ **Secret Found - {secret_type}!**\nYou found a secret and gained {coins} coins!"
        else:
            result = "🔍 **No Secret Here**\nYou searched but found nothing..."
        
        embed = discord.Embed(
            title=f"🏰 {self.parent_view.floor_name} - Room {self.parent_view.rooms_cleared}/{self.parent_view.total_rooms}",
            description=result,
            color=discord.Color.gold() if self.parent_view.secrets_found > 0 else discord.Color.greyple()
        )
        embed.add_field(name="❤️ Health", value=f"{self.parent_view.current_health or 0}/{self.parent_view.max_health or 0}", inline=True)
        embed.add_field(name="🗝️ Keys", value=str(self.parent_view.keys), inline=True)
        embed.add_field(name="✨ Secrets", value=f"{self.parent_view.secrets_found}/{self.parent_view.max_secrets}", inline=True)
        embed.add_field(name="💀 Deaths", value=str(self.parent_view.death_count), inline=True)
        embed.add_field(name="🚪 Doors Unlocked", value=f"W:{self.parent_view.wither_doors_unlocked} B:{self.parent_view.blood_doors_unlocked}", inline=True)
        embed.add_field(name="⚰️ Crypts", value=str(self.parent_view.crypts_opened), inline=True)
        
        await interaction.response.edit_message(embed=embed, view=self.parent_view)

class DungeonExitButton(discord.ui.Button):
    def __init__(self, view):
        super().__init__(label="🚪 Exit Dungeon", style=discord.ButtonStyle.gray, custom_id="dungeon_exit", row=1)
        self.parent_view = view
    
    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.parent_view.user_id:
            await interaction.response.send_message("This isn't your dungeon run!", ephemeral=True)
            return
        
        from utils.systems.party_system import PartySystem
        from utils.normalize import normalize_item_id
        from utils.compat import roll_loot as compat_roll_loot
        from utils.data.loot_tables import default_loot
        
        floor_id = self.parent_view.floor_name.lower().replace(' ', '')
        score = self.parent_view._calculate_score()
        
        embed = discord.Embed(
            title=f"🏰 {self.parent_view.floor_name} Run Complete!",
            description=f"**Score: {score}**",
            color=discord.Color.green()
        )
        embed.add_field(name="Rooms Cleared", value=f"{self.parent_view.rooms_cleared}/{self.parent_view.total_rooms}")
        embed.add_field(name="Secrets Found", value=f"{self.parent_view.secrets_found}/{self.parent_view.max_secrets}")
        embed.add_field(name="Damage Taken", value=str(self.parent_view.total_damage))
        
        floor_key = normalize_item_id(self.parent_view.floor_name)
        loot_table = await self.parent_view.bot.game_data.get_loot_table(floor_key, 'dungeon')
        if not loot_table:
            loot_table = {}
        
        player_stats = await StatCalculator.calculate_player_stats(self.parent_view.bot.db, self.parent_view.bot.game_data, self.parent_view.user_id)
        magic_find = player_stats.get('magic_find', 0)
        
        drops = await compat_roll_loot(self.parent_view.bot.game_data, loot_table, magic_find)
        items_obtained = []
        
        if self.parent_view.party_id:
            party = PartySystem.get_party_by_id(self.parent_view.party_id)
            if party:
                member_ids = [m['user_id'] for m in party['members']]
                member_data = [{'user_id': mid} for mid in member_ids]
                
                items_per_member = max(1, len(drops) // len(member_ids))
                
                for member_id in member_ids:
                    for item_id, amount in drops[:items_per_member]:
                        await self.parent_view.bot.db.add_item_to_inventory(member_id, item_id, amount)
                        if member_id == self.parent_view.user_id:
                            items_obtained.append(f"{item_id} x{amount}")
        else:
            for item_id, amount in drops:
                await self.parent_view.bot.db.add_item_to_inventory(self.parent_view.user_id, item_id, amount)
                items_obtained.append(f"{item_id} x{amount}")
        
        dungeon_loot = await self.parent_view._roll_dungeon_loot(floor_key, score, magic_find)
        for item_id, amount in dungeon_loot:
            await self.parent_view.bot.db.add_item_to_inventory(self.parent_view.user_id, item_id, amount)
            items_obtained.append(f"✨ {item_id.replace('_', ' ').title()} x{amount}")
        
        if 'keys' in loot_table:
            min_keys, max_keys = loot_table['keys']
            bonus_keys = random.randint(min_keys, max_keys)
            self.parent_view.keys += bonus_keys
        
        coin_rewards = (self.parent_view.rooms_cleared * 100) + (self.parent_view.secrets_found * 50) - (self.parent_view.death_count * 50)
        xp_rewards = (self.parent_view.rooms_cleared * 20) + (self.parent_view.secrets_found * 10)
        
        total_rewards = coin_rewards + self.parent_view.coins_gained_in_run
        
        if self.parent_view.party_id:
            party = PartySystem.get_party_by_id(self.parent_view.party_id)
            if party:
                member_data = party['members']
                
                coins_per_member = total_rewards // len(member_data)
                
                for member in member_data:
                    member_id = member['user_id']
                    await self.parent_view.bot.player_manager.add_coins(member_id, coins_per_member)
        else:
            await self.parent_view.bot.player_manager.add_coins(self.parent_view.user_id, total_rewards)
        
        if items_obtained:
            embed.add_field(name="🎁 Items Found", value="\n".join(items_obtained[:15]), inline=False)
        embed.add_field(name="🗝️ Keys Obtained", value=str(self.parent_view.keys), inline=True)
        embed.add_field(name="💰 Reward", value=f"{total_rewards} coins", inline=True)
        embed.add_field(name="⭐ XP Gained", value=f"{xp_rewards} XP", inline=True)
        
        stats = await self.parent_view.bot.db.get_player_stats(interaction.user.id)
        if stats:
            total_dungeons = stats.get('total_dungeons', 0) + 1
            await self.parent_view.bot.db.update_player_stats(interaction.user.id, total_dungeons=total_dungeons)
            
            from utils.systems.achievement_system import AchievementSystem
            await AchievementSystem.check_dungeon_achievements(self.parent_view.bot.db, interaction, interaction.user.id, total_dungeons)
            
            if score >= 300:
                await AchievementSystem.unlock_action_achievement(self.parent_view.bot.db, interaction, interaction.user.id, 'dungeon_s_rank')
            
            if self.parent_view.death_count == 0:
                await AchievementSystem.unlock_action_achievement(self.parent_view.bot.db, interaction, interaction.user.id, 'dungeon_no_death')
        
        if self.parent_view.party_id:
            await PartySystem.end_dungeon(self.parent_view.bot.db, self.parent_view.party_id)
            embed.set_footer(text=f"Party rewards distributed to {self.parent_view.party_size} members")
        
        stats = await self.parent_view.bot.db.get_dungeon_stats(self.parent_view.user_id)
        
        elapsed_time = 300
        
        await self.parent_view.bot.db.increment_dungeon_stats(
            self.parent_view.user_id,
            total_runs=1,
            secrets_found=self.parent_view.secrets_found,
            total_deaths=self.parent_view.death_count,
            catacombs_xp=xp_rewards
        )
        
        from utils.systems.badge_system import BadgeSystem
        dungeon_stats = await self.parent_view.bot.db.get_dungeon_stats(self.parent_view.user_id)
        if dungeon_stats:
            total_runs = dungeon_stats.get('total_runs', 0)
            if total_runs == 1:
                await BadgeSystem.unlock_badge(self.parent_view.bot.db, self.parent_view.user_id, 'first_dungeon')
            elif total_runs >= 100:
                await BadgeSystem.unlock_badge(self.parent_view.bot.db, self.parent_view.user_id, 'dungeon_master')
        
        if not stats or score > (stats['best_score'] if 'best_score' in stats else 0):
            await self.parent_view.bot.db.update_dungeon_stats(self.parent_view.user_id, best_score=score)
        
        fastest_run_val = stats['fastest_run'] if stats and 'fastest_run' in stats else 0
        if (
            not stats
            or (elapsed_time < (stats['fastest_run'] if 'fastest_run' in stats else 999999) and fastest_run_val > 0)
            or fastest_run_val == 0
        ):
            await self.parent_view.bot.db.update_dungeon_stats(self.parent_view.user_id, fastest_run=elapsed_time)
        
        self.parent_view.stop()
        for child in self.parent_view.children:
            if isinstance(child, Button):
                child.disabled = True 
        await interaction.response.edit_message(embed=embed, view=self.parent_view)

class DungeonGetHintButton(discord.ui.Button):
    def __init__(self, view):
        super().__init__(label="💡 Get Hint", style=discord.ButtonStyle.blurple, custom_id="dungeon_get_hint", row=1)
        self.parent_view = view
    
    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.parent_view.user_id:
            await interaction.response.send_message("This isn't your dungeon run!", ephemeral=True)
            return
        
        if not self.parent_view.current_puzzle:
            await interaction.response.send_message("❌ No active puzzle!", ephemeral=True)
            return
        
        hint = self.parent_view.current_puzzle.get_hint()
        
        if hint:
            attempts_remaining = self.parent_view.current_puzzle.max_attempts - self.parent_view.current_puzzle.attempts
            embed = discord.Embed(
                title=f"💡 Puzzle Hint",
                description=hint,
                color=discord.Color.blue()
            )
            embed.set_footer(text=f"Attempts remaining: {attempts_remaining}/{self.parent_view.current_puzzle.max_attempts}")
            await interaction.response.send_message(embed=embed, ephemeral=True)
        else:
            await interaction.response.send_message("❌ No hints available for this puzzle!", ephemeral=True)
