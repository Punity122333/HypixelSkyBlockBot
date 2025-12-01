import discord
from discord.ext import commands
from discord import app_commands
import random
from utils.stat_calculator import StatCalculator
from utils.systems.gathering_system import GatheringSystem
from utils.compat import roll_loot as compat_roll_loot, check_sea_creature_spawn
from utils.event_effects import EventEffects

class GatheringCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.event_effects = EventEffects(bot)

    @app_commands.command(name="mine", description="Go mining and collect resources")
    async def mine(self, interaction: discord.Interaction):
        await interaction.response.defer()
        has_pickaxe, tool_id = await self.bot.db.has_tool(interaction.user.id, 'pickaxe')
        if not has_pickaxe:
            embed = discord.Embed(
                title="❌ No Pickaxe!",
                description="You need a pickaxe to mine! Use `/begin` to get started, or `/craft` to make a better pickaxe.",
                color=discord.Color.red()
            )
            await interaction.followup.send(embed=embed)
            return
        import time
        progression = await self.bot.db.get_player_progression(interaction.user.id)
        if not progression or not progression.get('first_mine_date'):
            await self.bot.db.update_progression(
                interaction.user.id,
                first_mine_date=int(time.time())
            )
            from utils.achievement_tracker import AchievementTracker
            achievement = await AchievementTracker.unlock_achievement(self.bot.db, interaction.user.id, 'first_mine')
        
        event_multiplier = await self.event_effects.get_gathering_multiplier()
        xp_multiplier = await self.event_effects.get_xp_multiplier('mining')
        coin_multiplier = await self.event_effects.get_coin_multiplier()
        multiplier = await self.bot.db.get_tool_multiplier(interaction.user.id, 'pickaxe')
        
        ore_types = ['cobblestone', 'coal', 'iron_ingot', 'gold_ingot', 'diamond']
        selected_ores = random.sample(ore_types, k=random.randint(1, 3))
        
        total_xp = 0
        total_coins = 0
        items_found = {}
        skill_yield_multiplier = 1.0
        skill_drop_multiplier = 1.0
        mining_level = 0
        
        for ore_type in selected_ores:
            result = await GatheringSystem.mine_block(self.bot.db, interaction.user.id, ore_type)
            
            if result['success']:
                skill_yield_multiplier = result.get('skill_yield_multiplier', 1.0)
                skill_drop_multiplier = result.get('skill_drop_multiplier', 1.0)
                mining_level = result.get('skill_level', 0)
                
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
        mining_skill = next((s for s in skills if s['skill_name'] == 'mining'), None)
        new_level = mining_skill['level'] if mining_skill else 0
        if mining_skill:
            new_xp = mining_skill['xp'] + total_xp
            new_level = await self.bot.game_data.calculate_level_from_xp('mining', new_xp)
            await self.bot.db.update_skill(interaction.user.id, 'mining', xp=new_xp, level=new_level)
            from utils.achievement_tracker import AchievementTracker
            skill_achievements = await AchievementTracker.check_and_unlock_skill(self.bot.db, interaction.user.id, 'mining', new_level)
        await self.bot.player_manager.add_coins(interaction.user.id, total_coins)
        player_data = await self.bot.db.get_player(interaction.user.id)
        if player_data:
            await self.bot.db.update_player(
                interaction.user.id,
                total_earned=player_data.get('total_earned', 0) + total_coins,
                coins=player_data.get('coins', 0) + total_coins
            )
        embed = discord.Embed(
            title="⛏️ Mining Session Complete!",
            description=f"Using **{tool_id.replace('_', ' ').title()}** ({multiplier * event_multiplier:.1f}x efficiency)\n**Mining Level {mining_level}** ({skill_yield_multiplier:.2f}x yield, {skill_drop_multiplier:.2f}x drops)\nYou went mining and found:",
            color=discord.Color.blue()
        )
        if event_multiplier > 1.0 or xp_multiplier > 1.0 or coin_multiplier > 1.0:
            event_text = "🎪 **Active Event Bonuses:** "
            bonuses = []
            if event_multiplier > 1.0:
                bonuses.append(f"+{int((event_multiplier - 1) * 100)}% gathering")
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
            embed.add_field(name="No Ores Found", value="Better luck next time!", inline=False)
        embed.add_field(name="💰 Coins Earned", value=f"+{total_coins} coins", inline=False)
        embed.add_field(name="⭐ Mining XP", value=f"+{total_xp} XP", inline=False)
        embed.add_field(name="Current Level", value=f"Mining {new_level}", inline=False)
        await interaction.followup.send(embed=embed)

    @app_commands.command(name="farm", description="Farm crops")
    async def farm(self, interaction: discord.Interaction):
        await interaction.response.defer()
        has_hoe, tool_id = await self.bot.db.has_tool(interaction.user.id, 'hoe')
        if not has_hoe:
            embed = discord.Embed(
                title="❌ No Hoe!",
                description="You need a hoe to farm! Use `/begin` to get started, or `/craft` to make a better hoe.",
                color=discord.Color.red()
            )
            await interaction.followup.send(embed=embed)
            return
        import time
        progression = await self.bot.db.get_player_progression(interaction.user.id)
        if not progression or not progression.get('first_farm_date'):
            await self.bot.db.update_progression(
                interaction.user.id,
                first_farm_date=int(time.time())
            )
            from utils.achievement_tracker import AchievementTracker
            achievement = await AchievementTracker.unlock_achievement(self.bot.db, interaction.user.id, 'first_farm')
        
        event_multiplier = await self.event_effects.get_gathering_multiplier()
        xp_multiplier = await self.event_effects.get_xp_multiplier('farming')
        coin_multiplier = await self.event_effects.get_coin_multiplier()
        multiplier = await self.bot.db.get_tool_multiplier(interaction.user.id, 'hoe')
        
        crop_types = ['wheat', 'carrot', 'potato', 'pumpkin', 'melon']
        selected_crops = random.sample(crop_types, k=random.randint(1, 3))
        
        total_xp = 0
        total_coins = 0
        items_found = {}
        skill_yield_multiplier = 1.0
        skill_drop_multiplier = 1.0
        farming_level = 0
        
        for crop_type in selected_crops:
            result = await GatheringSystem.harvest_crop(self.bot.db, interaction.user.id, crop_type)
            
            if result['success']:
                skill_yield_multiplier = result.get('skill_yield_multiplier', 1.0)
                skill_drop_multiplier = result.get('skill_drop_multiplier', 1.0)
                farming_level = result.get('skill_level', 0)
                
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
            from utils.achievement_tracker import AchievementTracker
            skill_achievements = await AchievementTracker.check_and_unlock_skill(self.bot.db, interaction.user.id, 'farming', new_level)
        await self.bot.player_manager.add_coins(interaction.user.id, total_coins)
        player_data = await self.bot.db.get_player(interaction.user.id)
        if player_data:
            await self.bot.db.update_player(
                interaction.user.id,
                total_earned=player_data.get('total_earned', 0) + total_coins,
                coins=player_data.get('coins', 0) + total_coins
            )
        embed = discord.Embed(
            title="🚜 Farming Session Complete!",
            description=f"Using **{tool_id.replace('_', ' ').title()}** ({multiplier * event_multiplier:.1f}x efficiency)\n**Farming Level {farming_level}** ({skill_yield_multiplier:.2f}x yield, {skill_drop_multiplier:.2f}x drops)\nYou went farming and found:",
            color=discord.Color.green()
        )
        if event_multiplier > 1.0 or xp_multiplier > 1.0 or coin_multiplier > 1.0:
            event_text = "🎪 **Active Event Bonuses:** "
            bonuses = []
            if event_multiplier > 1.0:
                bonuses.append(f"+{int((event_multiplier - 1) * 100)}% gathering")
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
        has_rod, tool_id = await self.bot.db.has_tool(interaction.user.id, 'fishing_rod')
        if not has_rod:
            embed = discord.Embed(
                title="❌ No Fishing Rod!",
                description="You need a fishing rod to fish! Use `/begin` to get started or `/craft` to craft one.",
                color=discord.Color.red()
            )
            await interaction.followup.send(embed=embed)
            return
        
        xp_multiplier = await self.event_effects.get_xp_multiplier('fishing')
        coin_multiplier = await self.event_effects.get_coin_multiplier()
        
        result = await GatheringSystem.fish(self.bot.db, interaction.user.id)
        
        if not result['success']:
            await interaction.followup.send(f"❌ {result.get('error', 'Failed to fish')}", ephemeral=True)
            return
        
        total_xp = int(result['xp'] * xp_multiplier)
        total_coins = int(result['xp'] * 3 * coin_multiplier)
        
        catch = result['catch']
        is_sea_creature = result['is_sea_creature']
        fishing_level = result.get('skill_level', 0)
        skill_speed_multiplier = result.get('skill_speed_multiplier', 1.0)
        
        if is_sea_creature:
            embed = discord.Embed(
                title="🐟 Sea Creature Caught!",
                description=f"A **{catch['creature_id'].replace('_', ' ').title()}** appeared!",
                color=discord.Color.dark_blue()
            )
            embed.add_field(name="Health", value=f"{catch['health']} HP", inline=True)
            embed.add_field(name="Reward", value=f"{catch['coins']} coins", inline=True)
            total_coins += catch['coins']
            total_xp += catch['xp']
        else:
            await self.bot.db.add_item_to_inventory(interaction.user.id, catch['item_id'], catch['amount'])
            await self.bot.db.update_collection(interaction.user.id, catch['item_id'], catch['amount'])
            
            embed = discord.Embed(
                title="🎣 Fishing Session Complete!",
                description=f"Using **{tool_id.replace('_', ' ').title()}**\n**Fishing Level {fishing_level}** ({skill_speed_multiplier:.2f}x speed bonus)\nYou caught:",
                color=discord.Color.blue()
            )
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
        await self.bot.player_manager.add_coins(interaction.user.id, total_coins)
        player_data = await self.bot.db.get_player(interaction.user.id)
        if player_data:
            await self.bot.db.update_player(
                interaction.user.id,
                total_earned=player_data.get('total_earned', 0) + total_coins,
                coins=player_data.get('coins', 0) + total_coins
            )
        if xp_multiplier > 1.0 or coin_multiplier > 1.0:
            event_text = "🎪 **Active Event Bonuses:** "
            bonuses = []
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
        has_axe, tool_id = await self.bot.db.has_tool(interaction.user.id, 'axe')
        if not has_axe:
            embed = discord.Embed(
                title="❌ No Axe!",
                description="You need an axe to chop trees! Use `/begin` to get started or `/craft` to make one.",
                color=discord.Color.red()
            )
            await interaction.followup.send(embed=embed)
            return
        
        event_multiplier = await self.event_effects.get_gathering_multiplier()
        xp_multiplier = await self.event_effects.get_xp_multiplier('foraging')
        coin_multiplier = await self.event_effects.get_coin_multiplier()
        multiplier = await self.bot.db.get_tool_multiplier(interaction.user.id, 'axe')
        
        wood_types = ['oak_wood', 'jungle_wood', 'dark_oak_wood']
        selected_woods = random.sample(wood_types, k=random.randint(1, 3))
        
        total_xp = 0
        total_coins = 0
        items_found = {}
        skill_yield_multiplier = 1.0
        skill_drop_multiplier = 1.0
        foraging_level = 0
        
        for wood_type in selected_woods:
            result = await GatheringSystem.chop_tree(self.bot.db, interaction.user.id, wood_type)
            
            if result['success']:
                skill_yield_multiplier = result.get('skill_yield_multiplier', 1.0)
                skill_drop_multiplier = result.get('skill_drop_multiplier', 1.0)
                foraging_level = result.get('skill_level', 0)
                
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
        await self.bot.player_manager.add_coins(interaction.user.id, total_coins)
        player_data = await self.bot.db.get_player(interaction.user.id)
        if player_data:
            await self.bot.db.update_player(
                interaction.user.id,
                total_earned=player_data.get('total_earned', 0) + total_coins,
                coins=player_data.get('coins', 0) + total_coins
            )
        embed = discord.Embed(
            title="🪓 Foraging Session Complete!",
            description=f"Using **{tool_id.replace('_', ' ').title()}** ({multiplier * event_multiplier:.1f}x efficiency)\n**Foraging Level {foraging_level}** ({skill_yield_multiplier:.2f}x yield, {skill_drop_multiplier:.2f}x drops)\nYou went foraging and found:",
            color=discord.Color.dark_green()
        )
        if event_multiplier > 1.0 or xp_multiplier > 1.0 or coin_multiplier > 1.0:
            event_text = "🎪 **Active Event Bonuses:** "
            bonuses = []
            if event_multiplier > 1.0:
                bonuses.append(f"+{int((event_multiplier - 1) * 100)}% gathering")
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
        if taming_skill:
            new_xp = taming_skill['xp'] + xp_gained
            new_level = await self.bot.game_data.calculate_level_from_xp('taming', new_xp)
            await self.bot.db.update_skill(interaction.user.id, 'taming', xp=new_xp, level=new_level)
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
