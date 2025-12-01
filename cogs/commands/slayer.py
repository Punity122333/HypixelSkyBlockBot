import discord
from discord.ext import commands
from discord import app_commands
from discord.ui import View, Button
import random
import asyncio
from typing import Optional, TYPE_CHECKING, Tuple, Dict, Any
from utils.compat import roll_loot as compat_roll_loot
from utils.stat_calculator import StatCalculator
from utils.event_effects import EventEffects
from utils.decorators import auto_defer

if TYPE_CHECKING:
    from main import SkyblockBot
    from discord import Interaction, Message

class SlayerCombatView(View):
    def __init__(
        self,
        bot: "SkyblockBot",
        user_id: int,
        mob_name: str,
        mob_health: int,
        mob_damage: int,
        coins_reward: int,
        xp_reward: int,
        loot_table: Dict[str, Any],
    ):
        super().__init__(timeout=180)
        self.bot = bot
        self.user_id = user_id
        self.mob_name = mob_name
        self.mob_health = mob_health
        self.mob_max_health = mob_health
        self.mob_damage = mob_damage
        self.coins_reward = coins_reward
        self.xp_reward = xp_reward
        self.loot_table = loot_table
        
        self.player_health: Optional[int] = None
        self.player_max_health: Optional[int] = None
        self.player_stats: Optional[Dict[str, Any]] = None
        self.message: Optional["Message"] = None
        self.event_effects = EventEffects(bot)
        self.fight_in_progress = True
    
    async def interaction_check(self, interaction: "Interaction") -> bool:
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("This isn't your slayer fight!", ephemeral=True)
            return False
        return self.fight_in_progress

    def _create_health_bar(self, current: int, maximum: int) -> str:
        percentage = current / maximum if maximum > 0 else 0
        filled = int(percentage * 20)
        bar = "█" * filled + "░" * (20 - filled)
        return f"[{bar}]"

    @discord.ui.button(label="⚔️ Attack", style=discord.ButtonStyle.red)
    async def attack(self, interaction: "Interaction", button: Button):
        if self.player_stats is None:
            self.player_stats = await StatCalculator.calculate_player_stats(self.bot.db, self.bot.game_data, self.user_id)
        
        if self.player_health is None:
            self.player_health = int(self.player_stats['max_health'])
            self.player_max_health = int(self.player_stats['max_health'])
        
        combat_effects = StatCalculator.apply_combat_effects(self.player_stats, None)
        
        crit = random.random() * 100 < combat_effects['crit_chance']
        damage = int(combat_effects['base_damage'])
        if crit:
            damage = int(damage * combat_effects['crit_damage_multiplier'])
        
        ferocity_hits = 1 + (self.player_stats.get('ferocity', 0) // 100)
        total_damage = int(damage * ferocity_hits)
        self.mob_health -= total_damage
        
        embed = discord.Embed(title=f"⚔️ Slayer Boss Fight: {self.mob_name}", color=discord.Color.dark_red())
        
        if self.mob_health <= 0:
            slayer_id = self.mob_name.lower().split()[0]
            await self.bot.db.skills.update_slayer_xp(self.user_id, slayer_id, self.xp_reward)

            magic_find = self.player_stats.get('magic_find', 0)
            fortune = self.player_stats.get('looting', 0)
            drops = await compat_roll_loot(self.bot.game_data, self.loot_table, magic_find, fortune)
            
            items_obtained = []
            for item_id, amount in drops:
                await self.bot.db.add_item_to_inventory(self.user_id, item_id, amount)
                item_name = item_id.replace('_', ' ').title()
                items_obtained.append(f"{item_name} x{amount}")
                
                current_collection = await self.bot.db.get_collection(self.user_id, item_id)
                await self.bot.db.add_collection(self.user_id, item_id, current_collection + amount)
            
            mob_id = self.mob_name.lower().replace(' ', '_')
            pet_drop = await self.bot.game_data._try_drop_pet(mob_id, magic_find)
            if pet_drop:
                pet_type, pet_rarity = pet_drop
                await self.bot.db.add_player_pet(self.user_id, pet_type, pet_rarity)
                items_obtained.append(f"🐾 **{pet_rarity} {pet_type.title()} Pet!**")
            
            coins = self.coins_reward
            xp = self.xp_reward
            
            xp_multiplier = await self.event_effects.get_xp_multiplier('combat')
            coin_multiplier = await self.event_effects.get_coin_multiplier()
            
            xp = int(xp * xp_multiplier)
            coins = int(coins * coin_multiplier)
            
            embed.description = f"💀 You defeated the {self.mob_name}!"
            if items_obtained:
                embed.add_field(name="🎁 Items Dropped", value="\n".join(items_obtained[:10]), inline=False)
            else:
                embed.add_field(name="🎁 Items Dropped", value="No items dropped this time.", inline=False)
            
            reward_text = f"+{coins} coins\n+{xp} Slayer XP"
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
            
            self.fight_in_progress = False
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
            
            self.fight_in_progress = False
            self.stop()
            for child in self.children:
                if isinstance(child, Button):
                    child.disabled = True
            await interaction.response.edit_message(embed=embed, view=self)
            return
        
        hit_text = f"💥 **CRITICAL HIT!** You dealt {total_damage} damage!" if crit else f"⚔️ You dealt {total_damage} damage!"
        if ferocity_hits > 1:
            hit_text += f" ({ferocity_hits}x hits from Ferocity!)"
        embed.description = f"{hit_text}\n🩸 The {self.mob_name} dealt {mob_damage} damage to you!"
        
        mob_hp_bar = self._create_health_bar(self.mob_health, self.mob_max_health)
        player_hp_bar = self._create_health_bar(self.player_health or 0, self.player_max_health or 100)
        
        embed.add_field(name=f"{self.mob_name}", value=f"{mob_hp_bar}\n❤️ {self.mob_health}/{self.mob_max_health} HP", inline=False)
        embed.add_field(name="Your Health", value=f"{player_hp_bar}\n❤️ {self.player_health or 0}/{self.player_max_health or 0} HP", inline=False)
        
        await interaction.response.edit_message(embed=embed, view=self)
    
    @discord.ui.button(label="🛡️ Defend", style=discord.ButtonStyle.blurple)
    async def defend(self, interaction: "Interaction", button: Button):
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
        
        embed = discord.Embed(title=f"⚔️ Slayer Boss Fight: {self.mob_name}", color=discord.Color.blue())
        embed.description = f"🛡️ You defended! The {self.mob_name} dealt only {mob_damage} damage!"
        
        if self.player_health <= 0:
            embed.description = f"💀 You were defeated by the {self.mob_name}!"
            embed.add_field(name="Penalty", value="-500 coins")
            await self.bot.player_manager.remove_coins(self.user_id, 500)
            
            self.fight_in_progress = False
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
    async def ability(self, interaction: "Interaction", button: Button):
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
        
        embed = discord.Embed(title=f"⚔️ Slayer Boss Fight: {self.mob_name}", color=discord.Color.purple())
        
        if self.mob_health <= 0:
            slayer_id = self.mob_name.lower().split()[0]
            await self.bot.db.skills.update_slayer_xp(self.user_id, slayer_id, self.xp_reward)

            magic_find = self.player_stats.get('magic_find', 0)
            fortune = self.player_stats.get('looting', 0)
            drops = await compat_roll_loot(self.bot.game_data, self.loot_table, magic_find, fortune)
            
            items_obtained = []
            for item_id, amount in drops:
                await self.bot.db.add_item_to_inventory(self.user_id, item_id, amount)
                item_name = item_id.replace('_', ' ').title()
                items_obtained.append(f"{item_name} x{amount}")
                
                current_collection = await self.bot.db.get_collection(self.user_id, item_id)
                await self.bot.db.add_collection(self.user_id, item_id, current_collection + amount)
            
            mob_id = self.mob_name.lower().replace(' ', '_')
            pet_drop = await self.bot.game_data._try_drop_pet(mob_id, magic_find)
            if pet_drop:
                pet_type, pet_rarity = pet_drop
                await self.bot.db.add_player_pet(self.user_id, pet_type, pet_rarity)
                items_obtained.append(f"🐾 **{pet_rarity} {pet_type.title()} Pet!**")
            
            coins = self.coins_reward
            xp = self.xp_reward
            
            xp_multiplier = await self.event_effects.get_xp_multiplier('combat')
            coin_multiplier = await self.event_effects.get_coin_multiplier()
            
            xp = int(xp * xp_multiplier)
            coins = int(coins * coin_multiplier)
            
            embed.description = f"💀 You defeated the {self.mob_name} with your ability!"
            if items_obtained:
                embed.add_field(name="🎁 Items Dropped", value="\n".join(items_obtained[:10]), inline=False)
            else:
                embed.add_field(name="🎁 Items Dropped", value="No items dropped this time.", inline=False)
            
            reward_text = f"+{coins} coins\n+{xp} Slayer XP"
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
            
            self.fight_in_progress = False
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
            
            self.fight_in_progress = False
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
    async def run(self, interaction: "Interaction", button: Button):
        embed = discord.Embed(
            title="🏃 Fled from Battle",
            description=f"You ran away from the {self.mob_name}!",
            color=discord.Color.light_gray()
        )
        self.fight_in_progress = False
        self.stop()
        for child in self.children:
            if isinstance(child, Button):
                child.disabled = True
        await interaction.response.edit_message(embed=embed, view=self)
        
    async def on_timeout(self):
        if self.fight_in_progress and self.message:
            self.fight_in_progress = False
            for child in self.children:
                if isinstance(child, Button):
                    child.disabled = True
            
            embed = discord.Embed(
                title="⌛ Fight Timed Out",
                description=f"The fight against the {self.mob_name} ended due to inactivity. You gain no rewards.",
                color=discord.Color.red()
            )
            try:
                await self.message.edit(embed=embed, view=self)
            except discord.NotFound:
                pass


class SlayerCommands(commands.Cog):
    def __init__(self, bot: "SkyblockBot"):
        self.bot = bot

    @app_commands.command(name="slayer", description="Fight a slayer boss!")
    @app_commands.describe(boss="Choose a slayer boss", tier="Choose difficulty tier")
    @app_commands.choices(
        boss=[
            app_commands.Choice(name="Revenant Horror (Zombie)", value="revenant"),
            app_commands.Choice(name="Tarantula Broodfather (Spider)", value="tarantula"),
            app_commands.Choice(name="Sven Packmaster (Wolf)", value="sven"),
            app_commands.Choice(name="Voidgloom Seraph (Enderman)", value="voidgloom"),
            app_commands.Choice(name="Inferno Demonlord (Blaze)", value="inferno"),
        ],
        tier=[
            app_commands.Choice(name="Tier 1", value="1"),
            app_commands.Choice(name="Tier 2", value="2"),
            app_commands.Choice(name="Tier 3", value="3"),
            app_commands.Choice(name="Tier 4", value="4"),
            app_commands.Choice(name="Tier 5", value="5"),
        ]
    )
    @auto_defer
    async def slayer(self, interaction: "Interaction", boss: str, tier: str):
        tier_int = int(tier)
        
        await self.bot.player_manager.get_or_create_player( 
            interaction.user.id, interaction.user.name
        )
        
        base_stats = {
            'revenant': {'health': 50000, 'damage': 500, 'coins': 5000, 'xp': 500},
            'tarantula': {'health': 75000, 'damage': 750, 'coins': 7500, 'xp': 750},
            'sven': {'health': 100000, 'damage': 1000, 'coins': 10000, 'xp': 1000},
            'voidgloom': {'health': 150000, 'damage': 1500, 'coins': 15000, 'xp': 1500},
            'inferno': {'health': 250000, 'damage': 2500, 'coins': 25000, 'xp': 2500},
        }
        
        base = base_stats.get(boss)
        if not base:
            await interaction.followup.send("Yo, that's not a real boss! Pick a legit one.", ephemeral=True)
            return

        health_multiplier = (1.5 ** (tier_int - 1)) * tier_int
        damage_multiplier = (1.2 ** (tier_int - 1)) * tier_int
        reward_multiplier = tier_int 

        mob_health = int(base['health'] * health_multiplier)
        mob_damage = int(base['damage'] * damage_multiplier)
        coins_reward = int(base['coins'] * reward_multiplier)
        xp_reward = int(base['xp'] * reward_multiplier)
        
        loot_table_key = f"{boss}_t{tier}"
        loot_table = await self.bot.game_data.get_loot_table(loot_table_key, 'slayer')
        if not loot_table:
            loot_table = {}
        
        boss_name = f"{boss.title()} T{tier_int}"
        
        view = SlayerCombatView(self.bot, interaction.user.id, boss_name, mob_health, mob_damage, coins_reward, xp_reward, loot_table)
        
        player_stats = await StatCalculator.calculate_player_stats(self.bot.db, self.bot.game_data, interaction.user.id)
        player_health = int(player_stats.get('max_health', 100))
        
        player_hp_bar = view._create_health_bar(player_health, player_health)
        mob_hp_bar = view._create_health_bar(mob_health, mob_health)
        
        embed = discord.Embed(
            title=f"💀 Slayer Boss Fight: {boss_name}",
            description=f"A monstrous **{boss_name}** has spawned!\n\nCheck your stats and prepare to fight!",
            color=discord.Color.dark_red()
        )
        embed.add_field(name="Your Health", value=f"{player_hp_bar}\n❤️ {player_health}/{player_health} HP", inline=False)
        embed.add_field(name=f"{boss_name} Health", value=f"{mob_hp_bar}\n❤️ {mob_health}/{mob_health} HP", inline=False)
        embed.set_footer(text=f"Boss Damage: ~{mob_damage:,} | Expected Coin Reward: {coins_reward:,}")

        message = await interaction.followup.send(embed=embed, view=view)
        view.message = message

    @app_commands.command(name="slayer_stats", description="View your slayer statistics")
    @auto_defer
    async def slayer_stats(self, interaction: "Interaction"):
        await self.bot.player_manager.get_or_create_player(
            interaction.user.id, interaction.user.name
        )
        
        embed = discord.Embed(
            title=f"⚔️ {interaction.user.name}'s Slayer Stats",
            color=discord.Color.dark_red()
        )
        
        slayer_types = [
            ('revenant', '🧟 Revenant Horror'),
            ('tarantula', '🕷️ Tarantula Broodfather'),
            ('sven', '🐺 Sven Packmaster'),
            ('voidgloom', '👾 Voidgloom Seraph'),
            ('inferno', '🔥 Inferno Demonlord')
        ]
        
        total_kills = 0
        for slayer_id, slayer_name in slayer_types:
            stats = await self.bot.db.skills.get_slayer_stats(interaction.user.id, slayer_id)
            if stats:
                xp = stats.get('xp', 0)
                level = stats.get('level', 0)
                kills = stats.get('total_kills', 0)
                total_kills += kills
                embed.add_field(name=slayer_name, value=f"Level {level}\n{xp:,} XP", inline=True)
            else:
                embed.add_field(name=slayer_name, value="Level 0\n0 XP\n0 Kills", inline=True)
        
        embed.add_field(name="📊 Total Kills", value=f"{total_kills}", inline=False)
        
        await interaction.followup.send(embed=embed)

    @app_commands.command(name="slayer_info", description="View information about Slayer bosses and tiers")
    @auto_defer
    async def slayer_info(self, interaction: "Interaction"):
        embed = discord.Embed(
            title="Slayer Boss Information",
            description="Slayer bosses are tough enemies that must be defeated using the `/slayer` command. Higher tiers mean tougher fights but better rewards and XP!",
            color=discord.Color.dark_red()
        )
        
        embed.add_field(name="Revenant Horror (Zombie)", value="The original boss. Good for starting out.", inline=True)
        embed.add_field(name="Tarantula Broodfather (Spider)", value="Focuses on raw power and critical hits.", inline=True)
        embed.add_field(name="Sven Packmaster (Wolf)", value="Extremely fast, hard to hit, rewards speed gear.", inline=True)
        embed.add_field(name="Voidgloom Seraph (Enderman)", value="Grants access to powerful End gear and weapons.", inline=True)
        embed.add_field(name="Inferno Demonlord (Blaze)", value="The toughest of the bosses, requiring maxed gear.", inline=True)
        
        await interaction.followup.send(embed=embed)


async def setup(bot: "SkyblockBot"):
    await bot.add_cog(SlayerCommands(bot))