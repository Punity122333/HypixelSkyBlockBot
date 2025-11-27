import discord
from discord.ext import commands
from discord import app_commands

class SkillCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

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

    @app_commands.command(name="combat", description="Fight mobs!")
    async def combat(self, interaction: discord.Interaction):
        import random
        
        await self.bot.player_manager.get_or_create_player(
            interaction.user.id, interaction.user.name
        )
        
        mob_drops = [
            ('rotten_flesh', 3, 8, 5),
            ('bone', 2, 5, 6),
            ('string', 1, 4, 7),
            ('spider_eye', 1, 3, 8),
            ('gunpowder', 1, 2, 10),
            ('ender_pearl', 0, 1, 20),
        ]
        
        total_xp = 0
        total_coins = 0
        items_found = {}
        
        for item_id, min_amt, max_amt, xp in mob_drops:
            if random.random() > 0.4:
                amount = random.randint(min_amt, max_amt)
                if amount > 0:
                    await self.bot.db.add_item_to_inventory(interaction.user.id, item_id, amount)
                    items_found[item_id] = amount
                    total_xp += xp * amount
                    total_coins += amount * 4
        
        skills = await self.bot.db.get_skills(interaction.user.id)
        combat_skill = next((s for s in skills if s['skill_name'] == 'combat'), None)
        
        if combat_skill:
            new_xp = combat_skill['xp'] + total_xp
            new_level = await self.bot.game_data.calculate_level_from_xp('combat', new_xp)
            
            await self.bot.db.update_skill(interaction.user.id, 'combat', xp=new_xp, level=new_level)
            await self.bot.player_manager.add_coins(interaction.user.id, total_coins)
            
            player_data = await self.bot.db.get_player(interaction.user.id)
            if player_data:
                await self.bot.db.update_player(interaction.user.id, total_earned=player_data.get('total_earned', 0) + total_coins)
            
            embed = discord.Embed(
                title="⚔️ Combat Session Complete!",
                description=f"You defeated some enemies and found:",
                color=discord.Color.red()
            )
            
            for item_id, amount in list(items_found.items())[:10]:
                embed.add_field(name=item_id.replace('_', ' ').title(), value=f"{amount}x", inline=True)
            
            embed.add_field(name="💰 Coins Earned", value=f"+{total_coins} coins", inline=False)
            embed.add_field(name="⭐ Combat XP", value=f"+{total_xp} XP", inline=False)
            embed.add_field(name="Current Level", value=f"Combat {new_level}", inline=False)
            
            await interaction.response.send_message(embed=embed)

    @app_commands.command(name="alchemy", description="Brew potions!")
    async def alchemy(self, interaction: discord.Interaction):
        import random
        
        await self.bot.player_manager.get_or_create_player(
            interaction.user.id, interaction.user.name
        )
        
        xp_gained = random.randint(15, 60)
        
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
            
            await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(SkillCommands(bot))
