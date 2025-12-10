import discord
from discord.ext import commands
from discord import app_commands
from typing import TYPE_CHECKING
from utils.stat_calculator import StatCalculator
from components.views.slayer_combat_view import SlayerCombatView
from components.views.slayer_menu_view import SlayerMenuView
from utils.decorators import auto_defer

if TYPE_CHECKING:
    from main import SkyblockBot
    from discord import Interaction

class SlayerCommands(commands.Cog):
    def __init__(self, bot: "SkyblockBot"):
        self.bot = bot

    @app_commands.command(name="slayer", description="Access the Slayer system")
    async def slayer_menu(self, interaction: "Interaction"):
        await interaction.response.defer()
        
        await self.bot.player_manager.get_or_create_player(
            interaction.user.id, interaction.user.name
        )
        
        view = SlayerMenuView(self.bot, interaction.user.id, interaction.user.name)
        embed = await view.get_embed()
        
        await interaction.followup.send(embed=embed, view=view)

    @app_commands.command(name="slayer_fight", description="Fight a slayer boss!")
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
    async def slayer_fight(self, interaction: "Interaction", boss: str, tier: str):
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


async def setup(bot: "SkyblockBot"):
    await bot.add_cog(SlayerCommands(bot))