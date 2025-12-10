import discord
from components.buttons.slayer_buttons import (
    SlayerMainButton,
    SlayerStatsButton,
    SlayerInfoButton
)

class SlayerMenuView(discord.ui.View):
    def __init__(self, bot, user_id, username):
        super().__init__(timeout=180)
        self.bot = bot
        self.user_id = user_id
        self.username = username
        self.current_view = 'main'
        
        self.add_item(SlayerMainButton(self))
        self.add_item(SlayerStatsButton(self))
        self.add_item(SlayerInfoButton(self))
    
    async def get_embed(self):
        if self.current_view == 'main':
            return await self.get_main_embed()
        elif self.current_view == 'stats':
            return await self.get_stats_embed()
        elif self.current_view == 'info':
            return await self.get_info_embed()
        else:
            return await self.get_main_embed()
    
    async def get_main_embed(self):
        embed = discord.Embed(
            title="💀 Slayer System",
            description="Fight powerful bosses to earn Slayer XP and rare loot!",
            color=discord.Color.dark_red()
        )
        
        slayer_types = [
            ('revenant', '🧟 Revenant Horror', 'The original boss. Good for starting out.'),
            ('tarantula', '🕷️ Tarantula Broodfather', 'Focuses on raw power and critical hits.'),
            ('sven', '🐺 Sven Packmaster', 'Extremely fast, hard to hit, rewards speed gear.'),
            ('voidgloom', '👾 Voidgloom Seraph', 'Grants access to powerful End gear and weapons.'),
            ('inferno', '🔥 Inferno Demonlord', 'The toughest of the bosses, requiring maxed gear.')
        ]
        
        for slayer_id, slayer_name, desc in slayer_types:
            stats = await self.bot.db.skills.get_slayer_stats(self.user_id, slayer_id)
            if stats:
                level = stats.get('level', 0)
                xp = stats.get('xp', 0)
                embed.add_field(name=slayer_name, value=f"Level {level} ({xp:,} XP)\n{desc}", inline=False)
            else:
                embed.add_field(name=slayer_name, value=f"Level 0 (0 XP)\n{desc}", inline=False)
        
        embed.set_footer(text="Use the buttons below to view stats, info, or start a fight!")
        return embed
    
    async def get_stats_embed(self):
        embed = discord.Embed(
            title=f"⚔️ {self.username}'s Slayer Stats",
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
            stats = await self.bot.db.skills.get_slayer_stats(self.user_id, slayer_id)
            if stats:
                xp = stats.get('xp', 0)
                level = stats.get('level', 0)
                kills = stats.get('total_kills', 0)
                total_kills += kills
                embed.add_field(name=slayer_name, value=f"Level {level}\n{xp:,} XP", inline=True)
            else:
                embed.add_field(name=slayer_name, value="Level 0\n0 XP\n0 Kills", inline=True)
        
        embed.add_field(name="📊 Total Kills", value=f"{total_kills}", inline=False)
        
        return embed
    
    async def get_info_embed(self):
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
        
        return embed