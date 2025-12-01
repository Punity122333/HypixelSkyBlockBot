import discord
from discord.ext import commands
from discord import app_commands
from discord.ui import View, Button
import random
import asyncio
from typing import Optional, TYPE_CHECKING, Tuple
from utils.stat_calculator import StatCalculator
from utils.systems.combat_system import CombatSystem
from utils.compat import roll_loot as compat_roll_loot
from utils.event_effects import EventEffects

if TYPE_CHECKING:
    from main import SkyblockBot

class CombatView(View):
    def __init__(self, bot: "SkyblockBot", user_id: int, mob_name: str, mob_health: int, mob_damage: int, coins_reward: int, xp_reward: int):
        super().__init__(timeout=120)
        self.bot = bot
        self.user_id = user_id
        self.mob_name = mob_name
        self.mob_health = mob_health
        self.mob_max_health = mob_health
        self.mob_damage = mob_damage
        self.coins_reward = coins_reward
        self.xp_reward = xp_reward
        self.player_health: Optional[int] = None
        self.player_max_health: Optional[int] = None
        self.player_damage: int = 50
        self.player_stats: Optional[dict] = None
        self.message: Optional[discord.Message] = None
        self.event_effects = EventEffects(bot)
    
    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("This isn't your fight!", ephemeral=True)
            return False
        return True
    
    @discord.ui.button(label="⚔️ Attack", style=discord.ButtonStyle.red)
    async def attack_button(self, interaction: discord.Interaction, button: Button):
        if self.player_stats is None:
            self.player_stats = await StatCalculator.calculate_player_stats(self.bot.db, self.bot.game_data, self.user_id)
        
        if self.player_health is None:
            self.player_health = int(self.player_stats['max_health'])
            self.player_max_health = int(self.player_stats['max_health'])
        
        mob_defense = 0
        damage_result = await CombatSystem.calculate_player_damage(self.bot.db, self.user_id, mob_defense)
        
        total_damage = int(damage_result['damage'])
        crit = damage_result['is_crit']
        combat_level = damage_result.get('combat_level', 0)
        skill_multiplier = damage_result.get('skill_multiplier', 1.0)
        
        ferocity_hits = 1 + (self.player_stats.get('ferocity', 0) // 100)
        if ferocity_hits > 1:
            total_damage = int(total_damage * ferocity_hits)
        
        self.mob_health -= total_damage
        
        embed = discord.Embed(title=f"⚔️ Fighting {self.mob_name}", color=discord.Color.red())
        
        if self.mob_health <= 0:
            mob_id = self.mob_name.lower().replace(' ', '_')
            loot_table = await self.bot.game_data.get_loot_table(self.mob_name, 'mob')
            
            if not loot_table:
                loot_table = {}
            
            if 'coins' not in loot_table:
                loot_table['coins'] = (self.coins_reward // 2, self.coins_reward)
            if 'xp' not in loot_table:
                loot_table['xp'] = self.xp_reward
            
            magic_find = self.player_stats.get('magic_find', 0)
            fortune = self.player_stats.get('looting', 0)
            drops = await compat_roll_loot(self.bot.game_data, loot_table, magic_find, fortune)
            
            items_obtained = []
            for item_id, amount in drops:
                await self.bot.db.add_item_to_inventory(self.user_id, item_id, amount)
                item_name = item_id.replace('_', ' ').title()
                items_obtained.append(f"{item_name} x{amount}")
                
                current_collection = await self.bot.db.get_collection(self.user_id, item_id)
                await self.bot.db.add_collection(self.user_id, item_id, current_collection + amount)

            pet_drop = await self.bot.game_data._try_drop_pet(mob_id, magic_find)
            if pet_drop:
                pet_type, pet_rarity = pet_drop
                await self.bot.db.add_player_pet(self.user_id, pet_type, pet_rarity)
                items_obtained.append(f"🐾 **{pet_rarity} {pet_type.title()} Pet!**")
            
            coins = self.coins_reward
            xp = self.xp_reward
            
            xp_multiplier = await self.event_effects.get_xp_multiplier('combat')
            coin_multiplier = await self.event_effects.get_coin_multiplier()
            magic_find_bonus = await self.event_effects.get_magic_find_bonus()
            
            xp = int(xp * xp_multiplier)
            coins = int(coins * coin_multiplier)
            
            embed.description = f"💀 You defeated the {self.mob_name}!"
            if combat_level > 0:
                combat_drop_multiplier = 1.0 + (combat_level * 0.05)
                embed.description += f"\n⚔️ **Combat Level {combat_level}** - {skill_multiplier:.2f}x damage, {combat_drop_multiplier:.2f}x drops"
            
            if items_obtained:
                embed.add_field(name="🎁 Items Dropped", value="\n".join(items_obtained[:10]), inline=False)
            else:
                embed.add_field(name="🎁 Items Dropped", value="No items dropped this time.", inline=False)
            
            reward_text = f"+{coins} coins\n+{xp} Combat XP"
            if xp_multiplier > 1.0 or coin_multiplier > 1.0:
                reward_text += "\n🎪 Event bonuses active!"
            embed.add_field(name="💰 Reward", value=reward_text, inline=False)
            
            await self.bot.player_manager.add_coins(self.user_id, coins)
            
            player = await self.bot.db.get_player(self.user_id)
            if player:
                await self.bot.db.update_player(
                    interaction.user.id,
                    total_earned=player.get('total_earned', 0) + coins,
                    coins=player.get('coins', 0) + coins
                )

            
            skills = await self.bot.db.get_skills(self.user_id)
            combat_skill = next((s for s in skills if s['skill_name'] == 'combat'), None)
            if combat_skill:
                new_xp = combat_skill['xp'] + xp
                new_level = await self.bot.game_data.calculate_level_from_xp('combat', new_xp)
                await self.bot.db.update_skill(self.user_id, 'combat', xp=new_xp, level=new_level)
            
            self.stop()
            for child in self.children:
                if isinstance(child, Button):
                    child.disabled = True   
            await interaction.response.edit_message(embed=embed, view=self)
            return
        
        mob_damage = random.randint(self.mob_damage - 5, self.mob_damage + 5)
        damage_reduction = StatCalculator.calculate_damage_reduction(
            self.player_stats['defense'], 
            self.player_stats.get('true_defense', 0)
        )
        mob_damage = int(mob_damage * (1 - damage_reduction))
        mob_damage = max(1, mob_damage)
        self.player_health = (self.player_health or 0) - mob_damage
        
        if self.player_health <= 0:
            embed.description = f"💀 You were defeated by the {self.mob_name}!"
            embed.add_field(name="Penalty", value="-500 coins")
            await self.bot.player_manager.remove_coins(self.user_id, 500)   
            
            self.stop()
            for child in self.children:
                if isinstance(child, Button):
                    child.disabled = True   
            await interaction.response.edit_message(embed=embed, view=self)
            return
        
        hit_text = f"💥 **CRITICAL HIT!** You dealt {total_damage} damage!" if crit else f"⚔️ You dealt {total_damage} damage!"
        if ferocity_hits > 1:
            hit_text += f" ({ferocity_hits}x hits from Ferocity!)"
        if combat_level > 0:
            hit_text += f"\n⚔️ Combat Level {combat_level} ({skill_multiplier:.2f}x damage bonus)"
        embed.description = f"{hit_text}\n🩸 The {self.mob_name} dealt {mob_damage} damage to you!"
        
        mob_hp_bar = self._create_health_bar(self.mob_health, self.mob_max_health)
        player_hp_bar = self._create_health_bar(self.player_health or 0, self.player_max_health or 100)
        
        embed.add_field(name=f"{self.mob_name}", value=f"{mob_hp_bar}\n❤️ {self.mob_health}/{self.mob_max_health} HP", inline=False)
        embed.add_field(name="Your Health", value=f"{player_hp_bar}\n❤️ {self.player_health or 0}/{self.player_max_health or 0} HP", inline=False)
        
        await interaction.response.edit_message(embed=embed, view=self)
    
    @discord.ui.button(label="🛡️ Defend", style=discord.ButtonStyle.blurple)
    async def defend_button(self, interaction: discord.Interaction, button: Button):
        if self.player_stats is None:
            self.player_stats = await StatCalculator.calculate_player_stats(self.bot.db, self.bot.game_data, self.user_id)
        
        if self.player_health is None:
            self.player_health = int(self.player_stats['max_health'])
            self.player_max_health = int(self.player_stats['max_health'])
        
        mob_damage = random.randint(self.mob_damage - 5, self.mob_damage + 5)
        damage_reduction = StatCalculator.calculate_damage_reduction(
            self.player_stats['defense'], 
            self.player_stats.get('true_defense', 0)
        )
        mob_damage = int(mob_damage * (1 - damage_reduction) * 0.5)
        mob_damage = max(1, mob_damage)
        self.player_health = (self.player_health or 0) - mob_damage
        
        embed = discord.Embed(title=f"⚔️ Fighting {self.mob_name}", color=discord.Color.blue())
        embed.description = f"🛡️ You defended! The {self.mob_name} dealt only {mob_damage} damage!"
        
        if self.player_health <= 0:
            embed.description = f"💀 You were defeated by the {self.mob_name}!"
            embed.add_field(name="Penalty", value="-500 coins")
            await self.bot.player_manager.remove_coins(self.user_id, 500)   
            
            self.stop()
            for child in self.children:
                if isinstance(child, Button):
                    child.disabled = True   
            await interaction.response.edit_message(embed=embed, view=self)
            return
        
        mob_hp_bar = self._create_health_bar(self.mob_health, self.mob_max_health)
        player_hp_bar = self._create_health_bar(self.player_health or 0, self.player_max_health or 100)
        
        embed.add_field(name=f"{self.mob_name}", value=f"{mob_hp_bar}\n❤️ {self.mob_health}/{self.mob_max_health} HP", inline=False)
        embed.add_field(name="Your Health", value=f"{player_hp_bar}\n❤️ {self.player_health or 0}/{self.player_max_health or 0} HP", inline=False)
        
        await interaction.response.edit_message(embed=embed, view=self)
    
    @discord.ui.button(label="✨ Use Ability", style=discord.ButtonStyle.green)
    async def ability_button(self, interaction: discord.Interaction, button: Button):
        if self.player_stats is None:
            self.player_stats = await StatCalculator.calculate_player_stats(self.bot.db, self.bot.game_data, self.user_id)
        
        if self.player_health is None:
            self.player_health = int(self.player_stats['max_health'])
            self.player_max_health = int(self.player_stats['max_health'])
        
        mana_cost = 50
        current_mana = self.player_stats.get('mana', self.player_stats['max_mana'])
        if current_mana < mana_cost:
            await interaction.response.send_message("❌ Not enough mana!", ephemeral=True)
            return
        
        combat_effects = StatCalculator.apply_combat_effects(self.player_stats, None)
        ability_multiplier = 3 + (self.player_stats.get('ability_damage', 0) / 100)
        ability_damage = int(combat_effects['base_damage'] * ability_multiplier)
        self.mob_health -= ability_damage
        
        await self.bot.db.update_player(self.user_id, mana=current_mana - mana_cost)
        
        embed = discord.Embed(title=f"⚔️ Fighting {self.mob_name}", color=discord.Color.purple())
        
        if self.mob_health <= 0:
            mob_id = self.mob_name.lower().replace(' ', '_')
            loot_table = await self.bot.game_data.get_loot_table(self.mob_name, 'mob')
            
            if not loot_table:
                loot_table = {}
            
            if 'coins' not in loot_table:
                loot_table['coins'] = (self.coins_reward // 2, self.coins_reward)
            if 'xp' not in loot_table:
                loot_table['xp'] = self.xp_reward
            
            magic_find = self.player_stats.get('magic_find', 0)
            fortune = self.player_stats.get('looting', 0)
            drops = await compat_roll_loot(self.bot.game_data, loot_table, magic_find, fortune)
            
            items_obtained = []
            for item_id, amount in drops:
                await self.bot.db.add_item_to_inventory(self.user_id, item_id, amount)
                item_name = item_id.replace('_', ' ').title()
                items_obtained.append(f"{item_name} x{amount}")
                
                current_collection = await self.bot.db.get_collection(self.user_id, item_id)
                await self.bot.db.add_collection(self.user_id, item_id, current_collection + amount)
            
            pet_drop = await self.bot.game_data._try_drop_pet(mob_id, magic_find)
            if pet_drop:
                pet_type, pet_rarity = pet_drop
                await self.bot.db.add_player_pet(self.user_id, pet_type, pet_rarity)
                items_obtained.append(f"🐾 **{pet_rarity} {pet_type.title()} Pet!**")
            
            coins = self.coins_reward
            xp = self.xp_reward
            
            xp_multiplier = await self.event_effects.get_xp_multiplier('combat')
            coin_multiplier = await self.event_effects.get_coin_multiplier()
            magic_find_bonus = await self.event_effects.get_magic_find_bonus()
            
            xp = int(xp * xp_multiplier)
            coins = int(coins * coin_multiplier)
            
            embed.description = f"💀 You defeated the {self.mob_name} with your ability!"
            if items_obtained:
                embed.add_field(name="🎁 Items Dropped", value="\n".join(items_obtained[:10]), inline=False)
            else:
                embed.add_field(name="🎁 Items Dropped", value="No items dropped this time.", inline=False)
            
            reward_text = f"+{coins} coins\n+{xp} Combat XP"
            if xp_multiplier > 1.0 or coin_multiplier > 1.0:
                reward_text += "\n🎪 Event bonuses active!"
            embed.add_field(name="💰 Reward", value=reward_text, inline=False)
            
            await self.bot.player_manager.add_coins(self.user_id, coins)
            
            player = await self.bot.db.get_player(self.user_id)
            if player:
                await self.bot.db.update_player(
                    interaction.user.id,
                    total_earned=player.get('total_earned', 0) + coins,
                    coins=player.get('coins', 0) + coins
                )
                
            skills = await self.bot.db.get_skills(self.user_id)
            combat_skill = next((s for s in skills if s['skill_name'] == 'combat'), None)
            if combat_skill:
                new_xp = combat_skill['xp'] + xp
                new_level = await self.bot.game_data.calculate_level_from_xp('combat', new_xp)
                await self.bot.db.update_skill(self.user_id, 'combat', xp=new_xp, level=new_level)
            
            self.stop()
            for child in self.children:
                if isinstance(child, Button):
                    child.disabled = True   
            await interaction.response.edit_message(embed=embed, view=self)
            return
        
        mob_damage = random.randint(self.mob_damage - 5, self.mob_damage + 5)
        damage_reduction = StatCalculator.calculate_damage_reduction(
            self.player_stats['defense'], 
            self.player_stats.get('true_defense', 0)
        )
        mob_damage = int(mob_damage * (1 - damage_reduction))
        mob_damage = max(1, mob_damage)
        self.player_health = (self.player_health or 0) - mob_damage
        
        if self.player_health <= 0:
            embed.description = f"💀 You were defeated by the {self.mob_name}!"
            embed.add_field(name="Penalty", value="-500 coins")
            await self.bot.player_manager.remove_coins(self.user_id, 500)   
            
            self.stop()
            for child in self.children:
                if isinstance(child, Button):
                    child.disabled = True   
            await interaction.response.edit_message(embed=embed, view=self)
            return
        
        embed.description = f"✨ Your ability dealt {ability_damage} damage! (-{mana_cost} mana)\n🩸 The {self.mob_name} dealt {mob_damage} damage to you!"
        
        mob_hp_bar = self._create_health_bar(self.mob_health, self.mob_max_health)
        player_hp_bar = self._create_health_bar(self.player_health or 0, self.player_max_health or 100)
        
        embed.add_field(name=f"{self.mob_name}", value=f"{mob_hp_bar}\n❤️ {self.mob_health}/{self.mob_max_health} HP", inline=False)
        embed.add_field(name="Your Health", value=f"{player_hp_bar}\n❤️ {self.player_health or 0}/{self.player_max_health or 0} HP", inline=False)
        
        await interaction.response.edit_message(embed=embed, view=self)
    
    @discord.ui.button(label="🏃 Run Away", style=discord.ButtonStyle.gray)
    async def run_button(self, interaction: discord.Interaction, button: Button):
        embed = discord.Embed(
            title="🏃 Fled from Battle",
            description=f"You ran away from the {self.mob_name}!",
            color=discord.Color.light_gray()
        )
        self.stop()
        for child in self.children:
            if isinstance(child, Button):
                child.disabled = True   
        await interaction.response.edit_message(embed=embed, view=self)
    
    def _create_health_bar(self, current: int, maximum: int) -> str:
        percentage = current / maximum if maximum > 0 else 0
        filled = int(percentage * 20)
        bar = "█" * filled + "░" * (20 - filled)
        return f"[{bar}]"

class CombatCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="fight", description="Fight monsters interactively!")
    @app_commands.describe(location="Choose where to fight")
    @app_commands.choices(location=[
        app_commands.Choice(name="🏝️ Hub (Easy)", value="hub"),
        app_commands.Choice(name="🕷️ Spider's Den (Medium)", value="spiders_den"),
        app_commands.Choice(name="🌋 Crimson Isle (Hard)", value="crimson_isle"),
        app_commands.Choice(name="🔚 The End (Very Hard)", value="end"),
        app_commands.Choice(name="🔥 Nether (Extreme)", value="nether"),
        app_commands.Choice(name="🕳️ Deep Caverns (????)", value="deep_caverns"),
    ])
    async def fight(self, interaction: discord.Interaction, location: str):
        await interaction.response.defer()
        
        player = await self.bot.player_manager.get_or_create_player(   
            interaction.user.id, interaction.user.name
        )
        
        from utils.systems.progression_system import ProgressionSystem
        
        skills = await self.bot.db.get_skills(interaction.user.id)
        combat_skill = next((s for s in skills if s['skill_name'] == 'combat'), None)
        combat_level = combat_skill['level'] if combat_skill else 0
        
        can_access, message = ProgressionSystem.can_access_combat_location(
            location, combat_level, player.get('total_earned', 0)
        )
        
        if not can_access:
            embed = discord.Embed(
                title="🚫 Location Locked",
                description=message,
                color=discord.Color.red()
            )
            embed.add_field(name="Your Combat Level", value=str(combat_level), inline=True)
            embed.add_field(name="Total Earned", value=f"{player.get('total_earned', 0):,} coins", inline=True)
            embed.set_footer(text="Fight in unlocked areas to level up and earn coins!")
            await interaction.followup.send(embed=embed, ephemeral=True)
            return
        
        mob_list = await self.bot.game_data.get_mobs_by_location(location)
        
        if not mob_list:
            mobs = {
                'hub': [
                    ('Zombie', 50, 5, 50, 10),
                    ('Skeleton', 40, 8, 60, 12),
                    ('Spider', 35, 6, 55, 11),
                    ('Lapis Zombie', 75, 9, 100, 15),
                ],
                'spiders_den': [
                    ('Cave Spider', 60, 10, 80, 15),
                    ('Spider', 50, 9, 70, 13),
                    ('Spider Jockey', 100, 15, 150, 25),
                    ('Broodfather', 250, 25, 500, 100),
                ],
                'crimson_isle': [
                    ('Blaze', 100, 18, 200, 30),
                    ('Magma Cube', 90, 15, 180, 28),
                    ('Wither Skeleton', 125, 20, 250, 35),
                ],
                'end': [
                    ('Enderman', 150, 23, 300, 40),
                    ('Zealot', 250, 30, 600, 80),
                    ('Ender Dragon', 5000, 100, 5000, 500),
                ],
                'nether': [
                    ('Ghast', 200, 28, 400, 50),
                    ('Piglin Brute', 225, 30, 450, 55),
                    ('Wither', 7500, 125, 10000, 1000),
                ],
                'deep_caverns': [
                    ('Lapis Zombie', 75, 13, 120, 20),
                    ('Redstone Pigman', 90, 14, 150, 22),
                    ('Emerald Slime', 100, 15, 180, 25),
                ],
            }
            mob_data = random.choice(mobs.get(location, mobs['hub']))
            mob_name, mob_health, mob_damage, coins, xp = mob_data
        else:
            mob_data_dict = random.choice(mob_list)
            mob_name = mob_data_dict['mob_name']
            mob_health = mob_data_dict['health']
            mob_damage = mob_data_dict['damage']
            coins = mob_data_dict['coins_reward']
            xp = mob_data_dict['xp_reward']
        
        view = CombatView(self.bot, interaction.user.id, mob_name, mob_health, mob_damage, coins, xp)
        
        embed = discord.Embed(
            title=f"⚔️ A wild {mob_name} appeared!",
            description=f"Prepare for battle in {ProgressionSystem.COMBAT_UNLOCKS[location]['name']}!",
            color=discord.Color.red()
        )
        embed.add_field(name="Enemy Health", value=f"❤️ {mob_health} HP", inline=True)
        embed.add_field(name="Enemy Damage", value=f"⚔️ ~{mob_damage} damage", inline=True)
        embed.set_footer(text="Use the buttons below to fight!")
        
        await interaction.followup.send(embed=embed, view=view)
        view.message = await interaction.original_response()

    @app_commands.command(name="combat_locations", description="View all combat locations and their requirements")
    async def combat_locations(self, interaction: discord.Interaction):
        await interaction.response.defer()
        
        player = await self.bot.player_manager.get_or_create_player(   
            interaction.user.id, interaction.user.name
        )
        
        from utils.systems.progression_system import ProgressionSystem
        
        skills = await self.bot.db.get_skills(interaction.user.id)
        combat_skill = next((s for s in skills if s['skill_name'] == 'combat'), None)
        combat_level = combat_skill['level'] if combat_skill else 0
        
        locations = ProgressionSystem.get_available_combat_locations(
            combat_level, player.get('total_earned', 0)
        )
        
        embed = discord.Embed(
            title="⚔️ Combat Locations",
            description=f"**Your Combat Level:** {combat_level}\n**Total Earned:** {player.get('total_earned', 0):,} coins\n",
            color=discord.Color.blue()
        )
        
        for loc in locations:
            status = "✅ Unlocked" if loc['unlocked'] else "🔒 Locked"
            difficulty_stars = "⭐" * loc['difficulty']
            
            requirements = f"Level {loc['required_level']}, {loc['required_coins']:,} coins earned"
            
            embed.add_field(
                name=f"{status} {loc['name']} {difficulty_stars}",
                value=f"**Requirements:** {requirements}\n{loc['message']}",
                inline=False
            )
        
        await interaction.followup.send(embed=embed)

    @app_commands.command(name="boss", description="Fight a boss!")
    @app_commands.describe(boss="Boss to fight")
    @app_commands.choices(boss=[
        app_commands.Choice(name="Broodfather", value="broodfather"),
        app_commands.Choice(name="Sven Packmaster", value="sven"),
        app_commands.Choice(name="Revenant Horror", value="revenant"),
        app_commands.Choice(name="Ender Dragon", value="dragon"),
        app_commands.Choice(name="Necron", value="necron"),
        app_commands.Choice(name="Goldor", value="goldor"),
    ])
    async def boss(self, interaction: discord.Interaction, boss: str):
        await self.bot.player_manager.get_or_create_player(   
            interaction.user.id, interaction.user.name
        )
        
        boss_stats = {
            'broodfather': (1000, 50, 1000, 200),
            'sven': (1500, 60, 1500, 250),
            'revenant': (2000, 70, 2000, 300),
            'dragon': (10000, 200, 5000, 1000),
            'necron': (20000, 300, 10000, 2000),
            'goldor': (25000, 350, 12000, 2500),
        }
        
        health, damage, coins, xp = boss_stats.get(boss, boss_stats['broodfather'])
        
        view = CombatView(self.bot, interaction.user.id, boss.title(), health, damage, coins, xp)
        
        embed = discord.Embed(
            title=f"💀 Boss Fight: {boss.title()}",
            description="A powerful boss has appeared!",
            color=discord.Color.dark_red()
        )
        embed.add_field(name="Boss Health", value=f"❤️ {health} HP", inline=True)
        embed.add_field(name="Boss Damage", value=f"⚔️ ~{damage} damage", inline=True)
        embed.set_footer(text="Use the buttons below to fight the boss!")
        
        await interaction.response.send_message(embed=embed, view=view)
        view.message = await interaction.original_response()

async def setup(bot):
    await bot.add_cog(CombatCommands(bot))
