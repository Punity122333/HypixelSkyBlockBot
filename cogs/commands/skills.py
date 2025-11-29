import discord
from discord.ext import commands
from discord import app_commands
import random
from utils.event_effects import EventEffects

class SkillCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.event_effects = EventEffects(bot)

    @app_commands.command(name="skills", description="View all your skills")
    async def skills(self, interaction: discord.Interaction):
        await self.bot.player_manager.get_or_create_player(
            interaction.user.id, interaction.user.name
        )
        
        skills = await self.bot.db.get_skills(interaction.user.id)
        
        embed = discord.Embed(
            title=f"📚 {interaction.user.name}'s Skills",
            color=discord.Color.green()
        )
        
        for skill in skills:
            next_level_xp = await self.bot.game_data.get_xp_for_level(skill['skill_name'], skill['level'] + 1)
            current_level_xp = await self.bot.game_data.get_xp_for_level(skill['skill_name'], skill['level'])
            progress = skill['xp'] - current_level_xp
            needed = next_level_xp - current_level_xp
            
            bar_length = 10
            filled = int((progress / needed) * bar_length) if needed > 0 else bar_length
            bar = '█' * filled + '░' * (bar_length - filled)
            
            embed.add_field(
                name=f"{skill['skill_name'].title()} - Level {skill['level']}",
                value=f"{bar} ({progress:,}/{needed:,} XP)",
                inline=False
            )
        
        await interaction.response.send_message(embed=embed)


    @app_commands.command(name="alchemy", description="Brew potions!")
    async def alchemy(self, interaction: discord.Interaction):
        import random
        
        await self.bot.player_manager.get_or_create_player(
            interaction.user.id, interaction.user.name
        )
        
        xp_gained = random.randint(15, 60)
        
        xp_multiplier = await self.event_effects.get_xp_multiplier('alchemy')
        xp_gained = int(xp_gained * xp_multiplier)
        
        skills = await self.bot.db.get_skills(interaction.user.id)
        alchemy_skill = next((s for s in skills if s['skill_name'] == 'alchemy'), None)
        
        if alchemy_skill:
            new_xp = alchemy_skill['xp'] + xp_gained
            new_level = await self.bot.game_data.calculate_level_from_xp('alchemy', new_xp)
            
            await self.bot.db.update_skill(interaction.user.id, 'alchemy', xp=new_xp, level=new_level)
            
            embed = discord.Embed(
                title="🧪 Alchemy",
                description=f"You brewed some potions!",
                color=discord.Color.orange()
            )
            embed.add_field(name="XP Gained", value=f"+{xp_gained} Alchemy XP", inline=True)
            embed.add_field(name="Current Level", value=f"Alchemy {new_level}", inline=True)
            
            if xp_multiplier > 1.0:
                event_text = f"🎪 **Active Event Bonuses:** +{int((xp_multiplier - 1) * 100)}% XP"
                current_desc = embed.description or ""
                embed.description = f"{current_desc}\n{event_text}"
            
            await interaction.response.send_message(embed=embed)

    @app_commands.command(name="carpentry", description="Improve your carpentry skill!")
    async def carpentry(self, interaction: discord.Interaction):
        await self.bot.player_manager.get_or_create_player(
            interaction.user.id, interaction.user.name
        )
        
        xp_gained = random.randint(10, 50)
        
        xp_multiplier = await self.event_effects.get_xp_multiplier('carpentry')
        xp_gained = int(xp_gained * xp_multiplier)
        
        skills = await self.bot.db.get_skills(interaction.user.id)
        carpentry_skill = next((s for s in skills if s['skill_name'] == 'carpentry'), None)
        
        if carpentry_skill:
            new_xp = carpentry_skill['xp'] + xp_gained
            new_level = await self.bot.game_data.calculate_level_from_xp('carpentry', new_xp)
            
            await self.bot.db.update_skill(interaction.user.id, 'carpentry', xp=new_xp, level=new_level)
            
            embed = discord.Embed(
                title="🪵 Carpentry",
                description=f"You crafted some furniture!",
                color=discord.Color.from_rgb(139, 69, 19)
            )
            embed.add_field(name="XP Gained", value=f"+{xp_gained} Carpentry XP", inline=True)
            embed.add_field(name="Current Level", value=f"Carpentry {new_level}", inline=True)
            
            if xp_multiplier > 1.0:
                event_text = f"🎪 **Active Event Bonuses:** +{int((xp_multiplier - 1) * 100)}% XP"
                current_desc = embed.description or ""
                embed.description = f"{current_desc}\n{event_text}"
            
            await interaction.response.send_message(embed=embed)

    @app_commands.command(name="runecrafting", description="Level up your runecrafting!")
    async def runecrafting(self, interaction: discord.Interaction):
        await self.bot.player_manager.get_or_create_player(
            interaction.user.id, interaction.user.name
        )
        
        xp_gained = random.randint(5, 30)
        
        xp_multiplier = await self.event_effects.get_xp_multiplier('runecrafting')
        xp_gained = int(xp_gained * xp_multiplier)
        
        skills = await self.bot.db.get_skills(interaction.user.id)
        runecrafting_skill = next((s for s in skills if s['skill_name'] == 'runecrafting'), None)
        
        if runecrafting_skill:
            new_xp = runecrafting_skill['xp'] + xp_gained
            new_level = await self.bot.game_data.calculate_level_from_xp('runecrafting', new_xp)
            
            await self.bot.db.update_skill(interaction.user.id, 'runecrafting', xp=new_xp, level=new_level)
            
            embed = discord.Embed(
                title="🔮 Runecrafting",
                description=f"You combined some runes!",
                color=discord.Color.purple()
            )
            embed.add_field(name="XP Gained", value=f"+{xp_gained} Runecrafting XP", inline=True)
            embed.add_field(name="Current Level", value=f"Runecrafting {new_level}", inline=True)
            
            if xp_multiplier > 1.0:
                event_text = f"🎪 **Active Event Bonuses:** +{int((xp_multiplier - 1) * 100)}% XP"
                current_desc = embed.description or ""
                embed.description = f"{current_desc}\n{event_text}"
            
            await interaction.response.send_message(embed=embed)

    @app_commands.command(name="social", description="Increase your social skill!")
    async def social(self, interaction: discord.Interaction):
        await self.bot.player_manager.get_or_create_player(
            interaction.user.id, interaction.user.name
        )
        
        xp_gained = random.randint(10, 40)
        
        xp_multiplier = await self.event_effects.get_xp_multiplier('social')
        xp_gained = int(xp_gained * xp_multiplier)
        
        skills = await self.bot.db.get_skills(interaction.user.id)
        social_skill = next((s for s in skills if s['skill_name'] == 'social'), None)
        
        if social_skill:
            new_xp = social_skill['xp'] + xp_gained
            new_level = await self.bot.game_data.calculate_level_from_xp('social', new_xp)
            
            await self.bot.db.update_skill(interaction.user.id, 'social', xp=new_xp, level=new_level)
            
            embed = discord.Embed(
                title="👥 Social",
                description=f"You interacted with other players!",
                color=discord.Color.blue()
            )
            embed.add_field(name="XP Gained", value=f"+{xp_gained} Social XP", inline=True)
            embed.add_field(name="Current Level", value=f"Social {new_level}", inline=True)
            
            if xp_multiplier > 1.0:
                event_text = f"🎪 **Active Event Bonuses:** +{int((xp_multiplier - 1) * 100)}% XP"
                current_desc = embed.description or ""
                embed.description = f"{current_desc}\n{event_text}"
            
            await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(SkillCommands(bot))
