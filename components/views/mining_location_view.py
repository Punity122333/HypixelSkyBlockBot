import discord
from discord.ui import View, Button


class MiningLocationView(View):
    def __init__(self, bot, user_id):
        super().__init__(timeout=60)
        self.bot = bot
        self.user_id = user_id
        
        normal_button = Button(label="⛏️ Normal Mining", style=discord.ButtonStyle.green, custom_id="mine_normal")
        normal_button.callback = self.mine_normal
        self.add_item(normal_button)
        
        dwarven_button = Button(label="🏔️ Dwarven Mines", style=discord.ButtonStyle.blurple, custom_id="mine_dwarven")
        dwarven_button.callback = self.mine_dwarven
        self.add_item(dwarven_button)
    
    async def mine_normal(self, interaction: discord.Interaction):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("This isn't your menu!", ephemeral=True)
            return
        
        await interaction.response.defer()
        
        from utils.systems.gathering_system import GatheringSystem
        from utils.systems.achievement_system import AchievementSystem
        from utils.event_effects import EventEffects
        from utils.systems.hotm_system import HeartOfTheMountainSystem
        from utils.systems.dwarven_mines_system import DwarvenMinesSystem
        import random
        import time
        
        progression = await self.bot.db.get_player_progression(interaction.user.id)
        if not progression or not progression.get('first_mine_date'):
            await self.bot.db.update_progression(
                interaction.user.id,
                first_mine_date=int(time.time())
            )
            await AchievementSystem.unlock_single_achievement(self.bot.db, interaction, interaction.user.id, 'first_mine')
        
        equipped_items = await self.bot.db.get_equipped_items(interaction.user.id)
        pickaxe = equipped_items.get('pickaxe')
        if not pickaxe:
            await interaction.followup.send("❌ You need to equip a pickaxe to mine!", ephemeral=True)
            return
        
        tool_id = pickaxe['item_id']
        
        event_effects = EventEffects(self.bot)
        active_events = await event_effects.get_active_events()
        event_multiplier = await event_effects.get_gathering_multiplier() if active_events else 1.0
        xp_multiplier = await event_effects.get_xp_multiplier('mining') if active_events else 1.0
        coin_multiplier = await event_effects.get_coin_multiplier() if active_events else 1.0
        fortune_bonus = await event_effects.get_fortune_bonus('mining') if active_events else 0
        multiplier = await self.bot.db.get_tool_multiplier(interaction.user.id, 'pickaxe')
        
        event_bonuses = {}
        if fortune_bonus > 0:
            event_bonuses['mining_fortune'] = fortune_bonus
        
        ore_types = ['coal', 'iron_ingot', 'gold_ingot', 'diamond', 'emerald', 'lapis_lazuli', 'redstone']
        selected_ores = random.sample(ore_types, k=min(3, len(ore_types)))
        
        total_xp = 0
        total_coins = 0
        items_found = {}
        skill_yield_multiplier = 1.0
        skill_drop_multiplier = 1.0
        mining_level = 0
        tool_bonuses_display = None
        
        for ore_type in selected_ores:
            result = await GatheringSystem.mine_block(self.bot.db, interaction.user.id, ore_type, event_bonuses)
            
            if result['success']:
                skill_yield_multiplier = result.get('skill_yield_multiplier', 1.0)
                skill_drop_multiplier = result.get('skill_drop_multiplier', 1.0)
                mining_level = result.get('skill_level', 0)
                if not tool_bonuses_display and 'tool_bonuses' in result:
                    tool_bonuses_display = result['tool_bonuses']
                
                for drop in result['drops']:
                    item_id = drop['item_id']
                    base_amount = drop['amount']
                    amount = int(base_amount * multiplier * event_multiplier)
                    amount = max(1, amount)
                    
                    await self.bot.db.add_item_to_inventory(interaction.user.id, item_id, amount)
                    await self.bot.db.update_collection(interaction.user.id, item_id, amount)
                    
                    item_name = item_id.replace('_', ' ').title()
                    items_found[item_name] = items_found.get(item_name, 0) + amount
                    
                    if item_id in ['lapis_lazuli', 'redstone']:
                        await DwarvenMinesSystem.update_commission_progress(
                            self.bot.db, interaction.user.id, f'{item_id}_mining', amount
                        )
                
                xp_gained = int(result['xp'] * event_multiplier)
                total_xp += xp_gained
                total_coins += int(xp_gained * 0.5)
        
        total_xp = int(total_xp * xp_multiplier)
        total_coins = int(total_coins * coin_multiplier)
        
        skills = await self.bot.db.get_skills(interaction.user.id)
        mining_skill = next((s for s in skills if s['skill_name'] == 'mining'), None)
        new_level = mining_skill['level'] if mining_skill else 0
        
        if mining_skill:
            new_xp = mining_skill['xp'] + total_xp
            new_level = await self.bot.game_data.calculate_level_from_xp('mining', new_xp)
            await self.bot.db.update_skill(interaction.user.id, 'mining', xp=new_xp, level=new_level)
        
        from utils.systems.achievement_system import AchievementSystem
        await AchievementSystem.check_skill_achievements(self.bot.db, interaction, interaction.user.id, 'mining', new_level)
        
        from utils.systems.badge_system import BadgeSystem
        await BadgeSystem.check_and_unlock_badges(self.bot.db, interaction.user.id, 'skill', skill_name='mining', level=new_level)
        if new_level >= 50:
            await BadgeSystem.check_and_unlock_badges(self.bot.db, interaction.user.id, 'skill_50')
        
        hotm_xp = int(total_xp * 0.5)
        hotm_result = await HeartOfTheMountainSystem.add_hotm_xp(self.bot.db, interaction.user.id, hotm_xp)
        
        await self.bot.player_manager.add_coins(interaction.user.id, total_coins)
        
        embed = discord.Embed(
            title="⛏️ Mining Session Complete!",
            description=f"Using **{tool_id.replace('_', ' ').title()}** ({multiplier * event_multiplier:.1f}x efficiency)\n**Mining Level {mining_level}** ({skill_yield_multiplier:.2f}x yield, {skill_drop_multiplier:.2f}x drops)\nYou went mining and found:",
            color=discord.Color.blue()
        )

        if tool_bonuses_display:
            tool_bonus_text = []
            if tool_bonuses_display.get('fortune', 0) > 0:
                tool_bonus_text.append(f"+{int(tool_bonuses_display['fortune'])} Mining Fortune")
            if tool_bonuses_display.get('speed', 0) > 0:
                tool_bonus_text.append(f"+{int(tool_bonuses_display['speed'])} Mining Speed")
            if tool_bonuses_display.get('yield_multiplier', 1.0) > 1.0:
                tool_bonus_text.append(f"{tool_bonuses_display['yield_multiplier']:.2f}x Ore Yield")
            if tool_bonuses_display.get('breaking_power', 0) > 0:
                tool_bonus_text.append(f"+{int(tool_bonuses_display['breaking_power'])} Breaking Power")
            if tool_bonus_text:
                current_desc = embed.description or ""
                embed.description = f"{current_desc}\n🔧 **Tool Bonuses:** {' • '.join(tool_bonus_text)}"

        active_events = await event_effects.get_active_events()
        if active_events and (event_multiplier > 1.0 or xp_multiplier > 1.0 or coin_multiplier > 1.0 or fortune_bonus > 0):
            event_text = "🎪 **Active Event Bonuses:** "
            bonuses = []
            if event_multiplier > 1.0:
                bonuses.append(f"+{int((event_multiplier - 1) * 100)}% gathering")
            if fortune_bonus > 0:
                bonuses.append(f"+{fortune_bonus} mining fortune")
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
            embed.add_field(name="No Resources Found", value="Better luck next time!", inline=False)
        
        embed.add_field(name="💰 Coins Earned", value=f"+{total_coins} coins", inline=False)
        embed.add_field(name="⭐ Mining XP", value=f"+{total_xp} XP", inline=False)
        embed.add_field(name="⛏️ HOTM XP", value=f"+{hotm_xp} XP", inline=False)
        embed.add_field(name="Current Level", value=f"Mining {new_level}", inline=False)
        
        if hotm_result.get('tier_up'):
            embed.add_field(
                name="🎉 HOTM TIER UP!",
                value=f"Tier {hotm_result['new_tier']} (+{hotm_result['tokens_gained']} tokens)",
                inline=False
            )
        
        await interaction.followup.send(embed=embed)
    
    async def mine_dwarven(self, interaction: discord.Interaction):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("This isn't your menu!", ephemeral=True)
            return
        
        await interaction.response.defer()
        
        from utils.systems.gathering_system import GatheringSystem
        from utils.systems.hotm_system import HeartOfTheMountainSystem
        from utils.systems.dwarven_mines_system import DwarvenMinesSystem
        from utils.event_effects import EventEffects
        import random
        
        skills = await self.bot.db.get_skills(interaction.user.id)
        mining_skill = next((s for s in skills if s['skill_name'] == 'mining'), None)
        mining_level = mining_skill['level'] if mining_skill else 0
        
        if mining_level < 12:
            await interaction.followup.send(
                f"❌ You need Mining Level 12+ to access the Dwarven Mines! (Current: {mining_level})",
                ephemeral=True
            )
            return
        
        equipped_items = await self.bot.db.get_equipped_items(interaction.user.id)
        pickaxe = equipped_items.get('pickaxe')
        if not pickaxe:
            await interaction.followup.send("❌ You need to equip a pickaxe to mine!", ephemeral=True)
            return
        
        tool_id = pickaxe['item_id']
        
        dwarven_progress = await DwarvenMinesSystem.get_dwarven_progress(self.bot.db, interaction.user.id)
        
        if not dwarven_progress['mithril_unlocked']:
            await interaction.followup.send("❌ You haven't unlocked the Dwarven Mines yet! Complete more commissions.", ephemeral=True)
            return
        
        event_effects = EventEffects(self.bot)
        active_events = await event_effects.get_active_events()
        event_multiplier = await event_effects.get_gathering_multiplier() if active_events else 1.0
        xp_multiplier = await event_effects.get_xp_multiplier('mining') if active_events else 1.0
        coin_multiplier = await event_effects.get_coin_multiplier() if active_events else 1.0
        fortune_bonus = await event_effects.get_fortune_bonus('mining') if active_events else 0
        multiplier = await self.bot.db.get_tool_multiplier(interaction.user.id, 'pickaxe')
        
        hotm_stats = await HeartOfTheMountainSystem.calculate_hotm_stats(self.bot.db, interaction.user.id)
        
        ore_types = ['mithril', 'titanium'] if dwarven_progress['titanium_unlocked'] else ['mithril']
        ore_types.extend(['hard_stone', 'coal', 'iron_ingot'])
        
        selected_ores = random.sample(ore_types, k=min(3, len(ore_types)))
        
        total_xp = 0
        total_coins = 0
        items_found = {}
        mithril_powder = 0
        skill_yield_multiplier = 1.0
        skill_drop_multiplier = 1.0
        mining_level = 0
        
        for ore_type in selected_ores:
            result = await GatheringSystem.mine_block(self.bot.db, interaction.user.id, ore_type, {})
            
            if result['success']:
                skill_yield_multiplier = result.get('skill_yield_multiplier', 1.0)
                skill_drop_multiplier = result.get('skill_drop_multiplier', 1.0)
                mining_level = result.get('skill_level', 0)
                
                for drop in result['drops']:
                    item_id = drop['item_id']
                    base_amount = drop['amount']
                    
                    fortune_bonus = hotm_stats.get('mining_fortune', 0)
                    fortune_multiplier = 1.0 + (fortune_bonus / 100)
                    
                    amount = int(base_amount * multiplier * event_multiplier * fortune_multiplier)
                    amount = max(1, amount)
                    
                    await self.bot.db.add_item_to_inventory(interaction.user.id, item_id, amount)
                    await self.bot.db.update_collection(interaction.user.id, item_id, amount)
                    
                    item_name = item_id.replace('_', ' ').title()
                    items_found[item_name] = items_found.get(item_name, 0) + amount
                    
                    if item_id == 'mithril':
                        powder_gain = int(amount * (1.0 + hotm_stats.get('powder_percent', 0) / 100))
                        mithril_powder += powder_gain
                        await DwarvenMinesSystem.update_commission_progress(
                            self.bot.db, interaction.user.id, 'mithril_mining', amount
                        )
                    elif item_id == 'titanium':
                        powder_gain = int(amount * 3 * (1.0 + hotm_stats.get('powder_percent', 0) / 100))
                        mithril_powder += powder_gain
                        await DwarvenMinesSystem.update_commission_progress(
                            self.bot.db, interaction.user.id, 'titanium_mining', amount
                        )
                    elif item_id == 'hard_stone':
                        await DwarvenMinesSystem.update_commission_progress(
                            self.bot.db, interaction.user.id, 'hard_stone_mining', amount
                        )
                
                xp_gained = int(result['xp'] * event_multiplier)
                total_xp += xp_gained
                total_coins += int(xp_gained * 0.8)
        
        total_xp = int(total_xp * xp_multiplier)
        total_coins = int(total_coins * coin_multiplier)
        
        skills = await self.bot.db.get_skills(interaction.user.id)
        mining_skill = next((s for s in skills if s['skill_name'] == 'mining'), None)
        new_level = mining_skill['level'] if mining_skill else 0
        
        if mining_skill:
            new_xp = mining_skill['xp'] + total_xp
            new_level = await self.bot.game_data.calculate_level_from_xp('mining', new_xp)
            await self.bot.db.update_skill(interaction.user.id, 'mining', xp=new_xp, level=new_level)
        
        from utils.systems.achievement_system import AchievementSystem
        await AchievementSystem.check_skill_achievements(self.bot.db, interaction, interaction.user.id, 'mining', new_level)
        
        from utils.systems.badge_system import BadgeSystem
        await BadgeSystem.check_and_unlock_badges(self.bot.db, interaction.user.id, 'skill', skill_name='mining', level=new_level)
        if new_level >= 50:
            await BadgeSystem.check_and_unlock_badges(self.bot.db, interaction.user.id, 'skill_50')
        
        hotm_xp = int(total_xp * 0.8)
        hotm_result = await HeartOfTheMountainSystem.add_hotm_xp(self.bot.db, interaction.user.id, hotm_xp)
        
        if mithril_powder > 0:
            await HeartOfTheMountainSystem.add_powder(self.bot.db, interaction.user.id, 'mithril', mithril_powder)
        
        await self.bot.player_manager.add_coins(interaction.user.id, total_coins)
        
        embed = discord.Embed(
            title="⛏️ Dwarven Mines Session Complete!",
            description=f"Using **{tool_id.replace('_', ' ').title()}** ({multiplier * event_multiplier:.1f}x efficiency)\n**Mining Level {mining_level}** ({skill_yield_multiplier:.2f}x yield, {skill_drop_multiplier:.2f}x drops)\nYou mined in the depths of the Dwarven Mines and found:",
            color=discord.Color.dark_orange()
        )
        
        active_events = await event_effects.get_active_events()
        if active_events and (event_multiplier > 1.0 or xp_multiplier > 1.0 or coin_multiplier > 1.0 or fortune_bonus > 0):
            event_text = "🎪 **Active Event Bonuses:** "
            bonuses = []
            if event_multiplier > 1.0:
                bonuses.append(f"+{int((event_multiplier - 1) * 100)}% gathering")
            if fortune_bonus > 0:
                bonuses.append(f"+{fortune_bonus} mining fortune")
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
            embed.add_field(name="No Resources Found", value="Better luck next time!", inline=False)
        
        embed.add_field(name="💰 Coins Earned", value=f"+{total_coins} coins", inline=False)
        embed.add_field(name="⭐ Mining XP", value=f"+{total_xp} XP", inline=False)
        embed.add_field(name="⛏️ HOTM XP", value=f"+{hotm_xp} XP", inline=False)
        
        if mithril_powder > 0:
            embed.add_field(name="💎 Mithril Powder", value=f"+{mithril_powder}", inline=False)
        
        embed.add_field(name="Current Level", value=f"Mining {new_level}", inline=False)
        
        if hotm_result.get('tier_up'):
            embed.add_field(
                name="🎉 HOTM TIER UP!",
                value=f"Tier {hotm_result['new_tier']} (+{hotm_result['tokens_gained']} tokens)",
                inline=False
            )
        
        await interaction.followup.send(embed=embed)
