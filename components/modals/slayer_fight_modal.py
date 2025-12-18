import discord
from discord.ui import Modal, TextInput, Select
from typing import TYPE_CHECKING
from utils.stat_calculator import StatCalculator
from components.views.slayer_combat_view import SlayerCombatView

if TYPE_CHECKING:
    from discord import Interaction

class SlayerFightModal(Modal):
    def __init__(self, parent_view):
        super().__init__(title="Start Slayer Fight", timeout=180)
        self.parent_view = parent_view
        
        self.boss_input = TextInput(
            label="Boss Type",
            placeholder="revenant, tarantula, sven, voidgloom, or inferno",
            required=True,
            max_length=20
        )
        
        self.tier_input = TextInput(
            label="Tier (1-5)",
            placeholder="Enter tier: 1, 2, 3, 4, or 5",
            required=True,
            max_length=1
        )
        
        self.add_item(self.boss_input)
        self.add_item(self.tier_input)
    
    async def on_submit(self, interaction: "Interaction"):
        await interaction.response.defer()
        
        boss = self.boss_input.value.lower().strip()
        tier_str = self.tier_input.value.strip()
        
        valid_bosses = ['revenant', 'tarantula', 'sven', 'voidgloom', 'inferno']
        if boss not in valid_bosses:
            await interaction.followup.send("Invalid boss type! Choose from: revenant, tarantula, sven, voidgloom, inferno", ephemeral=True)
            return
        
        try:
            tier_int = int(tier_str)
            if tier_int < 1 or tier_int > 5:
                raise ValueError()
        except ValueError:
            await interaction.followup.send("Invalid tier! Choose a number between 1 and 5.", ephemeral=True)
            return
        
        bot = self.parent_view.bot
        user_id = self.parent_view.user_id
        
        base_stats = {
            'revenant': {'health': 50000, 'damage': 500, 'coins': 5000, 'xp': 500},
            'tarantula': {'health': 75000, 'damage': 750, 'coins': 7500, 'xp': 750},
            'sven': {'health': 100000, 'damage': 1000, 'coins': 10000, 'xp': 1000},
            'voidgloom': {'health': 150000, 'damage': 1500, 'coins': 15000, 'xp': 1500},
            'inferno': {'health': 250000, 'damage': 2500, 'coins': 25000, 'xp': 2500},
        }
        
        base = base_stats[boss]
        
        health_multiplier = (1.5 ** (tier_int - 1)) * tier_int
        damage_multiplier = (1.2 ** (tier_int - 1)) * tier_int
        reward_multiplier = tier_int 

        mob_health = int(base['health'] * health_multiplier)
        mob_damage = int(base['damage'] * damage_multiplier)
        coins_reward = int(base['coins'] * reward_multiplier)
        xp_reward = int(base['xp'] * reward_multiplier)
        
        loot_table_key = f"{boss}_t{tier_int}"
        loot_table = await bot.game_data.get_loot_table(loot_table_key, 'slayer')
        if not loot_table:
            loot_table = {}
        
        boss_name = f"{boss.title()} T{tier_int}"
        
        view = SlayerCombatView(bot, user_id, boss_name, mob_health, mob_damage, coins_reward, xp_reward, loot_table)
        
        player_stats = await StatCalculator.calculate_player_stats(bot.db, bot.game_data, user_id)
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
