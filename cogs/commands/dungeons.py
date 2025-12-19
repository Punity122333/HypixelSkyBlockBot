import discord
from discord.ext import commands
from discord import app_commands
from utils.decorators import auto_defer
from utils.systems.party_system import PartySystem
from utils.systems.dungeon_system import DungeonSystem
from components.views.dungeon_view import DungeonView

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
            
            result = await PartySystem.start_dungeon(self.bot.db, interaction.user.id, floor)
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
        
        stats = await self.bot.db.get_dungeon_stats(interaction.user.id)
        
        if not stats:
            await self.bot.db.update_dungeon_stats(interaction.user.id)
            stats = await self.bot.db.get_dungeon_stats(interaction.user.id)
        
        catacombs_level = stats['catacombs_level'] if stats else 0
        total_runs = stats['total_runs'] if stats else 0
        secrets_found = stats['secrets_found'] if stats else 0
        best_score = stats['best_score'] if stats else 0
        fastest_run = stats['fastest_run'] if stats else 0
        total_deaths = stats['total_deaths'] if stats else 0
        
        def get_rank(score):
            if score >= 300:
                return "S+"
            elif score >= 270:
                return "S"
            elif score >= 240:
                return "A"
            elif score >= 210:
                return "B"
            elif score >= 180:
                return "C"
            else:
                return "D"
        
        rank = get_rank(best_score) if best_score > 0 else "N/A"
        best_score_text = f"{best_score} ({rank})" if best_score > 0 else "N/A"
        
        if fastest_run > 0:
            minutes = fastest_run // 60
            seconds = fastest_run % 60
            fastest_run_text = f"{minutes}m {seconds}s"
        else:
            fastest_run_text = "N/A"
        
        embed = discord.Embed(
            title=f"🏰 {interaction.user.name}'s Dungeon Stats",
            color=discord.Color.purple()
        )
        
        embed.add_field(name="Catacombs Level", value=str(catacombs_level), inline=True)
        embed.add_field(name="Total Runs", value=f"{total_runs:,}", inline=True)
        embed.add_field(name="Secrets Found", value=f"{secrets_found:,}", inline=True)
        
        embed.add_field(name="Best Score", value=best_score_text, inline=True)
        embed.add_field(name="Fastest Run", value=fastest_run_text, inline=True)
        embed.add_field(name="Deaths", value=f"{total_deaths:,}", inline=True)
        
        await interaction.followup.send(embed=embed)

async def setup(bot):
    await bot.add_cog(DungeonCommands(bot))