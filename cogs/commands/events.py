import discord
from discord.ext import commands
from discord import app_commands
import time
from utils.decorators import auto_defer

class EventCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def get_active_events(self):
        current_time = int(time.time())
        
        active_events = []
        upcoming_events = []
        
        events = await self.bot.game_data.get_all_game_events()
        
        for event in events:
            start_offset = event.get('start_offset', 0)
            adjusted_time = current_time - start_offset
            cycle_position = adjusted_time % event['occurs_every']
            
            if cycle_position < event['duration']:
                time_remaining = event['duration'] - cycle_position
                active_events.append({**event, 'time_remaining': time_remaining})
            else:
                time_until_next = event['occurs_every'] - cycle_position
                upcoming_events.append({**event, 'time_until': time_until_next})
        
        return active_events, upcoming_events

    def format_time(self, seconds: int) -> str:
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        
        if hours > 0:
            return f"{hours}h {minutes}m"
        else:
            return f"{minutes}m"

    @app_commands.command(name="events", description="View active SkyBlock events")
    @auto_defer
    async def events(self, interaction: discord.Interaction):
        active_events, upcoming_events = await self.get_active_events()
        
        embed = discord.Embed(
            title="🎪 SkyBlock Events",
            description="Special events with bonuses and rewards!",
            color=discord.Color.magenta()
        )
        
        if active_events:
            for event in active_events:
                time_left = self.format_time(event['time_remaining'])
                embed.add_field(
                    name=f"✅ {event['name']}",
                    value=f"{event['description']}\n⏰ Ends in: {time_left}",
                    inline=False
                )
        else:
            embed.add_field(
                name="No Active Events",
                value="Check back later for special events!",
                inline=False
            )
        
        if upcoming_events:
            upcoming_events.sort(key=lambda x: x['time_until'])
            next_events = upcoming_events[:3]
            
            upcoming_text = ""
            for event in next_events:
                time_until = self.format_time(event['time_until'])
                upcoming_text += f"**{event['name']}** - Starts in {time_until}\n"
            
            embed.add_field(
                name="� Upcoming Events",
                value=upcoming_text,
                inline=False
            )
        
        embed.set_footer(text="Events provide special bonuses and exclusive rewards!")
        
        await interaction.followup.send(embed=embed)

    @app_commands.command(name="calendar", description="View the SkyBlock calendar")
    @auto_defer
    async def calendar(self, interaction: discord.Interaction):
        current_time = int(time.time())
        day_of_year = (current_time // 86400) % 365
        season_day = day_of_year % 31
        month = (day_of_year // 31) % 12
        year = (current_time // 86400) // 365
        
        seasons = await self.bot.game_data.get_all_seasons()
        if not seasons:
            seasons = ['Early Spring', 'Spring', 'Late Spring', 
                       'Early Summer', 'Summer', 'Late Summer',
                       'Early Autumn', 'Autumn', 'Late Autumn',
                       'Early Winter', 'Winter', 'Late Winter']
        
        mayors = await self.bot.game_data.get_all_mayors()
        if mayors:
            current_mayor_data = mayors[year % len(mayors)]
            current_mayor = current_mayor_data.get('mayor_name', current_mayor_data.get('name', 'Unknown'))
            mayor_perks_value = current_mayor_data.get('perks', 'No special perks')
        else:
            mayors_list = ['Diana', 'Derpy', 'Paul', 'Jerry', 'Marina', 'Aatrox']
            current_mayor = mayors_list[(year % len(mayors_list))]
            
            mayor_perks = {
                'Diana': '🏹 +50% Pet XP\n🎯 Better pet drops',
                'Derpy': '📚 +50% Skill XP\n💰 +50% Shop prices',
                'Paul': '💰 -10% Shop prices\n📦 +1 Minion slot',
                'Jerry': '🎁 Random perks\n🎲 Mystery bonuses',
                'Marina': '🎣 +100% Fishing XP\n🐟 Better sea creatures',
                'Aatrox': '⚔️ +100% Slayer XP\n👹 Better slayer drops'
            }
            mayor_perks_value = mayor_perks.get(current_mayor, 'No special perks')
        
        embed = discord.Embed(
            title="📅 SkyBlock Calendar",
            description=f"**{seasons[month]}, Day {season_day + 1}, Year {year + 123}**",
            color=discord.Color.green()
        )
        
        _, upcoming_events = await self.get_active_events()
        if upcoming_events:
            upcoming_events.sort(key=lambda x: x['time_until'])
            events_text = ""
            for event in upcoming_events[:5]:
                time_until = self.format_time(event['time_until'])
                events_text += f"• {event['name'].replace('🌙', '').replace('⛏️', '').replace('🌾', '').replace('🎣', '').replace('💰', '').replace('🐉', '').strip()} ({time_until})\n"
            
            embed.add_field(
                name="📅 Upcoming Events",
                value=events_text,
                inline=False
            )
        
        embed.add_field(
            name=f"🎭 Mayor: {current_mayor}",
            value=mayor_perks_value,
            inline=False
        )
        
        next_bank_interest = 5 - (day_of_year % 5)
        embed.add_field(
            name="🏦 Next Bank Interest",
            value=f"In {next_bank_interest} day{'s' if next_bank_interest != 1 else ''}",
            inline=True
        )
        
        next_election = 7 - (day_of_year % 7)
        embed.add_field(
            name="🗳️ Next Election",
            value=f"In {next_election} day{'s' if next_election != 1 else ''}",
            inline=True
        )
        
        embed.set_footer(text="The calendar affects game events and bonuses!")
        
        await interaction.followup.send(embed=embed)

async def setup(bot):
    await bot.add_cog(EventCommands(bot))

