import discord
from discord.ext import commands
from discord import app_commands
import random
from utils.stat_calculator import StatCalculator
from utils.systems.gathering_system import GatheringSystem
from utils.systems.achievement_system import AchievementSystem
from utils.event_effects import EventEffects
from components.views.mining_location_view import MiningLocationView

class GatheringCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.event_effects = EventEffects(bot)

    @app_commands.command(name="mine", description="Go mining and collect resources")
    async def mine(self, interaction: discord.Interaction):
        view = MiningLocationView(self.bot, interaction.user.id)
        await interaction.response.send_message(
            "⛏️ **Choose your mining location:**",
            view=view,
            ephemeral=True
        )

    @app_commands.command(name="farm", description="Farm crops")
    async def farm(self, interaction: discord.Interaction):
        await interaction.response.defer()
        equipped_items = await self.bot.db.get_equipped_items(interaction.user.id)
        hoe = equipped_items.get('hoe')
        if not hoe:
            embed = discord.Embed(
                title="❌ No Hoe!",
                description="You need to equip a hoe to farm! Use `/begin` to get started, or `/craft` to make a better hoe.",
                color=discord.Color.red()
            )
            await interaction.followup.send(embed=embed)
            return
        
        tool_id = hoe['item_id']
        
        import time
        progression = await self.bot.db.get_player_progression(interaction.user.id)
        if not progression or not progression.get('first_farm_date'):
            await self.bot.db.update_progression(
                interaction.user.id,
                first_farm_date=int(time.time())
            )
            # Unlock first farm achievement
            await AchievementSystem.unlock_single_achievement(self.bot.db, interaction, interaction.user.id, 'first_farm')
        
        active_events = await self.event_effects.get_active_events()
        event_multiplier = await self.event_effects.get_gathering_multiplier() if active_events else 1.0
        xp_multiplier = await self.event_effects.get_xp_multiplier('farming') if active_events else 1.0
        coin_multiplier = await self.event_effects.get_coin_multiplier() if active_events else 1.0
        fortune_bonus = await self.event_effects.get_fortune_bonus('farming') if active_events else 0
        multiplier = await self.bot.db.get_tool_multiplier(interaction.user.id, 'hoe')
        
        event_bonuses = {}
        if fortune_bonus > 0:
            event_bonuses['farming_fortune'] = fortune_bonus
        
        crop_types = ['wheat', 'carrot', 'potato', 'pumpkin', 'melon']
        selected_crops = random.sample(crop_types, k=random.randint(1, 3))
        
        total_xp = 0
        total_coins = 0
        items_found = {}
        skill_yield_multiplier = 1.0
        skill_drop_multiplier = 1.0
        farming_level = 0
        
        tool_bonuses_display = None
        for crop_type in selected_crops:
            result = await GatheringSystem.harvest_crop(self.bot.db, interaction.user.id, crop_type, event_bonuses)
            
            if result['success']:
                skill_yield_multiplier = result.get('skill_yield_multiplier', 1.0)
                skill_drop_multiplier = result.get('skill_drop_multiplier', 1.0)
                farming_level = result.get('skill_level', 0)
                if not tool_bonuses_display and 'tool_bonuses' in result:
                    tool_bonuses_display = result['tool_bonuses']
                
                for drop in result['drops']:
                    item_id = drop['item_id']
                    amount = int(drop['amount'] * multiplier * event_multiplier)
                    amount = max(1, amount)
                    
                    await self.bot.db.add_item_to_inventory(interaction.user.id, item_id, amount)
                    await self.bot.db.update_collection(interaction.user.id, item_id, amount)
                    
                    item_name = item_id.replace('_', ' ').title()
                    items_found[item_name] = items_found.get(item_name, 0) + amount
                
                xp_gained = int(result['xp'] * event_multiplier)
                total_xp += xp_gained
                total_coins += int(xp_gained * 0.6)
        
        total_xp = int(total_xp * xp_multiplier)
        total_coins = int(total_coins * coin_multiplier)
        skills = await self.bot.db.get_skills(interaction.user.id)
        farming_skill = next((s for s in skills if s['skill_name'] == 'farming'), None)
        new_level = farming_skill['level'] if farming_skill else 0
        if farming_skill:
            new_xp = farming_skill['xp'] + total_xp
            new_level = await self.bot.game_data.calculate_level_from_xp('farming', new_xp)
            await self.bot.db.update_skill(interaction.user.id, 'farming', xp=new_xp, level=new_level)
        
        await AchievementSystem.check_skill_achievements(self.bot.db, interaction, interaction.user.id, 'farming', new_level)
        
        from utils.systems.badge_system import BadgeSystem
        await BadgeSystem.check_and_unlock_badges(self.bot.db, interaction.user.id, 'skill', skill_name='farming', level=new_level)
        if new_level >= 50:
            await BadgeSystem.check_and_unlock_badges(self.bot.db, interaction.user.id, 'skill_50')
        await self.bot.player_manager.add_coins(interaction.user.id, total_coins)
        embed = discord.Embed(
            title="🚜 Farming Session Complete!",
            description=f"Using **{tool_id.replace('_', ' ').title()}** ({multiplier * event_multiplier:.1f}x efficiency)\n**Farming Level {farming_level}** ({skill_yield_multiplier:.2f}x yield, {skill_drop_multiplier:.2f}x drops)\nYou went farming and found:",
            color=discord.Color.green()
        )

        if tool_bonuses_display:
            tool_bonus_text = []
            if tool_bonuses_display.get('fortune', 0) > 0:
                tool_bonus_text.append(f"+{int(tool_bonuses_display['fortune'])} Farming Fortune")
            if tool_bonuses_display.get('yield_multiplier', 1.0) > 1.0:
                tool_bonus_text.append(f"{tool_bonuses_display['yield_multiplier']:.2f}x Crop Yield")
            if tool_bonus_text:
                current_desc = embed.description or ""
                embed.description = f"{current_desc}\n🔧 **Tool Bonuses:** {' • '.join(tool_bonus_text)}"

        active_events = await self.event_effects.get_active_events()
        if active_events and (event_multiplier > 1.0 or xp_multiplier > 1.0 or coin_multiplier > 1.0 or fortune_bonus > 0):
            event_text = "🎪 **Active Event Bonuses:** "
            bonuses = []
            if event_multiplier > 1.0:
                bonuses.append(f"+{int((event_multiplier - 1) * 100)}% gathering")
            if fortune_bonus > 0:
                bonuses.append(f"+{fortune_bonus} farming fortune")
            if xp_multiplier > 1.0:
                bonuses.append(f"+{int((xp_multiplier - 1) * 100)}% XP")
            if coin_multiplier > 1.0:
                bonuses.append(f"+{int((coin_multiplier - 1) * 100)}% coins")
            current_desc = embed.description or ""
            embed.description = f"{current_desc}\n{event_text}{', '.join(bonuses)}"
        if len(items_found.items()) != 0:
            for item_name, amount in list(items_found.items())[:10]:
                embed.add_field(name=item_name, value=f"{amount}x", inline=True)
        else:
            embed.add_field(name="No Crops Found", value="Better luck next time!", inline=False)
        embed.add_field(name="💰 Coins Earned", value=f"+{total_coins} coins", inline=False)
        embed.add_field(name="⭐ Farming XP", value=f"+{total_xp} XP", inline=False)
        embed.add_field(name="Current Level", value=f"Farming {new_level}", inline=False)
        await interaction.followup.send(embed=embed)

    @app_commands.command(name="fish", description="Go fishing")
    async def fish(self, interaction: discord.Interaction):
        await interaction.response.defer()
        equipped_items = await self.bot.db.get_equipped_items(interaction.user.id)
        fishing_rod = equipped_items.get('fishing_rod')
        if not fishing_rod:
            embed = discord.Embed(
                title="❌ No Fishing Rod!",
                description="You need to equip a fishing rod to fish! Use `/begin` to get started or `/craft` to craft one.",
                color=discord.Color.red()
            )
            await interaction.followup.send(embed=embed)
            return
        
        tool_id = fishing_rod['item_id']
        
        import time
        progression = await self.bot.db.get_player_progression(interaction.user.id)
        if not progression or not progression.get('first_fish_date'):
            await self.bot.db.update_progression(
                interaction.user.id,
                first_fish_date=int(time.time())
            )
            await AchievementSystem.unlock_single_achievement(self.bot.db, interaction, interaction.user.id, 'first_fish')
        
        active_events = await self.event_effects.get_active_events()
        xp_multiplier = await self.event_effects.get_xp_multiplier('fishing') if active_events else 1.0
        coin_multiplier = await self.event_effects.get_coin_multiplier() if active_events else 1.0
        sea_creature_bonus = await self.event_effects.get_sea_creature_bonus() if active_events else 0
        
        event_bonuses = {}
        if sea_creature_bonus > 0:
            event_bonuses['sea_creature_chance'] = sea_creature_bonus
        
        result = await GatheringSystem.fish(self.bot.db, interaction.user.id, event_bonuses)
        
        if not result['success']:
            await interaction.followup.send(f"❌ {result.get('error', 'Failed to fish')}", ephemeral=True)
            return
        
        total_xp = int(result['xp'] * xp_multiplier)
        total_coins = int(result['xp'] * 3 * coin_multiplier)
        
        catch = result['catch']
        is_sea_creature = result['is_sea_creature']
        fishing_level = result.get('skill_level', 0)
        skill_speed_multiplier = result.get('skill_speed_multiplier', 1.0)
        tool_bonuses = result.get('tool_bonuses', {})
        
        if is_sea_creature:
            from components.views.sea_creature_combat_view import SeaCreatureCombatView
            
            creature_name = catch['creature_id'].replace('_', ' ').title()
            creature_health = catch['health']
            creature_damage = int(creature_health * 0.1)
            
            view = SeaCreatureCombatView(
                self.bot, 
                interaction.user.id, 
                creature_name, 
                creature_health, 
                creature_damage, 
                catch['coins'], 
                catch['xp']
            )
            
            embed = discord.Embed(
                title=f"🐟 A wild {creature_name} appeared!",
                description="A sea creature has been hooked! Prepare for battle!",
                color=discord.Color.dark_blue()
            )
            embed.add_field(name="Enemy Health", value=f"❤️ {creature_health} HP", inline=True)
            embed.add_field(name="Enemy Damage", value=f"⚔️ ~{creature_damage} damage", inline=True)
            embed.add_field(name="Potential Reward", value=f"💰 {catch['coins']} coins\n⭐ {catch['xp']} XP", inline=False)
            embed.set_footer(text="Use the buttons below to fight!")
            
            await interaction.followup.send(embed=embed, view=view)
            view.message = await interaction.original_response()
            return
        else:
            await self.bot.db.add_item_to_inventory(interaction.user.id, catch['item_id'], catch['amount'])
            await self.bot.db.update_collection(interaction.user.id, catch['item_id'], catch['amount'])
            
            embed = discord.Embed(
                title="🎣 Fishing Session Complete!",
                description=f"Using **{tool_id.replace('_', ' ').title()}**\n**Fishing Level {fishing_level}** ({skill_speed_multiplier:.2f}x speed bonus)\nYou caught:",
                color=discord.Color.blue()
            )

            tool_bonus_text = []
            if tool_bonuses.get('speed', 0) > 0:
                tool_bonus_text.append(f"+{int(tool_bonuses['speed'])} Fishing Speed")
            if tool_bonuses.get('fortune', 0) > 0:
                tool_bonus_text.append(f"+{int(tool_bonuses['fortune'])}% Sea Creature Chance")
            if tool_bonus_text:
                current_desc = embed.description or ""
                embed.description = f"{current_desc}\n🔧 **Tool Bonuses:** {' • '.join(tool_bonus_text)}"
            
            item_name = catch['item_id'].replace('_', ' ').title()
            embed.add_field(name=item_name, value=f"{catch['amount']}x ({catch['rarity'].upper()})", inline=False)
        skills = await self.bot.db.get_skills(interaction.user.id)
        fishing_skill = next((s for s in skills if s['skill_name'] == 'fishing'), None)
        new_level = fishing_skill['level'] if fishing_skill else 0
        if fishing_skill:
            total_xp = int(total_xp * xp_multiplier)
            total_coins = int(total_coins * coin_multiplier)
            new_xp = fishing_skill['xp'] + total_xp
            new_level = await self.bot.game_data.calculate_level_from_xp('fishing', new_xp)
            await self.bot.db.update_skill(interaction.user.id, 'fishing', xp=new_xp, level=new_level)
        
        await AchievementSystem.check_skill_achievements(self.bot.db, interaction, interaction.user.id, 'fishing', new_level)
        
        from utils.systems.badge_system import BadgeSystem
        await BadgeSystem.check_and_unlock_badges(self.bot.db, interaction.user.id, 'skill', skill_name='fishing', level=new_level)
        if new_level >= 50:
            await BadgeSystem.check_and_unlock_badges(self.bot.db, interaction.user.id, 'skill_50')
        await self.bot.player_manager.add_coins(interaction.user.id, total_coins)

        active_events = await self.event_effects.get_active_events()
        if active_events and (xp_multiplier > 1.0 or coin_multiplier > 1.0 or sea_creature_bonus > 0):
            event_text = "🎪 **Active Event Bonuses:** "
            bonuses = []
            if sea_creature_bonus > 0:
                bonuses.append(f"+{sea_creature_bonus}% sea creature chance")
            if xp_multiplier > 1.0:
                bonuses.append(f"+{int((xp_multiplier - 1) * 100)}% XP")
            if coin_multiplier > 1.0:
                bonuses.append(f"+{int((coin_multiplier - 1) * 100)}% coins")
            current_desc = embed.description or ""
            embed.description = f"{current_desc}\n{event_text}{', '.join(bonuses)}"
        embed.add_field(name="💰 Coins Earned", value=f"+{total_coins} coins", inline=False)
        embed.add_field(name="⭐ Fishing XP", value=f"+{total_xp} XP", inline=False)
        embed.add_field(name="Current Level", value=f"Fishing {new_level}", inline=False)
        await interaction.followup.send(embed=embed)

    @app_commands.command(name="forage", description="Chop trees")
    async def forage(self, interaction: discord.Interaction):
        await interaction.response.defer()
        equipped_items = await self.bot.db.get_equipped_items(interaction.user.id)
        axe = equipped_items.get('axe')
        if not axe:
            embed = discord.Embed(
                title="❌ No Axe!",
                description="You need to equip an axe to chop trees! Use `/begin` to get started or `/craft` to make one.",
                color=discord.Color.red()
            )
            await interaction.followup.send(embed=embed)
            return
        
        tool_id = axe['item_id']
        
        import time
        progression = await self.bot.db.get_player_progression(interaction.user.id)
        if not progression or not progression.get('first_forage_date'):
            await self.bot.db.update_progression(
                interaction.user.id,
                first_forage_date=int(time.time())
            )
            await AchievementSystem.unlock_single_achievement(self.bot.db, interaction, interaction.user.id, 'first_forage')
        
        active_events = await self.event_effects.get_active_events()
        event_multiplier = await self.event_effects.get_gathering_multiplier() if active_events else 1.0
        xp_multiplier = await self.event_effects.get_xp_multiplier('foraging') if active_events else 1.0
        coin_multiplier = await self.event_effects.get_coin_multiplier() if active_events else 1.0
        fortune_bonus = await self.event_effects.get_fortune_bonus('foraging') if active_events else 0
        multiplier = await self.bot.db.get_tool_multiplier(interaction.user.id, 'axe')
        
        event_bonuses = {}
        if fortune_bonus > 0:
            event_bonuses['foraging_fortune'] = fortune_bonus
        
        wood_types = ['oak_wood', 'jungle_wood', 'dark_oak_wood']
        selected_woods = random.sample(wood_types, k=random.randint(1, 3))
        
        total_xp = 0
        total_coins = 0
        items_found = {}
        skill_yield_multiplier = 1.0
        skill_drop_multiplier = 1.0
        foraging_level = 0
        tool_bonuses_display = None
        
        for wood_type in selected_woods:
            result = await GatheringSystem.chop_tree(self.bot.db, interaction.user.id, wood_type, event_bonuses)
            
            if result['success']:
                skill_yield_multiplier = result.get('skill_yield_multiplier', 1.0)
                skill_drop_multiplier = result.get('skill_drop_multiplier', 1.0)
                foraging_level = result.get('skill_level', 0)
                if not tool_bonuses_display and 'tool_bonuses' in result:
                    tool_bonuses_display = result['tool_bonuses']
                
                for drop in result['drops']:
                    item_id = drop['item_id']
                    amount = int(drop['amount'] * multiplier * event_multiplier)
                    amount = max(1, amount)
                    
                    await self.bot.db.add_item_to_inventory(interaction.user.id, item_id, amount)
                    await self.bot.db.update_collection(interaction.user.id, item_id, amount)
                    
                    item_name = item_id.replace('_', ' ').title()
                    items_found[item_name] = items_found.get(item_name, 0) + amount
                
                xp_gained = int(result['xp'] * event_multiplier)
                total_xp += xp_gained
                total_coins += int(xp_gained * 0.6)
        
        total_xp = int(total_xp * xp_multiplier)
        total_coins = int(total_coins * coin_multiplier)
        
        skills = await self.bot.db.get_skills(interaction.user.id)
        foraging_skill = next((s for s in skills if s['skill_name'] == 'foraging'), None)
        new_level = foraging_skill['level'] if foraging_skill else 0
        if foraging_skill:
            new_xp = foraging_skill['xp'] + total_xp
            new_level = await self.bot.game_data.calculate_level_from_xp('foraging', new_xp)
            await self.bot.db.update_skill(interaction.user.id, 'foraging', xp=new_xp, level=new_level)
        
        await AchievementSystem.check_skill_achievements(self.bot.db, interaction, interaction.user.id, 'foraging', new_level)
        
        from utils.systems.badge_system import BadgeSystem
        await BadgeSystem.check_and_unlock_badges(self.bot.db, interaction.user.id, 'skill', skill_name='foraging', level=new_level)
        if new_level >= 50:
            await BadgeSystem.check_and_unlock_badges(self.bot.db, interaction.user.id, 'skill_50')
        await self.bot.player_manager.add_coins(interaction.user.id, total_coins)
        embed = discord.Embed(
            title="🪓 Foraging Session Complete!",
            description=f"Using **{tool_id.replace('_', ' ').title()}** ({multiplier * event_multiplier:.1f}x efficiency)\n**Foraging Level {foraging_level}** ({skill_yield_multiplier:.2f}x yield, {skill_drop_multiplier:.2f}x drops)\nYou went foraging and found:",
            color=discord.Color.dark_green()
        )
        
        if tool_bonuses_display:
            tool_bonus_text = []
            if tool_bonuses_display.get('fortune', 0) > 0:
                tool_bonus_text.append(f"+{int(tool_bonuses_display['fortune'])} Foraging Fortune")
            if tool_bonuses_display.get('yield_multiplier', 1.0) > 1.0:
                tool_bonus_text.append(f"{tool_bonuses_display['yield_multiplier']:.2f}x Wood Yield")
            if tool_bonus_text:
                current_desc = embed.description or ""
                embed.description = f"{current_desc}\n🔧 **Tool Bonuses:** {' • '.join(tool_bonus_text)}"

        active_events = await self.event_effects.get_active_events()
        if active_events and (event_multiplier > 1.0 or xp_multiplier > 1.0 or coin_multiplier > 1.0 or fortune_bonus > 0):
            event_text = "🎪 **Active Event Bonuses:** "
            bonuses = []
            if event_multiplier > 1.0:
                bonuses.append(f"+{int((event_multiplier - 1) * 100)}% gathering")
            if fortune_bonus > 0:
                bonuses.append(f"+{fortune_bonus} foraging fortune")
            if xp_multiplier > 1.0:
                bonuses.append(f"+{int((xp_multiplier - 1) * 100)}% XP")
            if coin_multiplier > 1.0:
                bonuses.append(f"+{int((coin_multiplier - 1) * 100)}% coins")
            current_desc = embed.description or ""
            embed.description = f"{current_desc}\n{event_text}{', '.join(bonuses)}"
        if len(items_found.items()) != 0:
            for item_name, amount in list(items_found.items())[:10]:
                embed.add_field(name=item_name, value=f"{amount}x", inline=True)
        else:
            embed.add_field(name="No Wood Found", value="Better luck next time!", inline=False)
        embed.add_field(name="💰 Coins Earned", value=f"+{total_coins} coins", inline=False)
        embed.add_field(name="⭐ Foraging XP", value=f"+{total_xp} XP", inline=False)
        embed.add_field(name="Current Level", value=f"Foraging {new_level}", inline=False)
        await interaction.followup.send(embed=embed)

    @app_commands.command(name="taming", description="Level up your taming!")
    async def taming(self, interaction: discord.Interaction):
        await interaction.response.defer()
        player = await self.bot.player_manager.get_or_create_player(
            interaction.user.id, interaction.user.name
        )
        player_stats = await StatCalculator.calculate_player_stats(self.bot.db, self.bot.game_data, interaction.user.id)
        pet_luck = player_stats.get('pet_luck', 0)
        xp_gained = random.randint(10, 45)
        xp_multiplier = await self.event_effects.get_xp_multiplier('taming')
        xp_gained = int(xp_gained * xp_multiplier)
        xp_gained = int(xp_gained * (1 + pet_luck / 100))
        skills = await self.bot.db.get_skills(interaction.user.id)
        taming_skill = next((s for s in skills if s['skill_name'] == 'taming'), None)
        new_level = taming_skill['level'] if taming_skill else 0
        if taming_skill:
            new_xp = taming_skill['xp'] + xp_gained
            new_level = await self.bot.game_data.calculate_level_from_xp('taming', new_xp)
            await self.bot.db.update_skill(interaction.user.id, 'taming', xp=new_xp, level=new_level)
        
        await AchievementSystem.check_skill_achievements(self.bot.db, interaction, interaction.user.id, 'taming', new_level)
        
        from utils.systems.badge_system import BadgeSystem
        await BadgeSystem.check_and_unlock_badges(self.bot.db, interaction.user.id, 'skill', skill_name='taming', level=new_level)
        if new_level >= 50:
            await BadgeSystem.check_and_unlock_badges(self.bot.db, interaction.user.id, 'skill_50')
        embed = discord.Embed(
            title="🐾 Taming Training!",
            description=f"You spent time with your pets!",
            color=discord.Color.purple()
        )
        if xp_multiplier > 1.0:
            event_text = f"🎪 **Active Event Bonuses:** +{int((xp_multiplier - 1) * 100)}% XP"
            current_desc = embed.description or ""
            embed.description = f"{current_desc}\n{event_text}"
        embed.add_field(name="⭐ Taming XP", value=f"+{xp_gained} XP", inline=False)
        embed.add_field(name="🍀 Pet Luck Bonus", value=f"{pet_luck:.1f}%", inline=False)
        await interaction.followup.send(embed=embed)


async def setup(bot):
    await bot.add_cog(GatheringCommands(bot))
