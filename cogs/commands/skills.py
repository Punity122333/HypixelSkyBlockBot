import discord
from discord.ext import commands
from discord import app_commands
import random
from utils.event_effects import EventEffects
from utils.stat_calculator import StatCalculator

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
        await interaction.response.defer()
        await self.bot.player_manager.get_or_create_player(
            interaction.user.id, interaction.user.name
        )
        
        active_events = await self.event_effects.get_active_events()
        xp_multiplier = await self.event_effects.get_xp_multiplier('alchemy') if active_events else 1.0
        
        player_stats = await StatCalculator.calculate_player_stats(self.bot.db, self.bot.game_data, interaction.user.id)
        xp_gained = random.randint(15, 60)
        xp_gained = int(xp_gained * xp_multiplier)
        pet_luck = player_stats.get('pet_luck', 0)
        xp_gained = int(xp_gained * (1 + pet_luck / 100))
        skills = await self.bot.db.get_skills(interaction.user.id)
        alchemy_skill = next((s for s in skills if s['skill_name'] == 'alchemy'), None)
        new_level = alchemy_skill['level'] if alchemy_skill else 0
        
        potions_brewed = []
        all_potions = [
            'awkward_potion', 'speed_potion_1', 'strength_potion_1', 'regeneration_potion_1', 
            'defense_potion_1', 'critical_potion_1', 'fishing_potion_1', 'mining_potion_1',
            'farming_potion_1', 'combat_potion_1', 'intelligence_potion_1', 'foraging_potion_1'
        ]
        
        if new_level >= 10:
            all_potions.extend(['speed_potion_2', 'strength_potion_2', 'regeneration_potion_2', 
                               'defense_potion_2', 'critical_potion_2', 'magic_find_potion_1'])
        
        if new_level >= 20:
            all_potions.extend(['speed_potion_3', 'strength_potion_3', 'crit_damage_potion_1',
                               'intelligence_potion_2', 'true_defense_potion_1', 'ability_damage_potion_1'])
        
        if new_level >= 30:
            all_potions.extend(['magic_find_potion_2', 'crit_damage_potion_2', 'ferocity_potion_1',
                               'pet_luck_potion_1', 'attack_speed_potion_1'])
        
        if new_level >= 40:
            all_potions.extend(['magic_find_potion_3', 'ability_damage_potion_2', 'ferocity_potion_2',
                               'true_defense_potion_2', 'attack_speed_potion_2'])
        
        num_potions = random.randint(2, 4)
        for _ in range(num_potions):
            potion = random.choice(all_potions)
            amount = random.randint(1, 3)
            await self.bot.db.add_item_to_inventory(interaction.user.id, potion, amount)
            potion_name = potion.replace('_', ' ').title()
            potions_brewed.append(f"{potion_name} x{amount}")
        
        if alchemy_skill:
            new_xp = alchemy_skill['xp'] + xp_gained
            new_level = await self.bot.game_data.calculate_level_from_xp('alchemy', new_xp)
            await self.bot.db.update_skill(interaction.user.id, 'alchemy', xp=new_xp, level=new_level)
            from utils.systems.badge_system import BadgeSystem
            await BadgeSystem.check_and_unlock_badges(self.bot.db, interaction.user.id, 'skill', skill_name='alchemy', level=new_level)
            if new_level >= 50:
                await BadgeSystem.check_and_unlock_badges(self.bot.db, interaction.user.id, 'skill_50')
        embed = discord.Embed(
            title="🧪 Alchemy Session Complete!",
            description=f"You brewed some potions!",
            color=discord.Color.orange()
        )

        active_events = await self.event_effects.get_active_events()
        if active_events and xp_multiplier > 1.0:
            event_text = f"🎪 **Active Event Bonuses:** +{int((xp_multiplier - 1) * 100)}% XP"
            current_desc = embed.description or ""
            embed.description = f"{current_desc}\n{event_text}"
        
        embed.add_field(name="🧪 Potions Brewed", value="\n".join(potions_brewed), inline=False)
        embed.add_field(name="⭐ Alchemy XP", value=f"+{xp_gained} XP", inline=False)
        embed.add_field(name="Current Level", value=f"Alchemy {new_level}", inline=False)
        await interaction.followup.send(embed=embed)

    @app_commands.command(name="carpentry", description="Improve your carpentry skill!")
    async def carpentry(self, interaction: discord.Interaction):
        await interaction.response.defer()
        await self.bot.player_manager.get_or_create_player(
            interaction.user.id, interaction.user.name
        )
        
        active_events = await self.event_effects.get_active_events()
        xp_multiplier = await self.event_effects.get_xp_multiplier('carpentry') if active_events else 1.0
        
        player_stats = await StatCalculator.calculate_player_stats(self.bot.db, self.bot.game_data, interaction.user.id)
        xp_gained = random.randint(10, 50)
        xp_gained = int(xp_gained * xp_multiplier)
        pet_luck = player_stats.get('pet_luck', 0)
        xp_gained = int(xp_gained * (1 + pet_luck / 100))
        skills = await self.bot.db.get_skills(interaction.user.id)
        carpentry_skill = next((s for s in skills if s['skill_name'] == 'carpentry'), None)
        new_level = carpentry_skill['level'] if carpentry_skill else 0
        if carpentry_skill:
            new_xp = carpentry_skill['xp'] + xp_gained
            new_level = await self.bot.game_data.calculate_level_from_xp('carpentry', new_xp)
            await self.bot.db.update_skill(interaction.user.id, 'carpentry', xp=new_xp, level=new_level)
            from utils.systems.badge_system import BadgeSystem
            await BadgeSystem.check_and_unlock_badges(self.bot.db, interaction.user.id, 'skill', skill_name='carpentry', level=new_level)
            if new_level >= 50:
                await BadgeSystem.check_and_unlock_badges(self.bot.db, interaction.user.id, 'skill_50')
            
            from utils.systems.achievement_system import AchievementSystem
            await AchievementSystem.check_skill_achievements(self.bot.db, interaction, interaction.user.id, 'carpentry', new_level)
        embed = discord.Embed(
            title="🪵 Carpentry Session Complete!",
            description=f"You crafted some furniture!",
            color=discord.Color.from_rgb(139, 69, 19)
        )
        
        # Get active events to check if we should display bonuses
        active_events = await self.event_effects.get_active_events()
        if active_events and xp_multiplier > 1.0:
            event_text = f"🎪 **Active Event Bonuses:** +{int((xp_multiplier - 1) * 100)}% XP"
            current_desc = embed.description or ""
            embed.description = f"{current_desc}\n{event_text}"
        
        embed.add_field(name="⭐ Carpentry XP", value=f"+{xp_gained} XP", inline=False)
        embed.add_field(name="Current Level", value=f"Carpentry {new_level}", inline=False)
        await interaction.followup.send(embed=embed)

    @app_commands.command(name="runecrafting", description="Level up your runecrafting!")
    async def runecrafting(self, interaction: discord.Interaction):
        await interaction.response.defer()
        await self.bot.player_manager.get_or_create_player(
            interaction.user.id, interaction.user.name
        )
        
        active_events = await self.event_effects.get_active_events()
        xp_multiplier = await self.event_effects.get_xp_multiplier('runecrafting') if active_events else 1.0
        
        player_stats = await StatCalculator.calculate_player_stats(self.bot.db, self.bot.game_data, interaction.user.id)
        xp_gained = random.randint(5, 30)
        xp_gained = int(xp_gained * xp_multiplier)
        pet_luck = player_stats.get('pet_luck', 0)
        xp_gained = int(xp_gained * (1 + pet_luck / 100))
        skills = await self.bot.db.get_skills(interaction.user.id)
        runecrafting_skill = next((s for s in skills if s['skill_name'] == 'runecrafting'), None)
        new_level = runecrafting_skill['level'] if runecrafting_skill else 0
        
        runes_crafted = []
        basic_runes = ['speed_rune', 'strength_rune', 'health_rune', 'defense_rune']
        rare_runes = ['intelligence_rune', 'crit_damage_rune', 'crit_chance_rune', 
                     'mining_fortune_rune', 'farming_fortune_rune', 'foraging_fortune_rune',
                     'fishing_speed_rune', 'sea_creature_rune', 'attack_speed_rune']
        epic_runes = ['magic_find_rune', 'ferocity_rune', 'true_defense_rune', 'pet_luck_rune']
        legendary_runes = ['ability_damage_rune']
        
        num_runes = random.randint(2, 4)
        for _ in range(num_runes):
            rune = random.choice(basic_runes)
            amount = random.randint(1, 3)
            await self.bot.db.add_item_to_inventory(interaction.user.id, rune, amount)
            rune_name = rune.replace('_', ' ').title()
            runes_crafted.append(f"{rune_name} x{amount}")
        
        if new_level >= 5 and random.random() < 0.3:
            rune = random.choice(rare_runes)
            amount = random.randint(1, 2)
            await self.bot.db.add_item_to_inventory(interaction.user.id, rune, amount)
            rune_name = rune.replace('_', ' ').title()
            runes_crafted.append(f"✨ {rune_name} x{amount}")
        
        if new_level >= 15 and random.random() < 0.1:
            rune = random.choice(epic_runes)
            await self.bot.db.add_item_to_inventory(interaction.user.id, rune, 1)
            rune_name = rune.replace('_', ' ').title()
            runes_crafted.append(f"⭐ {rune_name} x1")
        
        if new_level >= 20 and random.random() < 0.05:
            rune = random.choice(legendary_runes)
            await self.bot.db.add_item_to_inventory(interaction.user.id, rune, 1)
            rune_name = rune.replace('_', ' ').title()
            runes_crafted.append(f"🌟 {rune_name} x1")
        
        if runecrafting_skill:
            new_xp = runecrafting_skill['xp'] + xp_gained
            new_level = await self.bot.game_data.calculate_level_from_xp('runecrafting', new_xp)
            await self.bot.db.update_skill(interaction.user.id, 'runecrafting', xp=new_xp, level=new_level)
            from utils.systems.badge_system import BadgeSystem
            await BadgeSystem.check_and_unlock_badges(self.bot.db, interaction.user.id, 'skill', skill_name='runecrafting', level=new_level)
            if new_level >= 50:
                await BadgeSystem.check_and_unlock_badges(self.bot.db, interaction.user.id, 'skill_50')
            
            from utils.systems.achievement_system import AchievementSystem
            await AchievementSystem.check_skill_achievements(self.bot.db, interaction, interaction.user.id, 'runecrafting', new_level)
        embed = discord.Embed(
            title="🔮 Runecrafting Session Complete!",
            description=f"You combined some runes!",
            color=discord.Color.purple()
        )

        active_events = await self.event_effects.get_active_events()
        if active_events and xp_multiplier > 1.0:
            event_text = f"🎪 **Active Event Bonuses:** +{int((xp_multiplier - 1) * 100)}% XP"
            current_desc = embed.description or ""
            embed.description = f"{current_desc}\n{event_text}"
        
        embed.add_field(name="🔮 Runes Crafted", value="\n".join(runes_crafted), inline=False)
        embed.add_field(name="⭐ Runecrafting XP", value=f"+{xp_gained} XP", inline=False)
        embed.add_field(name="Current Level", value=f"Runecrafting {new_level}", inline=False)
        await interaction.followup.send(embed=embed)

    @app_commands.command(name="social", description="Increase your social skill!")
    async def social(self, interaction: discord.Interaction):
        await interaction.response.defer()
        await self.bot.player_manager.get_or_create_player(
            interaction.user.id, interaction.user.name
        )
        
        active_events = await self.event_effects.get_active_events()
        xp_multiplier = await self.event_effects.get_xp_multiplier('social') if active_events else 1.0
        
        player_stats = await StatCalculator.calculate_player_stats(self.bot.db, self.bot.game_data, interaction.user.id)
        xp_gained = random.randint(10, 40)
        xp_gained = int(xp_gained * xp_multiplier)
        pet_luck = player_stats.get('pet_luck', 0)
        xp_gained = int(xp_gained * (1 + pet_luck / 100))
        skills = await self.bot.db.get_skills(interaction.user.id)
        social_skill = next((s for s in skills if s['skill_name'] == 'social'), None)
        new_level = social_skill['level'] if social_skill else 0
        if social_skill:
            new_xp = social_skill['xp'] + xp_gained
            new_level = await self.bot.game_data.calculate_level_from_xp('social', new_xp)
            await self.bot.db.update_skill(interaction.user.id, 'social', xp=new_xp, level=new_level)
            from utils.systems.badge_system import BadgeSystem
            await BadgeSystem.check_and_unlock_badges(self.bot.db, interaction.user.id, 'skill', skill_name='social', level=new_level)
            if new_level >= 50:
                await BadgeSystem.check_and_unlock_badges(self.bot.db, interaction.user.id, 'skill_50')
            
            from utils.systems.achievement_system import AchievementSystem
            await AchievementSystem.check_skill_achievements(self.bot.db, interaction, interaction.user.id, 'social', new_level)
        embed = discord.Embed(
            title="👥 Social Session Complete!",
            description=f"You interacted with other players!",
            color=discord.Color.blue()
        )

        active_events = await self.event_effects.get_active_events()
        if active_events and xp_multiplier > 1.0:
            event_text = f"🎪 **Active Event Bonuses:** +{int((xp_multiplier - 1) * 100)}% XP"
            current_desc = embed.description or ""
            embed.description = f"{current_desc}\n{event_text}"
        
        embed.add_field(name="⭐ Social XP", value=f"+{xp_gained} XP", inline=False)
        embed.add_field(name="Current Level", value=f"Social {new_level}", inline=False)
        await interaction.followup.send(embed=embed)

async def setup(bot):
    await bot.add_cog(SkillCommands(bot))
