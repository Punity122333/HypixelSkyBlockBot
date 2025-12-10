import discord
from discord.ext import commands
from discord import app_commands
from discord.ui import View, Button
import random
from components.views.combat_view import CombatView

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
                    ('Zombie', 50, 5, 50, 10, 1),
                    ('Skeleton', 40, 8, 60, 12, 1),
                    ('Spider', 35, 6, 55, 11, 1),
                    ('Lapis Zombie', 75, 9, 100, 15, 5),
                ],
                'spiders_den': [
                    ('Cave Spider', 60, 10, 80, 15, 5),
                    ('Spider', 50, 9, 70, 13, 5),
                    ('Spider Jockey', 100, 15, 150, 25, 10),
                    ('Broodfather', 250, 25, 500, 100, 30),
                ],
                'crimson_isle': [
                    ('Blaze', 100, 18, 200, 30, 10),
                    ('Magma Cube', 90, 15, 180, 28, 10),
                    ('Wither Skeleton', 125, 20, 250, 35, 15),
                ],
                'end': [
                    ('Enderman', 150, 23, 300, 40, 15),
                    ('Zealot', 250, 30, 600, 80, 25),
                    ('Ender Dragon', 5000, 100, 5000, 500, 50),
                ],
                'nether': [
                    ('Ghast', 200, 28, 400, 50, 20),
                    ('Piglin Brute', 225, 30, 450, 55, 20),
                    ('Wither', 7500, 125, 10000, 1000, 60),
                ],
                'deep_caverns': [
                    ('Lapis Zombie', 75, 13, 120, 20, 5),
                    ('Redstone Pigman', 90, 14, 150, 22, 10),
                    ('Emerald Slime', 100, 15, 180, 25, 10),
                ],
            }
            mob_data = random.choice(mobs.get(location, mobs['hub']))
            mob_name, mob_health, mob_damage, coins, xp, mob_level = mob_data
        else:
            mob_row = random.choice(mob_list)
            mob_data_dict = dict(mob_row)
            mob_name = mob_data_dict['mob_name']
            mob_level = mob_data_dict['level'] if 'level' in mob_data_dict else 1
            
            from utils.systems.combat_system import CombatSystem
            scaling = await CombatSystem.get_mob_level_scaling(self.bot.db, mob_level)
            
            mob_health = int(mob_data_dict['health'] * scaling['health_multiplier'])
            mob_damage = int(mob_data_dict['damage'] * scaling['damage_multiplier'])
            coins = int(mob_data_dict['coins_reward'] * scaling['coins_multiplier'])
            xp = int(mob_data_dict['xp_reward'] * scaling['xp_multiplier'])
        
        view = CombatView(self.bot, interaction.user.id, mob_name, mob_health, mob_damage, coins, xp)
        
        level_color = discord.Color.green()
        if mob_level >= 10:
            level_color = discord.Color.gold()
        if mob_level >= 25:
            level_color = discord.Color.red()
        if mob_level >= 50:
            level_color = discord.Color.purple()
        
        embed = discord.Embed(
            title=f"⚔️ A wild {mob_name} [Lv {mob_level}] appeared!",
            description=f"Prepare for battle in {ProgressionSystem.COMBAT_UNLOCKS[location]['name']}!",
            color=level_color
        )
        embed.add_field(name="Enemy Health", value=f"❤️ {mob_health} HP", inline=True)
        embed.add_field(name="Enemy Damage", value=f"⚔️ ~{mob_damage} damage", inline=True)
        embed.add_field(name="Level", value=f"🎯 {mob_level}", inline=True)
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
