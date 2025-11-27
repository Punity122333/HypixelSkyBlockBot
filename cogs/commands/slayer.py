import discord
from discord.ext import commands
from discord import app_commands
import random

class SlayerCommands(commands.Cog):
    def __init__(self, bot):
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
    async def slayer(self, interaction: discord.Interaction, boss: str, tier: str):
        await interaction.response.defer()
        
        await self.bot.player_manager.get_or_create_player(
            interaction.user.id, interaction.user.name
        )
        
        tier_int = int(tier)
        
        boss_info_from_db = await self.bot.game_data.get_slayer_boss(boss)
        
        if not boss_info_from_db:
            boss_data = {
                'revenant': {
                    'name': 'Revenant Horror',
                    'emoji': '🧟',
                    'xp': [5, 25, 100, 500, 1500],
                    'cost': [2000, 7500, 20000, 50000, 100000]
                },
                'tarantula': {
                    'name': 'Tarantula Broodfather',
                    'emoji': '🕷️',
                    'xp': [5, 25, 100, 500, 1000],
                    'cost': [2000, 7500, 20000, 50000, 100000]
                },
                'sven': {
                    'name': 'Sven Packmaster',
                    'emoji': '🐺',
                    'xp': [10, 30, 120, 600, 1800],
                    'cost': [2000, 7500, 20000, 50000, 100000]
                },
                'voidgloom': {
                    'name': 'Voidgloom Seraph',
                    'emoji': '👾',
                    'xp': [10, 50, 200, 1000, 2500],
                    'cost': [2000, 10000, 30000, 75000, 150000]
                },
                'inferno': {
                    'name': 'Inferno Demonlord',
                    'emoji': '🔥',
                    'xp': [10, 50, 250, 1200, 3000],
                    'cost': [2000, 10000, 30000, 75000, 150000]
                }
            }
            boss_info = boss_data.get(boss)
        else:
            tier_data = boss_info_from_db.get('tier_data', {})
            tier_key = f'tier_{tier_int}'
            tier_info = tier_data.get(tier_key, {})
            boss_info = {
                'name': boss_info_from_db['name'],
                'emoji': boss_info_from_db['emoji'],
                'xp': tier_info.get('xp', [5, 25, 100, 500, 1500]),
                'cost': tier_info.get('cost', [2000, 7500, 20000, 50000, 100000])
            }
        
        if not boss_info:
            await interaction.followup.send("❌ Invalid boss type!", ephemeral=True)
            return
        
        cost = boss_info['cost'][tier_int - 1]
        
        player = await self.bot.db.get_player(interaction.user.id)
        if player['coins'] < cost:
            await interaction.followup.send(
                f"❌ You need {cost:,} coins to start this slayer quest!",
                ephemeral=True
            )
            return
        
        await self.bot.player_manager.remove_coins(interaction.user.id, cost)
        
        success = random.random() > 0.2
        
        if success:
            xp_gained = boss_info['xp'][tier_int - 1]
            
            slayer_drops_from_db = await self.bot.game_data.get_slayer_drops(boss)
            
            if not slayer_drops_from_db:
                slayer_drops = {
                    'revenant': [('revenant_flesh', 2, 10), ('revenant_viscera', 1, 3), ('beheaded_horror', 0, 1)],
                    'tarantula': [('tarantula_web', 2, 8), ('toxic_arrow_poison', 1, 4), ('digested_mosquito', 0, 1)],
                    'sven': [('wolf_tooth', 2, 8), ('hamster_wheel', 1, 3), ('overflux_capacitor', 0, 1)],
                    'voidgloom': [('null_sphere', 2, 6), ('void_conqueror_enderman_skin', 1, 2), ('summoning_eye', 0, 1)],
                    'inferno': [('inferno_fuel', 3, 10), ('blaze_rod', 2, 5), ('fire_stone', 1, 2)],
                }
                drops = slayer_drops.get(boss, [('rotten_flesh', 1, 3)])
            else:
                drops = slayer_drops_from_db
            
            items_obtained = []
            for item_id, min_amt, max_amt in drops:
                if max_amt > 0 and random.random() > 0.3:
                    amount = random.randint(min_amt, max_amt)
                    if amount > 0:
                        await self.bot.db.add_item_to_inventory(interaction.user.id, item_id, amount)
                        items_obtained.append(f"{item_id} x{amount}")
            
            coins_reward = random.randint(cost // 10, cost // 5)
            
            await self.bot.player_manager.add_coins(interaction.user.id, coins_reward)
            
            player_data = await self.bot.db.get_player(interaction.user.id)
            if player_data:
                await self.bot.db.update_player(interaction.user.id, total_earned=player_data.get('total_earned', 0) + coins_reward)
            
            embed = discord.Embed(
                title=f"{boss_info['emoji']} Slayer Quest Complete!",
                description=f"You defeated {boss_info['name']} T{tier}!",
                color=discord.Color.green()
            )
            if items_obtained:
                embed.add_field(name="🎁 Items Dropped", value="\n".join(items_obtained), inline=False)
            embed.add_field(name="XP Gained", value=f"+{xp_gained} Slayer XP", inline=True)
            embed.add_field(name="Coins", value=f"+{coins_reward:,} coins", inline=True)
            net = coins_reward - cost
            embed.add_field(name="Net Profit", value=f"{net:+,} coins", inline=True)
            
            await interaction.followup.send(embed=embed)
        else:
            embed = discord.Embed(
                title=f"💀 Slayer Quest Failed",
                description=f"You were defeated by {boss_info['name']} T{tier}!",
                color=discord.Color.red()
            )
            embed.add_field(name="Coins Lost", value=f"-{cost:,} coins", inline=False)
            
            await interaction.followup.send(embed=embed)

    @app_commands.command(name="slayer_stats", description="View your slayer statistics")
    async def slayer_stats(self, interaction: discord.Interaction):
        await interaction.response.defer()
        
        await self.bot.player_manager.get_or_create_player(
            interaction.user.id, interaction.user.name
        )
        
        embed = discord.Embed(
            title=f"⚔️ {interaction.user.name}'s Slayer Stats",
            color=discord.Color.dark_red()
        )
        
        embed.add_field(name="🧟 Revenant Horror", value="Level 7\n2,450 XP", inline=True)
        embed.add_field(name="🕷️ Tarantula Broodfather", value="Level 6\n1,820 XP", inline=True)
        embed.add_field(name="🐺 Sven Packmaster", value="Level 8\n3,120 XP", inline=True)
        
        embed.add_field(name="👾 Voidgloom Seraph", value="Level 5\n980 XP", inline=True)
        embed.add_field(name="🔥 Inferno Demonlord", value="Level 4\n650 XP", inline=True)
        embed.add_field(name="📊 Total Kills", value="487", inline=True)
        
        await interaction.followup.send(embed=embed)

async def setup(bot):
    await bot.add_cog(SlayerCommands(bot))
