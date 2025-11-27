import discord
from discord.ext import commands
from discord import app_commands
import random
from utils.stat_calculator import StatCalculator
from utils.compat import roll_loot as compat_roll_loot, check_sea_creature_spawn

class GatheringCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

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
        
        player_stats = await StatCalculator.calculate_player_stats(self.bot.db, self.bot.game_data, interaction.user.id)
        gathering_effects = StatCalculator.apply_gathering_effects(player_stats, 'pickaxe')
        
        multiplier = await self.bot.db.get_tool_multiplier(interaction.user.id, 'pickaxe')
        total_efficiency = multiplier * (1 + gathering_effects['speed_bonus'] / 100)
        
        player = await self.bot.player_manager.get_or_create_player(
            interaction.user.id, interaction.user.name
        )
        
        ore_types = ['cobblestone', 'coal', 'iron', 'gold', 'diamond']
        if player_stats.get('mining_speed', 0) > 100:
            ore_types.extend(['emerald', 'mithril'])
        
        total_xp = 0
        total_coins = 0
        items_found = {}
        fortune = int(gathering_effects['fortune_bonus'])
        
        for ore_type in ore_types:
            loot_table = await self.bot.game_data.get_loot_table(ore_type, 'mining')
            if loot_table:
                magic_find = player_stats.get('magic_find', 0)
                
                drops = await compat_roll_loot(self.bot.game_data, loot_table, magic_find, fortune)
                for item_id, amount in drops:
                    amount = int(amount * total_efficiency)
                    if amount > 0:
                        await self.bot.db.add_item_to_inventory(interaction.user.id, item_id, amount)
                        await self.bot.db.update_collection(interaction.user.id, item_id, amount)
                        items_found[item_id] = items_found.get(item_id, 0) + amount
                        total_xp += amount * 5
                        total_coins += amount * 2
        
        skills = await self.bot.db.get_skills(interaction.user.id)
        mining_skill = next((s for s in skills if s['skill_name'] == 'mining'), None)
        if mining_skill:
            new_xp = mining_skill['xp'] + total_xp
            new_level = await self.bot.game_data.calculate_level_from_xp('mining', new_xp)
            await self.bot.db.update_skill(interaction.user.id, 'mining', xp=new_xp, level=new_level)
        
        await self.bot.player_manager.add_coins(interaction.user.id, total_coins)
        
        player_data = await self.bot.db.get_player(interaction.user.id)
        if player_data:
            await self.bot.db.update_player(interaction.user.id, total_earned=player_data.get('total_earned', 0) + total_coins)
        
        embed = discord.Embed(
            title="⛏️ Mining Session Complete!",
            description=f"Using **{tool_id.replace('_', ' ').title()}** ({total_efficiency:.1f}x efficiency)\nMining Fortune: +{fortune}\nYou went mining and found:",
            color=discord.Color.blue()
        )
        
        for item_id, amount in list(items_found.items())[:10]:
            embed.add_field(name=item_id.replace('_', ' ').title(), value=f"{amount}x", inline=True)
        
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
        
        player_stats = await StatCalculator.calculate_player_stats(self.bot.db, self.bot.game_data, interaction.user.id)
        gathering_effects = StatCalculator.apply_gathering_effects(player_stats, 'hoe')
        
        multiplier = await self.bot.db.get_tool_multiplier(interaction.user.id, 'hoe')
        total_efficiency = multiplier * (1 + gathering_effects['speed_bonus'] / 100)
        
        player = await self.bot.player_manager.get_or_create_player(
            interaction.user.id, interaction.user.name
        )
        
        crop_types = ['wheat', 'carrot', 'potato', 'sugar_cane', 'pumpkin', 'melon']
        
        total_xp = 0
        total_coins = 0
        items_found = {}
        fortune = int(gathering_effects['fortune_bonus'])
        
        for crop_type in crop_types:
            loot_table = await self.bot.game_data.get_loot_table(crop_type, 'farming')
            if loot_table:
                magic_find = player_stats.get('magic_find', 0)
                
                drops = await compat_roll_loot(self.bot.game_data, loot_table, magic_find, fortune)
                for item_id, amount in drops:
                    amount = int(amount * total_efficiency)
                    if amount > 0:
                        await self.bot.db.add_item_to_inventory(interaction.user.id, item_id, amount)
                        await self.bot.db.update_collection(interaction.user.id, item_id, amount)
                        items_found[item_id] = items_found.get(item_id, 0) + amount
                        total_xp += amount * 4
                        total_coins += amount * 2
        
        skills = await self.bot.db.get_skills(interaction.user.id)
        farming_skill = next((s for s in skills if s['skill_name'] == 'farming'), None)
        if farming_skill:
            new_xp = farming_skill['xp'] + total_xp
            new_level = await self.bot.game_data.calculate_level_from_xp('farming', new_xp)
            await self.bot.db.update_skill(interaction.user.id, 'farming', xp=new_xp, level=new_level)
        
        await self.bot.player_manager.add_coins(interaction.user.id, total_coins)
        
        player_data = await self.bot.db.get_player(interaction.user.id)
        if player_data:
            await self.bot.db.update_player(interaction.user.id, total_earned=player_data.get('total_earned', 0) + total_coins)
        
        embed = discord.Embed(
            title="🌾 Farming Session Complete!",
            description=f"Using **{tool_id.replace('_', ' ').title()}** ({total_efficiency:.1f}x efficiency)\nFarming Fortune: +{fortune}\nYou harvested crops:",
            color=discord.Color.green()
        )
        
        for item_id, amount in list(items_found.items())[:10]:
            embed.add_field(name=item_id.replace('_', ' ').title(), value=f"{amount}x", inline=True)
        
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
                total_xp += amount * 50
                total_coins += amount * 100
            
            for item_id, amount in items_found.items():
                embed.add_field(name=item_id.replace('_', ' ').title(), value=f"{amount}x", inline=True)
        else:
            loot_table = await self.bot.game_data.get_loot_table('normal', 'fishing')
            if not loot_table:
                loot_table = {}
            
            for _ in range(random.randint(3, 8)):
                drops = await compat_roll_loot(self.bot.game_data, loot_table, magic_find)
                for item_id, amount in drops:
                    amount = int(amount * multiplier)
                    if amount > 0:
                        await self.bot.db.add_item_to_inventory(interaction.user.id, item_id, amount)
                        await self.bot.db.update_collection(interaction.user.id, item_id, amount)
                        items_found[item_id] = items_found.get(item_id, 0) + amount
                        total_xp += amount * 5
                        total_coins += amount * 5
            
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
            new_xp = fishing_skill['xp'] + total_xp
            new_level = await self.bot.game_data.calculate_level_from_xp('fishing', new_xp)
            await self.bot.db.update_skill(interaction.user.id, 'fishing', xp=new_xp, level=new_level)
        
        await self.bot.player_manager.add_coins(interaction.user.id, total_coins)
        
        player_data = await self.bot.db.get_player(interaction.user.id)
        if player_data:
            await self.bot.db.update_player(interaction.user.id, total_earned=player_data.get('total_earned', 0) + total_coins)
        
        embed.add_field(name="💰 Coins Earned", value=f"+{total_coins} coins", inline=False)
        embed.add_field(name="⭐ Fishing XP", value=f"+{total_xp} XP", inline=False)
        
        await interaction.followup.send(embed=embed)
        
        embed = discord.Embed(
            title="🎣 Fishing Session Complete!",
            description="You caught:",
            color=discord.Color.blue()
        )
        
        for item_name, amount in items_found.items():
            embed.add_field(name=item_name, value=f"{amount}x", inline=True)
        
        embed.add_field(name="💰 Coins Earned", value=f"+{total_coins} coins", inline=False)
        embed.add_field(name="⭐ Fishing XP", value=f"+{total_xp} XP", inline=False)
        
        await interaction.followup.send(embed=embed)
    
    @app_commands.command(name="forage", description="Chop trees")
    async def forage(self, interaction: discord.Interaction):
        await interaction.response.defer()
        
        player = await self.bot.player_manager.get_or_create_player(
            interaction.user.id, interaction.user.name
        )
        
        woods_from_db = await self.bot.game_data.get_gathering_drops('foraging', 'wood')
        
        if not woods_from_db:
            woods = [
                ('oak_wood', 'Oak Wood', 4, 12, 5),
                ('jungle_wood', 'Jungle Wood', 3, 8, 6),
                ('dark_oak_wood', 'Dark Oak Wood', 2, 6, 7),
            ]
        else:
            woods = []
            for wood_data in woods_from_db:
                item_id = wood_data['item_id']
                item_name = item_id.replace('_', ' ').title()
                min_amt = wood_data['min_amount']
                max_amt = wood_data['max_amount']
                xp = 5
                woods.append((item_id, item_name, min_amt, max_amt, xp))
        
        total_xp = 0
        total_coins = 0
        items_found = {}
        
        for item_id, item_name, min_amt, max_amt, xp in woods:
            if random.random() > 0.4:
                amount = random.randint(min_amt, max_amt)
                await self.bot.db.add_item_to_inventory(interaction.user.id, item_id, amount)
                await self.bot.db.update_collection(interaction.user.id, item_name, amount)
                items_found[item_name] = amount
                total_xp += xp * amount
                total_coins += amount * 3
        
        skills = await self.bot.db.get_skills(interaction.user.id)
        foraging_skill = next((s for s in skills if s['skill_name'] == 'foraging'), None)
        if foraging_skill:
            new_xp = foraging_skill['xp'] + total_xp
            new_level = await self.bot.game_data.calculate_level_from_xp('foraging', new_xp)
            await self.bot.db.update_skill(interaction.user.id, 'foraging', xp=new_xp, level=new_level)
        
        await self.bot.player_manager.add_coins(interaction.user.id, total_coins)
        
        player_data = await self.bot.db.get_player(interaction.user.id)
        if player_data:
            await self.bot.db.update_player(interaction.user.id, total_earned=player_data.get('total_earned', 0) + total_coins)
        
        embed = discord.Embed(
            title="🪓 Foraging Session Complete!",
            description="You chopped wood:",
            color=discord.Color.dark_green()
        )
        
        for item_name, amount in items_found.items():
            embed.add_field(name=item_name, value=f"{amount}x", inline=True)
        
        embed.add_field(name="💰 Coins Earned", value=f"+{total_coins} coins", inline=False)
        embed.add_field(name="⭐ Foraging XP", value=f"+{total_xp} XP", inline=False)
        
        await interaction.followup.send(embed=embed)
    
    
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

    @app_commands.command(name="taming", description="Level up your taming!")
    async def taming(self, interaction: discord.Interaction):
        await interaction.response.defer()
        
        await self.bot.player_manager.get_or_create_player(
            interaction.user.id, interaction.user.name
        )
        
        xp_gained = random.randint(10, 45)
        
        skills = await self.bot.db.get_skills(interaction.user.id)
        taming_skill = next((s for s in skills if s['skill_name'] == 'taming'), None)
        
        if taming_skill:
            new_xp = taming_skill['xp'] + xp_gained
            new_level = await self.bot.game_data.calculate_level_from_xp('taming', new_xp)
            
            await self.bot.db.update_skill(interaction.user.id, 'taming', xp=new_xp, level=new_level)
            
            embed = discord.Embed(
                title="🐾 Taming",
                description=f"You gained taming experience!",
                color=discord.Color.teal()
            )
            embed.add_field(name="XP Gained", value=f"+{xp_gained} Taming XP", inline=True)
            embed.add_field(name="Current Level", value=f"Taming {new_level}", inline=True)
            
            await interaction.followup.send(embed=embed)

async def setup(bot):
    await bot.add_cog(GatheringCommands(bot))
