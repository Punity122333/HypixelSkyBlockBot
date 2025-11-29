import discord
from discord.ext import commands
from discord import app_commands
import random
from utils.stat_calculator import StatCalculator
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
        
        player_stats = await StatCalculator.calculate_player_stats(self.bot.db, self.bot.game_data, interaction.user.id)
        gathering_effects = StatCalculator.apply_gathering_effects(player_stats, 'pickaxe')
        
        event_multiplier = await self.event_effects.get_gathering_multiplier()
        xp_multiplier = await self.event_effects.get_xp_multiplier('mining')
        coin_multiplier = await self.event_effects.get_coin_multiplier()
        
        multiplier = await self.bot.db.get_tool_multiplier(interaction.user.id, 'pickaxe')
        total_efficiency = multiplier * (1 + gathering_effects['speed_bonus'] / 100) * event_multiplier
        
        player = await self.bot.player_manager.get_or_create_player(
            interaction.user.id, interaction.user.name
        )
        
        ores_from_db = await self.bot.game_data.get_gathering_drops('mining', 'ore')
        
        if not ores_from_db:
            ores = [
                ('cobblestone', 'Cobblestone', 4, 12, 5),
                ('coal', 'Coal', 4, 12, 5),
                ('iron', 'Iron', 4, 12, 5),
            ]
        else:
            ores = []
            for ore_data in ores_from_db:
                item_id = ore_data['item_id']
                item_name = item_id.replace('_', ' ').title()
                min_amt = ore_data['min_amt']
                max_amt = ore_data['max_amt']
                xp = 5
                ores.append((item_id, item_name, 4, 12, xp))
        
        total_xp = 0
        total_coins = 0
        items_found = {}
        
        for ore, ore_name, min_amt, max_amt, xp in ores:
            if random.random() > 0.3:
                base_amount = random.randint(min_amt, max_amt)
                fortune_multiplier = 1 + (gathering_effects['fortune_bonus'] / 100)
                amount = int(base_amount * fortune_multiplier * total_efficiency)
                amount = max(1, amount)
                await self.bot.db.add_item_to_inventory(interaction.user.id, ore, amount)
                await self.bot.db.update_collection(interaction.user.id, ore, amount)
                items_found[ore_name] = amount
                total_xp += int(5 * amount * total_efficiency)
                total_coins += int(3 * amount * total_efficiency)
        
        total_xp = int(total_xp * xp_multiplier)
        total_coins = int(total_coins * coin_multiplier)
        
        skills = await self.bot.db.get_skills(interaction.user.id)
        mining_skill = next((s for s in skills if s['skill_name'] == 'mining'), None)
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
            description=f"Using **{tool_id.replace('_', ' ').title()}** ({total_efficiency:.1f}x efficiency)\nYou went mining and found:",
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
        
        player_stats = await StatCalculator.calculate_player_stats(self.bot.db, self.bot.game_data, interaction.user.id)
        gathering_effects = StatCalculator.apply_gathering_effects(player_stats, 'hoe')
        
        event_multiplier = await self.event_effects.get_gathering_multiplier()
        xp_multiplier = await self.event_effects.get_xp_multiplier('farming')
        coin_multiplier = await self.event_effects.get_coin_multiplier()
        
        multiplier = await self.bot.db.get_tool_multiplier(interaction.user.id, 'hoe')
        total_efficiency = multiplier * (1 + gathering_effects['speed_bonus'] / 100) * event_multiplier
        
        player = await self.bot.player_manager.get_or_create_player(
            interaction.user.id, interaction.user.name
        )
        
        crops_from_db = await self.bot.game_data.get_gathering_drops('farming', 'crop')
        
        if not crops_from_db:
            crops = [
                ('wheat', 'Wheat', 4, 12, 5),
                ('carrot', 'Carrot', 4, 12, 5),
                ('potato', 'Potato', 4, 12, 5),
            ]
        else:
            crops = []
            for crop_data in crops_from_db:
                item_id = crop_data['item_id']
                item_name = item_id.replace('_', ' ').title()
                min_amt = crop_data['min_amt']
                max_amt = crop_data['max_amt']
                xp = 5
                crops.append((item_id, item_name, 4, 12, xp))
        
        total_xp = 0
        total_coins = 0
        items_found = {}
        
        for item_id, item_name, min_amt, max_amt, xp in crops:
            if random.random() > 0.4:
                base_amount = random.randint(min_amt, max_amt)
                fortune_multiplier = 1 + (gathering_effects['fortune_bonus'] / 100)
                amount = int(base_amount * fortune_multiplier * total_efficiency)
                amount = max(1, amount)
                await self.bot.db.add_item_to_inventory(interaction.user.id, item_id, amount)
                await self.bot.db.update_collection(interaction.user.id, item_name, amount)
                items_found[item_name] = amount
                total_xp += int(5 * amount * total_efficiency)
                total_coins += int(3 * amount * total_efficiency)
        
        total_xp = int(total_xp * xp_multiplier)
        total_coins = int(total_coins * coin_multiplier)
        
        skills = await self.bot.db.get_skills(interaction.user.id)
        farming_skill = next((s for s in skills if s['skill_name'] == 'farming'), None)
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
            description=f"Using **{tool_id.replace('_', ' ').title()}** ({total_efficiency:.1f}x efficiency)\nYou went farming and found:",
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
        
        player_stats = await StatCalculator.calculate_player_stats(self.bot.db, self.bot.game_data, interaction.user.id)
        gathering_effects = StatCalculator.apply_gathering_effects(player_stats, 'fishing_rod')
        
        xp_multiplier = await self.event_effects.get_xp_multiplier('fishing')
        coin_multiplier = await self.event_effects.get_coin_multiplier()
        
        multiplier = await self.bot.db.get_tool_multiplier(interaction.user.id, 'fishing_rod')
        
        player = await self.bot.player_manager.get_or_create_player(
            interaction.user.id, interaction.user.name
        )
        
        total_xp = 0
        total_coins = 0
        items_found = {}
        
        sea_creature_chance = gathering_effects.get('sea_creature_chance', 0)
        magic_find = player_stats.get('magic_find', 0)
        
        if check_sea_creature_spawn(sea_creature_chance):
            loot_table = await self.bot.game_data.get_loot_table('sea_creature', 'fishing')
            if not loot_table:
                loot_table = {}
            drops = await compat_roll_loot(self.bot.game_data, loot_table, magic_find)
            
            embed = discord.Embed(
                title="🐟 Sea Creature Caught!",
                description=f"A sea creature appeared! (Sea Creature Chance: {sea_creature_chance:.1f}%)",
                color=discord.Color.dark_blue()
            )
            
            for item_id, amount in drops:
                await self.bot.db.add_item_to_inventory(interaction.user.id, item_id, amount)
                items_found[item_id] = amount
                total_xp += 250 * amount
                total_coins += 150 * amount
            
            for item_id, amount in items_found.items():
                embed.add_field(name=item_id.replace('_', ' ').title(), value=f"{amount}x", inline=True)
        else:
            loot_table = await self.bot.game_data.get_loot_table('normal', 'fishing')
            if not loot_table:
                loot_table = {}
            
            fortune_multiplier = 1 + (gathering_effects['fortune_bonus'] / 100)
            total_efficiency = multiplier * (1 + gathering_effects['speed_bonus'] / 100)
            for _ in range(random.randint(3, 8)):
                drops = await compat_roll_loot(self.bot.game_data, loot_table, magic_find)
                for item_id, amount in drops:
                    amount = int(amount * fortune_multiplier * total_efficiency)
                    if amount > 0:
                        await self.bot.db.add_item_to_inventory(interaction.user.id, item_id, amount)
                        await self.bot.db.update_collection(interaction.user.id, item_id, amount)
                        items_found[item_id] = items_found.get(item_id, 0) + amount
                        total_xp += int(5 * amount * total_efficiency)
                        total_coins += int(3 * amount * total_efficiency)
            
            embed = discord.Embed(
                title="🎣 Fishing Session Complete!",
                description=f"Using **{tool_id.replace('_', ' ').title()}**\nFishing Speed: +{gathering_effects['speed_bonus']}\nSea Creature Chance: {sea_creature_chance:.1f}%\nYou caught:",
                color=discord.Color.blue()
            )
            
            for item_id, amount in list(items_found.items())[:10]:
                embed.add_field(name=item_id.replace('_', ' ').title(), value=f"{amount}x", inline=True)
        
        skills = await self.bot.db.get_skills(interaction.user.id)
        fishing_skill = next((s for s in skills if s['skill_name'] == 'fishing'), None)
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
        
        player_stats = await StatCalculator.calculate_player_stats(self.bot.db, self.bot.game_data, interaction.user.id)
        gathering_effects = StatCalculator.apply_gathering_effects(player_stats, 'axe')
        
        event_multiplier = await self.event_effects.get_gathering_multiplier()
        xp_multiplier = await self.event_effects.get_xp_multiplier('foraging')
        coin_multiplier = await self.event_effects.get_coin_multiplier()
        
        multiplier = await self.bot.db.get_tool_multiplier(interaction.user.id, 'axe')
        total_efficiency = multiplier * (1 + gathering_effects['speed_bonus'] / 100) * event_multiplier
        
        player = await self.bot.player_manager.get_or_create_player(
            interaction.user.id, interaction.user.name
        )
        
        wood_types_from_db = await self.bot.game_data.get_gathering_drops('foraging', 'wood')
        
        if not wood_types_from_db:
            wood_types = [
                ('oak_wood', 'Oak Wood', 4, 12, 5),
                ('jungle_wood', 'Jungle Wood', 4, 12, 5),
            ]
        else:
            wood_types = []
            for wood_data in wood_types_from_db:
                item_id = wood_data['item_id']
                item_name = item_id.replace('_', ' ').title()
                min_amt = wood_data['min_amt']
                max_amt = wood_data['max_amt']
                xp = 5
                wood_types.append((item_id, item_name, 4, 12, xp))
        
        total_xp = 0
        total_coins = 0
        items_found = {}
        
        for item_id, item_name, min_amt, max_amt, xp in wood_types:
            if random.random() > 0.4:
                base_amount = random.randint(min_amt, max_amt)
                fortune_multiplier = 1 + (gathering_effects['fortune_bonus'] / 100)
                amount = int(base_amount * fortune_multiplier * total_efficiency)
                amount = max(1, amount)
                await self.bot.db.add_item_to_inventory(interaction.user.id, item_id, amount)
                await self.bot.db.update_collection(interaction.user.id, item_name, amount)
                items_found[item_name] = amount
                total_xp += int(5 * amount * total_efficiency)
                total_coins += int(3 * amount * total_efficiency)
        
        total_xp = int(total_xp * xp_multiplier)
        total_coins = int(total_coins * coin_multiplier)
        
        skills = await self.bot.db.get_skills(interaction.user.id)
        foraging_skill = next((s for s in skills if s['skill_name'] == 'foraging'), None)
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
            description=f"Using **{tool_id.replace('_', ' ').title()}** ({total_efficiency:.1f}x efficiency)\nYou went foraging and found:",
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
        
        await interaction.followup.send(embed=embed)
    
    @app_commands.command(name="taming", description="Level up your taming!")
    async def taming(self, interaction: discord.Interaction):
        await interaction.response.defer()
        
        player = await self.bot.player_manager.get_or_create_player(
            interaction.user.id, interaction.user.name
        )
        
        xp_gained = random.randint(10, 45)
        
        xp_multiplier = await self.event_effects.get_xp_multiplier('taming')
        xp_gained = int(xp_gained * xp_multiplier)
        
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
        
        await interaction.followup.send(embed=embed)


async def setup(bot):
    await bot.add_cog(GatheringCommands(bot))
